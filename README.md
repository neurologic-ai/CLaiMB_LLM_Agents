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
python -m main
```
- This will scan all input data in DAG like structure and writes results to `runs_mvp_scanner/run_<timestamp>.json`.

### **2. Run the FastAPI Endpoints**

```sh
uvicorn fastapi_data_platform_agent:app --reload
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

```
ClaiMB_LLM_Agents/
├── agents/
│   ├── data_pipeline_agent.py       #(LLM functions)
│   ├── prompts.py                   #(Contains the prompts of the LLM functions) 
│   └── snapshot_collectors.py       #(Simoulates the data colection from various sources, presently dependent on config/config.yaml)
|
├── config/
│   └── config.yaml                  #(config file for snapshot_collectors.py)
│
├── data/Input                       #(Input JSONs)
│   └── ...json
│
├── logs/
│   └── data_platform_analyzer.log   #(logs are stored here)
│    
├── runs_mvp_scanner/                #(The output JSONs of each runs are stored here)
│   ├── run_1757144480.json          
|   └── ...
│
├── fastapi_data_platform_agent.py   #(FastAPI endpoints)
├── mvp_data_platform_scanner.py     #(orchestrates the LLM functions in a DAG topo order)
├── main.py                          #(runs the mvp)
├── .env    
├── .gitignore  
├── requirements.txt                
└── README.md                      
```

---

## License

( Our chosen license)

---

## Contact

For questions or contributions, open an issue or pull request on GitHub.
