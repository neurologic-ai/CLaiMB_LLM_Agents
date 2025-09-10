# workflows/monitor_workflow.py
from __future__ import annotations
from typing import Dict, Any, List, Iterable, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from textwrap import shorten
import os, json, time

from loguru import logger

from agent_layer.cloud_infra_agent.aimri_mapping import CLOUD_INFRA_METRIC_TO_AIMRI
from agent_layer.cloud_infra_agent.registry import CATEGORIES, LEVEL0, LEVEL1_DEPS
from agent_layer.cloud_infra_agent.tool_loader import load_function
from data_collection_agents.cloud_infra_agent.logging_utils import timed

# ---------------------------
# Helpers for formatting logs
# ---------------------------

def _short(s: str, width: int = 180) -> str:
    return shorten((s or "").replace("\n", " ").strip(), width=width, placeholder="...")

def _metric_line(m: dict) -> str:
    mid = m.get("metric_id", "?")
    score = m.get("score", "—")
    band = m.get("band") or (m.get("evidence") or {}).get("band")
    cat  = m.get("category") or (m.get("evidence") or {}).get("category")
    rat  = _short(m.get("rationale", ""))

    gaps = m.get("gaps") or []
    flags = m.get("flags") or (m.get("evidence") or {}).get("flags") or []
    if isinstance(flags, dict): flags = list(flags.keys())
    if flags and not isinstance(flags, list): flags = [str(flags)]

    band_s = f" | band={band}" if band is not None else ""
    cat_s  = f" | category={cat}" if cat else ""
    gf = f" | gaps={len(gaps)}" if gaps else ""
    ff = f" | flags={len(flags)}" if flags else ""
    return f"[{mid}] score={score}{band_s}{cat_s} | {rat}{gf}{ff}"

class debug_timed:
    """DEBUG-only timer that prints exactly like your target format."""
    def __init__(self, section: str):
        self.section = section
        self.t0 = 0.0
    def __enter__(self):
        self.t0 = time.perf_counter()
        logger.debug(f"▶️ start: {self.section}")
        return self
    def __exit__(self, exc_type, exc, tb):
        dur_ms = (time.perf_counter() - self.t0) * 1000.0
        # note the two spaces after colon to match example: "✅ done:  LLM.call ..."
        logger.debug(f"✅ done:  {self.section} ({dur_ms:.2f} ms)")

#Helper for aimri mapping
def _aimri_for(metric_id: str) -> List[Dict[str, str]]:
    """Return AIMRI mapping for a Cloud Infra metric."""
    return CLOUD_INFRA_METRIC_TO_AIMRI.get(metric_id, [])


# ---------------------------
# Core setup / ingest
# ---------------------------

# Known metrics (strict allow-list)
KNOWN_METRICS = (
    set(LEVEL0)
    | set(LEVEL1_DEPS.keys())
    | {m for cat in CATEGORIES.values() for m in (cat.get("metrics", {}) or {}).keys()}
)

def setup(config: Dict[str, Any]) -> Dict[str, Any]:
    return config or {}

def ingest(context: Dict[str, Any]) -> Dict[str, Any]:
    return context or {}

def _ctx_for(metric_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
    c = context.get(metric_id, {})
    if isinstance(c, dict) and c and "params" not in c:
        return {"params": c}
    return c

# ---------- DAG-based execution ----------
# L0 = everything listed in LEVEL0 that is NOT explicitly a Level-1 metric
L0_PARALLEL: List[str] = [m for m in LEVEL0 if m not in LEVEL1_DEPS]
# All L1 candidates come from the LEVEL1_DEPS keys
L1_ALL: List[str] = sorted(LEVEL1_DEPS.keys())

def _present_in_ctx(metric_id: str, ctx: Dict[str, Any]) -> bool:
    """Treat exact key as present."""
    return (metric_id in ctx)

def _call_metric(metric_id: str, ctx_for_metric: Dict[str, Any]) -> dict:
    """Run a metric with the single-dict calling convention; add DEBUG LLM timing + INFO summary."""
    fn = load_function(metric_id)  # dotted id
    with timed(f"metric.{metric_id}"):
        try:
            with debug_timed("LLM.call"):
                out = fn(ctx_for_metric) or {}
        except Exception as e:
            logger.exception(f"[runner] Exception in metric '{metric_id}': {e}")
            return {
                "metric_id": metric_id,
                "score": 0.0,
                "rationale": f"runner exception: {e}",
                "gaps": [],
                "evidence": {},
                "aimri_mapping": _aimri_for(metric_id),
            }

    out.setdefault("metric_id", metric_id)
    out["aimri_mapping"] = _aimri_for(metric_id)
    logger.info(_metric_line(out))
    return out

def _run_parallel_stable(metric_ctx_map: Dict[str, Dict[str, Any]], max_workers: int) -> Dict[str, Any]:
    """Run a set of metrics in parallel. Deterministic submission + keyed assembly."""
    results: Dict[str, Any] = {}
    if not metric_ctx_map:
        return results

    ordered = sorted(metric_ctx_map.items(), key=lambda kv: kv[0])
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futs = {pool.submit(_call_metric, m, c): m for m, c in ordered}
        for fut in as_completed(futs):
            m = futs[fut]
            try:
                results[m] = fut.result()
            except Exception as e:
                logger.exception(f"[runner] Exception collecting future for '{m}': {e}")
                results[m] = {"metric_id": m, "score": 0.0, "rationale": f"runner exception (future): {e},","aimri_mapping": _aimri_for(m),}
    return results

# ---------- aggregation helpers ----------
def _normalize(weights: Dict[str, float]) -> Dict[str, float]:
    total = sum(w for w in weights.values() if isinstance(w, (int, float)))
    if total <= 0:
        n = len(weights) or 1
        return {k: 1.0 / n for k in weights}
    return {k: float(w) / total for k, w in weights.items()}

def _score_of(v: Any):
    return v.get("score") if isinstance(v, dict) else None

def aggregate(results: Dict[str, Any], config: Dict[str, Any] | None = None) -> Dict[str, Any]:
    cfg = config or {}

    # Allow runtime overrides but keep base structure
    cat_cfg = {k: dict(v) for k, v in CATEGORIES.items()}
    if "category_weights" in cfg:
        for c, w in cfg["category_weights"].items():
            if c in cat_cfg:
                cat_cfg[c]["weight"] = w
    if "metric_weights" in cfg:
        for c, mws in cfg["metric_weights"].items():
            if c in cat_cfg and isinstance(mws, dict):
                cat_cfg[c]["metrics"] = {**cat_cfg[c].get("metrics", {}), **mws}

    cat_w_norm = _normalize({c: meta.get("weight", 0.0) for c, meta in cat_cfg.items()})
    breakdown, category_scores = [], {}
    overall_acc = overall_used = 0.0

    for c, meta in cat_cfg.items():
        mw = meta.get("metrics", {}) or {}
        mw_norm = _normalize(mw) if mw else {}
        parts, acc, used = [], 0.0, 0.0
        for m, w in mw_norm.items():
            sc = _score_of(results.get(m))
            parts.append({"metric": m, "weight": w, "score": sc})
            if isinstance(sc, (int, float)):
                acc += w * sc
                used += w
        cat_score = (acc / used) if used > 0 else None
        category_scores[c] = cat_score
        cw = cat_w_norm.get(c, 0.0)
        breakdown.append({"name": c, "weight": cw, "effective_weight_sum": used, "metrics": parts})
        if isinstance(cat_score, (int, float)) and cw > 0:
            overall_acc += cw * cat_score
            overall_used += cw

    overall_score = (overall_acc / overall_used) if overall_used > 0 else None
    simple_scores = [v.get("score") for v in results.values()
                     if isinstance(v, dict) and isinstance(v.get("score"), (int, float))]
    simple_avg = (sum(simple_scores) / len(simple_scores)) if simple_scores else None

    return {
        "overall_score": overall_score,
        "category_scores": category_scores,
        "breakdown": breakdown,
        "simple_average_debug": simple_avg,
        "count_metrics": len(results),
        "scored_metrics": len(simple_scores),
    }

def report(results: Dict[str, Any], summary: Dict[str, Any]) -> Dict[str, Any]:
    return {"metrics": results, "summary": summary}

def _save_json(path: str, data: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def _summarize_end(results: Dict[str, Any], summary: Dict[str, Any], out_path: str) -> None:
    # Top 5 lowest scores
    scored: List[Tuple[str, float]] = [
        (m, v.get("score")) for m, v in results.items()
        if isinstance(v, dict) and isinstance(v.get("score"), (int, float))
    ]
    scored.sort(key=lambda x: (x[1], x[0]))
    worst = scored[:5]

    cats = summary.get("category_scores", {}) or {}
    cats_line = ", ".join([
        f"{c}={cats[c]:.2f}" if isinstance(cats[c], (int, float)) else f"{c}=—"
        for c in sorted(cats.keys())
    ])

    overall = summary.get("overall_score")
    simple_avg = summary.get("simple_average_debug")

    def _fmt(v): return f"{v:.2f}" if isinstance(v, (int, float)) else "—"

    logger.info("🟩 RUN SUMMARY")
    logger.info(f"• overall={_fmt(overall)} | simple_avg={_fmt(simple_avg)}")
    logger.info(f"• categories: {cats_line or '—'}")
    if worst:
        worst_line = "; ".join([f"{m}={s:.1f}" for m, s in worst])
        logger.info(f"• top risks: {worst_line}")
    else:
        logger.info("• top risks: —")
    logger.info(f"• saved: {out_path}")

# ---------- Orchestrator (L0 parallel + L1 waves) ----------
def run_workflow(config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    with timed("setup"):
        cfg = setup(config)
    with timed("ingest"):
        ctx = ingest(context)

    # Header exactly in the order/wording you requested
    present = sorted(ctx.keys())
    logger.info(f"📦 context: {len(present)} inputs → {present}")
    logger.info("🟦 RUN START")
    run_id = cfg.get("run_id", "(auto)")
    max_workers = int(cfg.get("max_workers", 8))
    logger.info(f"• run_id={run_id} • max_workers={max_workers}")

    # -------- Level 0: Parallel island --------
    l0_planned = [m for m in L0_PARALLEL if _present_in_ctx(m, ctx)]
    logger.info(f"🔹 L0 parallel: {len(l0_planned)} metrics → {l0_planned}")
    l0_ctx_map = {m: _ctx_for(m, ctx) for m in l0_planned}

    with timed("L0.parallel"):
        results: Dict[str, Any] = _run_parallel_stable(l0_ctx_map, max_workers=max_workers)

    # -------- Level 1: Parallel waves (deps → deps outputs injected) --------
    remaining = {m for m in L1_ALL if _present_in_ctx(m, ctx)}
    logger.info(f"🔶 L1 candidates: {len(remaining)} → {sorted(remaining)}")

    wave_index = 0
    while remaining:
        ready = [m for m in sorted(remaining) if all(d in results for d in LEVEL1_DEPS.get(m, []))]
        if not ready:
            # deps missing for the remaining; record and break
            for m in sorted(remaining):
                missing = [d for d in LEVEL1_DEPS.get(m, []) if d not in results]
                logger.warning(f"⏭️  skip '{m}' (missing deps {missing})")
                results[m] = {
                    "metric_id": m,
                    "score": 0.0,
                    "rationale": f"skipped: unsatisfied dependencies {missing}",
                    "aimri_mapping": _aimri_for(m), 
                }
            break

        logger.info(f"🔸 L1 wave#{wave_index}: {len(ready)} → {ready}")
        wave_ctx_map: Dict[str, Dict[str, Any]] = {}
        for m in ready:
            base = _ctx_for(m, ctx)  # preserves {"params": ...}
            deps_payload = {d: results[d] for d in LEVEL1_DEPS.get(m, [])}
            merged = dict(base)
            merged["deps"] = deps_payload
            wave_ctx_map[m] = merged

        with timed(f"L1.wave#{wave_index}.parallel"):
            wave_results = _run_parallel_stable(wave_ctx_map, max_workers=max_workers)
        results.update(wave_results)
        remaining.difference_update(ready)
        wave_index += 1

    # -------- Aggregate + Save --------
    with timed("aggregate"):
        summ = aggregate(results, cfg)
    final = report(results, summ)

    output_path = cfg.get("output_path")
    save_dir = cfg.get("save_dir") or "./runs"
    with timed("persist"):
        if output_path:
            _save_json(output_path, final)
            out_path = output_path
        else:
            ts = int(time.time())
            os.makedirs(save_dir, exist_ok=True)
            out_path = os.path.join(save_dir, f"run-{ts}.json")
            _save_json(out_path, final)

    _summarize_end(final.get("metrics", {}), final.get("summary", {}), out_path)
    logger.info("🟪 RUN END")
    return final
