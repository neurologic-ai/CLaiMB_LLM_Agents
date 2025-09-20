from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional

class RunStatus(BaseModel):
    run_id: str
    status: str = Field(description="queued | running | finished | failed")
    queued_at: Optional[str] = None
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    artifact_path: Optional[str] = None
    log_path: Optional[str] = None
    error: Optional[str] = None