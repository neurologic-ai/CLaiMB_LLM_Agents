# agent_layer/aimri_mapping_mlops.py
from __future__ import annotations
from typing import Dict, List

MLOPS_METRIC_TO_AIMRI: Dict[str, List[Dict[str, str]]] = {
    # -------- mlflow.* --------
    "mlflow.experiment_completeness_band": [
        {"dimension": "03. AI/ML Capabilities",          "subsection": "3.3 MLOps Maturity"},
        {"dimension": "08. Process Maturity",            "subsection": "8.5 Measurement & Metrics"},
    ],
    "mlflow.lineage_coverage_band": [
        {"dimension": "05. Governance & Ethics",         "subsection": "5.4 Transparency Practices"},
        {"dimension": "02. Data Management & Quality",   "subsection": "2.3 Data Governance"},
    ],
    "mlflow.experiment_velocity_band": [
        {"dimension": "07. Cultural Readiness",          "subsection": "7.1 Innovation Mindset"},
        {"dimension": "06. Strategic Alignment",         "subsection": "6.5 Innovation Management"},
    ],
    "mlflow.registry_hygiene_band": [
        {"dimension": "05. Governance & Ethics",         "subsection": "5.2 Regulatory Compliance"},
        {"dimension": "09. Foundation Model Operations", "subsection": "9.2 Domain Adaptation & Fine-tuning"},
    ],
    "mlflow.validation_artifacts_band": [
        {"dimension": "02. Data Management & Quality",   "subsection": "2.2 Data Quality"},
        {"dimension": "13. AI Risk & Resilience",        "subsection": "13.1 Model Reliability & Robustness"},
    ],
    "mlflow.reproducibility_band": [
        {"dimension": "13. AI Risk & Resilience",        "subsection": "13.1 Model Reliability & Robustness"},
        {"dimension": "08. Process Maturity",            "subsection": "8.4 Operational Excellence"},
    ],

    # -------- aml.* --------
    "aml.endpoint_slo_band": [
        {"dimension": "09. Foundation Model Operations", "subsection": "9.1 Model Integration & Deployment"},
        {"dimension": "13. AI Risk & Resilience",        "subsection": "13.4 Operational Continuity"},
    ],
    "aml.jobs_flow_band": [
        {"dimension": "08. Process Maturity",            "subsection": "8.3 Quality Assurance"},
        {"dimension": "03. AI/ML Capabilities",          "subsection": "3.3 MLOps Maturity"},
    ],
    "aml.monitoring_coverage_band": [
        {"dimension": "13. AI Risk & Resilience",        "subsection": "13.1 Model Reliability & Robustness"},
        {"dimension": "03. AI/ML Capabilities",          "subsection": "3.4 Model Governance"},
    ],
    "aml.registry_governance_band": [
        {"dimension": "05. Governance & Ethics",         "subsection": "5.2 Regulatory Compliance"},
        {"dimension": "03. AI/ML Capabilities",          "subsection": "3.4 Model Governance"},
    ],
    "aml.cost_correlation_band": [
        {"dimension": "12. AI Business Value & ROI",     "subsection": "12.2 Cost Reduction & Efficiency"},
        {"dimension": "06. Strategic Alignment",         "subsection": "6.2 Leadership Support"},
    ],

    # -------- sm.* (SageMaker) --------
    "sm.endpoint_slo_scaling_band": [
        {"dimension": "09. Foundation Model Operations", "subsection": "9.3 Performance Optimization"},
        {"dimension": "13. AI Risk & Resilience",        "subsection": "13.4 Operational Continuity"},
    ],
    "sm.pipeline_flow_band": [
        {"dimension": "08. Process Maturity",            "subsection": "8.3 Quality Assurance"},
        {"dimension": "03. AI/ML Capabilities",          "subsection": "3.3 MLOps Maturity"},
    ],
    "sm.experiments_lineage_band": [
        {"dimension": "05. Governance & Ethics",         "subsection": "5.4 Transparency Practices"},
        {"dimension": "02. Data Management & Quality",   "subsection": "2.3 Data Governance"},
    ],
    "sm.clarify_coverage_band": [
        {"dimension": "01. Technical Infrastructure",    "subsection": "1.1 Algorithmic Fairness & Bias Mitigation"},
        {"dimension": "05. Governance & Ethics",         "subsection": "5.3 Risk Management"},
    ],
    "sm.cost_efficiency_band": [
        {"dimension": "12. AI Business Value & ROI",     "subsection": "12.2 Cost Reduction & Efficiency"},
        {"dimension": "13. AI Risk & Resilience",        "subsection": "13.2 Data Dependability & Trust"},
    ],

    # -------- cicd.* --------
    "cicd.deploy_frequency_band": [
        {"dimension": "08. Process Maturity",            "subsection": "8.1 Project Management"},
        {"dimension": "03. AI/ML Capabilities",          "subsection": "3.2 Production Deployment"},
    ],
    "cicd.lead_time_band": [
        {"dimension": "08. Process Maturity",            "subsection": "8.4 Operational Excellence"},
        {"dimension": "06. Strategic Alignment",         "subsection": "6.5 Innovation Management"},
    ],
    "cicd.change_failure_rate_band": [
        {"dimension": "13. AI Risk & Resilience",        "subsection": "13.1 Model Reliability & Robustness"},
        {"dimension": "08. Process Maturity",            "subsection": "8.3 Quality Assurance"},
    ],
    "cicd.policy_gates_band": [
        {"dimension": "05. Governance & Ethics",         "subsection": "5.2 Regulatory Compliance"},
        {"dimension": "03. AI/ML Capabilities",          "subsection": "3.4 Model Governance"},
    ],
}