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