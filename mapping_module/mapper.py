from __future__ import annotations
import json
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from pathlib import Path
import yaml

from data_collection_agents.enterprise_systems_agent.base_agent import BaseMicroAgent
from mapping_module.prompts import ELABORATE_SYSTEM, MAP_SYSTEM, MAP_USER_TEMPLATE




@dataclass
class AimriPoint:
    id: str
    name: str
    dimension: str
    aliases: List[str]


def load_taxonomy(path: str) -> List[AimriPoint]:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    pts: List[AimriPoint] = []
    for p in data.get("points", []):
        pts.append(
            AimriPoint(
                id=str(p["id"]),
                name=p["name"],
                dimension=p.get("dimension", ""),
                aliases=[a.lower() for a in (p.get("aliases") or [])],
            )
        )
    return pts


def _compact_taxonomy(points: List[AimriPoint]) -> str:
    # Provide only essentials to the model for determinism & lower token usage
    minimal = [{"id": p.id, "name": p.name, "aliases": p.aliases} for p in points]
    return json.dumps(minimal, ensure_ascii=False, separators=(",", ":"))


class AimriMapperAgent(BaseMicroAgent):
    """
    Uses BaseMicroAgent._call_llm for a 2-hop flow:
      1) Elaborate each metric's short description.
      2) Ask for top-3 AIMRI points with confidences (strict JSON).
    """

    def __init__(
        self,
        taxonomy_path: str = "configs/aimri_points.yaml",
        model_elaborate: str = "gpt-4o-mini",
        model_map: str = "gpt-4o-mini",
        temperature_elab: float = 0.2,
        temperature_map: float = 0.0,
        api_key: Optional[str] = None,
    ):
        super().__init__(model=model_map, temperature=temperature_map, api_key=api_key)
        self.taxonomy_path = taxonomy_path
        self.points = load_taxonomy(taxonomy_path)
        self.model_elaborate = model_elaborate
        self.temperature_elab = temperature_elab

    # ---- Hop 1: elaborate the metric description ----
    def elaborate_metric(self, metric_id: str, short_desc: str) -> str:
        user_prompt = f"Metric: {metric_id}\nShort blurb:\n{short_desc}\n\nExpand now."
        # temporarily change model/temperature for elaboration
        prev_model, prev_temp = self.model, self.temperature
        self.model, self.temperature = self.model_elaborate, self.temperature_elab
        out = self._call_llm(prompt=user_prompt, system_prompt=ELABORATE_SYSTEM, max_tokens=450)
        self.model, self.temperature = prev_model, prev_temp
        return (out or "").strip()

    # ---- Hop 2: ask for top-3 AIMRI mappings ----
    def map_elaborated(self, elaborated: str) -> List[Dict[str, Any]]:
        tax_str = _compact_taxonomy(self.points)
        user_prompt = MAP_USER_TEMPLATE.replace("{{TAXONOMY}}", tax_str).replace("{{DESC}}", elaborated)
        raw = self._call_llm(prompt=user_prompt, system_prompt=MAP_SYSTEM, max_tokens=500)
        try:
            data = self._parse_json_response(raw)
            items = data.get("mappings", []) if isinstance(data, dict) else []
        except Exception:
            items = []

        # validate IDs and enrich with dimension/name from taxonomy
        by_id = {p.id: p for p in self.points}
        results: List[Dict[str, Any]] = []
        for it in items[:3]:
            pid = str(it.get("point_id", "")).strip()
            if pid in by_id:
                p = by_id[pid]
                results.append(
                    {
                        "point_id": p.id,
                        "point_name": p.name,
                        "dimension": p.dimension,
                        "confidence": round(float(it.get("confidence", 0.0)), 3),
                        "rationale": (it.get("rationale", "") or "")[:500],
                    }
                )
        results.sort(key=lambda r: r["confidence"], reverse=True)
        return results[:3]

    # ---- Public single-call API used by your orchestrator/batch ----
    def map_metric(self, metric_id: str, short_desc: str) -> Dict[str, Any]:
        elaborated = self.elaborate_metric(metric_id, short_desc)
        mappings = self.map_elaborated(elaborated)
        return {
            "metric_id": metric_id,
            "elaborated_description": elaborated,
            "mappings": mappings,
        }

    # ---- Optional: batch API expected by your BaseMicroAgent interface ----
    def evaluate(self, code_snippets: List[str], context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Here we treat each 'code_snippet' as a metric short description string.
        context can carry: metric_ids (same length), taxonomy_path override, etc.
        """
        metric_ids = (context or {}).get("metric_ids", [])
        out: List[Dict[str, Any]] = []
        for i, desc in enumerate(code_snippets):
            mid = metric_ids[i] if i < len(metric_ids) else f"metric_{i+1}"
            out.append(self.map_metric(mid, desc))
        return {"results": out}
