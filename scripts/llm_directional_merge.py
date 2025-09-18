# from __future__ import annotations
# import argparse
# import json
# import os
# import re
# import time
# from pathlib import Path
# from typing import Any, Dict, Iterable, List, Tuple
# from collections import defaultdict
# from concurrent.futures import ThreadPoolExecutor, as_completed

# from dotenv import load_dotenv
# from loguru import logger

# load_dotenv()

# try:
#     from openai import OpenAI
#     from openai import APIError, RateLimitError, APITimeoutError
# except Exception as e:
#     raise SystemExit("Please install OpenAI SDK v1+: pip install openai") from e

# OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# if not OPENAI_API_KEY:
#     raise SystemExit("OPENAI_API_KEY is missing. Put it in your .env or shell.")
# client = OpenAI(api_key=OPENAI_API_KEY)

# MAX_WORKERS = int(os.getenv("LLM_MAX_WORKERS", "4"))
# BATCH_SIZE = 30  # gaps per LLM call for extraction

# # -------------------------
# # Utilities
# # -------------------------
# def _sort_key(label: str) -> tuple:
#     """Sort '8.4 Operational Excellence' naturally → (8,4,...)"""
#     if not isinstance(label, str):
#         return (999, 999, str(label))
#     nums = re.findall(r"\d+", label)
#     if len(nums) == 0:
#         return (999, 999, label)
#     if len(nums) == 1:
#         return (int(nums[0]), 0, label)
#     return (int(nums[0]), int(nums[1]), label)

# def _is_metric_block(d: Any) -> bool:
#     """
#     A metric block must have 'gaps' (or 'gap') list and an AIMRI mapping.
#     We do NOT require 'score' here (LLM-only step).
#     """
#     if not isinstance(d, dict):
#         return False
#     has_gaps = isinstance(d.get("gaps"), list) or isinstance(d.get("gap"), list)
#     has_map = isinstance(d.get("aimri"), list) or isinstance(d.get("aimri_mapping"), list)
#     return has_gaps and has_map

# def _extract_metric_blocks(payload: Any) -> Iterable[Dict[str, Any]]:
#     """
#     Accept shapes like:
#       - {"metrics": { "<id>": {...}, ...}}
#       - {"results": { "<id>": {...}, ...}}
#       - or top-level mapping { "<id>": {...}, ...}
#     """
#     if not isinstance(payload, dict):
#         return
#     for top_key in ("metrics", "results"):
#         node = payload.get(top_key)
#         if isinstance(node, dict):
#             for v in node.values():
#                 if _is_metric_block(v):
#                     yield v
#     for v in payload.values():
#         if _is_metric_block(v):
#             yield v

# def _normalize_mapping_item(item: Any) -> Tuple[str | None, str | None]:
#     if not isinstance(item, dict):
#         return (None, None)
#     dim = item.get("dimension")
#     sub = item.get("subsection")
#     return (dim.strip() if isinstance(dim, str) else None,
#             sub.strip() if isinstance(sub, str) else None)

# # -------------------------
# # LLM helpers (with retries)
# # -------------------------
# def _chat(messages: List[Dict[str, str]], temperature: float = 0.0, max_retries: int = 5) -> str:
#     """Thin wrapper around chat.completions with basic retry/backoff."""
#     delay = 1.0
#     for attempt in range(1, max_retries + 1):
#         try:
#             resp = client.chat.completions.create(
#                 model=OPENAI_MODEL,
#                 temperature=temperature,
#                 messages=messages,
#             )
#             return resp.choices[0].message.content or ""
#         except (RateLimitError, APITimeoutError, APIError) as e:
#             logger.warning(f"LLM call failed (attempt {attempt}/{max_retries}): {e}")
#             if attempt == max_retries:
#                 raise
#             time.sleep(delay)
#             delay = min(delay * 2, 10.0)
#     return ""

# # Few-shot for directional extraction
# DIR_FEWSHOTS = [
#     ("High p90 indicates delays → analyze resolution times for outliers → reduce p90 to ≤90m (unlocks band 4).",
#      "Analyze resolution time outliers and reduce p90 to ≤90m."),
#     ("Execution share low → increase AI execution percentage → achieve ≥50% executions using AI.",
#      "Increase AI execution percentage to ≥50% of executions."),
#     ("Inconsistent naming conventions → standardize naming across the codebase → enhance readability.",
#      "Standardize naming conventions across the codebase."),
#     ("No lineage documented → roll out automated lineage → document all tables’ data flows.",
#      "Roll out automated lineage and document data flows for all tables."),
#     ("Sensitive fields untagged → implement sensitive-data tagging policy → monitor compliance.",
#      "Implement sensitive-data tagging policy and monitor compliance."),
# ]

# def _llm_extract_directional(lines: List[str]) -> List[str]:
#     """Extract the actionable/imperative phrasing for each gap line."""
#     if not lines:
#         return []
#     system = (
#         "You extract ONLY the actionable 'directional' part of each recommendation line. "
#         "Return concise imperative sentences. Return a JSON array of strings."
#     )
#     shots = []
#     for raw, dirx in DIR_FEWSHOTS:
#         shots.append({"role": "user", "content": raw})
#         shots.append({"role": "assistant", "content": dirx})

#     user = (
#         "Extract the directional/actionable part of each input line. "
#         "Respond ONLY with a JSON array of strings (same length as input).\n\n"
#         "Input lines:\n" + "\n".join([f"- {t}" for t in lines])
#     )
#     content = _chat(
#         messages=[{"role": "system", "content": system}] + shots + [{"role": "user", "content": user}],
#         temperature=0.0,
#     ).strip()

#     try:
#         out = json.loads(content)
#         if isinstance(out, list) and all(isinstance(s, str) for s in out):
#             # keep length aligned
#             if len(out) != len(lines):
#                 out = (out + lines)[:len(lines)]
#             return [s.strip() for s in out]
#     except Exception:
#         logger.debug("LLM didn't return valid JSON; falling back to raw lines.")
#     return [s.strip() for s in lines]

# def _llm_merge_similar(label: str, lines: List[str], max_items: int = 8) -> List[Dict[str, Any]]:
#     """
#     Ask the LLM to cluster near-duplicates without weights.
#     Returns list of {"recommendation": str, "members": [str,...]} (≤ max_items).
#     """
#     if not lines:
#         return []
#     system = (
#         "Cluster near-duplicate recommendations into a small set of distinct items. "
#         "For each cluster, provide: "
#         '{"recommendation": str (concise imperative), "members": [str,...]}. '
#         f"Keep at most {max_items} clusters. Return ONLY a JSON array of objects."
#     )
#     user = (
#         f"Context label: {label}\n"
#         "Input recommendations (JSON array of strings):\n" + json.dumps(lines, ensure_ascii=False)
#     )
#     content = _chat(
#         messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
#         temperature=0.1,
#     ).strip()

#     try:
#         arr = json.loads(content)
#         cleaned = []
#         for obj in arr:
#             rec = str(obj.get("recommendation", "")).strip()
#             members = obj.get("members") or []
#             if rec:
#                 cleaned.append({
#                     "recommendation": rec,
#                     "members": [str(m).strip() for m in members][:50],
#                     "count": len(members) if isinstance(members, list) else 1,
#                 })
#         # sort by cluster size desc
#         cleaned.sort(key=lambda x: x.get("count", 0), reverse=True)
#         return cleaned[:max_items]
#     except Exception:
#         logger.debug("Merge LLM returned non-JSON; fallback to naive distinct list.")
#         # naive unique list
#         uniq = list(dict.fromkeys([s.strip() for s in lines if s.strip()]))
#         return [{"recommendation": u, "members": [u], "count": 1} for u in uniq[:max_items]]

# def _llm_summarize(label: str, merged: List[Dict[str, Any]]) -> str:
#     """Create a short bullet summary ranked by cluster size."""
#     if not merged:
#         return ""
#     system = (
#         "Write a short bullet summary (3–6 bullets) of the merged recommendations. "
#         "Rank by cluster size (count). Each bullet: imperative + (count). No extra commentary."
#     )
#     payload = [{"recommendation": m["recommendation"], "count": m.get("count", 1)} for m in merged]
#     user = (
#         f"Label: {label}\n"
#         "Merged items (JSON):\n" + json.dumps(payload, ensure_ascii=False) +
#         "\nReturn ONLY the bullet list."
#     )
#     return _chat(
#         messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
#         temperature=0.2,
#     ).strip()

# # -------------------------
# # Core: collect → extract → merge → summarize
# # -------------------------
# def collect_inputs(inputs_root: Path):
#     """Scan all JSON files and collect gap lines per subsection and per dimension."""
#     files = sorted(inputs_root.rglob("*.json"))
#     files_processed = 0
#     metrics_seen = 0
#     subs_gaps: Dict[str, List[str]] = defaultdict(list)
#     dim_gaps: Dict[str, List[str]] = defaultdict(list)

#     for jf in files:
#         try:
#             data = json.loads(jf.read_text(encoding="utf-8", errors="ignore"))
#             files_processed += 1
#         except Exception as e:
#             logger.warning(f"Skipping unreadable JSON: {jf} ({e})")
#             continue

#         for metric in _extract_metric_blocks(data):
#             metrics_seen += 1

#             gaps = metric.get("gaps")
#             if gaps is None:
#                 gaps = metric.get("gap")
#             if not isinstance(gaps, list) or not gaps:
#                 continue

#             mappings = metric.get("aimri") or metric.get("aimri_mapping") or []
#             subs_set, dims_set = set(), set()
#             for item in mappings:
#                 dim, sub = _normalize_mapping_item(item)
#                 if sub: subs_set.add(sub)
#                 if dim: dims_set.add(dim)

#             if not subs_set and not dims_set:
#                 continue

#             # append raw gaps for every mapped subsection/dimension
#             for sub in subs_set:
#                 subs_gaps[sub].extend([str(g).strip() for g in gaps if str(g).strip()])
#             for dim in dims_set:
#                 dim_gaps[dim].extend([str(g).strip() for g in gaps if str(g).strip()])

#     return files_processed, metrics_seen, subs_gaps, dim_gaps

# def process_label(label: str, raw_lines: List[str]) -> Tuple[str, Dict[str, Any]]:
#     """
#     Extract directionals (batched), merge similar with LLM, and summarize.
#     Returns (label, payload).
#     """
#     logger.info(f"[start] {label} ({len(raw_lines)} gap lines)")
#     # 1) Extract directionals in batches
#     dir_all: List[str] = []
#     for i in range(0, len(raw_lines), BATCH_SIZE):
#         batch = raw_lines[i:i+BATCH_SIZE]
#         extracted = _llm_extract_directional(batch)
#         dir_all.extend(extracted)

#     # 2) Merge near-duplicates
#     merged = _llm_merge_similar(label, dir_all, max_items=8)

#     # 3) Summarize
#     summary = _llm_summarize(label, merged)

#     out = {
#         "total_raw_lines": len(raw_lines),
#         "directionals_count": len(dir_all),
#         "merged_recommendations": merged,   # [{"recommendation","members","count"}]
#         "summary": summary,
#     }
#     logger.info(f"[done]  {label} → {len(merged)} merged, {len(dir_all)} directionals")
#     return label, out

# def run_llm_pipeline(inputs_root: Path) -> Dict[str, Any]:
#     files_processed, metrics_seen, subs_gaps, dim_gaps = collect_inputs(inputs_root)
#     logger.info(f"Files processed: {files_processed} | metric blocks: {metrics_seen}")
#     logger.info(f"Subsections: {len(subs_gaps)} | Dimensions: {len(dim_gaps)}")

#     subsections_out: Dict[str, Any] = {}
#     dimensions_out: Dict[str, Any] = {}

#     # Parallel per-subsection
#     logger.info(f"Processing subsections in parallel (max_workers={MAX_WORKERS})…")
#     with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
#         futs = [ex.submit(process_label, sub, subs_gaps[sub]) for sub in subs_gaps.keys()]
#         for f in as_completed(futs):
#             label, payload = f.result()
#             subsections_out[label] = payload

#     # Parallel per-dimension
#     logger.info(f"Processing dimensions in parallel (max_workers={MAX_WORKERS})…")
#     with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
#         futs = [ex.submit(process_label, dim, dim_gaps[dim]) for dim in dim_gaps.keys()]
#         for f in as_completed(futs):
#             label, payload = f.result()
#             dimensions_out[label] = payload

#     # Sort keys for stable output
#     subsections_out = {k: subsections_out[k] for k in sorted(subsections_out.keys(), key=_sort_key)}
#     dimensions_out  = {k: dimensions_out[k]  for k in sorted(dimensions_out.keys(),  key=_sort_key)}

#     return {
#         "meta": {
#             "inputs_root": str(inputs_root.resolve()),
#             "files_processed": files_processed,
#             "metrics_seen": metrics_seen,
#             "subsections_count": len(subsections_out),
#             "dimensions_count": len(dimensions_out),
#             "model": OPENAI_MODEL,
#             "notes": "LLM-only (directional extraction + merge + summarize). No scoring.",
#         },
#         "subsections": subsections_out,
#         "dimensions": dimensions_out,
#     }

# # -------------------------
# # CLI
# # -------------------------
# def main():
#     ap = argparse.ArgumentParser(description="LLM-only: Extract directionals, merge & summarize recommendations.")
#     ap.add_argument("--inputs-root", required=True, help="Root folder containing agent output JSONs (recursively).")
#     ap.add_argument("--out", default="aimri_directional_merged.json", help="Output JSON path.")
#     args = ap.parse_args()

#     inputs_root = Path(args.inputs_root)
#     out_path = Path(args.out)
#     out_path.parent.mkdir(parents=True, exist_ok=True)

#     logger.remove()
#     logger.add(lambda m: print(m, end=""), level="INFO")

#     logger.info(f"Starting LLM pipeline | model={OPENAI_MODEL} | root={inputs_root}")
#     payload = run_llm_pipeline(inputs_root)
#     out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
#     logger.info(f"Wrote {out_path}")

# if __name__ == "__main__":
#     main()