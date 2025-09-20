from __future__ import annotations
from typing import Dict, List, Optional
import threading

from .models import RunStatus

class ThreadSafeRuns:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._runs: Dict[str, RunStatus] = {}

    def put(self, status: RunStatus) -> None:
        with self._lock:
            self._runs[status.run_id] = status

    def get(self, run_id: str) -> Optional[RunStatus]:
        with self._lock:
            return self._runs.get(run_id)

    def update(self, run_id: str, **fields) -> Optional[RunStatus]:
        with self._lock:
            st = self._runs.get(run_id)
            if not st:
                return None
            for k, v in fields.items():
                setattr(st, k, v)
            self._runs[run_id] = st
            return st

    def list_sorted(self) -> List[RunStatus]:
        with self._lock:
            items = list(self._runs.values())
        items.sort(key=lambda r: r.started_at or r.queued_at or "", reverse=True)
        return items

    def latest(self) -> Optional[RunStatus]:
        items = self.list_sorted()
        return items[0] if items else None