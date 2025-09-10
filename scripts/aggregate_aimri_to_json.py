#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

import re

def _sort_key(label: str) -> tuple:
    """
    Turn subsection/dimension labels like '8.4 Operational Excellence'
    into a numeric tuple (8, 4, 'Operational Excellence') for natural ordering.
    Works for both dimensions ('08. Process Maturity') and subsections ('8.4 ...').
    """
    if not isinstance(label, str):
        return (999, 999, str(label))

    # match like "08. Process Maturity" or "8.4 Operational Excellence"
    nums = re.findall(r"\d+", label)
    if len(nums) == 0:
        return (999, 999, label)
    if len(nums) == 1:
        return (int(nums[0]), 0, label)
    if len(nums) >= 2:
        return (int(nums[0]), int(nums[1]), label)
    return (999, 999, label)

def _is_metric_block(d: Any) -> bool:
    """A metric block must have a numeric 'score' and 'aimri' or 'aimri_mapping' as a list."""
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
    """
    Extract metric blocks from a JSON payload.

    Accepts shapes like:
    - {"metrics": { "<id>": {...metric...}, ... }}
    - {"results": { "<id>": {...metric...}, ... }}   # <— add this
    - { "<id>": {...metric...}, ... }  (top-level mapping)
    """
    if isinstance(payload, dict):
        # shape 1: nested under "metrics"
        m = payload.get("metrics")
        if isinstance(m, dict):
            for v in m.values():
                if _is_metric_block(v):
                    yield v

        # shape 2: nested under "results"  <-- ADD THIS BLOCK
        r = payload.get("results")
        if isinstance(r, dict):
            for v in r.values():
                if _is_metric_block(v):
                    yield v

        # shape 3: top-level keys
        for v in payload.values():
            if _is_metric_block(v):
                yield v


def _normalize_mapping_item(item: Any) -> Tuple[str | None, str | None]:
    """Return (dimension, subsection) or (None, None) if unusable."""
    if not isinstance(item, dict):
        return (None, None)
    dim = item.get("dimension")
    sub = item.get("subsection")
    if isinstance(dim, str):
        dim = dim.strip()
    else:
        dim = None
    if isinstance(sub, str):
        sub = sub.strip()
    else:
        sub = None
    return (dim, sub)


def _round2(x: float) -> float:
    return float(f"{x:.2f}")


def aggregate_tree(inputs_root: Path) -> Dict[str, Any]:
    """
    Recursively read all *.json under inputs_root and compute:
      - per-subsection weighted scores
      - per-dimension weighted scores

    Weighting rule per metric:
      If metric maps to k subsections:
        numerator += score*(1/k)
        denominator += 1/k
      (deduped per metric)
    """
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
            # skip unreadable file
            continue

        for metric in _extract_metric_blocks_from_json(data):
            metrics_seen += 1

            # score
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

    # Build tables
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
        "subsections": {
            k: subsections[k]
            for k in sorted(subsections.keys(), key=_sort_key)
        },
        "dimensions": {
            k: dimensions[k]
            for k in sorted(dimensions.keys(), key=_sort_key)
        },
    }


def main():
    ap = argparse.ArgumentParser(description="Aggregate AIMRI scores (JSON → JSON).")
    ap.add_argument("--inputs-root", required=True, help="Root folder containing agent outputs (recursively).")
    ap.add_argument("--out", default="aimri_aggregate.json", help="Output JSON path.")
    args = ap.parse_args()

    root = Path(args.inputs_root)
    result = aggregate_tree(root)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()