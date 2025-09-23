from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, Iterable, Tuple
import json
import re

# ---------- AIMRI 15-category weights (same as your old code) ----------
CATEGORY_WEIGHTS: Dict[str, float] = {
    "01. Technical Infrastructure": 10.0,
    "02. Data Management & Quality": 5.0,
    "03. AI/ML Capabilities": 20.0,
    "04. Talent & Skills": 5.0,
    "05. Governance & Ethics": 5.0,
    "06. Strategic Alignment": 5.0,
    "07. Cultural Readiness": 5.0,
    "08. Process Maturity": 5.0,
    "09. Foundation Model Operations": 5.0,
    "10. Generative AI Capabilities": 5.0,
    "11. Responsible AI & Social Impact": 5.0,
    "12. AI Business Value & ROI": 5.0,
    "13. AI Risk & Resilience": 5.0,
    "14. AI Ecosystem & External Integration": 5.0,
    "15. AI Leadership & Vision": 10.0,
}

# ---------- helpers copied from your old aggregator ----------
def _sort_key(label: str) -> tuple:
    if not isinstance(label, str):
        return (999, 999, str(label))
    nums = re.findall(r"\d+", label)
    if len(nums) == 0:
        return (999, 999, label)
    if len(nums) == 1:
        return (int(nums[0]), 0, label)
    if len(nums) >= 2:
        return (int(nums[0]), int(nums[1]), label)
    return (999, 999, label)

def _round2(x: float) -> float:
    return float(f"{x:.2f}")

def _is_metric_block(d: Any) -> bool:
    if not isinstance(d, dict):
        return False
    if "score" not in d:
        return False
    try:
        float(d["score"])
    except Exception:
        return False
    mappings = d.get("aimri") or d.get("aimri_mapping")
    return isinstance(mappings, list)

def _extract_metric_blocks_from_json(payload: Any) -> Iterable[Dict[str, Any]]:
    if isinstance(payload, dict):
        m = payload.get("metrics")
        if isinstance(m, dict):
            for v in m.values():
                if _is_metric_block(v):
                    yield v
        r = payload.get("results")  # some agents use "results"
        if isinstance(r, dict):
            for v in r.values():
                if _is_metric_block(v):
                    yield v
        for v in payload.values():   # allow top-level { "<id>": metric }
            if _is_metric_block(v):
                yield v

def _normalize_mapping_item(item: Any) -> Tuple[str | None, str | None]:
    if not isinstance(item, dict):
        return (None, None)
    dim = item.get("dimension")
    sub = item.get("subsection")
    dim = dim.strip() if isinstance(dim, str) else None
    sub = sub.strip() if isinstance(sub, str) else None
    return (dim, sub)

def _aggregate_tree(inputs_root: Path) -> Dict[str, Any]:
    subsection_num: Dict[str, float] = {}
    subsection_den: Dict[str, float] = {}
    subsection_contribs: Dict[str, int] = {}

    dimension_num: Dict[str, float] = {}
    dimension_den: Dict[str, float] = {}
    dimension_contribs: Dict[str, int] = {}

    files = sorted(inputs_root.rglob("*.json"))
    metrics_seen = 0
    metrics_used = 0
    files_processed = 0

    for jf in files:
        try:
            data = json.loads(jf.read_text(encoding="utf-8", errors="ignore"))
            files_processed += 1
        except Exception:
            continue

        for metric in _extract_metric_blocks_from_json(data):
            metrics_seen += 1
            try:
                score = float(metric.get("score"))
            except Exception:
                continue

            mappings = metric.get("aimri") or metric.get("aimri_mapping")
            if not isinstance(mappings, list) or not mappings:
                continue

            subs_set = set()
            dims_set = set()
            for item in mappings:
                dim, sub = _normalize_mapping_item(item)
                if sub:
                    subs_set.add(sub)
                if dim:
                    dims_set.add(dim)

            k_subs = len(subs_set)
            k_dims = len(dims_set)

            if k_subs > 0:
                share = 1.0 / k_subs
                for sub in subs_set:
                    subsection_num[sub] = subsection_num.get(sub, 0.0) + score * share
                    subsection_den[sub] = subsection_den.get(sub, 0.0) + share
                    subsection_contribs[sub] = subsection_contribs.get(sub, 0) + 1

            if k_dims > 0:
                share = 1.0 / k_dims
                for dim in dims_set:
                    dimension_num[dim] = dimension_num.get(dim, 0.0) + score * share
                    dimension_den[dim] = dimension_den.get(dim, 0.0) + share
                    dimension_contribs[dim] = dimension_contribs.get(dim, 0) + 1

            if k_subs > 0 or k_dims > 0:
                metrics_used += 1

    subsections: Dict[str, Dict[str, float | int]] = {}
    for sub, den in subsection_den.items():
        if den > 0:
            score = subsection_num.get(sub, 0.0) / den
            subsections[sub] = {
                "score": _round2(score),
                "numerator": _round2(subsection_num.get(sub, 0.0)),
                "denominator": _round2(den),
                "metric_contributions": int(subsection_contribs.get(sub, 0)),
            }

    dimensions: Dict[str, Dict[str, float | int]] = {}
    for dim, den in dimension_den.items():
        if den > 0:
            score = dimension_num.get(dim, 0.0) / den
            dimensions[dim] = {
                "score": _round2(score),
                "numerator": _round2(dimension_num.get(dim, 0.0)),
                "denominator": _round2(den),
                "metric_contributions": int(dimension_contribs.get(dim, 0)),
            }

    return {
        "meta": {
            "inputs_root": str(inputs_root.resolve()),
            "files_processed": files_processed,
            "metrics_seen": metrics_seen,
            "metrics_used": metrics_used,
            "subsections_count": len(subsections),
            "dimensions_count": len(dimensions),
        },
        "subsections": {k: subsections[k] for k in sorted(subsections.keys(), key=_sort_key)},
        "dimensions":  {k: dimensions[k]  for k in sorted(dimensions.keys(),  key=_sort_key)},
    }

def _weighted_final(dimensions: Dict[str, Dict[str, Any]], weights: Dict[str, float]) -> Dict[str, Any]:
    total = sum(weights.values()) or 1.0
    final = 0.0
    breakdown = {}
    for dim, row in dimensions.items():
        s = float(row["score"])
        w = weights.get(dim, 0.0) / total
        final += s * w
        breakdown[dim] = {
            "score": s,
            "weight": round(w, 4),
            "weighted": round(s * w, 4),
        }
    return {"final_score": _round2(final), "breakdown": breakdown}

# ---------- Public scorer API (drop-in) ----------
class ScoringAgent:
    """
    New implementation, old behavior:
    - Read ALL agent JSON outputs under `inputs_root`
    - Aggregate per-dimension scores from metric->AIMRI mappings (even split)
    - Apply CATEGORY_WEIGHTS for overall
    """
    def __init__(self, *, category_weights: Dict[str, float] | None = None):
        self.category_weights = category_weights or CATEGORY_WEIGHTS

    def run(self, inputs_root: str | Path) -> Dict[str, Any]:
        root = Path(inputs_root)
        tree = _aggregate_tree(root)
        # category_scores = simple {dim: score}
        category_scores = {k: float(v["score"]) for k, v in tree["dimensions"].items()}
        # overall
        wf = _weighted_final(tree["dimensions"], self.category_weights)
        overall = float(wf["final_score"])
        return {
            "overall_score": overall,
            "category_scores": category_scores,
            "details": {
                "weights_used": self.category_weights,
                "weighted_breakdown": wf["breakdown"],
                "subsections": tree["subsections"],
                "dimensions": tree["dimensions"],
                "meta": tree["meta"],
            },
        }