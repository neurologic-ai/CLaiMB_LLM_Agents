# orchestrator/utils.py
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any
import uuid
from loguru import logger

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


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def new_run_id(prefix: str) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    uid = uuid.uuid4().hex[:8]
    return f"{prefix}-{ts}-{uid}"

def ensure_dirs(*dirs: Path) -> None:
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)

def write_tail(path: Path, tail: int) -> str:
    try:
        data = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""
    if tail <= 0:
        return data
    lines = data.splitlines()
    return "\n".join(lines[-tail:])

def load_json(path: Path) -> Dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        return {"error": f"failed to read {str(path)}: {e}"}
    
def setup_base_logging(service_logs_dir: Path, level: str = "INFO") -> None:
    service_logs_dir.mkdir(parents=True, exist_ok=True)
    logger.remove()
    logger.add(lambda m: print(m, end=""), level=level, backtrace=False, diagnose=False)
    logger.add(service_logs_dir / "service.log", level=level, rotation="10 MB", retention=10, compression="zip")

class RunSink:
    """Context manager to add/remove a per-run log sink safely."""
    def __init__(self, log_path: Path, level: str = "INFO"):
        self.log_path = log_path
        self.level = level
        self._sink_id = None

    def __enter__(self):
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self._sink_id = logger.add(self.log_path, level=self.level, rotation="5 MB", retention=5, compression="zip")
        return self

    def __exit__(self, exc_type, exc, tb):
        if self._sink_id is not None:
            try:
                logger.remove(self._sink_id)
            except ValueError:
                # already removed or invalid id
                pass