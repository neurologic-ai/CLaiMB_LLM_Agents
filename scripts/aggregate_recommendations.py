# #!/usr/bin/env python3
# """
# Aggregate & prioritize recommendations across all agent outputs.

# What it does (per your mentor's guidance):
# 1) Parses every JSON under --inputs-root (recursively).
# 2) For each metric:
#    - Extracts *directional recommendations* from `gaps`/`gap` (keeps only the action part).
#    - Computes per-recommendation importance = (5 - metric_score) * (1 / k),
#      where k = number of recommendations extracted for that metric.
#    - Assigns each recommendation to *every mapped subsection* (and its parent dimension).
# 3) Deduplicates/merges similar recommendations *within the same subsection*
#    using fuzzy matching (no external deps).
#    - When merged, importance values are SUMMED.
# 4) Rolls up to dimensions. Optionally applies weights if provided.
# 5) Writes a single JSON with sorted subsections (like "8.1", "8.2", …)
#    and a dimension rollup.

# Input folder shape:
# - agent_layer_outputs/
#    ├── bi_tracker.json
#    ├── enterprise_systems.json
#    ├── ml_ops.json
#    ├── data_platform.json
#    └── ... (any other *.json)

# Run:
#   python aggregate_recommendations.py \
#       --inputs-root agent_layer_outputs \
#       --out mentor_prioritized_recos.json \
#       --dimension-weights weights.json     # (optional)

# weights.json example:
# {
#   "08. Process Maturity": 0.60,
#   "02. Data Management & Quality": 0.40
# }
# """

# from __future__ import annotations
# import argparse
# import json
# import re
# from dataclasses import dataclass, field
# from pathlib import Path
# from typing import Any, Dict, Iterable, List, Optional, Tuple
# from difflib import SequenceMatcher


# # ----------------------------
# # Parsing & normalizing helpers
# # ----------------------------

# def _sort_key(label: str) -> tuple:
#     """
#     Turn labels like:
#       - '08. Process Maturity'
#       - '8.4 Operational Excellence'
#     into numeric tuples for natural ordering:
#       ('8.4 ...') -> (8, 4, '...')
#       ('08. ...') -> (8, 0, '...')
#     """
#     if not isinstance(label, str):
#         return (999, 999, str(label))
#     nums = re.findall(r"\d+", label)
#     if len(nums) == 0:
#         return (999, 999, label)
#     if len(nums) == 1:
#         return (int(nums[0]), 0, label)
#     return (int(nums[0]), int(nums[1]), label)


# def _is_metric_block(d: Any) -> bool:
#     """A metric block must have a numeric 'score' and have 'aimri' OR 'aimri_mapping' list."""
#     if not isinstance(d, dict):
#         return False
#     if "score" not in d:
#         return False
#     try:
#         float(d["score"])
#     except Exception:
#         return False
#     mappings = d.get("aimri") or d.get("aimri_mapping")
#     return isinstance(mappings, list)


# def _extract_metric_blocks_from_json(payload: Any) -> Iterable[Dict[str, Any]]:
#     """
#     Accepts shapes like:
#     - {"metrics": { "<id>": {...metric...}, ... }}
#     - { "<id>": {...metric...}, ... }  (top-level mapping)
#     - {"results": { "<id>": {...metric...}, ... }}  (seen in Data Platform)
#     """
#     if not isinstance(payload, dict):
#         return

#     # shape 1: nested under "metrics"
#     m = payload.get("metrics")
#     if isinstance(m, dict):
#         for v in m.values():
#             if _is_metric_block(v):
#                 yield v

#     # shape 2: nested under "results"
#     r = payload.get("results")
#     if isinstance(r, dict):
#         for v in r.values():
#             if _is_metric_block(v):
#                 yield v

#     # shape 3: top-level keys
#     for v in payload.values():
#         if _is_metric_block(v):
#             yield v


# def _normalize_mapping_item(item: Any) -> Tuple[Optional[str], Optional[str]]:
#     """Return (dimension, subsection) or (None, None)."""
#     if not isinstance(item, dict):
#         return (None, None)
#     dim = item.get("dimension")
#     sub = item.get("subsection")
#     dim = dim.strip() if isinstance(dim, str) else None
#     sub = sub.strip() if isinstance(sub, str) else None
#     return (dim, sub)


# # ----------------------------
# # Recommendation extraction
# # ----------------------------

# # Patterns to peel off the *action* part from a gap string.
# ARROW_SPLIT = re.compile(r"→|->|=>|⇒|➔|➜")
# LEADING_PHRASE = re.compile(
#     r"^(?:fix|improve|increase|reduce|add|implement|enforce|enable|establish|standardize|complete|refactor|monitor|"
#     r"automate|introduce|right-size|set up|configure|tighten|conduct|train|deploy|create|document|"
#     r"optimi[sz]e|validate|restructure|harden|cache|retry|alert)\b",
#     re.IGNORECASE
# )

# def _extract_actions_from_gap(g: str) -> List[str]:
#     """
#     Heuristic to keep only the *directional* part of a gap line.
#     Strategy:
#       1) If the string contains an arrow, take the RIGHTMOST side (after the last arrow).
#       2) Else, if we see an imperative verb at the start, keep as-is.
#       3) Else, try to split on '→' semantics within text (e.g., 'X ... → do Y').
#       4) Else, drop if it's purely diagnostic.
#     Returns 0..N action phrases (usually 0 or 1).
#     """
#     if not isinstance(g, str):
#         return []

#     s = g.strip()
#     if not s:
#         return []

#     # Prefer rightmost arrow split
#     if ARROW_SPLIT.search(s):
#         parts = ARROW_SPLIT.split(s)
#         last = parts[-1].strip().strip(".; ")
#         if last:
#             return [last]

#     # If starts with imperative, keep as-is
#     if LEADING_PHRASE.search(s):
#         t = s.strip().strip(".; ")
#         return [t] if t else []

#     # Sometimes "Do X to achieve Y" — try extracting after 'to ' if it looks imperative
#     m = re.search(r"\bto\b\s+(.*)$", s, flags=re.IGNORECASE)
#     if m:
#         tail = m.group(1).strip().strip(".; ")
#         if tail:
#             return [tail]

#     # If we find a clause with verbs like 'implement/standardize/etc' anywhere, try to keep from there.
#     m2 = re.search(r"(implement|standardize|complete|refactor|monitor|automate|introduce|right-size|set up|configure|tighten|conduct|train|deploy|create|document|optimi[sz]e|validate|restructure|harden|cache|retry|alert)\b.*", s, flags=re.IGNORECASE)
#     if m2:
#         t = s[m2.start():].strip().strip(".; ")
#         if t:
#             return [t]

#     # Otherwise treat as diagnostic (no action extracted)
#     return []


# def _collect_gaps(metric: Dict[str, Any]) -> List[str]:
#     """
#     Normalize gaps array:
#       - Some agents use 'gaps', some used 'gap'.
#       - Ensure list of strings.
#     """
#     raw = metric.get("gaps")
#     if raw is None:
#         raw = metric.get("gap")
#     if raw is None:
#         return []
#     if isinstance(raw, str):
#         raw = [raw]
#     if isinstance(raw, list):
#         return [str(x) for x in raw if isinstance(x, (str, int, float))]
#     return []


# # ----------------------------
# # Clustering / merging helpers
# # ----------------------------

# def _normalize_for_match(s: str) -> str:
#     s = s.lower().strip()
#     s = re.sub(r"[^a-z0-9\s]", " ", s)
#     s = re.sub(r"\s+", " ", s)
#     return s


# def _similar(a: str, b: str, threshold: float = 0.82) -> bool:
#     ra = _normalize_for_match(a)
#     rb = _normalize_for_match(b)
#     if not ra or not rb:
#         return False
#     return SequenceMatcher(None, ra, rb).ratio() >= threshold


# @dataclass
# class RecItem:
#     text: str
#     importance: float
#     sources: List[str] = field(default_factory=list)     # metric_ids
#     samples: List[str] = field(default_factory=list)     # raw original gap lines


# # ----------------------------
# # Main aggregation
# # ----------------------------

# def aggregate_recommendations(
#     inputs_root: Path,
#     dimension_weights: Optional[Dict[str, float]] = None
# ) -> Dict[str, Any]:
#     """
#     Walk all JSON files; extract + score + merge recommendations per subsection,
#     then roll up to dimensions. Optionally apply dimension weights.
#     """
#     files = sorted(inputs_root.rglob("*.json"))
#     files_processed = 0
#     metrics_seen = 0
#     metrics_used = 0

#     # subsection -> list[RecItem]
#     subsection_recs: Dict[str, List[RecItem]] = {}
#     # subsection -> set(dimensions) (for roll-up consistency)
#     subsection_dims: Dict[str, set] = {}

#     # dimension totals (after merging)
#     # we'll compute later by summing subsection totals under each dimension
#     for jf in files:
#         try:
#             data = json.loads(jf.read_text(encoding="utf-8", errors="ignore"))
#             files_processed += 1
#         except Exception:
#             continue

#         for metric in _extract_metric_blocks_from_json(data):
#             metrics_seen += 1

#             # score
#             try:
#                 score = float(metric.get("score"))
#             except Exception:
#                 continue

#             # mappings
#             mappings = metric.get("aimri") or metric.get("aimri_mapping")
#             if not isinstance(mappings, list) or not mappings:
#                 continue

#             # Collect unique subsections & dimensions for this metric
#             subs_set, dims_set = set(), set()
#             for item in mappings:
#                 dim, sub = _normalize_mapping_item(item)
#                 if sub:
#                     subs_set.add(sub)
#                 if dim:
#                     dims_set.add(dim)

#             # Extract action items from gaps
#             gaps = _collect_gaps(metric)
#             actions: List[str] = []
#             raw_to_action: Dict[str, List[str]] = {}
#             for g in gaps:
#                 acts = _extract_actions_from_gap(g)
#                 if acts:
#                     actions.extend(acts)
#                     raw_to_action[g] = acts

#             # If a metric has no actionable gaps, skip (we don't want diagnostics only)
#             k = len(actions)
#             if k == 0:
#                 continue

#             # Importance per recommendation
#             per_importance = max(0.0, (5.0 - score)) * (1.0 / k)

#             metric_id = str(metric.get("metric_id") or "")

#             # Assign each action to every mapped subsection
#             for sub in subs_set:
#                 subsection_dims.setdefault(sub, set()).update(dims_set)
#                 lst = subsection_recs.setdefault(sub, [])
#                 for act in actions:
#                     lst.append(
#                         RecItem(
#                             text=act,
#                             importance=per_importance,
#                             sources=[metric_id] if metric_id else [],
#                             samples=[k for k, vs in raw_to_action.items() if act in vs]
#                         )
#                     )

#             metrics_used += 1

#     # ---- Merge duplicates (within each subsection) ----
#     merged_subsections: Dict[str, List[Dict[str, Any]]] = {}
#     for sub, items in subsection_recs.items():
#         clusters: List[List[RecItem]] = []
#         for it in items:
#             placed = False
#             for cluster in clusters:
#                 # Compare with cluster representative (first item)
#                 if _similar(it.text, cluster[0].text):
#                     cluster.append(it)
#                     placed = True
#                     break
#             if not placed:
#                 clusters.append([it])

#         # Reduce clusters
#         merged_list: List[Dict[str, Any]] = []
#         for cl in clusters:
#             # pick a representative (use the most frequent shortest string)
#             rep = sorted(cl, key=lambda r: (len(_normalize_for_match(r.text)), r.text))[0]
#             text = rep.text
#             importance_sum = round(sum(x.importance for x in cl), 4)
#             sources = sorted({sid for x in cl for sid in x.sources if sid})
#             sample_gaps = []
#             for x in cl:
#                 for s in x.samples:
#                     if s not in sample_gaps:
#                         sample_gaps.append(s)
#             merged_list.append({
#                 "text": text,
#                 "importance": importance_sum,
#                 "sources": sources,
#                 "examples": sample_gaps[:5]
#             })

#         # sort by importance desc, then alpha
#         merged_subsections[sub] = sorted(merged_list, key=lambda d: (-d["importance"], d["text"]))

#     # ---- Compute subsection totals and map to dimensions ----
#     subsections_out: Dict[str, Dict[str, Any]] = {}
#     dim_totals: Dict[str, float] = {}
#     for sub in merged_subsections:
#         recs = merged_subsections[sub]
#         total_importance = round(sum(r["importance"] for r in recs), 4)
#         dims = sorted(subsection_dims.get(sub, set()), key=_sort_key)
#         subsections_out[sub] = {
#             "total_importance": total_importance,
#             "dimensions": dims,
#             "recommendations": recs
#         }
#         # distribute total into each parent dimension (subsection belongs to a single dimension in practice,
#         # but we tolerate multiple just in case)
#         for d in dims or []:
#             dim_totals[d] = dim_totals.get(d, 0.0) + total_importance

#     # ---- Build dimensions table (optional weighting) ----
#     dimensions_out: Dict[str, Dict[str, Any]] = {}
#     for dim, total in dim_totals.items():
#         if dimension_weights and dim in dimension_weights:
#             w = float(dimension_weights[dim])
#             dimensions_out[dim] = {
#                 "total_importance": round(total, 4),
#                 "weight": w,
#                 "weighted_importance": round(total * w, 4)
#             }
#         else:
#             dimensions_out[dim] = {
#                 "total_importance": round(total, 4)
#             }

#     # ---- Top-N overall (across all subsections) ----
#     flat_all: List[Tuple[str, Dict[str, Any]]] = []
#     for sub, payload in subsections_out.items():
#         for r in payload["recommendations"]:
#             flat_all.append((sub, r))
#     top_overall = sorted(flat_all, key=lambda t: -t[1]["importance"])[:50]
#     top_overall_out = [
#         {
#             "subsection": sub,
#             "text": r["text"],
#             "importance": r["importance"],
#             "sources": r.get("sources", [])
#         }
#         for sub, r in top_overall
#     ]

#     # ---- Final JSON ----
#     return {
#         "meta": {
#             "inputs_root": str(inputs_root.resolve()),
#             "files_processed": files_processed,
#             "metrics_seen": metrics_seen,
#             "metrics_used": metrics_used,
#             "subsections_count": len(subsections_out),
#             "dimensions_count": len(dimensions_out),
#             "notes": [
#                 "Importance per recommendation = (5 - metric_score) * (1 / k), k = #actionable recommendations extracted for that metric.",
#                 "Recommendations are deduplicated/merged per subsection via fuzzy matching (difflib, threshold=0.82).",
#                 "Totals at dimension level are sums of subsection totals. Optional weights scale totals."
#             ]
#         },
#         "subsections": {
#             k: subsections_out[k]
#             for k in sorted(subsections_out.keys(), key=_sort_key)
#         },
#         "dimensions": {
#             k: dimensions_out[k]
#             for k in sorted(dimensions_out.keys(), key=_sort_key)
#         },
#         "top_recommendations_overall": top_overall_out
#     }


# # ----------------------------
# # CLI
# # ----------------------------

# def main():
#     ap = argparse.ArgumentParser(description="Aggregate & prioritize recommendations (JSON → JSON).")
#     ap.add_argument("--inputs-root", required=True, help="Root folder containing agent outputs (recursively).")
#     ap.add_argument("--out", default="mentor_prioritized_recos.json", help="Output JSON path.")
#     ap.add_argument("--dimension-weights", default=None, help="Optional JSON file: {dimension: weight, ...}.")
#     args = ap.parse_args()

#     inputs_root = Path(args.inputs_root)
#     if not inputs_root.exists():
#         raise SystemExit(f"inputs-root not found: {inputs_root}")

#     weights = None
#     if args.dimension_weights:
#         wpath = Path(args.dimension_weights)
#         if wpath.exists():
#             try:
#                 weights = json.loads(wpath.read_text(encoding="utf-8"))
#             except Exception:
#                 weights = None

#     result = aggregate_recommendations(inputs_root, weights)

#     out_path = Path(args.out)
#     out_path.parent.mkdir(parents=True, exist_ok=True)
#     out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
#     print(f"Wrote {out_path}")


# if __name__ == "__main__":
#     main()