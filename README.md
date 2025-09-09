# Enterprise Systems Agent: Automated Enterprise Workflow & Integration Assessment

Enterprise Systems Agent is a comprehensive pipeline for **automated assessment of enterprise platforms (Salesforce, ServiceNow, SAP, Workday, iPaaS, RPA, etc.)**.  
It evaluates workflows, SLAs, integration health, AI penetration, and platform risks using both static inputs and LLM-powered micro-agents.

---

## Features

- **Workflow Analysis:** SLA adherence, automation coverage, backlog aging, throughput, incident resolution.
- **Integration & Data Health:** API reliability, sync latency, topology stability, duplicate detection, data quality checks.
- **AI Integration & Outcomes:** AI penetration, uplift in outcomes, governance coverage.
- **Platform Health & Risk:** Customization debt, change failure rate, operational continuity.
- **LLM Orchestration:** Scoring with rationale, flags, gaps, and AIMRI-aligned mappings.
- **DAG Execution:** Runs metrics in dependency-aware “waves” for consistency.
- **Microservice Ready:** Exposed as a FastAPI service with `/run`, `/status`, `/logs`, etc.

---

## Requirements

- Python 3.9+
- [pip](https://pip.pypa.io/en/stable/)
- [OpenAI API key](https://platform.openai.com/account/api-keys)

---

## Installation

1. **Clone the repository:**
   ```sh
   git clone <your-enterprise-systems-repo-url>
   cd Enterprise-Systems-Agent

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

### **1.  Run Once via Orchestrator**

```sh
python -m  mvp.enterprise_runonce
```
- 	Collects a snapshot of enterprise systems and writes results to `runs_enterprise/`.

### **2. Run as API **

```sh
uvicorn api:app --reload --port 8080 
```
- Endpoints: • GET /health → service check • POST /run → start a run • GET /status/{run_id} → check status • GET /runs → list all runs • GET /logs/{run_id} → logs • GET /latest → latest run metadata.

### **3. Run Only LLM Backbones**

```sh
python data_collection_agents/enterprise_systems_agent/main.py
```

### **4. View Results**

- **Agent layer results:**  
  `runs_mlops_mvp/bi-tracker-{run_id}.json`(Agent results)
- **LLM Backbone results:**  
  `data/Output`

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
python run_once.py
# 3. See results in data/dev_platform_outputs.json
```

---

## Project Structure

```
ClaimbAI/
├── agent_layer/
│   └── enterrise_systems/
│       ├── orchestrator_enterprise.py   # EnterpriseOrchestrator (class-based)
│       ├── tool_loader_enterprise.py    # compute_* → grader mapping
│       ├── registry_enterprise.py       # DAG registry (dependencies, categories)
│       ├── router.py
│       ├── snapshot_enterprise.py       # Snapshot(dummy input)
│       ├── aimri_mapping.py             # AIMRI mappings for enterprise metrics
│       └── validate.py
│ 
│── data/                        #LLM Backbone related inputs and outputs
│   ├── sample_inputs/
│   └── Outputs/
│
├── data_collection_agents/
│   └── enterrise_systems_agent/
│       ├── base_agent.py 
│       ├── llm_engine.py        # BIUsageLLM (metric graders)
│       ├── canonical.py
│       └── logging_utils.py
│
│├── api.py                      # FastAPI microservice
│
├── workflows/                   # Snapshot collector + orchestrator call
│   └── enterprise_workflow.py   
│
├── mvp/
│   └── run_once.py                  # CLI entrypoint
├── logs/                        # Run + service logs
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
