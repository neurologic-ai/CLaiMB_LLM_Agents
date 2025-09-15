from __future__ import annotations
from typing import List, Dict

# ---------- Agent-specific System Prompts (Elaboration) ----------

ELABORATE_SYSTEM_GENERIC = (
    "You are a senior cloud/enterprise systems analyst. "
    "Expand the short metric description into a clear, domain-grounded explanation. "
    "Focus on WHAT it measures (boundaries, scope, components), not HOW it is computed. "
    "Return only JSON."
)

ELABORATE_SYSTEM_CLOUD = (
    "You are a Cloud Infrastructure and FinOps analyst. "
    "Expand the short metric description into a clear, domain-grounded explanation. "
    "Focus on WHAT aspect of cloud infrastructure/operations is being measured "
    "(e.g., tagging, utilization, scaling, reliability, security, cost). "
    "Avoid implementation details; Return only JSON."
)

ELABORATE_SYSTEM_BI = (
    "You are a Business Intelligence adoption and governance analyst. "
    "Expand the short metric description into a clear, domain-grounded explanation. "
    "Focus on WHAT aspect of BI usage, engagement, content governance, or decision support is being measured. "
    "Avoid implementation details; Return only JSON."
)

ELABORATE_SYSTEM_ENTERPRISE = (
    "You are an Enterprise Systems and Process analyst. "
    "Expand the short metric description into a clear, domain-grounded explanation. "
    "Focus on WHAT aspect of ERP/HR/ITSM workflows, controls, and automation is being measured. "
    "Avoid implementation details; Return only JSON."
)

ELABORATE_SYSTEM_CODE_REPO = (
    "You are a senior software engineering and MLOps reviewer. "
    "Your task is to expand a short metric description into a clear, domain-grounded explanation "
    "for code repositories and ML engineering workflows. "
    "Clarify WHAT is measured (scope, boundaries, typical signals), not HOW to compute it. "
    "Avoid implementation details, thresholds, or tool-specific commands. "
    "Be neutral and factual. Return only JSON."
)

ELABORATE_SYSTEMS: Dict[str, str] = {
    "cloud_infra": ELABORATE_SYSTEM_CLOUD,
    "bi_tracker": ELABORATE_SYSTEM_BI,
    "enterprise_system": ELABORATE_SYSTEM_ENTERPRISE,
    "code_repo": ELABORATE_SYSTEM_CODE_REPO
}

def get_elaborate_system(agent_key: str) -> str:
    return ELABORATE_SYSTEMS.get(agent_key, ELABORATE_SYSTEM_GENERIC)

# ---------- System Prompts (AIMRI Mapping) ----------
# NOTE: No biasing to particular AIMRI categories. Use domain knowledge only.

MAP_SYSTEM_GENERIC = (
    "You are mapping metrics to AIMRI categories using domain knowledge only. "
    "Do not bias toward any category; select the best matches based on semantics and scope. "
    "Return only JSON."
)

MAP_SYSTEM_CODE_REPO = (
    "You are mapping code-repository metrics to AIMRI points using domain knowledge only. "
    "Do not bias toward any AIMRI category. "
    "Select the best 1–5 matches by semantic proximity and scope. "
    "Rank by relevance and apply an elbow cutoff if confidence drops. "
    "For each selection, provide a confidence in [0,1] and a one-sentence rationale. "
    "Return only JSON."
)

MAP_SYSTEMS: Dict[str, str] = {
    # "cloud_infra": MAP_SYSTEM_CLOUD,
    # "bi_tracker": MAP_SYSTEM_BI,
    # "enterprise_system": MAP_SYSTEM_ENTERPRISE,
    "code_repo": MAP_SYSTEM_CODE_REPO
}

def get_map_system(agent_key: str) -> str:
    return MAP_SYSTEMS.get(agent_key, MAP_SYSTEM_GENERIC)
    
# ---------- User Prompts ----------

def elaborate_user(metric_id: str, name: str, description: str) -> str:
    return f"""Expand the following metric description using domain knowledge.
Metric id: {metric_id}
Metric name: {name}
Short description: {description}

Return a STRICT JSON with keys:
- metric_id (string)
- name (string)
- elaborated_description (string: 5-6 crisp sentences focusing on WHAT is measured and scope/boundaries)
"""

def map_user(metric_id: str, name: str, elaborated: str, aimri_catalog: List[Dict[str, str]]) -> str:
    catalog_str = "\n".join([f"{i+1}. {p['id']} — {p['category']} / {p['name']}" for i,p in enumerate(aimri_catalog)])
    return f"""Metric:
- id: {metric_id}
- name: {name}
- description: {elaborated}

AIMRI Catalog (id — Category / Name):
{catalog_str}

Task:
1) Using domain knowledge only (no bias), identify the most relevant AIMRI points (1 to 5).
2) For each candidate, produce:
   - dimension: "NN. Category"
   - subsection: "N.M Title"
   - confidence: float in [0,1]
   - rationale: one sentence explaining the semantic fit
3) Apply an elbow cutoff on confidence: include items until confidence drops sharply; cap at 5.
Return STRICT JSON:
{{
  "metric_id": "{metric_id}",
  "mappings": [{{"dimension": "NN. Category", "subsection": "N.M Title", "confidence": 0.0, "rationale": "..."}}...]
}}
"""
# --- PATCH START: canonicalize AIMRI catalog in the user prompt (no output schema changes) ---
def map_user(metric_id: str, name: str, elaborated: str, aimri_catalog: List[Dict[str, str]]) -> str:
    # Build a clean, machine-readable catalog: no slashes/emdashes.
    # Example record:
    # {"id":"8.3","dimension":"08. Process Maturity","subsection":"8.3 Quality Assurance"}
    def _records():
        recs = []
        for p in aimri_catalog:
            ident = p["id"].strip()
            category = p["category"].strip()
            subname = p["name"].strip()
            major = int(float(ident.split(".")[0]))
            recs.append({
                "id": ident,
                "dimension": f"{major:02d}. {category}",
                "subsection": f"{ident} {subname}",
            })
        return recs

    # Local import avoids adding a top-level dependency change
    import json as _json
    catalog_json = _json.dumps(_records(), ensure_ascii=False, indent=2)

    return f"""Metric:
- id: {metric_id}
- name: {name}
- description: {elaborated}

AIMRI_CATALOG (canonical JSON for reference):
```json
{catalog_json}

Task:
1) Using domain knowledge only (no bias), identify the most relevant AIMRI points (1 to 5).
2) For each candidate, produce:
   - dimension: "NN. Category"
   - subsection: "N.M Title"
   - confidence: float in [0,1]
   - rationale: one sentence explaining the semantic fit
3) Apply an elbow cutoff on confidence: include items until confidence drops sharply; cap at 5.
Return STRICT JSON:
{{
  "metric_id": "{metric_id}",
  "mappings": [{{"dimension": "NN. Category", "subsection": "N.M Title", "confidence": 0.0, "rationale": "..."}}...]
}}
"""