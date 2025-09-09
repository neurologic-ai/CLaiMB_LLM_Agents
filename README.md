# ClaimbAI: Automated AI/ML Repository Quality Assessment

## This Readme is exclusively meant for running the DATA_PLATFORM_ANALYZER agent. 

## Requirements

- Python 3.13.12
- [pip](https://pip.pypa.io/en/stable/)
- [OpenAI API key](https://platform.openai.com/account/api-keys)


---

## Installation

1. **Clone the repository:**
   ```sh
   git clone --branch DATA_PLATFORM_ANALYZER https://github.com/neurologic-ai/CLaiMB_LLM_Agents
   cd CLaiMB_LLM_Agents
   ```

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

### **1. Run the Agent using main.py (Recommended)**

```sh
python -m mvp.main
```
- This will scan all input data in DAG like structure and writes results to `runs_mvp_scanner/run_<timestamp>.json`.

### **2. Run the FastAPI Endpoints**

```sh
uvicorn services.AGENT_DATA_PLATFORM_ANALYZER.fastapi_data_platform_agent:app --reload
```

### **4. View Results**

- **Aggregate results:**  
  `runs_mvp_scanner/run_<timestamp>.json`   
- **Checking FastAPI endpoints:**  
  go to `http://127.0.0.1:8000/docs` 
  ```
  Endpoints :

  * GET  /health          - Checks status 
  * POST /run             - Initiates a data scan
  * GET  /runs            - Shows list of all runs
  * GET  /latest          - Returns the latest run JSON
  * GET  /runs/{run_id}   - Returns the specific run JSON
  * GET  /runs/latest/{n} - Returns the last 'n' runs JSON.
  ```

---


## Project Structure

AGENT_DATA_PLATFORM_ANALYZER

```
ClaimbAI/
├── agent_layer/
|   └──  AGENT_DATA_PLATFORM_ANALYZER
│        ├── data_pipeline_agent.py          # LLM Functions
│        ├── prompts.py                      # Prompts for the LLM Functions             
│        └── aimri_mapping.py                # AIMRI dimension mappings
│ 
├── agent_layer_output/          
|   └──  AGENT_DATA_PLATFORM_ANALYZER
|        ├── run_<timestamp>.json            # JSON output for each run 
|        └── ...
│ 
│── data/                                    
|   └──  AGENT_DATA_PLATFORM_ANALYZER
│        └──  Input/...                      # Input JSONs
|
├── logs/AGENT_DATA_PLATFORM_ANALYZER/       # Run logs
│
├── services/
|   └──  AGENT_DATA_PLATFORM_ANALYZER
│        └── fastapi_data_platform_agent.py  # FastAPI service       
│
├── workflows/                   
|   └──  AGENT_DATA_PLATFORM_ANALYZER
│        ├── mvp_data_platform_scanner.py    # Agent
│        └── snapshot_collectors.py          # data collector simulator
|
├── mvp/
|   └──  AGENT_DATA_PLATFORM_ANALYZER
|        └── main.py                         # CLI entrypoint                 
├── .env                                     # OPENAI_API_KEY
├── requirements.txt
└── README.md                                # this file               
```

---

## License

( Our chosen license)

---

## Contact

For questions or contributions, open an issue or pull request on GitHub.

git clone --branch AGENT_ML_OPS_MONITOR https://github.com/neurologic-ai/CLaiMB_LLM_Agents