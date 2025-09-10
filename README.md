# Cloud Infra Agent (CLaiMB)

**Cloud Infrastructure Agent** to score infra maturity using deterministic metrics (tagging coverage, compute/k8s utilization, etc.).  
You can run the agent **via CLI** *or* **via API (FastAPI)**.

---

## 📦 Repository Structure
```text
CLaiMB_LLM_Agents/
├─ agent_layer/                         
│  └─ cloud_infra_agent/
│     ├─ amiri_mapping.py               # AIMRI dimension mappings
│     ├─ orchestrator.py                # CloudInfraOrchestrator (entry used by CLI/API)
│     ├─ registry.py                    # (LEVEL0, LEVEL1 metrics)
│     ├─ schemas.py
│     ├─ tool_loader.py
│     └─ validate.py     
├─ data_collection_agents/               # Backbone "Cloud Infra Agent" (DO NOT MODIFY backbone)
│  └─ cloud_infra_agent/
├─ data/
│  └─ inputs/
│     └─ cloud_infra_inputs/
│        └─ Sample2/                     # Example per-metric JSONs (edit to try your own)
├─ mvp/
│  └─ cloud_infra_runonce.py             # Simple CLI wrapper around CloudInfraOrchestrator
├─ services/
│  └─ cloud_infra_service.py             # FastAPI service (run/status/list endpoints)
├─ agent_layer_outputs/
│  └─ cloud_infra/                       # Default <run_id>.json outputs (configurable)
├─ logs/
│  └─ cloud_infra/                       # Default per-run logs (configurable)
├─ workflows/
│  └─ cloud_infra_workflow.py            # L0 fan-out, L1-after-deps execution plan
├─ .env.example                          # Copy to .env and edit
├─ README.md
└─ requirements.txt
```

---

## 🧰 Requirements
- Python 3.10+
- `pip install -r requirements.txt`

Setup:
```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env       # then edit values
```

---

## 🚀 How to Run

You have **two** supported ways to run the agent.

### Option A — CLI (recommended for local runs)

The orchestrator is exposed via `mvp.cloud_infra_runonce`.

```bash
# Basic run (writes agent_layer_outputs/cloud_infra/<run_id>.json and logs/cloud_infra/<run_id>.log)
python -m mvp.cloud_infra_runonce --batch-dir data/inputs/cloud_infra_inputs/Sample2
```

Common flags:

```bash
# choose output + logs folders, enable JSON logs, control workers
python -m mvp.cloud_infra_runonce \  --batch-dir data/inputs/cloud_infra_inputs/Sample2 \  --runs-dir agent_layer_outputs/cloud_infra \  --log-dir logs/cloud_infra \  --serialize-logs \  --max-workers 8
```

Artifacts:
- Output JSON: `agent_layer_outputs/cloud_infra/<run_id>.json`
- Log file: `logs/cloud_infra/<run_id>.log`

---

### Option B — API (FastAPI)

The API wraps the same orchestrator class. Before starting the server, set at least **`BATCH_DIR`** so the API knows where to read inputs from. You can also configure `RUNS_DIR`, `LOGS_DIR`, and an `API_KEY` for header‑based auth.

```bash
# Start the server
uvicorn services.cloud_infra_service:app --reload --host 127.0.0.1 --port 8000
```

#### Endpoints
- `GET /health` → `{"status":"ok"}`
- `POST /run` → triggers a run, returns `{run_id, output_path, log_path, output, log}`
- `GET /runs` → list runs (most‑recent first)
- `GET /runs/latest` → latest run with output and log
- `GET /runs/{run_id}` → get a specific run
- `GET /runs/last/{n}` → get last n number of runs

If `API_KEY` is set, pass it via the `X-API-Key` header.

#### Example (with `curl`)
```bash
# Trigger a run (platform is optional; defaults to "aws", run_id is optional, if not provided it genearate run_id)
curl -X POST "http://127.0.0.1:8000/run"   -H "Content-Type: application/json"   -H "X-API-Key: $API_KEY"   -d '{"platform":"aws","run_id":"run-$(date -u +%Y%m%dT%H%M%SZ)"}'

# Get latest run
curl -H "X-API-Key: $API_KEY" "http://127.0.0.1:8000/runs/latest"
```

> Note: The API requires `BATCH_DIR`. For CLI, you pass `--batch-dir` directly.

---

## ⚙️ Configuration

Key environment variables (used by API):
| Variable     | Purpose                                  | Default |
|--------------|------------------------------------------|---------|
| `BATCH_DIR`  | Folder containing metric input JSONs      | — (required for API) |
| `RUNS_DIR`   | Where to store `<run_id>.json` outputs     | `agent_layer_outputs/cloud_infra`  |
| `LOGS_DIR`   | Where to store `<run_id>.log` files        | `logs/cloud_infra`  |
| `API_KEY`    | Optional header auth for API requests      | — (required for API)   |

Metric‑to‑file mapping is defined in `data_collection_agents/cloud_infra_agent/config.py` (`Input_File_For_Metric_map`).

---

## 📊 What Happens During a Run

1. Orchestrator loads metric inputs from `--batch-dir` (or `BATCH_DIR` for API).
2. Level‑0 metrics execute (fan‑out), then Level‑1 metrics execute after deps.
3. Aggregated results are written to `agent_layer_outputs/cloud_infra/<run_id>.json`; logs to `logs/cloud_infra/<run_id>.log`.
