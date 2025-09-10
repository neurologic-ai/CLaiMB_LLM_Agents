# agent_layer/aimri_mapping_code_repo.py
from __future__ import annotations
from typing import Dict, List

# AIMRI lookup for Code Repo Agent metrics — keys must match metric_id in your output.
CODE_REPO_METRIC_TO_AIMRI: Dict[str, List[Dict[str, str]]] = {
    # --- code.* ---
    "code.cyclomatic_complexity_band": [
        {"dimension": "04. Talent & Skills",             "subsection": "4.1 Technical Expertise"},
        {"dimension": "08. Process Maturity",            "subsection": "8.3 Quality Assurance"},
        {"dimension": "01. Technical Infrastructure",    "subsection": "1.2 Computing Resources"},
    ],
    "code.maintainability_band": [
        {"dimension": "08. Process Maturity",            "subsection": "8.3 Quality Assurance"},
        {"dimension": "08. Process Maturity",            "subsection": "8.4 Operational Excellence"},
        {"dimension": "04. Talent & Skills",             "subsection": "4.1 Technical Expertise"},
    ],
    "code.docstring_coverage_band": [
        {"dimension": "08. Process Maturity",            "subsection": "8.2 Documentation Practices"},
        {"dimension": "04. Talent & Skills",             "subsection": "4.1 Technical Expertise"},
        {"dimension": "05. Governance & Ethics",         "subsection": "5.5 Transparency Practices"},
    ],
    "code.nested_loops_band": [
        {"dimension": "01. Technical Infrastructure",    "subsection": "1.2 Computing Resources"},
        {"dimension": "08. Process Maturity",            "subsection": "8.4 Operational Excellence"},
        {"dimension": "04. Talent & Skills",             "subsection": "4.1 Technical Expertise"},
    ],

    # --- fs.* ---
    "fs.tests_practice": [
        {"dimension": "08. Process Maturity",            "subsection": "8.3 Quality Assurance"},
        {"dimension": "13. AI Risk & Resilience",       "subsection": "13.1 Model Reliability & Robustness"},
    ],
    "fs.env_config_maturity": [
        {"dimension": "01. Technical Infrastructure",    "subsection": "1.3 Development Environment"},
        {"dimension": "13. AI Risk & Resilience",       "subsection": "13.2 Data Dependability & Trust"},
    ],
    "fs.ci_cd_maturity": [
        {"dimension": "08. Process Maturity",            "subsection": "8.1 Project Management"},
        {"dimension": "08. Process Maturity",            "subsection": "8.4 Operational Excellence"},
    ],
    "fs.deployment_maturity": [
        {"dimension": "01. Technical Infrastructure",    "subsection": "1.4 Integration Architecture"},
        {"dimension": "09. Foundation Model Operations", "subsection": "9.3 Performance Optimization"},
    ],
    "fs.experiment_org": [
        {"dimension": "07. Cultural Readiness",          "subsection": "7.1 Innovation Mindset"},
        {"dimension": "07. Cultural Readiness",          "subsection": "7.4 Decision Making"},
    ],
    "fs.project_structure": [
        {"dimension": "01. Technical Infrastructure",    "subsection": "1.3 Development Environment"},
        {"dimension": "08. Process Maturity",            "subsection": "8.4 Operational Excellence"},
    ],

    # --- infra.* ---
    "infra.parallel_patterns": [
        {"dimension": "01. Technical Infrastructure",    "subsection": "1.2 Computing Resources"},
        {"dimension": "13. AI Risk & Resilience",       "subsection": "13.1 Model Reliability & Robustness"},
    ],
    "infra.inference_endpoint": [
        {"dimension": "01. Technical Infrastructure",    "subsection": "1.4 Integration Architecture"},
        {"dimension": "03. AI/ML Capabilities",          "subsection": "3.3 MLOps Maturity"},
        {"dimension": "09. Foundation Model Operations", "subsection": "9.1 Model Integration & Deployment"},
        {"dimension": "09. Foundation Model Operations", "subsection": "9.5 Scaling & Distribution"},
    ],
    "infra.model_export": [
        {"dimension": "02. Data Management & Quality",   "subsection": "2.1 Data Architecture"},
        {"dimension": "02. Data Management & Quality",   "subsection": "2.2 Data Quality"},
        {"dimension": "02. Data Management & Quality",   "subsection": "2.4 Data Operations"},
    ],
    "infra.data_pipeline": [
        {"dimension": "02. Data Management & Quality",   "subsection": "2.2 Data Quality"},
        {"dimension": "03. AI/ML Capabilities",          "subsection": "3.1 Model Development"},
    ],
    "infra.feature_engineering": [
        {"dimension": "01. Technical Infrastructure",    "subsection": "1.5 Security Infrastructure"},
        {"dimension": "05. Governance & Ethics",         "subsection": "5.2 Regulatory Compliance"},
        {"dimension": "11. Responsible AI & Social Impact", "subsection": "11.3 Privacy & Data Protection"},
        {"dimension": "13. AI Risk & Resilience",       "subsection": "13.5 Regulatory & Legal Compliance"},
    ],
    "infra.security_hygiene": [
        {"dimension": "01. Technical Infrastructure",    "subsection": "1.5 Security Infrastructure"},
        {"dimension": "05. Governance & Ethics",         "subsection": "5.2 Regulatory Compliance"},
        {"dimension": "11. Responsible AI & Social Impact", "subsection": "11.3 Privacy & Data Protection"},
        {"dimension": "13. AI Risk & Resilience",       "subsection": "13.5 Regulatory & Legal Compliance"},
    ],

    # --- ml.* ---
    "ml.framework_maturity": [
        {"dimension": "03. AI/ML Capabilities",          "subsection": "3.3 MLOps Maturity"},
        {"dimension": "08. Process Maturity",            "subsection": "8.4 Operational Excellence"},
    ],
    "ml.experiment_tracking": [
        {"dimension": "03. AI/ML Capabilities",          "subsection": "3.3 MLOps Maturity"},
        {"dimension": "08. Process Maturity",            "subsection": "8.5 Measurement & Metrics"},
    ],
    "ml.hpo_practice": [
        {"dimension": "03. AI/ML Capabilities",          "subsection": "3.1 Model Development"},
    ],
    "ml.data_validation": [
        {"dimension": "02. Data Management & Quality",   "subsection": "2.2 Data Quality"},
        {"dimension": "02. Data Management & Quality",   "subsection": "2.4 Data Operations"},
    ],
    "ml.training_practice": [
        {"dimension": "03. AI/ML Capabilities",          "subsection": "3.1 Model Development"},
        {"dimension": "08. Process Maturity",            "subsection": "8.4 Operational Excellence"},
    ],
    "ml.evaluation_practice": [
        {"dimension": "03. AI/ML Capabilities",          "subsection": "3.4 Model Governance"},
        {"dimension": "08. Process Maturity",            "subsection": "8.5 Measurement & Metrics"},
        {"dimension": "13. AI Risk & Resilience",       "subsection": "13.1 Model Reliability & Robustness"},
    ],
}