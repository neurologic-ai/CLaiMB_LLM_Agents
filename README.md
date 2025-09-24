# CLaiMB LLM Agents: Multi-Agent Orchestrator for AI/ML Maturity Assessment

CLaiMB LLM Agents is a unified framework of automated assessment agents designed to evaluate enterprise AI/ML readiness and operational maturity across infrastructure, data platforms, MLOps, BI adoption, Code repositories and enterprise systems.

The orchestrator integrates deterministic metrics (e.g., tagging coverage, refresh timeliness) with LLM-powered scoring micro-agents, producing AIMRI-aligned category scores and overall maturity levels. 

---

## 📦 Available Agents

- **BI Tracker Agent** – Automated assessment of BI platform usage, reliability, and governance.
- **ML Ops Agent** – Automated assessment of MLOps platforms, pipelines, and model operations.
- **Enterprise Systems Agent** – Automated assessment of enterprise workflows & integrations.
- **Cloud Infra Agent (CLaiMB)** – Automated scoring of cloud infrastructure maturity.
- **Data Platform Analyzer Agent** – Automated AI/ML repository and data platform quality assessment.
- **Development Environment Scanner** - Automated assessment of Code repositories
---

## 🧰 Requirements

- Python 3.9+ (agents may require 3.10+ in some cases)
- [pip](https://pip.pypa.io/en/stable/)
- [OpenAI API key](https://platform.openai.com/account/api-keys)  
- (Optional) [tiktoken](https://github.com/openai/tiktoken) for token counting

---

## ⚙️ Installation

1. **Clone the repository** (choose the branch you need, or main if merged):
   ```bash
   git clone https://github.com/neurologic-ai/CLaiMB_LLM_Agents
   cd CLaiMB_LLM_Agents

2. **Create and activate a virtual environment:** (may use conda as well)
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
python -m main_orchestrator.tick_cli
```
  • Runs collectors (cloud_infra, ml_ops, bi_tracker, enterprise_systems, data_platform).
	•	Aggregates into AIMRI category scores.
	•	Saves results in ./results.

### **2.  Run as API Service **

```sh
uvicorn main_orchestrator.app_main:app --reload --port 8000 
```
- Endpoints:
	•	GET  /health → service check
	•	POST /run → start a run
	•	GET  /status/{run_id} → check status
	•	GET  /runs → list all runs
	•	GET  /logs/{run_id} → logs
	•	GET  /latest → latest run metadata
  •	POST /run_all → start all agents run


### **4. View Results**

- **Orchestrator results:**  
  `orchestrator_output/` (Per Agent results)
- **LLM Backbone results**  
  `results/` (Scoring agent results)

---

## Configuration

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
# 1. Set up your .env as above
# 2. Run:
python -m main_orchestrator.tick_cli
# 3. See results in runs_bi_mvp/bi-tracker-{run_id}.json
```

---


## Project Structure

```
CLaiMB_LLM_Agents/
├── agent_layer/                  # Orchestrators + registries per agent
│   ├── cloud_infra_agent/
│   ├── ml_ops_agent/
│   ├── bi_tracker_agent/
│   ├── enterprise_systems/
│   └── AGENT_DATA_PLATFORM_ANALYZER/
│
├── data_collection_agents/       # Backbone agents
│   ├── cloud_infra_agent/
│   ├── ml_ops_agent/
│   ├── bi_tracker_agent/
│   ├── enterprise_systems_agent/
│   └── data_platform_agent/
│
├── main_orchestrator/            # Central orchestrator + FastAPI microservice
│   ├── graph_orchestrator.py
│   ├── tick_cli.py
│   ├── survey_recalibrator.py
│   ├── adapters.py
│   ├── scoring.py
│   ├── feature_bus.py
│   └── app_main.py
│   
│── workflows/                    # Snapshot collector
│      
├── orchestrator_output/          # Consolidated orchestrator outputs(per agent results)
├── results/                      # Scoring agent results ( Recalibrated scores)
├── surveys/                      # Survey inputs (YAML/CSV)
├── metric_descriptions/          # Metrics Function descriptions (YAML/CSV)
├── requirements.txt
├── docker-compose.yml
├── Dockerfile
└── README.md                     # This file
```

---

## License

( Our chosen license)

---

## Contact

For questions or contributions, open an issue or pull request on GitHub.

git clone --branch AGENT_ML_OPS_MONITOR https://github.com/neurologic-ai/CLaiMB_LLM_Agents