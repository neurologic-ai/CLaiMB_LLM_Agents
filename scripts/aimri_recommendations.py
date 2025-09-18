# #!/usr/bin/env python3
# from __future__ import annotations
# import argparse
# import json
# import os
# import re
# from pathlib import Path
# from typing import Any, Dict, Iterable, List, Tuple
# from collections import defaultdict
# from loguru import logger

# # --- env / OpenAI ---
# from dotenv import load_dotenv
# load_dotenv()

# try:
#     from openai import OpenAI
# except ImportError:
#     raise SystemExit("Please: pip install openai>=1.0.0 python-dotenv")

# OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# if not OPENAI_API_KEY:
#     raise SystemExit("OPENAI_API_KEY not set. Export it or put it in your .env")

# client = OpenAI(api_key=OPENAI_API_KEY)

# # Configure loguru
# logger.remove()
# logger.add(lambda msg: print(msg, end=""), level="INFO")
# # -------------------------
# # Helpers
# # -------------------------
# def _sort_key(label: str) -> tuple:
#     """Natural sort for '8.4 Operational Excellence' and '08. Process Maturity'."""
#     if not isinstance(label, str):
#         return (999, 999, str(label))
#     nums = re.findall(r"\d+", label)
#     if len(nums) == 0:
#         return (999, 999, label)
#     if len(nums) == 1:
#         return (int(nums[0]), 0, label)
#     return (int(nums[0]), int(nums[1]), label)

# def _round2(x: float) -> float:
#     return float(f"{x:.2f}")

# def _score_float(x: Any, default: float = 3.0) -> float:
#     try:
#         return float(x)
#     except Exception:
#         return default

# def _is_metric_block(d: Any) -> bool:
#     """Metric block must have: numeric score, mappings (aimri/aimri_mapping), and gaps (gaps/gap)."""
#     if not isinstance(d, dict):
#         return False
#     if "score" not in d:
#         return False
#     try:
#         float(d["score"])
#     except Exception:
#         return False
#     has_map = isinstance(d.get("aimri"), list) or isinstance(d.get("aimri_mapping"), list)
#     if not has_map:
#         return False
#     has_gaps = isinstance(d.get("gaps"), list) or isinstance(d.get("gap"), list)
#     return has_gaps

# def _extract_metric_blocks(payload: Any) -> Iterable[Dict[str, Any]]:
#     """Accepts {"metrics": {...}} or {"results": {...}} or top-level dict of metrics."""
#     if not isinstance(payload, dict):
#         return
#     for top in ("metrics", "results"):
#         node = payload.get(top)
#         if isinstance(node, dict):
#             for v in node.values():
#                 if _is_metric_block(v):
#                     yield v
#     for v in payload.values():
#         if _is_metric_block(v):
#             yield v

# def _normalize_mapping_item(item: Any) -> Tuple[str | None, str | None]:
#     """Return (dimension, subsection) if strings; else (None, None)."""
#     if not isinstance(item, dict):
#         return (None, None)
#     dim = item.get("dimension")
#     sub = item.get("subsection")
#     dim = dim.strip() if isinstance(dim, str) else None
#     sub = sub.strip() if isinstance(sub, str) else None
#     return (dim, sub)

# # -------------------------
# # Few-shot: directional extraction
# # -------------------------
# DIR_FEWSHOTS = [
#     # enterprise / ops
#     ("High p90 indicates delays → analyze resolution times for outliers → reduce p90 to ≤90m (unlocks band 4).",
#      "Analyze resolution time outliers and reduce p90 to ≤90m."),
#     ("Execution share low → increase AI execution percentage → achieve ≥50% executions using AI.",
#      "Increase AI execution percentage to ≥50% of executions."),
#     ("Error rate exceeds SLO → implement error tracking and resolution → reduce error rate to ≤0.5%.",
#      "Implement error tracking and resolution to reduce error rate to ≤0.5%."),
#     # code repo / dev env
#     ("Inconsistent naming conventions → standardize naming across the codebase → enhance readability.",
#      "Standardize naming conventions across the codebase."),
#     ("High average complexity → refactor functions into smaller units → target avg complexity ≤10.",
#      "Refactor functions into smaller units to target average complexity ≤10."),
#     # data platform
#     ("No lineage documented → roll out automated lineage → document all tables’ data flows.",
#      "Roll out automated lineage and document data flows for all tables."),
#     ("Sensitive fields untagged → implement sensitive-data tagging policy → monitor compliance.",
#      "Implement sensitive-data tagging policy and monitor compliance."),
#     ("Stale table beyond SLA → fix ingestion pipeline → restore freshness to SLA.",
#      "Fix the ingestion pipeline to restore freshness to SLA."),
#     # cloud / infra
#     ("Underutilized compute → right-size clusters and enable autoscaling → reduce waste.",
#      "Right-size clusters and enable autoscaling to reduce waste."),
#     ("Public exposure detected → lock down security groups and WAF → disable public access.",
#      "Lock down security groups/WAF and disable public access."),
#     # mlops
#     ("Low experiment hygiene → enforce metadata and artifacts → improve reproducibility.",
#      "Enforce metadata and artifacts to improve reproducibility."),
#     ("Weak monitoring coverage → enable drift and performance monitors → alert on anomalies.",
#      "Enable drift/performance monitoring and alert on anomalies."),
# ]

# def llm_extract_directionals(lines: List[str]) -> List[str]:
#     """
#     Extract *directional* (imperative) phrase for each gap sentence.
#     Returns a list of same length; fallback to originals on parse failure.
#     """
#     if not lines:
#         return []

#     system = (
#         "Extract the actionable 'directional' part from each recommendation line. "
#         "Return ONLY concise imperative sentences, no bullets, no quotes."
#     )
#     shots = []
#     for raw, dirx in DIR_FEWSHOTS:
#         shots.append({"role": "user", "content": raw})
#         shots.append({"role": "assistant", "content": dirx})

#     user = (
#         "Return a JSON array of strings containing only the directive for each input line.\n\n"
#         "Input lines:\n" + "\n".join([f"- {t}" for t in lines]) +
#         "\n\nRespond ONLY with a JSON array of strings."
#     )

#     resp = client.chat.completions.create(
#         model=OPENAI_MODEL,
#         temperature=0.0,
#         messages=[{"role": "system", "content": system}] + shots + [{"role": "user", "content": user}],
#     )
#     content = (resp.choices[0].message.content or "").strip()
#     try:
#         out = json.loads(content)
#         if isinstance(out, list) and all(isinstance(x, str) for x in out):
#             if len(out) != len(lines):
#                 out = (out + lines)[:len(lines)]
#             return [x.strip() for x in out]
#     except Exception:
#         pass
#     return lines

# # -------------------------
# # LLM clustering/merging + summarization
# # -------------------------
# def llm_merge_similar(label: str, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
#     """
#     Cluster near-duplicate recommendations and **SUM** their 'importance'.
#     Expect input: [{"text": str, "importance": float, "source": {...}}, ...]
#     Returns: [{"recommendation": str, "importance": float, "members": [str,...]}]
#     """
#     if not items:
#         return []

#     system = (
#         "You merge near-duplicate recommendations and SUM their importance. "
#         "Output a JSON list of objects with keys: recommendation (str), importance (float), members (list[str]). "
#         "Keep the recommendation imperative and concise. If many, keep top 5-10 groups by summed importance."
#     )
#     user = (
#         f"Context label: {label}\n"
#         "Items (JSON):\n" + json.dumps(items, ensure_ascii=False) +
#         "\n\nRespond ONLY with the JSON list."
#     )

#     resp = client.chat.completions.create(
#         model=OPENAI_MODEL,
#         temperature=0.1,
#         messages=[
#             {"role": "system", "content": system},
#             {"role": "user", "content": user},
#         ],
#     )
#     content = (resp.choices[0].message.content or "").strip()
#     try:
#         out = json.loads(content)
#         cleaned: List[Dict[str, Any]] = []
#         for obj in out:
#             rec = str(obj.get("recommendation", "")).strip()
#             if not rec:
#                 continue
#             imp = float(obj.get("importance", 0.0))
#             members = obj.get("members") or []
#             cleaned.append({
#                 "recommendation": rec,
#                 "importance": _round2(imp),
#                 "members": [str(m) for m in members][:5],
#             })
#         return cleaned
#     except Exception:
#         # conservative fallback: lexical merge by lowercased text
#         agg: Dict[str, Dict[str, Any]] = {}
#         for it in items:
#             key = it["text"].strip().lower()
#             bucket = agg.setdefault(key, {"recommendation": it["text"].strip(),
#                                           "importance": 0.0,
#                                           "members": []})
#             bucket["importance"] += float(it.get("importance", 0.0))
#             bucket["members"].append(it["text"])
#         return [{
#             "recommendation": v["recommendation"],
#             "importance": _round2(v["importance"]),
#             "members": v["members"][:25],
#         } for v in agg.values()]

# def llm_summarize(label: str, merged: List[Dict[str, Any]]) -> str:
#     """
#     Short, ranked bullet list (3–6 bullets), descending by importance.
#     """
#     if not merged:
#         return ""
#     system = (
#         "Write a short, ranked bullet list of recommendations (3–6 bullets). "
#         "Start with highest-importance. Each bullet: directive + (importance). No extra commentary."
#     )
#     payload = [{"recommendation": m["recommendation"], "importance": m["importance"]} for m in merged]
#     user = (
#         f"Context: {label}\n"
#         "Merged recommendations (JSON):\n" + json.dumps(payload, ensure_ascii=False) +
#         "\n\nReturn ONLY the bullet list."
#     )
#     resp = client.chat.completions.create(
#         model=OPENAI_MODEL,
#         temperature=0.2,
#         messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
#     )
#     return (resp.choices[0].message.content or "").strip()

# # -------------------------
# # Core aggregation
# # -------------------------
# def aggregate_recommendations(inputs_root: Path, weights_path: Path | None) -> Dict[str, Any]:
#     files = sorted(inputs_root.rglob("*.json"))
#     files_processed = 0
#     metrics_seen = 0
#     metrics_used = 0

#     # Collectors
#     subs_items: Dict[str, List[Dict[str, Any]]] = defaultdict(list)  # subsection -> items
#     subs_raw:   Dict[str, List[Dict[str, Any]]] = defaultdict(list)  # keep raw copies for audit
#     dim_items:  Dict[str, List[Dict[str, Any]]] = defaultdict(list)  # dimension  -> items

#     for jf in files:
#         logger.info(f"Processing file: {jf}")
#         try:
#             data = json.loads(jf.read_text(encoding="utf-8", errors="ignore"))
#             files_processed += 1
#         except Exception as e:
#             logger.warning(f"Skipping unreadable file {jf}: {e}")
#             continue

#         for metric in _extract_metric_blocks(data):
#             metrics_seen += 1
#             metric_id = str(metric.get("metric_id", "unknown"))
#             logger.debug(f"Found metric {metric_id}")
#             score = _score_float(metric.get("score"), 3.0)

#             mappings = metric.get("aimri") or metric.get("aimri_mapping") or []
#             gaps = metric.get("gaps")
#             if gaps is None:
#                 gaps = metric.get("gap")
#             if not isinstance(gaps, list) or not mappings:
#                 continue

#             # unique sets
#             subs_set = set()
#             dims_set = set()
#             for m in mappings:
#                 dim, sub = _normalize_mapping_item(m)
#                 if sub: subs_set.add(sub)
#                 if dim: dims_set.add(dim)

#             if not subs_set and not dims_set:
#                 continue

#             k_subs = max(1, len(subs_set))
#             k_dims = max(1, len(dims_set))

#             # importance shares (per mentor): (5 - score) * (1 / number_of_entries)
#             imp_sub = (5.0 - score) * (1.0 / k_subs) if k_subs > 0 else 0.0
#             imp_dim = (5.0 - score) * (1.0 / k_dims) if k_dims > 0 else 0.0

#             # Extract directional phrases once per metric
#             logger.info(f"Extracting directionals for {len(gaps)} gap(s) in metric {metric_id}")
#             directionals = llm_extract_directionals(gaps)
#             if len(directionals) != len(gaps):
#                 directionals = (directionals + gaps)[:len(gaps)]

#             metric_id = str(metric.get("metric_id", "unknown"))

#             for sub in subs_set:
#                 for raw, dirx in zip(gaps, directionals):
#                     item = {
#                         "text": dirx.strip(),
#                         "importance": imp_sub,
#                         "source": {
#                             "metric_id": metric_id,
#                             "score": score,
#                         },
#                     }
#                     subs_items[sub].append(item)
#                     subs_raw[sub].append(item)

#             for dim in dims_set:
#                 for raw, dirx in zip(gaps, directionals):
#                     item = {
#                         "text": dirx.strip(),
#                         "importance": imp_dim,
#                         "source": {
#                             "metric_id": metric_id,
#                             "score": score,
#                         },
#                     }
#                     dim_items[dim].append(item)

#             metrics_used += 1

#     # Merge + summarize per subsection
#     subsections_out: Dict[str, Any] = {}
#     for sub in sorted(subs_items.keys(), key=_sort_key):
#         logger.info(f"Merging {len(subs_items[sub])} recommendations for subsection {sub}")
#         merged = llm_merge_similar(sub, subs_items[sub])
#         logger.info(f"Summarizing subsection {sub} with {len(merged)} merged items")
#         summary = llm_summarize(sub, merged)
#         total_imp = _round2(sum(float(m["importance"]) for m in merged))
#         subsections_out[sub] = {
#             "merged_recommendations": merged,
#             "summary": summary,
#             "total_importance": total_imp,
#         }

#     # Merge + summarize per dimension (category)
#     dimensions_out: Dict[str, Any] = {}
#     for dim in sorted(dim_items.keys(), key=_sort_key):
#         logger.info(f"Merging {len(subs_items[sub])} recommendations for dimensions {sub}")
#         merged = llm_merge_similar(dim, dim_items[dim])
#         logger.info(f"Summarizing subsection {sub} with {len(merged)} merged items")
#         summary = llm_summarize(dim, merged)
#         total_imp = _round2(sum(float(m["importance"]) for m in merged))
#         dimensions_out[dim] = {
#             "merged_recommendations": merged,
#             "summary": summary,
#             "total_importance": total_imp,
#         }

#     # Apply optional weights
#     weighted_overall = None
#     weights = None
#     if weights_path is not None and weights_path.exists():
#         try:
#             weights = json.loads(weights_path.read_text(encoding="utf-8"))
#             # normalize weights to floats
#             weights = {str(k): float(v) for k, v in weights.items()}
#         except Exception:
#             weights = None

#     if weights:
#         acc = 0.0
#         for dim, obj in dimensions_out.items():
#             w = float(weights.get(dim, 1.0))
#             obj["weight"] = _round2(w)
#             obj["weighted_total_importance"] = _round2(w * float(obj["total_importance"]))
#             acc += w * float(obj["total_importance"])
#         weighted_overall = _round2(acc)
    
#     logger.success(f"Processed {files_processed} files, {metrics_used}/{metrics_seen} metrics used")

#     result = {
#         "meta": {
#             "inputs_root": str(inputs_root.resolve()),
#             "files_processed": files_processed,
#             "metrics_seen": metrics_seen,
#             "metrics_used": metrics_used,
#             "subsections_count": len(subsections_out),
#             "dimensions_count": len(dimensions_out),
#             "model": OPENAI_MODEL,
#             "importance_formula": "(5 - score) * (1 / number_of_entries)",
#             "notes": "number_of_entries is #subsections for subsection items; #dimensions for dimension items",
#             "weights_file": str(weights_path) if weights_path else None,
#         },
#         "subsections": subsections_out,
#         "dimensions": dimensions_out,
#     }
#     if weighted_overall is not None:
#         result["dimension_weighted_overall"] = weighted_overall
#     return result

# # -------------------------
# # CLI
# # -------------------------
# def main():
#     ap = argparse.ArgumentParser(description="AIMRI LLM recommendations (direction → importance → merge → summarize).")
#     ap.add_argument("--inputs-root", required=True, help="Root with agent JSON outputs (recursively).")
#     ap.add_argument("--out", default="data/aimri_recommendations.json", help="Output JSON path.")
#     ap.add_argument("--weights-json", default=None, help="Optional JSON file mapping dimension name → weight.")
#     args = ap.parse_args()

#     inputs_root = Path(args.inputs_root)
#     out_path = Path(args.out)
#     weights_path = Path(args.weights_json) if args.weights_json else None

#     out_path.parent.mkdir(parents=True, exist_ok=True)
#     payload = aggregate_recommendations(inputs_root, weights_path)
#     out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
#     print(f"Wrote {out_path}")

# if __name__ == "__main__":
#     main()