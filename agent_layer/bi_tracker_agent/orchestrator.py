# agent_layer/orchestrator.py
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from langchain_core.runnables import RunnableLambda, RunnableParallel


from agent_layer.bi_tracker_agent.registry import LEVEL0, LEVEL1_DEPS, CATEGORIES
from agent_layer.bi_tracker_agent.tool_loader import load_tool
from agent_layer.bi_tracker_agent.aimri_mapping import METRIC_TO_AIMRI


class BIOrchestrator:
    """
    Class-based orchestrator for BI Tracker.
    - Runs Level 0 metrics in parallel
    - Runs Level 1 metrics sequentially with dependency ordering
    - Normalizes and attaches AIMRI mappings to each metric
    - Aggregates categories and overall score
    """

    def __init__(self, out_dir: Optional[Path] = None) -> None:
        self.out_dir = Path(out_dir) if out_dir else None

    # ----------------- Helpers -----------------
    @staticmethod
    def _now_id(prefix: str = "bi-tracker") -> str:
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
        return f"{prefix}-{ts}"

    @staticmethod
    def _clamp_score(v: Any) -> float:
        try:
            x = int(v)
            return float(1 if x < 1 else 5 if x > 5 else x)
        except Exception:
            return 3.0

    def _normalize_metric(self, mid: str, m: Dict[str, Any]) -> Dict[str, Any]:
        m = dict(m or {})
        if "score" not in m:
            m["score"] = self._clamp_score(m.get("band", 3))
        else:
            m["score"] = self._clamp_score(m["score"])
        if "band" in m:
            del m["band"]

        m["aimri"] = METRIC_TO_AIMRI.get(mid, [])
        m["metric_id"] = mid
        return m

    def _aggregate(self, metrics: Dict[str, Dict[str, Any]]) -> Dict[str, float]:
        cat_scores: Dict[str, float] = {}
        overall = 0.0
        tot_cat_w = 0.0

        for cat, spec in CATEGORIES.items():
            cat_w = float(spec.get("weight", 0.5))
            met_weights: Dict[str, float] = spec.get("metrics", {})
            s = sum(met_weights.values()) or 1.0

            score = 0.0
            for m_id, w in met_weights.items():
                sc = self._clamp_score(metrics.get(m_id, {}).get("score", 3))
                score += (float(w) / s) * sc

            score = round(score, 2)
            cat_scores[cat] = score
            overall += cat_w * score
            tot_cat_w += cat_w

        overall_score = round(overall / tot_cat_w, 2) if tot_cat_w else 0.0
        return {**cat_scores, "overall_score": overall_score}

    # ----------------- Main Run -----------------
    def run(self, snapshot: Dict[str, Any], out_dir: Optional[Path] = None) -> Dict[str, Any]:
        """
        Deterministic execution:
        - Level 0 (parallel, no deps)
        - Level 1 (ordered by simple dependency list; no fan-in of outputs yet)
        - Aggregation (categories → overall)
        - Embed AIMRI mapping inside each metric result (`metrics[mid]["aimri"]`)

        If out_dir is provided, writes ./<out_dir>/<run_id>.json
        """
        load_dotenv()

        # ----- Level 0 in parallel -----
        l0_tools = {mid: RunnableLambda(lambda s, _m=mid: load_tool(_m)(s)) for mid in LEVEL0}
        l0_parallel = RunnableParallel(**l0_tools)
        l0_out: Dict[str, Dict[str, Any]] = l0_parallel.invoke(snapshot)

        # ----- Level 1 sequential (deps only for ordering) -----
        l1_out: Dict[str, Dict[str, Any]] = {}
        for mid, deps in LEVEL1_DEPS.items():
            # _missing is unused now, but kept for future checks/logging if needed
            _missing = [d for d in deps if d not in l0_out]
            l1_out[mid] = load_tool(mid)(snapshot)

        # ----- Merge, normalize, and embed AIMRI per metric -----
        raw_metrics: Dict[str, Dict[str, Any]] = {**l0_out, **l1_out}
        metrics: Dict[str, Dict[str, Any]] = {}

        for mid, m in raw_metrics.items():
            nm = self._normalize_metric(mid, m)  # <-- pass both args
            metrics[mid] = nm

        # ----- Aggregate -----
        aggregates = self._aggregate(metrics)

        # ----- Final payload -----
        result: Dict[str, Any] = {
            "run_id": self._now_id(),
            "metrics": metrics,
            "aggregates": aggregates,
        }

        # ----- Persistence -----
        dest_dir = out_dir or self.out_dir
        if dest_dir is not None:
            dest_dir = Path(dest_dir)
            dest_dir.mkdir(parents=True, exist_ok=True)
            artifact = dest_dir / f"{result['run_id']}.json"
            artifact.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
            result["artifact_path"] = str(artifact)

        return result


# ---- Optional functional wrapper (keeps old imports working) ----
def run(snapshot: Dict[str, Any], out_dir: Optional[Path] = None) -> Dict[str, Any]:
    orch = BIOrchestrator(out_dir=out_dir)
    return orch.run(snapshot, out_dir=out_dir)