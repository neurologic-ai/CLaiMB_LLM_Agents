# agent_layer/orchestrator.py
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, List

from dotenv import load_dotenv

# path bootstrap
import sys
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent_layer.dev_env_scanner.registry import LEVEL0, LEVEL1_DEPS, CATEGORIES  # noqa: E402
from agent_layer.dev_env_scanner.router import route, route_many                 # noqa: E402
from langchain_core.runnables import RunnableParallel           # noqa: E402

# NEW: import the code-repo AIMRI mapping
from agent_layer.dev_env_scanner.aimri_mapping import CODE_REPO_METRIC_TO_AIMRI  # noqa: E402


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")


def _now_id(prefix: str = "code-repo") -> str:
    return f"{prefix}-{now_utc_iso()}"


def _clamp_score(v: Any) -> int:
    try:
        x = int(v)
        return 1 if x < 1 else 5 if x > 5 else x
    except Exception:
        return 3


def _band_to_score(band_value: Any) -> int:
    """
    Your code-repo metrics already emit numeric 'band' (1..5).
    If a future metric returns A/B/C letters, map them here if needed.
    """
    # If it's numeric-ish, just clamp to 1..5
    try:
        return _clamp_score(int(band_value))
    except Exception:
        # Optional: letter mapping fallback (not currently used by your repo agent)
        letter = str(band_value).strip().upper()
        mapping = {"A": 5, "B": 4, "C": 3, "D": 2, "E": 1}
        return mapping.get(letter, 3)


# def _aggregate(metrics: Dict[str, Dict[str, Any]]) -> Dict[str, float]:
#     """
#     Category aggregation on 'score' (1..5) only.
#     """
#     cat_scores: Dict[str, float] = {}
#     overall = 0.0
#     tot_w = 0.0
#     for cat, spec in CATEGORIES.items():
#         cat_w = float(spec.get("weight", 0.5))
#         met_w: Dict[str, float] = spec.get("metrics", {})
#         s = sum(met_w.values()) or 1.0
#         score = 0.0
#         for mid, w in met_w.items():
#             sc = _clamp_score((metrics.get(mid) or {}).get("score", 3))
#             score += (float(w) / s) * float(sc)
#         score = round(score, 2)
#         cat_scores[cat] = score
#         overall += cat_w * score
#         tot_w += cat_w
#     cat_scores["overall_score"] = round(overall / tot_w, 2) if tot_w else 0.0
#     return cat_scores


# def _filter_mapping_for_present_metrics(mapping: Dict[str, List[Dict[str, str]]],
#                                         present_metric_ids: List[str]) -> Dict[str, List[Dict[str, str]]]:
#     present = set(present_metric_ids)
#     return {mid: mapping[mid] for mid in mapping.keys() & present}


# def _build_reverse_index(mapping: Dict[str, List[Dict[str, str]]]) -> Dict[str, List[str]]:
#     idx: Dict[str, List[str]] = {}
#     for mid, tags in mapping.items():
#         for t in tags or []:
#             dim = (t.get("dimension") or "").strip()
#             sub = (t.get("subsection") or "").strip()
#             key = f"{dim}: {sub}".strip(": ").strip()
#             if not key:
#                 continue
#             idx.setdefault(key, []).append(mid)
#     for k in list(idx.keys()):
#         idx[k] = sorted(set(idx[k]))
#     return dict(sorted(idx.items()))


# ----------------------------
# Class-based orchestrator (kept)
# ----------------------------
class CodeRepoOrchestrator:
    """
    Class-based orchestrator for the code-repo agent:
      - L0 parallel fanout (RunnableParallel)
      - L1 metrics (respecting declared deps presence)
      - normalize metrics to score-only; inject per-metric mapping
      - aggregate category and overall
      - optional artifact writing (final JSON already normalized)
    """

    def __init__(self, *, prefix: str = "code-repo") -> None:
        self.prefix = prefix

    def run(self, snapshot: Dict[str, Any], out_dir: Optional[Path] = None) -> Dict[str, Any]:
        """
        Snapshot must contain:
          - code_snippets: list[str]
          - file_paths:    list[str]
        """
        load_dotenv()

        # ----- Level 0 in parallel -----
        l0_runnables = route_many(LEVEL0)
        parallel = RunnableParallel(**l0_runnables)
        l0_out: Dict[str, Dict[str, Any]] = parallel.invoke(snapshot)

        # ----- Level 1 sequential -----
        l1_out: Dict[str, Dict[str, Any]] = {}
        for mid, deps in LEVEL1_DEPS.items():
            # deps are computed by L0; we could validate/log if missing
            _ = [d for d in deps if d not in l0_out]
            l1_out[mid] = route(mid).invoke(snapshot)

        # Merge
        raw_metrics: Dict[str, Dict[str, Any]] = {**l0_out, **l1_out}

        # Normalize: band → score (1..5), drop band, ensure 'score' right after metric_id,
        # and inject per-metric AIMRI mapping
        metrics: Dict[str, Dict[str, Any]] = {}
        for mid, m in (raw_metrics or {}).items():
            m = dict(m or {})
            # determine score
            score_val = m.get("score")
            if not isinstance(score_val, (int, float)):
                score_val = _band_to_score(m.get("band", 3))
            score = _clamp_score(score_val)

            # construct ordered dict: metric_id, score, then the rest
            out_obj: Dict[str, Any] = {}
            out_obj["metric_id"] = mid
            out_obj["score"] = score

            # keep rationale/flags/gaps if present
            if "rationale" in m:
                out_obj["rationale"] = m["rationale"]
            if "flags" in m:
                out_obj["flags"] = m["flags"]
            if "gaps" in m:
                out_obj["gaps"] = m["gaps"]

            # inject mapping inside the metric
            out_obj["aimri_mapping"] = CODE_REPO_METRIC_TO_AIMRI.get(mid, [])

            metrics[mid] = out_obj  # note: band intentionally omitted

        # Aggregates now based on score
        #aggregates = _aggregate(metrics)

        # Build top-level mapping/index (only for present metrics)
        #present_ids = list(metrics.keys())
        #aimri_mapping = _filter_mapping_for_present_metrics(CODE_REPO_METRIC_TO_AIMRI, present_ids)
        #aimri_index = _build_reverse_index(aimri_mapping)

        result = {
            "run_id": _now_id(self.prefix),
            "metrics": metrics,
            # "aggregates": aggregates,
            #"aimri_mapping": aimri_mapping,  # top-level copy
            #"aimri_index": aimri_index,      # reverse index
        }

        # Optional artifact write (already normalized)
        if out_dir is not None:
            out_dir = Path(out_dir)
            out_dir.mkdir(parents=True, exist_ok=True)
            artifact = out_dir / f"{result['run_id']}.json"
            artifact.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
            result["artifact_path"] = str(artifact)

        return result


# === Backwards-compatible functional API ===
def run(snapshot: Dict[str, Any], out_dir: Optional[Path] = None) -> Dict[str, Any]:
    orch = CodeRepoOrchestrator()
    return orch.run(snapshot, out_dir=out_dir)
