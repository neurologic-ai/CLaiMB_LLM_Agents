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
    try:
        x = int(v)
        return float(1 if x < 1 else 5 if x > 5 else x)
    except Exception:
        return 3.0

def _normalize_metric(m: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure only 'score' is present; drop any legacy 'band'."""
    m = dict(m or {})
    if "score" not in m:
        m["score"] = _clamp_score(m.get("band", 3))
    # remove any band to guarantee artifacts never show it
    if "band" in m:
        del m["band"]
    return m


def _build_reverse_index(mapping: Dict[str, List[Dict[str, str]]]) -> Dict[str, List[str]]:
    """
    Build AIMRI reverse index:
      "Dimension: Subsection" -> ["metric.id", ...]
    """
    idx: Dict[str, List[str]] = {}
    for mid, tags in mapping.items():
        for t in tags or []:
            dim = (t.get("dimension") or "").strip()
            sub = (t.get("subsection") or "").strip()
            key = f"{dim}: {sub}".strip(": ").strip()
            if not key:
                continue
            idx.setdefault(key, []).append(mid)
    # dedupe + sort for stable UI
    for k in list(idx.keys()):
        idx[k] = sorted(set(idx[k]))
    return dict(sorted(idx.items()))


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


def _filter_mapping_for_present_metrics(
    mapping: Dict[str, List[Dict[str, str]]],
    present_metric_ids: List[str],
) -> Dict[str, List[Dict[str, str]]]:
    """Limit the AIMRI mapping to only metrics that were actually computed in this run."""
    present = set(present_metric_ids)
    return {mid: mapping[mid] for mid in mapping.keys() & present}


# -----------------------------
# Orchestrator (functional API)
# -----------------------------
def run(snapshot: Dict[str, Any], out_dir: Optional[Path] = None) -> Dict[str, Any]:
    """
    Deterministic execution:
      - Level 0 (parallel, no deps)
      - Level 1 (ordered by simple dependency list; no fan-in of outputs yet)
      - Aggregation (categories → overall)
      - Augment output with AIMRI mapping (both metric→AIMRI and reverse index)

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
        _missing = [d for d in deps if d not in l0_out]
        l1_out[mid] = load_tool(mid)(snapshot)

    # ----- Merge & aggregate -----
    # After computing l0_out / l1_out and merging:
    metrics: Dict[str, Dict[str, Any]] = {**l0_out, **l1_out}

    # normalize to keep only 'score'
    for k, v in list(metrics.items()):
        metrics[k] = _normalize_metric(v)

    aggregates = _aggregate(metrics)

    # ----- AIMRI mapping (only for metrics present in this run) -----
    present_metric_ids = list(metrics.keys())
    aimri_mapping = _filter_mapping_for_present_metrics(METRIC_TO_AIMRI, present_metric_ids)
    aimri_index = _build_reverse_index(aimri_mapping)

    result: Dict[str, Any] = {
        "run_id": _now_id(),
        "metrics": metrics,
        "aggregates": aggregates,
        "aimri_mapping": aimri_mapping,
        "aimri_index": aimri_index,
    }

    # ----- Persistence -----
    if out_dir is not None:
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        artifact = out_dir / f"{result['run_id']}.json"
        artifact.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        result["artifact_path"] = str(artifact)

    return result