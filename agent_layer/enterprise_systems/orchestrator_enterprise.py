from __future__ import annotations
from typing import Any, Dict, List, Tuple
from datetime import datetime, timezone
from functools import partial

from langchain_core.runnables import RunnableParallel, RunnableLambda

from .registry_enterprise import REGISTRY, CATEGORIES, CATEGORY_WEIGHTS
from .router import route
from .aimri_mapping import ENTERPRISE_METRIC_TO_AIMRI

def now_utc_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")


def _clamp_1to5(v: Any) -> int:
    try:
        n = int(v)
    except Exception:
        n = 3
    return 1 if n < 1 else 5 if n > 5 else n


class EnterpriseOrchestrator:
    """
    Class-based orchestrator that:
      - builds multi-wave execution plan (topological 'Kahn-style' order)
      - runs each wave in parallel via RunnableParallel
      - aggregates category and overall scores
    """

    def __init__(
        self,
        registry: Dict[str, Dict[str, List[str]]] | None = None,
        categories: Dict[str, List[str]] | None = None,
        category_weights: Dict[str, float] | None = None,
    ) -> None:
        self.registry = registry or REGISTRY
        self.categories = categories or CATEGORIES
        self.category_weights = category_weights or CATEGORY_WEIGHTS

    # ---- planning ---------------------------------------------------------
    @staticmethod
    def _compute_waves(registry: Dict[str, Dict[str, List[str]]]) -> List[List[str]]:
        deps = {m: set(info.get("depends_on", [])) for m, info in registry.items()}
        remaining = set(registry.keys())
        waves: List[List[str]] = []

        while remaining:
            wave = sorted([m for m in remaining if not deps[m]])
            if not wave:
                raise ValueError("Cycle or invalid dependencies in REGISTRY.")
            waves.append(wave)
            remaining -= set(wave)
            for m in remaining:
                deps[m] -= set(wave)
        return waves

    @staticmethod
    def _avg(nums: List[float]) -> float:
        return round(sum(nums) / len(nums), 2) if nums else 0.0

    def _aggregate(self, results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Build category averages (1..5) and weighted overall using CATEGORY_WEIGHTS.
        """
        category_scores: Dict[str, float] = {}
        for cat, metric_ids in self.categories.items():
            vals = [
                float(results[m]["score"])
                for m in metric_ids
                if m in results and "score" in results[m]
            ]
            category_scores[cat] = self._avg(vals)

        overall = round(
            category_scores.get("data_management", 0.0) * self.category_weights.get("data_management", 0.0)
            + category_scores.get("analytics_readiness", 0.0) * self.category_weights.get("analytics_readiness", 0.0),
            2,
        )
        return {"categories": category_scores, "overall": overall}

    # ---- execution --------------------------------------------------------
    def run(self, snapshot: Dict[str, Any], verbose: bool = False) -> Tuple[Dict[str, Any], Dict[str, Any], List[List[str]]]:
        """
        Execute DAG in deterministic waves:
        - Each wave runs in parallel (RunnableParallel)
        - Children waves run after parents complete
        Returns: (results_by_metric, scores, waves)
        """
        waves = self._compute_waves(self.registry)
        raw_results: Dict[str, Dict[str, Any]] = {}
        ctx = {"snapshot": snapshot, "results": raw_results}

        for i, wave in enumerate(waves):
            tools = {m: route(m) for m in wave}
            parallel = RunnableParallel(
                **{m: RunnableLambda(lambda _inp, _m=m, _f=tools[m]: _f(ctx)) for m in wave}
            )
            out_map = parallel.invoke({})
            for m in wave:
                raw_results[m] = out_map[m]
            if verbose:
                print(f"Wave {i}: {', '.join(wave)}")

        # ---- normalize + inject mapping, convert band/Score -> score(1..5) ----
        results: Dict[str, Dict[str, Any]] = {}
        for m, r in raw_results.items():
            canonical_id = (r or {}).get("MetricID") or (r or {}).get("metric_id") or m
            score = _clamp_1to5(r.get("Score", r.get("band", r.get("score", 3))))
            obj: Dict[str, Any] = {
                "metric_id": canonical_id,
                "score": score,  # <-- your requested field (1..5)
                "rationale": r.get("rationale", "Limited evidence."),
                "flags": r.get("flags", []) or [],
                "gaps": r.get("gaps", []) or [],
                "aimri_mapping": ENTERPRISE_METRIC_TO_AIMRI.get(canonical_id, []),
            }
            results[m] = obj

        
        scores = self._aggregate(results)
        return results, scores, waves