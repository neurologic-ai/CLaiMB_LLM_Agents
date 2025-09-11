# ML Ops Agent: Automated MLOps Platform Assessment

ML Ops Agent is a robust, extensible pipeline for **automated assessment of MLOps platforms, pipelines, and model operations**.  
It evaluates workflows, orchestration, experiment tracking, deployment reliability, and governance readiness using both static signals and LLM-powered micro-agents.

---

## Features

- **Pipeline Analysis:** Detects training, evaluation, deployment, and monitoring steps across ML platforms.
- **Experiment Tracking:** MLflow/SageMaker/AzureML/Kubeflow pipeline detection and quality checks.
- **Automation Checks:** CI/CD integration, model retraining automation, and rollback mechanisms.
- **Governance & Compliance:** Versioning, lineage, reproducibility, and auditability.
- **Reliability Signals:** Change failure rate, deployment success, recovery times.
- **LLM Orchestration:** Automated scoring with rationale, flags, gaps, and AIMRI-aligned mappings.
- **Parallel Processing:** Executes metrics in DAG-ordered waves.
- **Extensible:** Add new micro-agents or platform-specific checks easily.
- **Microservice API (optional):** Can be wrapped into a FastAPI service similar to BI Tracker.

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
   git clone <your-mlops-agent-repo-url>
   cd ML-Ops-Agent

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

### **1. Run Once via Orchestrator**

```sh
 python mvp/mlops_runonce.py
```

- Collects a snapshot of platform + pipeline signals and writes results to `runs_mlops/`.

### **2.  Run as API**

```sh
uvicorn services.mlops_service:app --reload --port 8080 
```
- Endpoints: 
• GET /health → service check 
• POST /run → start a run 
• GET /status/{run_id} → check status 
• GET /runs → list all runs 
• GET /logs/{run_id} → logs 
• GET /latest → latest run metadata.

### **3.  Run Only LLM Backbones**

```sh
python data_collection_agents/ml_ops_agent/main.py
```
### **4. Update the Mappings using LLM**

```sh
python -m agent_layer.ml_ops_agent.update
```

### **5. View Results**

- **Agent layer results:**  
  `agent_layer_output/` (Agent results)
- **LLM Backbone results:**  
  `data/Outputs`

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
python mvp/mlops_runonce.py
# 3. See results in data/dev_platform_outputs.json
```

---

## Project Structure

```
ClaimbAI/
├── agent_layer/
│   └──  ml_ops_agent/
│        ├── orchestrator_mlops.py          # BIOrchestrator (class-based runner)
│        ├── tool_loader_mlops.py           # Metric → scorer mapping
│        ├── registry_mlops.py              # DAG (LEVEL0, LEVEL1 metrics)
│        ├── route_mlopsr.py  
│        ├── update.py                # Updates the aimri mappings
│        ├── map_db.py                # Contains the list of functions as well as the list of AIMRI parameters.            
│        └── aimri_mapping.py         # AIMRI dimension mappings
│ 
├── agent_layer_output/          # Agent outputs
│ 
│── data/                        #LLM Backbone related inputs and outputs
│   ├── Inputs/
│   └── Outputs/
│
├── data_collection_agents/
│   └── ml_ops_agent/
│       ├── base_agent.py 
│       ├── llm_engine.py        # BIUsageLLM (metric graders)
│       ├── canonical.py
│       └── logging_utils.py
│
├── services/
│   └── mlops_service.py         # FastAPI microservice
│
├── workflows/                   # Snapshot collector + orchestrator call
│   ├── ml_ops_workflow.py   
│   └── snapshot_mlops.py
│
├── mvp/mlops_runonce.py         # CLI entrypoint
├── logs/ml_ops/                 # Run + service logs
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
