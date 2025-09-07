# agent_layer/orchestrator.py
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from langchain_core.runnables import RunnableLambda, RunnableParallel

# --- repo-root on sys.path (so module runs work) ---
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent_layer.registry import LEVEL0, LEVEL1_DEPS, CATEGORIES  # noqa: E402
from agent_layer.tool_loader import load_tool  # noqa: E402
from agent_layer.aimri_mapping import METRIC_TO_AIMRI  # noqa: E402


# -----------------------------
# Helpers
# -----------------------------
def _now_id(prefix: str = "bi-tracker") -> str:
    """Return a UTC, filename-safe run id."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    return f"{prefix}-{ts}"


def _clamp_score(v: Any) -> float:
    """Coerce score-like value to float in [1..5] (default 3.0)."""
    try:
        x = int(v)
        return float(1 if x < 1 else 5 if x > 5 else x)
    except Exception:
        return 3.0


def _normalize_metric(m: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ensure only 'score' is present; drop any legacy 'band'.
    Also clamps score to [1..5].
    """
    m = dict(m or {})
    if "score" not in m:
        m["score"] = _clamp_score(m.get("band", 3))
    else:
        m["score"] = _clamp_score(m["score"])
    # remove any band to guarantee artifacts never show it
    if "band" in m:
        del m["band"]
    return m


def _aggregate(metrics: Dict[str, Dict[str, Any]]) -> Dict[str, float]:
    """
    Category aggregation on 'score' (1..5) only.
    """
    cat_scores: Dict[str, float] = {}
    overall = 0.0
    tot_cat_w = 0.0

    for cat, spec in CATEGORIES.items():
        cat_w = float(spec.get("weight", 0.5))
        met_weights: Dict[str, float] = spec.get("metrics", {})
        s = sum(met_weights.values()) or 1.0

        score = 0.0
        for m_id, w in met_weights.items():
            sc = _clamp_score(metrics.get(m_id, {}).get("score", 3))
            score += (float(w) / s) * sc

        score = round(score, 2)
        cat_scores[cat] = score
        overall += cat_w * score
        tot_cat_w += cat_w

    overall_score = round(overall / tot_cat_w, 2) if tot_cat_w else 0.0
    return {**cat_scores, "overall_score": overall_score}


# -----------------------------
# Orchestrator (functional API)
# -----------------------------
def run(snapshot: Dict[str, Any], out_dir: Optional[Path] = None) -> Dict[str, Any]:
    """
    Deterministic execution:
      - Level 0 (parallel, no deps)
      - Level 1 (ordered by simple dependency list; no fan-in of outputs yet)
      - Aggregation (categories → overall)
      - Embed AIMRI mapping inside each metric result (`metrics[mid]["aimri"]`)

    If out_dir is provided, writes ./<out_dir>/<run_id>.json
    """
    load_dotenv()  # ensure .env is loaded for the backbone

    # ----- Level 0 in parallel -----
    # bind metric id at definition to avoid closure surprises
    l0_tools = {
        mid: RunnableLambda(lambda s, _m=mid: load_tool(_m)(s))
        for mid in LEVEL0
    }
    l0_parallel = RunnableParallel(**l0_tools)
    l0_out: Dict[str, Dict[str, Any]] = l0_parallel.invoke(snapshot)

    # ----- Level 1 sequential (deps only for ordering) -----
    l1_out: Dict[str, Dict[str, Any]] = {}
    for mid, deps in LEVEL1_DEPS.items():
        _missing = [d for d in deps if d not in l0_out]  # kept for future validation/logging
        l1_out[mid] = load_tool(mid)(snapshot)

    # ----- Merge, normalize, and embed AIMRI per metric -----
    metrics: Dict[str, Dict[str, Any]] = {**l0_out, **l1_out}

    for mid, m in list(metrics.items()):
        nm = _normalize_metric(m)
        # Embed AIMRI tags directly into each metric object
        nm["aimri"] = METRIC_TO_AIMRI.get(mid, [])
        # Ensure metric_id is present and correct
        nm["metric_id"] = mid
        metrics[mid] = nm

    # ----- Aggregate -----
    aggregates = _aggregate(metrics)

    # ----- Final payload (no top-level aimri_mapping / aimri_index) -----
    result: Dict[str, Any] = {
        "run_id": _now_id(),
        "metrics": metrics,
        "aggregates": aggregates,
    }

    # ----- Persistence -----
    if out_dir is not None:
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        artifact = out_dir / f"{result['run_id']}.json"
        artifact.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        result["artifact_path"] = str(artifact)

    return result