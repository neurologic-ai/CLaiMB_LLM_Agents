# main_orchestrator/app_main.py
from __future__ import annotations
from fastapi import FastAPI
from typing import Any, Dict, Optional
from pydantic import BaseModel
from pathlib import Path
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
import json
import os
from dataclasses import asdict, is_dataclass

from main_orchestrator.graph_orchestrator import (
    FeatureBus,
    Orchestrator,
    OrchestratorState,
)
from fastapi import UploadFile, File, HTTPException
from main_orchestrator.input_schemas import CategoryWeightsModel
from main_orchestrator.collectors import build_collectors, _scores_from_aggregates_or_payload, _collect_gaps_from_metrics
from main_orchestrator.adapters import run_bi_adapter, run_mlops_adapter, run_enterprise_adapter, run_code_repo_adapter, run_data_platform_adapter, run_cloud_infra_adapter
from main_orchestrator.validate import _normalize_and_check_mlops, _normalize_and_check_bi, _normalize_and_check_enterprise
from datetime import datetime
from pydantic import HttpUrl
from main_orchestrator.utils import _load_latest_inputs, _save_latest_inputs
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()


SURVEY_OUT_SCORES = os.getenv("SURVEY_OUT_SCORES", "./results/survey_metric_scores.json")


app = FastAPI(title="AIMRI Multi-Agent Orchestrator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CodeRepoInput(BaseModel):
    repo_url: Optional[HttpUrl] = None
    repo_path: Optional[str] = None

def _to_dict_state(s):
    # normalize state to a plain dict (works for dataclass or dict-like)
    if is_dataclass(s):
        return asdict(s)
    try:
        return dict(s)
    except Exception:
        return s  # last resort

# --- Singletons ---
BUS = FeatureBus("./bus")
ORCH = Orchestrator(bus_root="./bus", results_root="./results")
STATE = _to_dict_state(OrchestratorState())
SCHED = BackgroundScheduler(daemon=True)
ARTIFACTS_ROOT = Path("orchestrator_output/agents")

Path("./results").mkdir(parents=True, exist_ok=True)
ARTIFACTS_ROOT.mkdir(parents=True, exist_ok=True)
Path("./bus").mkdir(parents=True, exist_ok=True)

# Required external inputs
BATCH_DIR = os.getenv("BATCH_DIR", "/app/cloud_infra_inputs/Sample2")
CODE_REPO = os.getenv("CODE_REPO", "https://github.com/deepakpadhi986/AI-Resume-Analyzer.git")
COLLECTORS = build_collectors(
    BUS,
    artifacts_root=ARTIFACTS_ROOT,
    cloud_batch_dir=BATCH_DIR,
    code_repo=CODE_REPO,
)


# --- Helpers ---
def tick_orchestrator(thread_id: str = "scheduler"):
    global STATE
    # If STATE is a dict, rewrap it as a dataclass for the graph input
    try:
        state_in = OrchestratorState(**STATE) if isinstance(STATE, dict) else STATE
    except TypeError:
        state_in = OrchestratorState()  # fallback

    new_state = ORCH.tick(state_in, thread_id=thread_id)
    STATE = _to_dict_state(new_state)

# --- Startup / Shutdown ---
@app.on_event("startup")
def on_startup():
    # Schedule collectors with safe max_instances=1
    SCHED.add_job(COLLECTORS["cloud_infra"].run, "interval", hours=6, id="cloud_infra", max_instances=1)
    SCHED.add_job(COLLECTORS["data_platform"].run, "interval", hours=12, id="data_platform", max_instances=1)
    SCHED.add_job(COLLECTORS["ml_ops"].run, "interval", hours=4, id="ml_ops", max_instances=1)
    SCHED.add_job(COLLECTORS["bi_tracker"].run, "interval", hours=24, id="bi_tracker", max_instances=1)
    SCHED.add_job(COLLECTORS["enterprise_systems"].run, "interval", hours=8, id="enterprise_systems", max_instances=1)
    SCHED.add_job(COLLECTORS["code_repo"].run, "interval", hours=24, id="code_repo", max_instances=1)

    # Orchestrator polling every minute (stable thread id)
    SCHED.add_job(lambda: tick_orchestrator("scheduler"), "interval", hours=4, id="orchestrator_tick", max_instances=1)
    SCHED.start()


@app.on_event("shutdown")
def on_shutdown():
    SCHED.shutdown(wait=False)


# --- API Models ---
class ManualRunRequest(BaseModel):
    agent: str


# --- Routes ---
@app.get("/health")
def health():
    return {"status": "ok"}



@app.post("/inputs/bi_tracker/upload_file")
async def upload_bi_tracker_file(file: UploadFile = File(...)):
    if file.content_type not in ("application/json", "text/json", "application/octet-stream"):
        raise HTTPException(status_code=415, detail="Upload a JSON file")

    raw = await file.read()
    try:
        data = json.loads(raw.decode("utf-8", errors="ignore"))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {e}")
    try:
        normalized, ignored = _normalize_and_check_bi(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    run_dir = Path("user_inputs") / "bi_tracker"
    run_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    p = run_dir / f"bi_input_{ts}.json"
    p.write_text(json.dumps(normalized, indent=2), encoding="utf-8")

    latest = _load_latest_inputs()
    latest["bi_tracker"] = {"input_path": str(p.resolve())}
    _save_latest_inputs(latest)

    return {"input_path": str(p), "ignored_fields": ignored}

@app.post("/inputs/ml_ops/upload_file")
async def upload_mlops_file(file: UploadFile = File(...)):
    if file.content_type not in ("application/json", "text/json", "application/octet-stream"):
        raise HTTPException(status_code=415, detail="Upload a JSON file")

    raw = await file.read()
    try:
        data = json.loads(raw.decode("utf-8", errors="ignore"))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {e}")

    try:
        normalized, ignored = _normalize_and_check_mlops(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    run_dir = Path("user_inputs") / "ml_ops"
    run_dir.mkdir(parents=True, exist_ok=True)
    p = run_dir / "latest.json"
    p.write_text(json.dumps(normalized, indent=2), encoding="utf-8")

    latest = _load_latest_inputs()
    latest["ml_ops"] = {"input_path": str(p.resolve())}
    _save_latest_inputs(latest)

    return {"input_path": str(p), "ignored_fields": ignored}

@app.post("/inputs/enterprise/upload_file")
async def upload_enterprise_file(file: UploadFile = File(...)):
    if file.content_type not in ("application/json", "text/json", "application/octet-stream"):
        raise HTTPException(status_code=415, detail="Upload a JSON file")

    raw = await file.read()
    try:
        data = json.loads(raw.decode("utf-8", errors="ignore"))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {e}")

    try:
        normalized, ignored = _normalize_and_check_enterprise(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    run_dir = Path("user_inputs") / "enterprise"
    run_dir.mkdir(parents=True, exist_ok=True)
    p = run_dir / "latest.json"
    p.write_text(json.dumps(normalized, indent=2), encoding="utf-8")

    latest = _load_latest_inputs()
    latest["enterprise"] = {"input_path": str(p.resolve())}
    _save_latest_inputs(latest)

    return {"input_path": str(p), "ignored_fields": ignored}

@app.post("/inputs/data_platform/upload_file")
async def upload_data_platform_file(file: UploadFile = File(...)):
    if file.content_type not in ("application/json", "text/json", "application/octet-stream"):
        raise HTTPException(status_code=415, detail="Upload a JSON file")

    raw = await file.read()
    try:
        data = json.loads(raw.decode("utf-8", errors="ignore"))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {e}")

    run_dir = Path("user_inputs") / "data_platform"
    run_dir.mkdir(parents=True, exist_ok=True)
    p = run_dir / "latest.json"
    p.write_text(json.dumps(data, indent=2), encoding="utf-8")

    latest = _load_latest_inputs()
    latest["data_platform"] = {"input_path": str(p.resolve())}
    _save_latest_inputs(latest)

    return {"input_path": str(p)}

@app.post("/inputs/cloud_infra/upload_file")
async def upload_cloud_infra_file(file: UploadFile = File(...)):
    if file.content_type not in ("application/json", "text/json", "application/octet-stream"):
        raise HTTPException(status_code=415, detail="Upload a JSON file")

    raw = await file.read()
    try:
        data = json.loads(raw.decode("utf-8", errors="ignore"))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {e}")

    if not isinstance(data, dict):
        raise HTTPException(status_code=400, detail="Cloud Infra input must be a JSON object")

    run_dir = Path("user_inputs") / "cloud_infra"
    run_dir.mkdir(parents=True, exist_ok=True)
    p = run_dir / "latest.json"
    p.write_text(json.dumps(data, indent=2), encoding="utf-8")

    latest = _load_latest_inputs()
    latest["cloud_infra"] = {"input_path": str(p.resolve())}
    _save_latest_inputs(latest)

    return {"input_path": str(p)}

@app.post("/inputs/code_repo")
def upload_code_repo(body: CodeRepoInput):

    if not body.repo_url and not body.repo_path:
        return {"error": "Provide either 'repo_url' or 'repo_path'."}

    latest = _load_latest_inputs()
    latest["code_repo"] = {
        "repo_url": str(body.repo_url) if body.repo_url else None,
        "repo_path": body.repo_path,
    }
    _save_latest_inputs(latest)

    return {
        "saved": True,
        "code_repo": latest["code_repo"],
        "message": "Code repo reference saved. Call /collect/code_repo/run_latest to run."
    }

@app.post("/inputs/category_weights")
def upload_category_weights(body: CategoryWeightsModel):
    weights = body.model_dump(by_alias=True)

    run_dir = Path("user_inputs") / "category_weights"
    run_dir.mkdir(parents=True, exist_ok=True)
    p = run_dir / "latest.json"
    p.write_text(json.dumps(weights, indent=2), encoding="utf-8")

    latest = _load_latest_inputs()
    latest["category_weights"] = {"input_path": str(p.resolve())}
    _save_latest_inputs(latest)

    return {"input_path": str(p), "weights": weights}

@app.get("/results/latest")
def latest_results():
    overall_path = ORCH.results_root / "latest_overall.json"
    categories_path = ORCH.results_root / "category_scores.json"
    gaps_path = ORCH.results_root / "category_gaps.json"

    overall = json.loads(overall_path.read_text()) if overall_path.exists() else None
    categories = json.loads(categories_path.read_text()) if categories_path.exists() else None
    gaps = json.loads(gaps_path.read_text()) if gaps_path.exists() else None

    return {
        "overall": overall,
        "categories": categories,
        "gaps": gaps,
        "state": {
            "updated_count": STATE.get("updated_count"),
            "last_scored_ts": STATE.get("last_scored_ts"),
            "latest_sign_ts": STATE.get("latest_sign_ts"),
        },
    }

@app.post("/collect/run_all")
def run_all_collectors():
    published: Dict[str, Any] = {}

    # --- pause background jobs to avoid concurrent scoring/runs ---
    paused_jobs = []
    job_ids = [
        "orchestrator_tick",
        "cloud_infra",
        "data_platform",
        "ml_ops",
        "bi_tracker",
        "enterprise_systems",
        "code_repo",
    ]
    try:
        for jid in job_ids:
            job = SCHED.get_job(jid)
            if job and job.next_run_time is not None:  # only pause if active
                SCHED.pause_job(jid)
                paused_jobs.append(jid)

        latest = _load_latest_inputs()

        # ---- BI Tracker ----
        bi_path = (latest.get("bi_tracker") or {}).get("input_path")
        if bi_path and Path(bi_path).exists():
            try:
                out_dir = ARTIFACTS_ROOT / "bi_tracker"
                artifact, aggregates, metrics = run_bi_adapter(out_dir, snapshot_path=bi_path)
                # compute category scores + gaps here to publish once
                payload = {"artifact_path": artifact, "aggregates": aggregates, "metrics": metrics}
                scores = _scores_from_aggregates_or_payload(payload)
                gaps = _collect_gaps_from_metrics(metrics)
                published["bi_tracker"] = BUS.publish("bi_tracker", scores or {}, gaps or {})
            except Exception as e:
                published["bi_tracker"] = {"error": str(e)}
        else:
            published["bi_tracker"] = {"skipped": "no uploaded input"}

        # ---- MLOps ----
        ml_path = (latest.get("ml_ops") or {}).get("input_path")
        if ml_path and Path(ml_path).exists():
            try:
                out_dir = ARTIFACTS_ROOT / "ml_ops"
                artifact, aggregates, metrics = run_mlops_adapter(out_dir, snapshot_path=ml_path)
                payload = {"artifact_path": artifact, "aggregates": aggregates, "metrics": metrics}
                scores = _scores_from_aggregates_or_payload(payload)
                gaps = _collect_gaps_from_metrics(metrics)
                published["ml_ops"] = BUS.publish("ml_ops", scores or {}, gaps or {})
            except Exception as e:
                published["ml_ops"] = {"error": str(e)}
        else:
            published["ml_ops"] = {"skipped": "no uploaded input"}

        # ---- Enterprise ----
        ent_path = (latest.get("enterprise") or {}).get("input_path")
        if ent_path and Path(ent_path).exists():
            try:
                out_dir = ARTIFACTS_ROOT / "enterprise_systems"
                artifact, scores_raw, metrics = run_enterprise_adapter(out_dir, snapshot_path=ent_path)
                # Convert enterprise payload to category scores for publishing
                cats = _scores_from_aggregates_or_payload(
                    {"artifact_path": artifact, "scores": scores_raw, "metrics": metrics}
                )
                gaps = _collect_gaps_from_metrics(metrics)
                published["enterprise_systems"] = BUS.publish("enterprise_systems", cats or {}, gaps or {})
            except Exception as e:
                published["enterprise_systems"] = {"error": str(e)}
        else:
            published["enterprise_systems"] = {"skipped": "no uploaded input"}

        # ---- Data Platform (input required) ----
        dp_info = latest.get("data_platform") or {}
        dp_path = dp_info.get("input_path")
        if dp_path and Path(dp_path).exists():
            try:
                out_dir = ARTIFACTS_ROOT / "data_platform"
                artifact, aggregates, metrics, extra = run_data_platform_adapter(out_dir, snapshot_path=dp_path)
                published["data_platform"] = BUS.publish("data_platform", aggregates or {}, metrics or {})
            except Exception as e:
                published["data_platform"] = {"error": str(e)}
        else:
            published["data_platform"] = {"skipped": "no uploaded input"}

        # ---- Cloud Infra (run only if uploaded input exists) ----
        ci_info = latest.get("cloud_infra") or {}
        ci_path = ci_info.get("input_path")
        if ci_path and Path(ci_path).exists():
            try:
                out_dir = ARTIFACTS_ROOT / "cloud_infra"
                artifact, aggregates, metrics = run_cloud_infra_adapter(
                    out_dir,
                    snapshot_path=ci_path,   # <— adapter updated to accept snapshot_path
                )
                payload = {"artifact_path": artifact, "aggregates": aggregates, "metrics": metrics}
                scores  = _scores_from_aggregates_or_payload(payload)
                gaps    = _collect_gaps_from_metrics(metrics)
                published["cloud_infra"] = BUS.publish("cloud_infra", scores or {}, gaps or {})
            except Exception as e:
                published["cloud_infra"] = {"error": str(e)}
        else:
            published["cloud_infra"] = {"skipped": "no uploaded input"}

        # ---- Code Repo ----
        cr_cfg = latest.get("code_repo") or {}
        repo_url, repo_path = cr_cfg.get("repo_url"), cr_cfg.get("repo_path")
        # ignore placeholder "string"
        if repo_url == "string":
            repo_url = None
        if repo_path == "string":
            repo_path = None

        if repo_url or repo_path:
            try:
                out_dir = ARTIFACTS_ROOT / "code_repo"
                artifact, aggregates, metrics, extra = run_code_repo_adapter(
                    out_dir, repo_url=repo_url, repo_path=repo_path
                )
                published["code_repo"] = BUS.publish("code_repo", aggregates or {}, metrics or {})
            except Exception as e:
                published["code_repo"] = {"error": str(e)}
        else:
            published["code_repo"] = {"skipped": "no uploaded input"}

        # ---- single scoring pass after all publishes ----
        tick_orchestrator(thread_id="manual-all-onepass")

        scores_path = Path(SURVEY_OUT_SCORES)
        # gaps_path = ORCH.results_root / "category_gaps.json"
        # gap_summaries_path = ORCH.results_root / "gap_summaries.json"
        recs_path = ORCH.results_root / "prioritized_recommendations.json"
        scores_json = json.loads(scores_path.read_text(encoding="utf-8")) if scores_path.exists() else None
        # gaps_json = json.loads(gaps_path.read_text(encoding="utf-8")) if gaps_path.exists() else None
        # gap_summaries_json = json.loads(gap_summaries_path.read_text(encoding="utf-8")) if gap_summaries_path.exists() else None
        recommendations_json = json.loads(recs_path.read_text(encoding="utf-8")) if recs_path.exists() else None
        
        _save_latest_inputs({})

        return {
            "scores": scores_json,
            #"gaps": gaps_json,
            #"gap_summaries": gap_summaries_json,
            "prioritized_recommendations": recommendations_json,
        }

    finally:
        for jid in paused_jobs:
            try:
                SCHED.resume_job(jid)
            except Exception:
                pass