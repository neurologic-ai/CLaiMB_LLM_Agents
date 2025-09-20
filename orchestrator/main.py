# orchestrator/app_main.py
from fastapi import FastAPI, HTTPException
from apscheduler.schedulers.background import BackgroundScheduler
from orchestrator.orchestrator import Orchestrator
from orchestrator.models import AgentSpec
from pathlib import Path

app = FastAPI(title="AIMRI Multi-Agent Orchestrator")

ORCH = Orchestrator(out_dir="results")
SCHED = BackgroundScheduler(daemon=True)

specs = {
    "bi_tracker": AgentSpec("bi_tracker", True),
    "code_repo": AgentSpec("code_repo", True),
    "cloud_infra": AgentSpec("cloud_infra", True),
    "data_platform": AgentSpec("data_platform", True),
    "enterprise": AgentSpec("enterprise", True),
    "ml_ops": AgentSpec("ml_ops", True),
}

@app.on_event("startup")
def startup():
    
    SCHED.add_job(lambda: ORCH.run_all(specs), "interval", hours=6)
    SCHED.start()

@app.on_event("shutdown")
def shutdown():
    SCHED.shutdown(wait=False)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/run")
def run_now():
    path = ORCH.run_all(specs)
    return {"artifact": str(path)}

@app.get("/results/latest")
def latest():
    files = sorted(Path("results").glob("all_agents_*.json"))
    if not files:
        raise HTTPException(status_code=404, detail="no runs yet")
    return files[-1].read_text()