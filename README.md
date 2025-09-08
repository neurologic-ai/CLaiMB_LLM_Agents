# BI Tracker: Automated Business Intelligence Platform Assessment

BI Tracker is a robust, extensible pipeline for **automated assessment of BI platform usage, reliability, governance, and data democratization**.  
It supports both direct signal extraction and advanced LLM-powered micro-agents to evaluate BI maturity, adoption, and operational best practices across dashboards and usage logs.

---

## Features

- **Usage Metrics:** DAU/MAU ratio, retention, active creators, session depth, drilldowns, weekly active trends.
- **Feature Adoption:** Cross-links, export rate, alerts usage.
- **Democratization:** Department coverage, self-service adoption.
- **Reliability:** Refresh timeliness, SLA breach streaks, query error rate.
- **Governance:** Coverage of governance rules, PII tagging, lineage.
- **Data Efficiency:** Source diversity, cost efficiency.
- **LLM Orchestration:** Automated scoring with rationale, flags, gaps, and AIMRI-aligned mappings.
- **Parallel Processing:** Runs metrics in dependency-ordered waves.
- **Extensible:** Add new metrics easily by updating the tool loader and registry.
- **Microservice API:** FastAPI endpoints for triggering runs, checking status, and viewing logs.

---

## Requirements

- Python 3.9+
- [pip](https://pip.pypa.io/en/stable/)
- [OpenAI API key](https://platform.openai.com/account/api-keys)
- (Optional) [tiktoken](https://github.com/openai/tiktoken) for token counting

---

## Installation

1. **Clone the repository:**
   ```sh
   git clone <your-bi-tracker-repo-url>
   cd BI-Tracker

2. **Create and activate a virtual environment:**
   ```sh
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

4. **Set up your `.env` file:**
   - Copy `.env.example` to `.env` and fill in your API keys and settings, or edit `.env` directly:
     ```
     OPENAI_API_KEY=sk-...

     ```

---

## Usage

### **1. Run Once via Orchestrator **

```sh
python run_once.py
```
- Collects a snapshot, runs orchestrator, and writes results to runs_bi_mvp/.

### **2.  Run as API Service **

```sh
uvicorn services.mlops_service:app --reload --port 8080 
```
- Endpoints:
	•	GET  /health → service check
	•	POST /run → start a run
	•	GET  /status/{run_id} → check status
	•	GET  /runs → list all runs
	•	GET  /logs/{run_id} → logs
	•	GET  /latest → latest run metadata

### **3. Run Only LLM Backbones **

```sh
python data_collection_agents/bi_tracker_agent/main.py
```

### **4. View Results**

- **results:**  
  `runs_bi_mvp/bi-tracker-{run_id}.json` (Agent results)  
  `data/micro_agents/aggregate.json` (LLM backbone results)
- **Per-repo results:**  
  `data/Outputs`

---

## Configuration

- **Model:**  
  Set `MICRO_AGENT_MODEL` in `.env` (e.g., `gpt-4o-mini`, `gpt-3.5-turbo`).

- **API Keys:**  
  - For OpenAI: `OPENAI_API_KEY`

---

## Troubleshooting

- **No output or errors:**  
  Check your `.env` for correct API keys and settings.  
  Check logs for error messages.

---

## Example: Quickstart

```sh
# 1. Clone some repos into useful_repos/
# 2. Set up your .env as above
# 3. Run:
python run_once.py
# 4. See results in runs_bi_mvp/bi-tracker-{run_id}.json
```

---

## Project Structure

```
ClaimbAI/
├── BI-Tracker/
├── agent_layer/
│   ├── orchestrator.py          # BIOrchestrator (class-based runner)
│   ├── tool_loader.py           # Metric → scorer mapping
│   ├── registry.py              # DAG (LEVEL0, LEVEL1 metrics)
│   ├── router.py              
│   └── aimri_mapping.py         # AIMRI dimension mappings
│
├── data_collection_agents/
│   └── bi_tracker_agent/
│       ├── base_agent.py 
│       ├── llm_engine.py        # BIUsageLLM (metric graders)
│       ├── canonical.py
│       └── logging_utils.py
│
├── api/
│   └── bi_tracker_service.py    # FastAPI microservice
│
├── workflows/
│   └── bi_tracker_workflow.py   # Snapshot collector + orchestrator call
│
├── run_once.py                  # CLI entrypoint
│
├── runs_bi_mvp/                 # Artifacts
├── logs/bi_tracker/             # Run + service logs
├── .env                         # OPENAI_API_KEY, OPENAI_MODEL (optional)
├── requirements.txt
└── README.md                    # this file
```

---

## License

( Our chosen license)

---

## Contact

For questions or contributions, open an issue or pull request on GitHub.
