# Cloud Infra Agent (CLaiMB)

**Cloud Infrastructure Agent** to score infra maturity using deterministic metrics (tagging coverage, compute/k8s utilization, etc.).  
You can run the agent **via CLI** *or* **via API (FastAPI)**.

---

## 📦 Repository Structure
```text
CLaiMB_LLM_Agents/
├─ agent_layer/                  # Orchestrator class and helpers
├─ cloud_infra_agent/            # Backbone metrics and utilities
│  └─ Data/
│     └─ Inputs/
│        └─ Sample2/             # Example input JSONs (per-metric)
├─ workflows/                    # monitor_workflow (L0/L1 orchestration)
├─ logs/                         # Per-run log files
├─ runs/                         # Per-run JSON outputs (<run_id>.json)
├─ api.py                        # FastAPI service (run/status/list endpoints)
├─ .env.example                  # Sample environment
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

The orchestrator is exposed as a CLI via `agent_layer.orchestrator`.  
**`--batch-dir` is required** and must point to a folder containing the per‑metric JSONs (e.g., `cloud_infra_agent/Data/Inputs/Sample2`).

```bash
# Basic run (writes runs/<run_id>.json and logs/<run_id>.log)
python -m agent_layer.orchestrator   --batch-dir cloud_infra_agent/Data/Inputs/Sample2

```

Artifacts:
- Output JSON: `runs/<run_id>.json`
- Log file: `logs/<run_id>.log`

### Option B — API (FastAPI)

The API wraps the same orchestrator class. Before starting the server, set at least **`BATCH_DIR`** so the API knows where to read inputs from. You can also configure `RUNS_DIR`, `LOGS_DIR`, and an `API_KEY` for header‑based auth.



uvicorn api:app --reload --host 127.0.0.1 --port 8000
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
| `RUNS_DIR`   | Where to store `<run_id>.json` outputs     | `runs`  |
| `LOGS_DIR`   | Where to store `<run_id>.log` files        | `logs`  |
| `API_KEY`    | Optional header auth for API requests      | — (required for API)   |

Metric‑to‑file mapping is defined in `cloud_infra_agent/config.py` (`Input_File_For_Metric_map`).

---

## 📊 What Happens During a Run

1. Orchestrator loads metric inputs from `--batch-dir` (or `BATCH_DIR` for API).
2. Level‑0 metrics execute (fan‑out), then Level‑1 metrics execute after deps.
3. Aggregated results are written to `runs/<run_id>.json`; logs to `logs/<run_id>.log`.
