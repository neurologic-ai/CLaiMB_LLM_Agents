# orchestrator/models.py
from dataclasses import dataclass
from typing import Any, Dict, Optional

@dataclass(frozen=True)
class AgentSpec:
    name: str
    enabled: bool = True
    timeout_sec: int = 900
    retries: int = 1

@dataclass
class AgentResult:
    name: str
    ok: bool
    artifact_path: Optional[str]
    aggregates: Any
    metrics: Any
    error: Optional[str]
    duration_sec: float

@dataclass
class CombinedResult:
    run_id: str
    started_at: str
    agents: Dict[str, AgentResult]