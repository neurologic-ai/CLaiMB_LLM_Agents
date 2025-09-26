# main_orchestrator/app_main.py
from __future__ import annotations
from fastapi import FastAPI
from pydantic import BaseModel
from pathlib import Path
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
import uuid
import json
import os
from dataclasses import asdict, is_dataclass

from main_orchestrator.graph_orchestrator import (
    FeatureBus,
    Orchestrator,
    OrchestratorState,
)
from main_orchestrator.collectors import build_collectors

app = FastAPI(title="AIMRI Multi-Agent Orchestrator")

load_dotenv()  # ensure OPENAI_API_KEY for scoring

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
    SCHED.add_job(lambda: tick_orchestrator("scheduler"), "interval", minutes=1, id="orchestrator_tick", max_instances=1)
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


@app.post("/collect/run")
def run_collect(req: ManualRunRequest):
    if req.agent not in COLLECTORS:
        return {"error": f"unknown agent: {req.agent}"}

    try:
        published = COLLECTORS[req.agent].run()  # dict with scores/gaps/sign file paths
    except Exception as e:
        return {"error": f"collector {req.agent} failed: {e}"}

    # use unique thread for each manual trigger → separate checkpoint streams
    tick_orchestrator(thread_id=f"manual-{uuid.uuid4().hex[:8]}")

    return {"published": published}


@app.get("/results/latest")
def latest_results():
    overall_path = ORCH.results_root / "latest_overall.json"
    categories_path = ORCH.results_root / "category_scores.json"

    overall = json.loads(overall_path.read_text()) if overall_path.exists() else None
    categories = json.loads(categories_path.read_text()) if categories_path.exists() else None

    return {
        "overall": overall,
        "categories": categories,
        "state": {
            "updated_count": STATE.get("updated_count"),
            "last_scored_ts": STATE.get("last_scored_ts"),
            "latest_sign_ts": STATE.get("latest_sign_ts"),
        },
    }
@app.post("/collect/run_all")
def run_all_collectors():
    published = {}
    for agent, collector in COLLECTORS.items():
        try:
            published[agent] = collector.run()
        except Exception as e:
            published[agent] = {"error": str(e)}
    # one orchestrator tick after all agents have run
    tick_orchestrator(thread_id=f"manual-all-{uuid.uuid4().hex[:8]}")
    return {"published": published}