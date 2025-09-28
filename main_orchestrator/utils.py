# orchestrator/utils.py
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict
def now_utc_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

def write_json(path: Path, payload: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

def sanitize(obj):
    if isinstance(obj, Path):
        return str(obj)
    if isinstance(obj, dict):
        return {k: sanitize(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [sanitize(v) for v in obj]
    return obj

_LATEST_INPUTS_PATH = Path("./results/latest_inputs.json")

def _latest_input_path(key: str) -> str | None:
    try:
        if _LATEST_INPUTS_PATH.exists():
            d = json.loads(_LATEST_INPUTS_PATH.read_text())
            v = (d.get(key) or {}).get("input_path")
            return v if (v and Path(v).exists()) else None
    except Exception:
        pass
    return None

def _latest_repo_spec() -> tuple[str | None, str | None]:
    try:
        if _LATEST_INPUTS_PATH.exists():
            d = json.loads(_LATEST_INPUTS_PATH.read_text())
            rec = d.get("code_repo") or {}
            return rec.get("repo_url"), rec.get("repo_path")
    except Exception:
        pass
    return (None, None)

LATEST_INPUTS_PATH = Path("./results/latest_inputs.json")

def _load_latest_inputs():
    if LATEST_INPUTS_PATH.exists():
        return json.loads(LATEST_INPUTS_PATH.read_text())
    return {}

def _save_latest_inputs(d: dict) -> None:
    LATEST_INPUTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    LATEST_INPUTS_PATH.write_text(json.dumps(d, indent=2))

def _parse_weights_arg(weights_raw: str | None, dimensions: Dict[str, dict]) -> Dict[str, float]:
    """
    Parse --weights "DimA=10,DimB=20" into a dict. If empty/invalid,
    return equal weights across discovered dimensions.
    """
    dims = list(dimensions.keys())
    if not dims:
        return {}  # nothing to weight yet

    if not weights_raw:
        # equal weights
        return {d: 1.0 for d in dims}

    parsed: Dict[str, float] = {}
    for part in weights_raw.split(","):
        part = part.strip()
        if not part:
            continue
        if "=" not in part:
            # ignore malformed piece
            continue
        k, v = part.split("=", 1)
        k, v = k.strip(), v.strip()
        try:
            parsed[k] = float(v)
        except ValueError:
            # ignore malformed value
            continue

    # If the user provided at least one valid pair, use only what they supplied.
    # (Dimensions not present in `parsed` will get 0 weight.)
    # If nothing valid parsed, fall back to equal weights.
    if parsed:
        return parsed

    return {d: 1.0 for d in dims}