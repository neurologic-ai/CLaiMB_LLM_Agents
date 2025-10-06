# agent_layer/dev_env_scanner/slicing.py
from __future__ import annotations
import os
from typing import Any, Dict, List, Optional, Tuple
from data_collection_agents.dev_env_scanner_agent.base_agent import BaseMicroAgent

from agent_layer.dev_env_scanner.wrappers import SLICE_RULES 

# Tunables (env overridable)
SNIPPET_MAX_CHARS = int(os.getenv("CODE_REPO_SNIPPET_MAX_CHARS", "1600"))   # ~500–700 tokens/snippet
BATCH_MAX_CHARS   = int(os.getenv("CODE_REPO_BATCH_MAX_CHARS",   "12000"))  # ~4k tokens/user msg

def _combine_results(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(a or {})
    def _to_band(x):
        try: return int(x)
        except Exception: return 3
    out["band"] = min(_to_band(a.get("band", 3)), _to_band(b.get("band", 3)))

    ra, rb = str(a.get("rationale", "")).strip(), str(b.get("rationale", "")).strip()
    if ra and rb: out["rationale"] = f"{ra} | {rb}"
    else: out["rationale"] = ra or rb or "No rationale."

    def _merge(xs, ys):
        seen, res = set(), []
        for v in (xs or []) + (ys or []):
            sv = str(v)
            if sv not in seen:
                seen.add(sv); res.append(sv)
        return res

    out["flags"] = _merge(a.get("flags", []), b.get("flags", []))
    out["gaps"]  = _merge(a.get("gaps",  []), b.get("gaps",  []))
    return out


def _evaluate_with_slicing(
    agent: BaseMicroAgent,
    metric_id: str,
    code_snippets: List[str],
    *,
    context: Dict[str, Any] | None = None
) -> Dict[str, Any]:
    # 1) Find rule
    rule = SLICE_RULES.get(metric_id, {})
    k: int = int(rule.get("k", 0) or 0)
    filters: Optional[Tuple[str, ...]] = rule.get("filters")

    # 2) Filter by keywords (case-insensitive); keep all if none matched
    selected = list(code_snippets or [])
    if filters:
        lf = tuple(str(f).lower() for f in filters)
        filtered = [s for s in selected if any(f in s.lower() for f in lf)]
        if filtered:
            selected = filtered

    # 3) Guarantee we have something
    if not selected:
        selected = code_snippets[:1]

    # 4) Truncate every snippet hard to prevent monsters
    selected = [ (s or "")[:SNIPPET_MAX_CHARS] for s in selected ]

    # 5) If k <= 0, use only batch-size budget; else also honor k per chunk
    def _make_batches(snips: List[str]) -> List[List[str]]:
        batches: List[List[str]] = []
        cur: List[str] = []
        cur_chars = 0
        for s in snips:
            s_len = len(s)
            # if adding this snippet blows batch budget, flush current batch
            if cur and (cur_chars + s_len) > BATCH_MAX_CHARS:
                batches.append(cur)
                cur, cur_chars = [], 0

            cur.append(s)
            cur_chars += s_len

            # also respect k if configured
            if k > 0 and len(cur) >= k:
                batches.append(cur)
                cur, cur_chars = [], 0

        if cur:
            batches.append(cur)
        return batches

    batches = _make_batches(selected)

    agg: Optional[Dict[str, Any]] = None
    for ch in batches:
        res = agent.evaluate(ch, context=context)
        agg = res if agg is None else _combine_results(agg, res)

    return agg