#!/usr/bin/env python3
from __future__ import annotations
import os, json
from pathlib import Path
from typing import Optional, List

from fastapi import FastAPI, BackgroundTasks, HTTPException, Query, Header
from pydantic import BaseModel
from loguru import logger
from dotenv import load_dotenv

from services_common.models import RunStatus
from services_common.registry import ThreadSafeRuns
from services_common.utils import ensure_dirs, now_iso, new_run_id, write_tail
from services_common.logging_utils import setup_base_logging, RunSink
from services_common.auth import require_api_key

load_dotenv()

RUNS_DIR  = Path(os.getenv("ENTERPRISE_RUNS_DIR", "runs_enterprise_mvp")).resolve()
LOGS_DIR  = Path(os.getenv("ENTERPRISE_LOGS_DIR", "logs/enterprise")).resolve()
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
API_ENV   = "ENTERPRISE_API_KEY"

ensure_dirs(RUNS_DIR, LOGS_DIR)
setup_base_logging(LOGS_DIR, LOG_LEVEL)

# Prefer class if available
try:
    from workflows.enterprise_workflow import EnterpriseWorkflow as EnterpriseRunner  # type: ignore
    _ENT_USES_CLASS = True
except Exception:
    from workflows.enterprise_workflow import run_workflow as enterprise_run_workflow  # type: ignore
    _ENT_USES_CLASS = False

app = FastAPI(title="Enterprise Systems Agent Service", version="1.0.0")
RUNS = ThreadSafeRuns()

class RunRequest(BaseModel):
    verbose: Optional[bool] = True
    run_id: Optional[str] = None

@app.get("/health")
def health(): return {"status": "ok"}

def _worker(run_id: str, verbose: bool, user_run_id: Optional[str]) -> None:
    log_path = LOGS_DIR / f"{run_id}.log"
    with RunSink(log_path, LOG_LEVEL):
        RUNS.update(run_id, status="running", started_at=now_iso(), log_path=str(log_path))
        try:
            logger.info(f"[ENT:{run_id}] starting…")
            if _ENT_USES_CLASS:
                wf = EnterpriseRunner(artifact_dir=RUNS_DIR, logs_dir=LOGS_DIR)
                out_path, _ = wf.run(run_id=user_run_id, verbose=verbose)
            else:
                out_path, _ = enterprise_run_workflow(run_id=user_run_id, verbose=verbose)
            RUNS.update(run_id, status="finished", finished_at=now_iso(), artifact_path=str(out_path))
            logger.info(f"[ENT:{run_id}] done → {out_path}")
        except Exception as e:
            msg = f"{type(e).__name__}: {e}"
            logger.exception(f"[ENT:{run_id}] FAILED: {msg}")
            RUNS.update(run_id, status="failed", finished_at=now_iso(), error=msg)

@app.post("/run", response_model=RunStatus)
def start_run(req: RunRequest, tasks: BackgroundTasks, x_api_key: Optional[str] = Header(default=None)):
    require_api_key(x_api_key, API_ENV)
    run_id = new_run_id("enterprise")
    RUNS.put(RunStatus(run_id=run_id, status="queued", queued_at=now_iso(), log_path=str(LOGS_DIR / f"{run_id}.log")))
    tasks.add_task(_worker, run_id, bool(req.verbose), req.run_id)
    return RUNS.get(run_id)  # type: ignore

@app.get("/status/{run_id}", response_model=RunStatus)
def status(run_id: str):
    st = RUNS.get(run_id)
    if not st: raise HTTPException(status_code=404, detail="run_id not found")
    return st

@app.get("/runs")
def runs() -> List[RunStatus]:
    return RUNS.list_sorted()

@app.get("/latest", response_model=RunStatus)
def latest():
    st = RUNS.latest()
    if not st: raise HTTPException(status_code=404, detail="no runs yet")
    return st

@app.get("/logs/{run_id}")
def logs(run_id: str, tail: int = Query(0, ge=0)):
    st = RUNS.get(run_id)
    if not st or not st.log_path: raise HTTPException(status_code=404, detail="no log for run_id")
    p = Path(st.log_path)
    if not p.exists(): return {"run_id": run_id, "log": ""}
    return {"run_id": run_id, "log": write_tail(p, min(tail, 5000))}

@app.get("/logs/latest")
def logs_latest(tail: int = Query(0, ge=0)):
    st = RUNS.latest()
    if not st: raise HTTPException(status_code=404, detail="no runs yet")
    return logs(st.run_id, tail)