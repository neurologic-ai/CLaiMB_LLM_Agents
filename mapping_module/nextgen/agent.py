from __future__ import annotations
import json
from typing import Any, Dict, List, Optional

from openai import OpenAI

from .taxonomy import load_taxonomy, compact_taxonomy


class NextGenAimriMapper:
    """
    Standalone mapper that talks directly to OpenAI SDK.
    Does not depend on BaseMicroAgent; fully self-contained.
    """

    def __init__(
        self,
        taxonomy_path: str,
        model_elaborate: str = "gpt-4o-mini",
        model_map: str = "gpt-4o-mini",
        temperature_elab: float = 0.2,
        temperature_map: float = 0.0,
        api_key: Optional[str] = None,
    ) -> None:
        self.taxonomy_path = taxonomy_path
        self.points = load_taxonomy(taxonomy_path)
        self.client = OpenAI(api_key=api_key) if api_key else OpenAI()
        self.model_elaborate = model_elaborate
        self.model_map = model_map
        self.temperature_elab = temperature_elab
        self.temperature_map = temperature_map

    def _complete(self, system: str, user: str, model: str, temperature: float, max_tokens: int = 512) -> str:
        resp = self.client.chat.completions.create(
            model=model,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            max_tokens=max_tokens,
        )
        return (resp.choices[0].message.content or "").strip()

    def elaborate_metric(self, metric_id: str, short_desc: str) -> str:
        from .prompts import ELABORATE_SYSTEM

        user_prompt = f"Metric: {metric_id}\nShort blurb:\n{short_desc}\n\nExpand now."
        return self._complete(
            system=ELABORATE_SYSTEM,
            user=user_prompt,
            model=self.model_elaborate,
            temperature=self.temperature_elab,
            max_tokens=450,
        )

    def map_elaborated(self, elaborated: str) -> List[Dict[str, Any]]:
        from .prompts import MAP_SYSTEM, MAP_USER_TEMPLATE

        tax_str = compact_taxonomy(self.points)
        user_prompt = MAP_USER_TEMPLATE.replace("{{TAXONOMY}}", tax_str).replace("{{DESC}}", elaborated)
        raw = self._complete(
            system=MAP_SYSTEM,
            user=user_prompt,
            model=self.model_map,
            temperature=self.temperature_map,
            max_tokens=500,
        )

        try:
            data = json.loads(raw)
            items = data.get("mappings", []) if isinstance(data, dict) else []
        except Exception:
            items = []

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

    def map_metric(self, metric_id: str, short_desc: str) -> Dict[str, Any]:
        elaborated = self.elaborate_metric(metric_id, short_desc)
        mappings = self.map_elaborated(elaborated)
        return {
            "metric_id": metric_id,
            "elaborated_description": elaborated,
            "mappings": mappings,
        }

