from __future__ import annotations
from loguru import logger
from pathlib import Path

def setup_logger(path: str | Path, level: str = "INFO") -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    logger.remove()
    logger.add(path, rotation="5 MB", retention=5, backtrace=True, diagnose=False, level=level)
    logger.add(lambda m: print(m, end=""), level=level)
