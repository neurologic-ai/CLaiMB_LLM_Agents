from __future__ import annotations
from loguru import logger
from pathlib import Path

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