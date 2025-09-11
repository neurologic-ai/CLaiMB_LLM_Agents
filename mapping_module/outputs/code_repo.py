from __future__ import annotations
from typing import Dict, List

CODE_REPO_METRIC_TO_AIMRI: Dict[str, List[dict]] = {
    "code.cyclomatic_complexity_band": [
        {"dimension": "8.3 — Process Maturity", "subsection": "Quality Assurance"},
        {"dimension": "4.1 — Talent & Skills", "subsection": "Technical Expertise"},
        {"dimension": "8.2 — Process Maturity", "subsection": "Documentation Practices"},
        {"dimension": "4.4 — Talent & Skills", "subsection": "Training & Development"}
    ],
    "code.maintainability_band": [
        {"dimension": "8.1 — Process Maturity", "subsection": "Project Management"},
        {"dimension": "8.2 — Process Maturity", "subsection": "Documentation Practices"},
        {"dimension": "8.3 — Process Maturity", "subsection": "Quality Assurance"},
        {"dimension": "4.1 — Talent & Skills", "subsection": "Technical Expertise"},
        {"dimension": "6.4 — Strategic Alignment", "subsection": "Innovation Management"}
    ],
    "code.docstring_coverage_band": [
        {"dimension": "8. Process Maturity", "subsection": "8.2 Documentation Practices"},
        {"dimension": "4. Talent & Skills", "subsection": "4.4 Training & Development"},
        {"dimension": "6. Strategic Alignment", "subsection": "6.4 Innovation Management"}
    ],
    "code.nested_loops_band": [
        {"dimension": "8.4 - Process Maturity", "subsection": "Operational Excellence"},
        {"dimension": "8.3 - Process Maturity", "subsection": "Quality Assurance"},
        {"dimension": "4.1 - Talent & Skills", "subsection": "Technical Expertise"},
        {"dimension": "3.1 - AI/ML Capabilities", "subsection": "Model Development"}
    ],
    "repo.tests_presence": [
        {"dimension": "8.3 — Process Maturity", "subsection": "Quality Assurance"},
        {"dimension": "8.4 — Process Maturity", "subsection": "Operational Excellence"},
        {"dimension": "4.1 — Talent & Skills", "subsection": "Technical Expertise"},
        {"dimension": "6.4 — Strategic Alignment", "subsection": "Innovation Management"},
        {"dimension": "3.1 — AI/ML Capabilities", "subsection": "Model Development"}
    ],
    "repo.env_config_hygiene": [
        {"dimension": "1.3", "subsection": "Technical Infrastructure / Development Environment"},
        {"dimension": "3.3", "subsection": "AI/ML Capabilities / MLOps Maturity"},
        {"dimension": "8.2", "subsection": "Process Maturity / Documentation Practices"},
        {"dimension": "4.4", "subsection": "Talent & Skills / Training & Development"}
    ],
    "repo.cicd_presence": [
        {"dimension": "1.4 - Technical Infrastructure", "subsection": "Integration Architecture"},
        {"dimension": "8.3 - Process Maturity", "subsection": "Quality Assurance"},
        {"dimension": "8.4 - Process Maturity", "subsection": "Operational Excellence"},
        {"dimension": "4.1 - Talent & Skills", "subsection": "Technical Expertise"},
        {"dimension": "6.4 - Strategic Alignment", "subsection": "Innovation Management"}
    ],
    "repo.deployment_readiness": [
        {"dimension": "1.1", "subsection": "Technical Infrastructure / Cloud Computing Capabilities"},
        {"dimension": "1.4", "subsection": "Technical Infrastructure / Integration Architecture"},
        {"dimension": "3.2", "subsection": "AI/ML Capabilities / Production Deployment"},
        {"dimension": "8.3", "subsection": "Process Maturity / Quality Assurance"},
        {"dimension": "8.4", "subsection": "Process Maturity / Operational Excellence"}
    ],
    "repo.experiments_management": [
        {"dimension": "3.3", "subsection": "AI/ML Capabilities / MLOps Maturity"},
        {"dimension": "8.2", "subsection": "Process Maturity / Documentation Practices"},
        {"dimension": "3.1", "subsection": "AI/ML Capabilities / Model Development"},
        {"dimension": "2.2", "subsection": "Data Management & Quality / Data Quality"},
        {"dimension": "8.4", "subsection": "Process Maturity / Operational Excellence"}
    ],
    "repo.project_structure": [
        {"dimension": "8.2 — Process Maturity", "subsection": "Documentation Practices"},
        {"dimension": "4.3 — Talent & Skills", "subsection": "Team Structure"},
        {"dimension": "6.4 — Strategic Alignment", "subsection": "Innovation Management"},
        {"dimension": "8.1 — Process Maturity", "subsection": "Project Management"}
    ],
    "parallel_patterns": [
        {"dimension": "1.1", "subsection": "Technical Infrastructure / Cloud Computing Capabilities"},
        {"dimension": "3.3", "subsection": "AI/ML Capabilities / MLOps Maturity"},
        {"dimension": "13.1", "subsection": "AI Risk & Resilience / Model Reliability & Robustness"},
        {"dimension": "8.3", "subsection": "Process Maturity / Quality Assurance"}
    ],
    "inference_endpoint": [
        {"dimension": "3.2 AI/ML Capabilities", "subsection": "Production Deployment"},
        {"dimension": "13.1 AI Risk & Resilience", "subsection": "Model Reliability & Robustness"},
        {"dimension": "1.4 Technical Infrastructure", "subsection": "Integration Architecture"},
        {"dimension": "3.3 AI/ML Capabilities", "subsection": "MLOps Maturity"},
        {"dimension": "8.3 Process Maturity", "subsection": "Quality Assurance"}
    ],
    "model_export": [
        {"dimension": "3.1 — AI/ML Capabilities", "subsection": "Model Development"},
        {"dimension": "3.2 — AI/ML Capabilities", "subsection": "Production Deployment"},
        {"dimension": "3.3 — AI/ML Capabilities", "subsection": "MLOps Maturity"},
        {"dimension": "9.1 — Foundation Model Operations", "subsection": "Model Integration & Deployment"},
        {"dimension": "4.1 — Talent & Skills", "subsection": "Technical Expertise"}
    ],
    "data_pipeline": [
        {"dimension": "2.1", "subsection": "Data Management & Quality / Data Architecture"},
        {"dimension": "2.4", "subsection": "Data Management & Quality / Data Operations"},
        {"dimension": "8.4", "subsection": "Process Maturity / Operational Excellence"},
        {"dimension": "1.4", "subsection": "Technical Infrastructure / Integration Architecture"}
    ],
    "feature_engineering": [
        {"dimension": "2.1", "subsection": "Data Management & Quality / Data Architecture"},
        {"dimension": "2.2", "subsection": "Data Management & Quality / Data Quality"},
        {"dimension": "3.1", "subsection": "AI/ML Capabilities / Model Development"},
        {"dimension": "3.3", "subsection": "AI/ML Capabilities / MLOps Maturity"},
        {"dimension": "8.2", "subsection": "Process Maturity / Documentation Practices"}
    ],
    "security_hygiene": [
        {"dimension": "1.5", "subsection": "Technical Infrastructure / Security Infrastructure"},
        {"dimension": "5.3", "subsection": "Governance & Ethics / Risk Management"},
        {"dimension": "5.2", "subsection": "Governance & Ethics / Regulatory Compliance"},
        {"dimension": "13.5", "subsection": "AI Risk & Resilience / Regulatory & Legal Compliance"}
    ],
    "ml.framework_maturity": [
        {"dimension": "3.1", "subsection": "AI/ML Capabilities / Model Development"},
        {"dimension": "3.3", "subsection": "AI/ML Capabilities / MLOps Maturity"},
        {"dimension": "4.1", "subsection": "Talent & Skills / Technical Expertise"},
        {"dimension": "8.2", "subsection": "Process Maturity / Documentation Practices"},
        {"dimension": "8.3", "subsection": "Process Maturity / Quality Assurance"}
    ],
    "ml.experiment_tracking": [
        {"dimension": "3.1 — AI/ML Capabilities", "subsection": "Model Development"},
        {"dimension": "3.3 — AI/ML Capabilities", "subsection": "MLOps Maturity"},
        {"dimension": "2.2 — Data Management & Quality", "subsection": "Data Quality"},
        {"dimension": "8.5 — Process Maturity", "subsection": "Measurement & Metrics"},
        {"dimension": "4.4 — Talent & Skills", "subsection": "Training & Development"}
    ],
    "ml.hpo_practice": [
        {"dimension": "3.1", "subsection": "AI/ML Capabilities / Model Development"},
        {"dimension": "3.3", "subsection": "AI/ML Capabilities / MLOps Maturity"},
        {"dimension": "13.1", "subsection": "AI Risk & Resilience / Model Reliability & Robustness"},
        {"dimension": "8.3", "subsection": "Process Maturity / Quality Assurance"}
    ],
    "ml.data_validation": [
        {"dimension": "2.2", "subsection": "Data Management & Quality / Data Quality"},
        {"dimension": "2.1", "subsection": "Data Management & Quality / Data Architecture"},
        {"dimension": "3.3", "subsection": "AI/ML Capabilities / MLOps Maturity"},
        {"dimension": "8.3", "subsection": "Process Maturity / Quality Assurance"},
        {"dimension": "2.4", "subsection": "Data Management & Quality / Data Operations"}
    ],
    "ml.training_practice": [
        {"dimension": "3.1 — AI/ML Capabilities", "subsection": "Model Development"},
        {"dimension": "3.3 — AI/ML Capabilities", "subsection": "MLOps Maturity"},
        {"dimension": "13.1 — AI Risk & Resilience", "subsection": "Model Reliability & Robustness"},
        {"dimension": "8.3 — Process Maturity", "subsection": "Quality Assurance"},
        {"dimension": "4.4 — Talent & Skills", "subsection": "Training & Development"}
    ],
    "ml.evaluation_practice": [
        {"dimension": "5.1 — Governance & Ethics", "subsection": "Ethical Framework"},
        {"dimension": "11.1 — Responsible AI & Social Impact", "subsection": "Algorithmic Fairness & Bias Mitigation"},
        {"dimension": "3.4 — AI/ML Capabilities", "subsection": "Model Governance"},
        {"dimension": "8.3 — Process Maturity", "subsection": "Quality Assurance"},
        {"dimension": "2.2 — Data Management & Quality", "subsection": "Data Quality"}
    ]
}
