# # services/agents_gateway.py
# from __future__ import annotations
# import os
# import uuid
# import json
# import threading
# from datetime import datetime, timezone
# from pathlib import Path
# from typing import Any, Dict, Optional

# from fastapi import FastAPI, APIRouter, BackgroundTasks, HTTPException, Header, Query
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel, Field
# from loguru import logger

# # ============
# # Imports to your existing agent code (adjust paths only if your repo differs)
# # ============

# # BI Tracker
# from workflows.bi_tracker_workflow import run_workflow as bi_run_workflow, collect_snapshot as bi_collect_snapshot

# # Code Repo
# from workflows.code_repo_workflow import CodeRepoWorkflow

# # Cloud Infra
# from agent_layer.cloud_infra_agent.orchestrator import CloudInfraOrchestrator

# # Data Platform Analyzer
# from workflows.AGENT_DATA_PLATFORM_ANALYZER.mvp_data_platform_scanner import run_once as data_platform_run_once

# # Enterprise Systems
# try:
#     # prefer the class if present
#     from workflows.enterprise_workflow import EnterpriseWorkflow as EnterpriseRunner
#     _ENTERPRISE_USES_CLASS = True
# except Exception:
#     from workflows.enterprise_workflow import run_workflow as enterprise_run_workflow  # type: ignore
#     _ENTERPRISE_USES_CLASS = False

# # ML Ops
# try:
#     from workflows.ml_ops_workflow import run_workflow as mlops_run_workflow
#     _MLOPS_DIRECT = True
# except Exception:
#     # older layout
#     from agent_layer.ml_ops_agent.orchestrator_mlops import run as mlops_run  # type: ignore
#     _MLOPS_DIRECT = False


# # ==============
# # App + CORS
# # ==============
# app = FastAPI(title="CLaiMB Agent Gateway", version="1.0.0")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=os.getenv("CORS_ALLOW_ORIGINS", "*").split(","),
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # ============
# # Shared helpers
# # ============

# def _now_iso() -> str:
#     return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# def _new_run_id(prefix: str) -> str:
#     ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
#     uid = uuid.uuid4().hex[:8]
#     return f"{prefix}-{ts}-{uid}"

# def _write_tail(path: Path, tail: int) -> str:
#     try:
#         data = path.read_text(encoding="utf-8", errors="ignore")
#     except Exception:
#         return ""
#     if tail <= 0:
#         return data
#     lines = data.splitlines()
#     return "\n".join(lines[-tail:])

# def _ensure_dirs(*dirs: Path) -> None:
#     for d in dirs:
#         d.mkdir(parents=True, exist_ok=True)

# def _load_json(path: Path) -> Dict[str, Any]:
#     try:
#         return json.loads(path.read_text(encoding="utf-8"))
#     except Exception as e:
#         return {"error": f"failed to read {str(path)}: {e}"}

# # Standard status model used by all agents
# class RunStatus(BaseModel):
#     run_id: str
#     status: str = Field(description="queued | running | finished | failed")
#     queued_at: Optional[str] = None
#     started_at: Optional[str] = None
#     finished_at: Optional[str] = None
#     artifact_path: Optional[str] = None
#     log_path: Optional[str] = None
#     error: Optional[str] = None

# # Generic in-memory registry type
# RunRegistry = Dict[str, RunStatus]
# RunLock = threading.Lock

# def _setup_logger(service_logs_dir: Path, level: str) -> None:
#     logger.remove()
#     logger.add(lambda msg: print(msg, end=""), level=level, backtrace=False, diagnose=False)
#     logger.add(service_logs_dir / "gateway.log", level=level, rotation="10 MB", retention=10, compression="zip")


# # ============
# # BI TRACKER ROUTER
# # ============
# bi_router = APIRouter()
# _BI_RUNS: RunRegistry = {}
# _BI_LOCK: RunLock = threading.Lock()
# _BI_ARTIFACT_DIR = Path(os.getenv("BI_ARTIFACT_DIR", "runs_bi_mvp")).resolve()
# _BI_LOG_DIR = Path(os.getenv("BI_LOG_DIR", "logs/bi_tracker")).resolve()
# _ensure_dirs(_BI_ARTIFACT_DIR, _BI_LOG_DIR)

# class BiRunRequest(BaseModel):
#     snapshot: Optional[Dict[str, Any]] = None
#     out_dir: Optional[str] = None

# @bi_router.get("/health")
# def bi_health():
#     return {"status": "ok"}

# def _bi_worker(run_id: str, snapshot: Optional[Dict[str, Any]], out_dir: Path) -> None:
#     run_log = _BI_LOG_DIR / f"{run_id}.log"
#     sink_id = logger.add(run_log, level=os.getenv("LOG_LEVEL", "INFO"), rotation="5 MB", retention=5, compression="zip")
#     try:
#         with _BI_LOCK:
#             st = _BI_RUNS[run_id]
#             st.status = "running"
#             st.started_at = _now_iso()
#             st.log_path = str(run_log)

#         snap = snapshot if snapshot is not None else bi_collect_snapshot()
#         logger.info(f"[BI:{run_id}] starting…")
#         res = bi_run_workflow()  # your run_workflow already handles its own snapshot; if not, switch to run_bi_tracker(snap, out_dir)
#         # Persist a thin reference if needed
#         artifact = res.get("artifact_path") or str(_BI_ARTIFACT_DIR / f"{run_id}.json")
#         if not res.get("artifact_path"):
#             Path(artifact).write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")

#         with _BI_LOCK:
#             st = _BI_RUNS[run_id]
#             st.status = "finished"
#             st.finished_at = _now_iso()
#             st.artifact_path = artifact
#         logger.info(f"[BI:{run_id}] done → {artifact}")
#     except Exception as e:
#         msg = f"{type(e).__name__}: {e}"
#         logger.exception(f"[BI:{run_id}] FAILED: {msg}")
#         with _BI_LOCK:
#             st = _BI_RUNS[run_id]
#             st.status = "failed"
#             st.finished_at = _now_iso()
#             st.error = msg
#     finally:
#         try:
#             logger.remove(sink_id)
#         except ValueError:
#             pass

# @bi_router.post("/run", response_model=RunStatus)
# def bi_run(req: BiRunRequest, tasks: BackgroundTasks):
#     run_id = _new_run_id("bi-tracker")
#     out_dir = Path(req.out_dir).resolve() if req.out_dir else _BI_ARTIFACT_DIR
#     _ensure_dirs(out_dir, _BI_LOG_DIR)
#     meta = RunStatus(run_id=run_id, status="queued", queued_at=_now_iso(), log_path=str(_BI_LOG_DIR / f"{run_id}.log"))
#     with _BI_LOCK:
#         _BI_RUNS[run_id] = meta
#     tasks.add_task(_bi_worker, run_id, req.snapshot, out_dir)
#     return meta

# @bi_router.get("/status/{run_id}", response_model=RunStatus)
# def bi_status(run_id: str):
#     with _BI_LOCK:
#         st = _BI_RUNS.get(run_id)
#         if not st:
#             raise HTTPException(status_code=404, detail="run_id not found")
#         return st

# @bi_router.get("/runs")
# def bi_runs():
#     with _BI_LOCK:
#         items = list(_BI_RUNS.values())
#     items.sort(key=lambda r: r.started_at or r.queued_at or "", reverse=True)
#     return items

# @bi_router.get("/latest", response_model=RunStatus)
# def bi_latest():
#     with _BI_LOCK:
#         items = [r for r in _BI_RUNS.values() if r.started_at or r.queued_at]
#     if not items:
#         raise HTTPException(status_code=404, detail="no runs yet")
#     items.sort(key=lambda r: r.started_at or r.queued_at or "", reverse=True)
#     return items[0]

# @bi_router.get("/logs/{run_id}")
# def bi_logs(run_id: str, tail: int = Query(0, ge=0)):
#     with _BI_LOCK:
#         st = _BI_RUNS.get(run_id)
#     if not st or not st.log_path:
#         raise HTTPException(status_code=404, detail="no log for run_id")
#     p = Path(st.log_path)
#     if not p.exists():
#         return {"run_id": run_id, "log": ""}
#     return {"run_id": run_id, "log": _write_tail(p, min(tail, 5000))}

# @bi_router.get("/logs/latest")
# def bi_logs_latest(tail: int = Query(0, ge=0)):
#     latest = bi_latest()
#     return bi_logs(latest.run_id, tail)

# # ============
# # CODE REPO ROUTER
# # ============
# code_router = APIRouter()
# _CODE_RUNS: RunRegistry = {}
# _CODE_LOCK: RunLock = threading.Lock()
# _CODE_RUNS_DIR = Path(os.getenv("CODE_RUNS_DIR", "runs_code_repo_mvp")).resolve()
# _CODE_LOGS_DIR = Path(os.getenv("CODE_LOGS_DIR", "logs/code_repo")).resolve()
# _ensure_dirs(_CODE_RUNS_DIR, _CODE_LOGS_DIR)

# class CodeRunRequest(BaseModel):
#     repo_path: str
#     run_id: Optional[str] = None

# def _code_worker(run_id: str, repo_path: str, user_run_id: Optional[str]) -> None:
#     run_log = _CODE_LOGS_DIR / f"{run_id}.log"
#     sink_id = logger.add(run_log, level=os.getenv("LOG_LEVEL", "INFO"), rotation="5 MB", retention=5, compression="zip")
#     try:
#         with _CODE_LOCK:
#             st = _CODE_RUNS[run_id]
#             st.status = "running"
#             st.started_at = _now_iso()
#             st.log_path = str(run_log)

#         logger.info(f"[CODE:{run_id}] starting on {repo_path}…")
#         wf = CodeRepoWorkflow(artifact_dir=_CODE_RUNS_DIR, logs_dir=_CODE_LOGS_DIR)
#         out_path, _result = wf.run(repo_path=repo_path, run_id=user_run_id)

#         with _CODE_LOCK:
#             st = _CODE_RUNS[run_id]
#             st.status = "finished"
#             st.finished_at = _now_iso()
#             st.artifact_path = str(out_path)

#         logger.info(f"[CODE:{run_id}] done → {out_path}")
#     except Exception as e:
#         msg = f"{type(e).__name__}: {e}"
#         logger.exception(f"[CODE:{run_id}] FAILED: {msg}")
#         with _CODE_LOCK:
#             st = _CODE_RUNS[run_id]
#             st.status = "failed"
#             st.finished_at = _now_iso()
#             st.error = msg
#     finally:
#         try:
#             logger.remove(sink_id)
#         except ValueError:
#             pass

# @code_router.get("/health")
# def code_health():
#     return {"status": "ok"}

# @code_router.post("/run", response_model=RunStatus)
# def code_run(req: CodeRunRequest, tasks: BackgroundTasks, x_api_key: Optional[str] = Header(default=None)):
#     # Optional simple API key
#     api_key = os.getenv("CODE_API_KEY")
#     if api_key and x_api_key != api_key:
#         raise HTTPException(status_code=401, detail="Invalid API key")

#     run_id = _new_run_id("code-repo")
#     meta = RunStatus(run_id=run_id, status="queued", queued_at=_now_iso(), log_path=str(_CODE_LOGS_DIR / f"{run_id}.log"))
#     with _CODE_LOCK:
#         _CODE_RUNS[run_id] = meta
#     tasks.add_task(_code_worker, run_id, req.repo_path, req.run_id)
#     return meta

# @code_router.get("/status/{run_id}", response_model=RunStatus)
# def code_status(run_id: str):
#     with _CODE_LOCK:
#         st = _CODE_RUNS.get(run_id)
#         if not st:
#             raise HTTPException(status_code=404, detail="run_id not found")
#         return st

# @code_router.get("/runs")
# def code_runs():
#     with _CODE_LOCK:
#         items = list(_CODE_RUNS.values())
#     items.sort(key=lambda r: r.started_at or r.queued_at or "", reverse=True)
#     return items

# @code_router.get("/latest", response_model=RunStatus)
# def code_latest():
#     with _CODE_LOCK:
#         items = [r for r in _CODE_RUNS.values() if r.started_at or r.queued_at]
#     if not items:
#         raise HTTPException(status_code=404, detail="no runs yet")
#     items.sort(key=lambda r: r.started_at or r.queued_at or "", reverse=True)
#     return items[0]

# @code_router.get("/logs/{run_id}")
# def code_logs(run_id: str, tail: int = Query(0, ge=0)):
#     with _CODE_LOCK:
#         st = _CODE_RUNS.get(run_id)
#     if not st or not st.log_path:
#         raise HTTPException(status_code=404, detail="no log for run_id")
#     p = Path(st.log_path)
#     if not p.exists():
#         return {"run_id": run_id, "log": ""}
#     return {"run_id": run_id, "log": _write_tail(p, min(tail, 5000))}

# @code_router.get("/logs/latest")
# def code_logs_latest(tail: int = Query(0, ge=0)):
#     latest = code_latest()
#     return code_logs(latest.run_id, tail)

# # ============
# # CLOUD INFRA ROUTER
# # ============
# cloud_router = APIRouter()
# _CLOUD_RUNS: RunRegistry = {}
# _CLOUD_LOCK: RunLock = threading.Lock()
# _CLOUD_RUNS_DIR = Path(os.getenv("CLOUD_RUNS_DIR", "agent_layer_outputs/cloud_infra")).resolve()
# _CLOUD_LOGS_DIR = Path(os.getenv("CLOUD_LOGS_DIR", "logs/cloud_infra")).resolve()
# _CLOUD_BATCH_DIR = os.getenv("CLOUD_BATCH_DIR", "")  # must be set or passed in req
# _ensure_dirs(_CLOUD_RUNS_DIR, _CLOUD_LOGS_DIR)

# class CloudRunRequest(BaseModel):
#     batch_dir: Optional[str] = None
#     run_id: Optional[str] = None

# @cloud_router.get("/health")
# def cloud_health():
#     return {"status": "ok"}

# def _cloud_worker(run_id: str, batch_dir: str, user_run_id: Optional[str]) -> None:
#     run_log = _CLOUD_LOGS_DIR / f"{run_id}.log"
#     sink_id = logger.add(run_log, level=os.getenv("LOG_LEVEL", "INFO"), rotation="5 MB", retention=5, compression="zip")
#     try:
#         with _CLOUD_LOCK:
#             st = _CLOUD_RUNS[run_id]
#             st.status = "running"
#             st.started_at = _now_iso()
#             st.log_path = str(run_log)

#         logger.info(f"[CLOUD:{run_id}] starting on {batch_dir}…")
#         orch = CloudInfraOrchestrator(
#             batch_dir=batch_dir,
#             runs_dir=str(_CLOUD_RUNS_DIR),
#             log_dir=str(_CLOUD_LOGS_DIR),
#             log_level=os.getenv("LOG_LEVEL", "INFO"),
#             serialize_logs=False,
#             max_workers=int(os.getenv("CLOUD_MAX_WORKERS", "8")),
#         )
#         orch.run_once(run_id=user_run_id)
#         # Find newest JSON as artifact reference
#         outs = sorted(_CLOUD_RUNS_DIR.glob("*.json"), key=lambda p: (p.stat().st_mtime, p.name))
#         artifact = str(outs[-1]) if outs else None

#         with _CLOUD_LOCK:
#             st = _CLOUD_RUNS[run_id]
#             st.status = "finished"
#             st.finished_at = _now_iso()
#             st.artifact_path = artifact
#         logger.info(f"[CLOUD:{run_id}] done → {artifact}")
#     except Exception as e:
#         msg = f"{type(e).__name__}: {e}"
#         logger.exception(f"[CLOUD:{run_id}] FAILED: {msg}")
#         with _CLOUD_LOCK:
#             st = _CLOUD_RUNS[run_id]
#             st.status = "failed"
#             st.finished_at = _now_iso()
#             st.error = msg
#     finally:
#         try:
#             logger.remove(sink_id)
#         except ValueError:
#             pass

# @cloud_router.post("/run", response_model=RunStatus)
# def cloud_run(req: CloudRunRequest, tasks: BackgroundTasks):
#     batch_dir = req.batch_dir or _CLOUD_BATCH_DIR
#     if not batch_dir:
#         raise HTTPException(status_code=400, detail="batch_dir not provided and CLOUD_BATCH_DIR not set")
#     run_id = _new_run_id("cloud-infra")
#     meta = RunStatus(run_id=run_id, status="queued", queued_at=_now_iso(), log_path=str(_CLOUD_LOGS_DIR / f"{run_id}.log"))
#     with _CLOUD_LOCK:
#         _CLOUD_RUNS[run_id] = meta
#     tasks.add_task(_cloud_worker, run_id, batch_dir, req.run_id)
#     return meta

# @cloud_router.get("/status/{run_id}", response_model=RunStatus)
# def cloud_status(run_id: str):
#     with _CLOUD_LOCK:
#         st = _CLOUD_RUNS.get(run_id)
#         if not st:
#             raise HTTPException(status_code=404, detail="run_id not found")
#         return st

# @cloud_router.get("/runs")
# def cloud_runs():
#     with _CLOUD_LOCK:
#         items = list(_CLOUD_RUNS.values())
#     items.sort(key=lambda r: r.started_at or r.queued_at or "", reverse=True)
#     return items

# @cloud_router.get("/latest", response_model=RunStatus)
# def cloud_latest():
#     with _CLOUD_LOCK:
#         items = [r for r in _CLOUD_RUNS.values() if r.started_at or r.queued_at]
#     if not items:
#         raise HTTPException(status_code=404, detail="no runs yet")
#     items.sort(key=lambda r: r.started_at or r.queued_at or "", reverse=True)
#     return items[0]

# @cloud_router.get("/logs/{run_id}")
# def cloud_logs(run_id: str, tail: int = Query(0, ge=0)):
#     with _CLOUD_LOCK:
#         st = _CLOUD_RUNS.get(run_id)
#     if not st or not st.log_path:
#         raise HTTPException(status_code=404, detail="no log for run_id")
#     p = Path(st.log_path)
#     if not p.exists():
#         return {"run_id": run_id, "log": ""}
#     return {"run_id": run_id, "log": _write_tail(p, min(tail, 5000))}

# @cloud_router.get("/logs/latest")
# def cloud_logs_latest(tail: int = Query(0, ge=0)):
#     latest = cloud_latest()
#     return cloud_logs(latest.run_id, tail)

# # ============
# # DATA PLATFORM ROUTER
# # ============
# data_router = APIRouter()
# _DATA_RUNS: RunRegistry = {}
# _DATA_LOCK: RunLock = threading.Lock()
# _DATA_RUNS_DIR = Path(os.getenv("DATA_RUNS_DIR", "agent_layer_outputs/AGENT_DATA_PLATFORM_ANALYZER")).resolve()
# _DATA_LOGS_DIR = Path(os.getenv("DATA_LOGS_DIR", "logs/AGENT_DATA_PLATFORM_ANALYZER")).resolve()
# _ensure_dirs(_DATA_RUNS_DIR, _DATA_LOGS_DIR)

# @data_router.get("/health")
# def data_health():
#     return {"status": "ok"}

# class DataRunRequest(BaseModel):
#     run_id: Optional[str] = None  # not used by the scanner, but accepted for symmetry

# def _data_worker(run_id: str) -> None:
#     run_log = _DATA_LOGS_DIR / f"{run_id}.log"
#     sink_id = logger.add(run_log, level=os.getenv("LOG_LEVEL", "INFO"), rotation="5 MB", retention=5, compression="zip")
#     try:
#         with _DATA_LOCK:
#             st = _DATA_RUNS[run_id]
#             st.status = "running"
#             st.started_at = _now_iso()
#             st.log_path = str(run_log)

#         logger.info(f"[DATA:{run_id}] starting…")
#         artifact_obj = data_platform_run_once()  # returns dict
#         # persist
#         out_path = _DATA_RUNS_DIR / f"{run_id}.json"
#         out_path.write_text(json.dumps(artifact_obj, indent=2, ensure_ascii=False), encoding="utf-8")

#         with _DATA_LOCK:
#             st = _DATA_RUNS[run_id]
#             st.status = "finished"
#             st.finished_at = _now_iso()
#             st.artifact_path = str(out_path)
#         logger.info(f"[DATA:{run_id}] done → {out_path}")
#     except Exception as e:
#         msg = f"{type(e).__name__}: {e}"
#         logger.exception(f"[DATA:{run_id}] FAILED: {msg}")
#         with _DATA_LOCK:
#             st = _DATA_RUNS[run_id]
#             st.status = "failed"
#             st.finished_at = _now_iso()
#             st.error = msg
#     finally:
#         try:
#             logger.remove(sink_id)
#         except ValueError:
#             pass

# @data_router.post("/run", response_model=RunStatus)
# def data_run(req: DataRunRequest, tasks: BackgroundTasks):
#     run_id = _new_run_id("data-scan")
#     meta = RunStatus(run_id=run_id, status="queued", queued_at=_now_iso(), log_path=str(_DATA_LOGS_DIR / f"{run_id}.log"))
#     with _DATA_LOCK:
#         _DATA_RUNS[run_id] = meta
#     tasks.add_task(_data_worker, run_id)
#     return meta

# @data_router.get("/status/{run_id}", response_model=RunStatus)
# def data_status(run_id: str):
#     with _DATA_LOCK:
#         st = _DATA_RUNS.get(run_id)
#         if not st:
#             raise HTTPException(status_code=404, detail="run_id not found")
#         return st

# @data_router.get("/runs")
# def data_runs():
#     with _DATA_LOCK:
#         items = list(_DATA_RUNS.values())
#     items.sort(key=lambda r: r.started_at or r.queued_at or "", reverse=True)
#     return items

# @data_router.get("/latest", response_model=RunStatus)
# def data_latest():
#     with _DATA_LOCK:
#         items = [r for r in _DATA_RUNS.values() if r.started_at or r.queued_at]
#     if not items:
#         raise HTTPException(status_code=404, detail="no runs yet")
#     items.sort(key=lambda r: r.started_at or r.queued_at or "", reverse=True)
#     return items[0]

# @data_router.get("/logs/{run_id}")
# def data_logs(run_id: str, tail: int = Query(0, ge=0)):
#     with _DATA_LOCK:
#         st = _DATA_RUNS.get(run_id)
#     if not st or not st.log_path:
#         raise HTTPException(status_code=404, detail="no log for run_id")
#     p = Path(st.log_path)
#     if not p.exists():
#         return {"run_id": run_id, "log": ""}
#     return {"run_id": run_id, "log": _write_tail(p, min(tail, 5000))}

# @data_router.get("/logs/latest")
# def data_logs_latest(tail: int = Query(0, ge=0)):
#     latest = data_latest()
#     return data_logs(latest.run_id, tail)

# # ============
# # ENTERPRISE ROUTER
# # ============
# enterprise_router = APIRouter()
# _ENT_RUNS: RunRegistry = {}
# _ENT_LOCK: RunLock = threading.Lock()
# _ENT_RUNS_DIR = Path(os.getenv("ENTERPRISE_RUNS_DIR", "runs_enterprise_mvp")).resolve()
# _ENT_LOGS_DIR = Path(os.getenv("ENTERPRISE_LOGS_DIR", "logs/enterprise")).resolve()
# _ensure_dirs(_ENT_RUNS_DIR, _ENT_LOGS_DIR)

# class EnterpriseRunRequest(BaseModel):
#     verbose: Optional[bool] = True
#     run_id: Optional[str] = None

# @enterprise_router.get("/health")
# def enterprise_health():
#     return {"status": "ok"}

# def _enterprise_worker(run_id: str, verbose: bool, user_run_id: Optional[str]) -> None:
#     run_log = _ENT_LOGS_DIR / f"{run_id}.log"
#     sink_id = logger.add(run_log, level=os.getenv("LOG_LEVEL", "INFO"), rotation="5 MB", retention=5, compression="zip")
#     try:
#         with _ENT_LOCK:
#             st = _ENT_RUNS[run_id]
#             st.status = "running"
#             st.started_at = _now_iso()
#             st.log_path = str(run_log)

#         logger.info(f"[ENT:{run_id}] starting…")
#         if _ENTERPRISE_USES_CLASS:
#             wf = EnterpriseRunner(artifact_dir=_ENT_RUNS_DIR, logs_dir=_ENT_LOGS_DIR)
#             out_path, _scores = wf.run(run_id=user_run_id, verbose=verbose)
#         else:
#             out_path, _scores = enterprise_run_workflow(run_id=user_run_id, verbose=verbose)  # type: ignore

#         with _ENT_LOCK:
#             st = _ENT_RUNS[run_id]
#             st.status = "finished"
#             st.finished_at = _now_iso()
#             st.artifact_path = str(out_path)

#         logger.info(f"[ENT:{run_id}] done → {out_path}")
#     except Exception as e:
#         msg = f"{type(e).__name__}: {e}"
#         logger.exception(f"[ENT:{run_id}] FAILED: {msg}")
#         with _ENT_LOCK:
#             st = _ENT_RUNS[run_id]
#             st.status = "failed"
#             st.finished_at = _now_iso()
#             st.error = msg
#     finally:
#         try:
#             logger.remove(sink_id)
#         except ValueError:
#             pass

# @enterprise_router.post("/run", response_model=RunStatus)
# def enterprise_run(req: EnterpriseRunRequest, tasks: BackgroundTasks, x_api_key: Optional[str] = Header(default=None)):
#     api_key = os.getenv("ENTERPRISE_API_KEY")
#     if api_key and x_api_key != api_key:
#         raise HTTPException(status_code=401, detail="Invalid API key")

#     run_id = _new_run_id("enterprise")
#     meta = RunStatus(run_id=run_id, status="queued", queued_at=_now_iso(), log_path=str(_ENT_LOGS_DIR / f"{run_id}.log"))
#     with _ENT_LOCK:
#         _ENT_RUNS[run_id] = meta
#     tasks.add_task(_enterprise_worker, run_id, bool(req.verbose), req.run_id)
#     return meta

# @enterprise_router.get("/status/{run_id}", response_model=RunStatus)
# def enterprise_status(run_id: str):
#     with _ENT_LOCK:
#         st = _ENT_RUNS.get(run_id)
#         if not st:
#             raise HTTPException(status_code=404, detail="run_id not found")
#         return st

# @enterprise_router.get("/runs")
# def enterprise_runs():
#     with _ENT_LOCK:
#         items = list(_ENT_RUNS.values())
#     items.sort(key=lambda r: r.started_at or r.queued_at or "", reverse=True)
#     return items

# @enterprise_router.get("/latest", response_model=RunStatus)
# def enterprise_latest():
#     with _ENT_LOCK:
#         items = [r for r in _ENT_RUNS.values() if r.started_at or r.queued_at]
#     if not items:
#         raise HTTPException(status_code=404, detail="no runs yet")
#     items.sort(key=lambda r: r.started_at or r.queued_at or "", reverse=True)
#     return items[0]

# @enterprise_router.get("/logs/{run_id}")
# def enterprise_logs(run_id: str, tail: int = Query(0, ge=0)):
#     with _ENT_LOCK:
#         st = _ENT_RUNS.get(run_id)
#     if not st or not st.log_path:
#         raise HTTPException(status_code=404, detail="no log for run_id")
#     p = Path(st.log_path)
#     if not p.exists():
#         return {"run_id": run_id, "log": ""}
#     return {"run_id": run_id, "log": _write_tail(p, min(tail, 5000))}

# @enterprise_router.get("/logs/latest")
# def enterprise_logs_latest(tail: int = Query(0, ge=0)):
#     latest = enterprise_latest()
#     return enterprise_logs(latest.run_id, tail)

# # ============
# # MLOPS ROUTER
# # ============
# mlops_router = APIRouter()
# _MLOPS_RUNS: RunRegistry = {}
# _MLOPS_LOCK: RunLock = threading.Lock()
# _MLOPS_ARTIFACT_DIR = Path(os.getenv("MLOPS_ARTIFACT_DIR", "runs_mlops_mvp")).resolve()
# _MLOPS_LOG_DIR = Path(os.getenv("MLOPS_LOG_DIR", "logs/mlops_monitor")).resolve()
# _ensure_dirs(_MLOPS_ARTIFACT_DIR, _MLOPS_LOG_DIR)

# class MlopsRunRequest(BaseModel):
#     out_dir: Optional[str] = None

# @mlops_router.get("/health")
# def mlops_health():
#     return {"status": "ok"}

# def _mlops_worker(run_id: str, out_dir: Path) -> None:
#     run_log = _MLOPS_LOG_DIR / f"{run_id}.log"
#     sink_id = logger.add(run_log, level=os.getenv("LOG_LEVEL", "INFO"), rotation="5 MB", retention=5, compression="zip")
#     try:
#         with _MLOPS_LOCK:
#             st = _MLOPS_RUNS[run_id]
#             st.status = "running"
#             st.started_at = _now_iso()
#             st.log_path = str(run_log)

#         logger.info(f"[MLOPS:{run_id}] starting…")
#         if _MLOPS_DIRECT:
#             artifact_path, aggregates, metrics = mlops_run_workflow()
#             payload = {"artifact_path": artifact_path, "aggregates": aggregates, "metrics": metrics}
#         else:
#             payload = mlops_run({}, out_dir=out_dir)  # older orchestrator signature

#         artifact = payload.get("artifact_path") or str(out_dir / f"{run_id}.json")
#         if not payload.get("artifact_path"):
#             Path(artifact).write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

#         with _MLOPS_LOCK:
#             st = _MLOPS_RUNS[run_id]
#             st.status = "finished"
#             st.finished_at = _now_iso()
#             st.artifact_path = artifact
#         logger.info(f"[MLOPS:{run_id}] done → {artifact}")
#     except Exception as e:
#         msg = f"{type(e).__name__}: {e}"
#         logger.exception(f"[MLOPS:{run_id}] FAILED: {msg}")
#         with _MLOPS_LOCK:
#             st = _MLOPS_RUNS[run_id]
#             st.status = "failed"
#             st.finished_at = _now_iso()
#             st.error = msg
#     finally:
#         try:
#             logger.remove(sink_id)
#         except ValueError:
#             pass

# @mlops_router.post("/run", response_model=RunStatus)
# def mlops_run(req: MlopsRunRequest, tasks: BackgroundTasks):
#     run_id = _new_run_id("mlops-monitor")
#     out_dir = Path(req.out_dir).resolve() if req.out_dir else _MLOPS_ARTIFACT_DIR
#     _ensure_dirs(out_dir, _MLOPS_LOG_DIR)
#     meta = RunStatus(run_id=run_id, status="queued", queued_at=_now_iso(), log_path=str(_MLOPS_LOG_DIR / f"{run_id}.log"))
#     with _MLOPS_LOCK:
#         _MLOPS_RUNS[run_id] = meta
#     tasks.add_task(_mlops_worker, run_id, out_dir)
#     return meta

# @mlops_router.get("/status/{run_id}", response_model=RunStatus)
# def mlops_status(run_id: str):
#     with _MLOPS_LOCK:
#         st = _MLOPS_RUNS.get(run_id)
#         if not st:
#             raise HTTPException(status_code=404, detail="run_id not found")
#         return st

# @mlops_router.get("/runs")
# def mlops_runs():
#     with _MLOPS_LOCK:
#         items = list(_MLOPS_RUNS.values())
#     items.sort(key=lambda r: r.started_at or r.queued_at or "", reverse=True)
#     return items

# @mlops_router.get("/latest", response_model=RunStatus)
# def mlops_latest():
#     with _MLOPS_LOCK:
#         items = [r for r in _MLOPS_RUNS.values() if r.started_at or r.queued_at]
#     if not items:
#         raise HTTPException(status_code=404, detail="no runs yet")
#     items.sort(key=lambda r: r.started_at or r.queued_at or "", reverse=True)
#     return items[0]

# @mlops_router.get("/logs/{run_id}")
# def mlops_logs(run_id: str, tail: int = Query(0, ge=0)):
#     with _MLOPS_LOCK:
#         st = _MLOPS_RUNS.get(run_id)
#     if not st or not st.log_path:
#         raise HTTPException(status_code=404, detail="no log for run_id")
#     p = Path(st.log_path)
#     if not p.exists():
#         return {"run_id": run_id, "log": ""}
#     return {"run_id": run_id, "log": _write_tail(p, min(tail, 5000))}

# @mlops_router.get("/logs/latest")
# def mlops_logs_latest(tail: int = Query(0, ge=0)):
#     latest = mlops_latest()
#     return mlops_logs(latest.run_id, tail)

# # ============
# # ROOT + ROUTER MOUNTS
# # ============
# @app.get("/health")
# def root_health():
#     return {"status": "ok", "agents": ["bi", "code", "cloud", "data", "enterprise", "mlops"]}

# # Configure the base log sinks once (env LOG_LEVEL, default INFO)
# _setup_logger(Path(os.getenv("GATEWAY_LOG_DIR", "logs/gateway")).resolve(), os.getenv("LOG_LEVEL", "INFO"))

# app.include_router(bi_router, prefix="/bi", tags=["BI Tracker"])
# app.include_router(code_router, prefix="/code", tags=["Code Repo"])
# app.include_router(cloud_router, prefix="/cloud", tags=["Cloud Infra"])
# app.include_router(data_router, prefix="/data", tags=["Data Platform"])
# app.include_router(enterprise_router, prefix="/enterprise", tags=["Enterprise Systems"])
# app.include_router(mlops_router, prefix="/mlops", tags=["ML Ops"])