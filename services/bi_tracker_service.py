#!/usr/bin/env python3
from __future__ import annotations
import os
from pathlib import Path
from typing import Any, Dict, Optional, List

from fastapi import FastAPI, BackgroundTasks, HTTPException, Query
from pydantic import BaseModel
from loguru import logger
from dotenv import load_dotenv

from services_common.models import RunStatus
from services_common.registry import ThreadSafeRuns
from services_common.utils import ensure_dirs, now_iso, new_run_id, write_tail
from services_common.logging_utils import setup_base_logging, RunSink

# Your BI implementations
from workflows.bi_tracker_workflow import run_workflow as bi_run_workflow

load_dotenv()

ARTIFACT_DIR = Path(os.getenv("BI_ARTIFACT_DIR", "runs_bi_mvp")).resolve()
LOG_DIR      = Path(os.getenv("BI_LOG_DIR", "logs/bi_tracker")).resolve()
LOG_LEVEL    = os.getenv("LOG_LEVEL", "INFO")
ensure_dirs(ARTIFACT_DIR, LOG_DIR)
setup_base_logging(LOG_DIR, LOG_LEVEL)

app = FastAPI(title="BI Tracker Service", version="1.0.0")
RUNS = ThreadSafeRuns()

class RunRequest(BaseModel):
    snapshot: Optional[Dict[str, Any]] = None
    out_dir: Optional[str] = None

@app.get("/health")
def health(): return {"status": "ok"}

def _worker(run_id: str, snapshot: Optional[Dict[str, Any]], out_dir: Path) -> None:
    log_path = LOG_DIR / f"{run_id}.log"
    with RunSink(log_path, LOG_LEVEL):
        RUNS.update(run_id, status="running", started_at=now_iso(), log_path=str(log_path))
        try:
            #snap = snapshot if snapshot is not None else bi_collect_snapshot()
            logger.info(f"[BI:{run_id}] starting…")
            res = bi_run_workflow()
            artifact = res.get("artifact_path") or str(ARTIFACT_DIR / f"{run_id}.json")
            if not res.get("artifact_path"):
                Path(artifact).write_text(
                    __import__("json").dumps(res, indent=2, ensure_ascii=False), encoding="utf-8"
                )
            RUNS.update(run_id, status="finished", finished_at=now_iso(), artifact_path=artifact)
            logger.info(f"[BI:{run_id}] done → {artifact}")
        except Exception as e:
            msg = f"{type(e).__name__}: {e}"
            logger.exception(f"[BI:{run_id}] FAILED: {msg}")
            RUNS.update(run_id, status="failed", finished_at=now_iso(), error=msg)

@app.post("/run", response_model=RunStatus)
def start_run(req: RunRequest, tasks: BackgroundTasks):
    run_id = new_run_id("bi-tracker")
    out_dir = Path(req.out_dir).resolve() if req.out_dir else ARTIFACT_DIR
    ensure_dirs(out_dir)
    RUNS.put(RunStatus(run_id=run_id, status="queued", queued_at=now_iso(), log_path=str(LOG_DIR / f"{run_id}.log")))
    tasks.add_task(_worker, run_id, req.snapshot, out_dir)
    return RUNS.get(run_id)  # type: ignore

@app.get("/status/{run_id}", response_model=RunStatus)
def get_status(run_id: str):
    st = RUNS.get(run_id)
    if not st: 
        raise HTTPException(status_code=404, detail="run_id not found")
    return st

@app.get("/runs")
def list_runs() -> List[RunStatus]:
    return RUNS.list_sorted()

@app.get("/latest", response_model=RunStatus)
def latest():
    st = RUNS.latest()
    if not st: 
        raise HTTPException(status_code=404, detail="no runs yet")
    return st

@app.get("/logs/{run_id}")
def logs(run_id: str, tail: int = Query(0, ge=0)):
    st = RUNS.get(run_id)
    if not st or not st.log_path: 
        raise HTTPException(status_code=404, detail="no log for run_id")
    p = Path(st.log_path)
    if not p.exists(): 
        return {"run_id": run_id, "log": ""}
    return {"run_id": run_id, "log": write_tail(p, min(tail, 5000))}

@app.get("/logs/latest")
def logs_latest(tail: int = Query(0, ge=0)):
    st = RUNS.latest()
    if not st: 
        raise HTTPException(status_code=404, detail="no runs yet")
    return logs(st.run_id, tail)