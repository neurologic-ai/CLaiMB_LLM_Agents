# # agent_layer/dev_env_scanner/improved_orchestrator.py
# from __future__ import annotations
# from functools import lru_cache
# from typing import Any, Dict, Iterable, List, Optional, Tuple

# from agent_layer.dev_env_scanner.registry import LEVEL0, LEVEL1_DEPS, CATEGORIES, SLICE_RULES
# from agent_layer.dev_env_scanner.router import route, route_many

# # ---------------------------
# # Chunking / small utilities
# # ---------------------------
# def chunk_snippet(text: str, max_chars: int = 8_000) -> List[str]:
#     """Split text into ~token-safe chunks; break on line boundaries."""
#     lines = text.splitlines(keepends=True)
#     chunks, cur, cur_len = [], [], 0
#     for line in lines:
#         if cur and cur_len + len(line) > max_chars:
#             chunks.append("".join(cur)); cur, cur_len = [], 0
#         cur.append(line); cur_len += len(line)
#     if cur:
#         chunks.append("".join(cur))
#     return chunks

# def _dedupe(seq: Iterable[str], limit: int) -> List[str]:
#     seen, out = set(), []
#     for item in seq:
#         if item not in seen:
#             out.append(item); seen.add(item)
#         if len(out) >= limit:
#             break
#     return out

# def slice_snippets(snips: List[str], k: int, filters: Optional[Tuple[str, ...]]) -> List[str]:
#     """Case-insensitive filter + cap to k."""
#     if not snips:
#         return []
#     if filters:
#         lf = tuple(s.lower() for s in filters)
#         filtered = [s for s in snips if any(f in s.lower() for f in lf)]
#         if filtered:
#             snips = filtered
#     return snips[:k]

# # --------------------------------
# # Runnable-aware chunking evaluator
# # --------------------------------
# def evaluate_with_chunking(runnable, metric_id: str, code_snippets: List[str]) -> Dict[str, Any]:
#     """
#     runnable: a RunnableLambda from route(metric_id) — call with .invoke(snapshot)
#     Aggregates worst band; merges rationale/flags/gaps.
#     """
#     combined: Dict[str, Any] = {"metric_id": metric_id, "band": 5, "flags": [], "gaps": [], "rationale": ""}

#     for snippet in code_snippets:
#         for chunk in chunk_snippet(snippet):
#             res = _cached_eval(metric_id, chunk, runnable)
#             combined["band"] = min(combined["band"], int(res.get("band", 3)))
#             r = (res.get("rationale") or "").strip()
#             if len(r) > len(combined["rationale"]):
#                 combined["rationale"] = r
#             combined["flags"].extend(res.get("flags", []))
#             combined["gaps"].extend(res.get("gaps", []))
#     combined["flags"] = _dedupe(combined["flags"], 10)
#     combined["gaps"]  = _dedupe(combined["gaps"], 6)
#     return combined

# @lru_cache(maxsize=1024)
# def _cached_eval(metric_id: str, chunk: str, _ignored) -> Dict[str, Any]:
#     """Cache per (metric_id, chunk). Router runnable is stable per metric, so we ignore it in the key."""
#     from agent_layer.dev_env_scanner.router import route  # late import to keep cache key stable
#     runnable = route(metric_id)
#     snapshot = {"code_snippets": [chunk], "file_paths": []}
#     return runnable.invoke(snapshot)  # IMPORTANT: use .invoke(..) with RunnableLambda

# # ---------------------------
# # Orchestrator
# # ---------------------------
# class ImprovedCodeRepoOrchestrator:
#     def __init__(self, *, prefix: str = "code-repo") -> None:
#         self.prefix = prefix

#     def _now(self) -> str:
#         from datetime import datetime, timezone
#         return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")

#     def run(self, snapshot: Dict[str, Any]) -> Dict[str, Any]:
#         # L0 in parallel (your RunnableParallel stays in the old orchestrator; here we call directly)
#         l0 = {mid: run.invoke(snapshot) for mid, run in route_many(LEVEL0).items()}

#         # L1 sequential; apply per-metric slicing/chunking for snippet-driven metrics
#         l1: Dict[str, Dict[str, Any]] = {}
#         for mid, _deps in LEVEL1_DEPS.items():
#             rule = SLICE_RULES.get(mid, {"k": 8, "filters": None})
#             cs   = snapshot.get("code_snippets", []) or []
#             runnable = route(mid)
#             if rule.get("k", 0) > 0:
#                 cs_f = slice_snippets(cs, rule.get("k", 8), rule.get("filters"))
#                 l1[mid] = evaluate_with_chunking(runnable, mid, cs_f)
#             else:
#                 l1[mid] = runnable.invoke(snapshot)

#         raw = {**l0, **l1}
#         metrics = self._normalize(raw)
#         aggregates = self._aggregate(metrics)
#         return {"run_id": f"{self.prefix}-{self._now()}", "metrics": metrics, "aggregates": aggregates}

#     def _normalize(self, raw: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
#         out: Dict[str, Dict[str, Any]] = {}
#         for mid, m in (raw or {}).items():
#             band = int(m.get("band", m.get("score", 3)))
#             band = 1 if band < 1 else 5 if band > 5 else band
#             out[mid] = {
#                 "metric_id": mid,
#                 "score": band,
#                 "rationale": m.get("rationale", "No rationale."),
#                 "flags": m.get("flags", []),
#                 "gaps": m.get("gaps", []),
#             }
#         return out

#     def _aggregate(self, metrics: Dict[str, Dict[str, Any]]) -> Dict[str, float]:
#         totals: Dict[str, float] = {}
#         overall = 0.0
#         tot_w = 0.0
#         for cat, spec in CATEGORIES.items():
#             w = float(spec.get("weight", 0.5))
#             met_w: Dict[str, float] = spec.get("metrics", {})
#             s = sum(met_w.values()) or 1.0
#             sc = 0.0
#             for mid, mw in met_w.items():
#                 sc += (mw / s) * float(metrics.get(mid, {}).get("score", 3))
#             sc = round(sc, 2)
#             totals[cat] = sc
#             overall += w * sc
#             tot_w += w
#         totals["overall_score"] = round(overall / tot_w, 2) if tot_w else 0.0
#         return totals