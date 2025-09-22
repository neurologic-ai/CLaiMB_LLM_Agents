AIMRI Mapping Pipeline — README

Purpose:
Given (a) an AIMRI catalog (JSON) and (b) per-agent metric descriptions (YAML), this pipeline:

Elaborates each metric description using domain knowledge, and

Maps each metric to the most relevant AIMRI points (1–5, elbow-cut).

Final outputs are written per agent in 'output' folder. Raw LLM outputs (JSON) are also saved for auditing in 'raw_llm_outputs'.

Directory Layout
mapping_module/
  aimri_points.json
  metric_descriptions/
    cloud_infra.yaml
    bi_tracker.yaml
    enterprise_system.yaml
    code_repo.yaml          
  outputs/
    cloud_infra.py          # generated
    bi_tracker.py           # generated
    enterprise_system.py    # generated
    code_repo.py            # generated
  raw_llm_outputs/          # generated audit artifacts
    cloud_infra/
      elaboration.json
      mapping.json
    ...
  logs/
    mapping.log
  base_agent.py
  io_utils.py
  mapper.py
  prompts.py
  run_mapping_batch.py


Inputs & Outputs:
Input A — AIMRI (JSON)

File: aimri_points.json

Shape:

{
  "aimri_points": [
    { "id": "8.4", "category": "Process Maturity", "name": "Operational Excellence" },
    { "id": "2.3", "category": "Data Management & Quality", "name": "Data Governance" },
    ...
  ]
}

Input B — Metrics (YAML per agent)

Folder: metric_descriptions/

Shape (two supported top-level forms):

# Preferred (under "metrics:")
metrics:
  - id: tagging.coverage
    description: "Resources: % with required business tags..."

  - id: compute.utilization
    description: "Compute fleet: proportion of capacity utilized."


or

# Also accepted: top-level list
- id: tagging.coverage
  name: Tagging Coverage
  description: "..."


Final Output (per agent)

Folder: outputs/

One Python file per agent, exactly in your target format:

from __future__ import annotations
from typing import Dict, List

CLOUD_INFRA_METRIC_TO_AIMRI: Dict[str, List[dict]] = {
    "tagging.coverage": [
        {"dimension": "02. Data Management & Quality", "subsection": "2.3 Data Governance"},
        {"dimension": "02. Data Management & Quality", "subsection": "2.4 Data Operations"},
    ],
    "compute.utilization": [
        {"dimension": "08. Process Maturity",           "subsection": "8.4 Operational Excellence"},
        {"dimension": "01. Technical Infrastructure",   "subsection": "1.2 Computing Resources"},
    ],
    ...
}

CLI runner anchored to the script’s directory. Supports:

single agent: --agent cloud_infra

single file: --file path/to/file.yaml

batch: default (all *.yaml in metric_descriptions/)

Prompts
Elaboration (agent-specific)

Neutral, domain-grounded “WHAT it measures” expansion (2–4 sentences).

Agents supported: cloud_infra, bi_tracker, enterprise_system, code_repo.

Mapping (neutral, for all agents)

No category bias; use domain knowledge only.

1–5 AIMRI points with an elbow cutoff in confidence (confidence+rationale are included in raw logs, not in final file).

Catalog is now provided in a canonical JSON form (see below). This dramatically reduces formatting drift.

Install & Setup
# (optional) create a venv
python3 -m venv venv
source venv/bin/activate


How to Run

From the parent directory of the package:

# Single agent by name (cloud_infra.yaml)
python -m mapping_module.run_mapping_batch --agent cloud_infra

# Single YAML file
python -m mapping_module.run_mapping_batch --file mapping_module/metric_descriptions/bi_tracker.yaml

# Batch (all YAMLs in metric_descriptions/)
python -m mapping_module.run_mapping_batch


All paths are anchored to the package directory (run_mapping_batch.py), so defaults just work:

aimri_points.json

metric_descriptions/

outputs/

logs/

Raw LLM Outputs (Auditing)

We persist one file per agent per step:

raw_llm_outputs/<agent>/elaboration.json
raw_llm_outputs/<agent>/mapping.json


Each contains:

{
  "agent": "cloud_infra",
  "kind": "mapping",
  "items": [
    {
      "metric_id": "tagging.coverage",
      "model": "gpt-4o-mini",
      "system": "...",
      "user": "... (includes the canonical JSON catalog) ...",
      "json": { "metric_id": "...", "mappings": [ { "dimension": "...", "subsection": "...", "confidence": 0.86, "rationale": "..."}, ... ] },
      "raw_text": null
    }
  ]
}


If parsing fails, we keep "json": {} and store "raw_text": "<exact LLM response>" — you never lose an output.

Final published files in outputs/ stay clean and unchanged (only dimension/subsection).
Confidence & rationale are only in these raw audit artifacts and logs.

Extending / Adding Agents

Add YAML in metric_descriptions/<agent>.yaml.

Elaboration prompt: in prompts.py, add ELABORATE_SYSTEM_<AGENT> and register it in ELABORATE_SYSTEMS[agent].

Mapping prompt: system prompts are neutral (no category bias); the catalog is canonical JSON.

Run:

python -m mapping_module.run_mapping_batch --agent <agent>
