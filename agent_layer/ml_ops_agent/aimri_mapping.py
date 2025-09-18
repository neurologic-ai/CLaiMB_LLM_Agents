from __future__ import annotations
from typing import Dict, List

MLOPS_METRIC_TO_AIMRI: Dict[str, List[dict]] = {
    "mlflow.experiment_completeness_band": [
        {"dimension": "08. Process Maturity", "subsection": "8.2 Documentation Practices"},
        {"dimension": "02. Data Management & Quality", "subsection": "2.2 Data Quality"},
        {"dimension": "03. AI/ML Capabilities", "subsection": "3.3 MLOps Maturity"},
        {"dimension": "04. Talent & Skills", "subsection": "4.1 Technical Expertise"},
        {"dimension": "05. Governance & Ethics", "subsection": "5.5 Transparency Practices"}
    ],
    "mlflow.lineage_coverage_band": [
        {"dimension": "08. Process Maturity", "subsection": "8.2 Documentation Practices"},
        {"dimension": "03. AI/ML Capabilities", "subsection": "3.3 MLOps Maturity"},
        {"dimension": "05. Governance & Ethics", "subsection": "5.4 Accountability Structure"},
        {"dimension": "02. Data Management & Quality", "subsection": "2.3 Data Governance"},
        {"dimension": "03. AI/ML Capabilities", "subsection": "3.4 Model Governance"}
    ],
    "mlflow.experiment_velocity_band": [
        {"dimension": "08. Process Maturity", "subsection": "8.4 Operational Excellence"},
        {"dimension": "03. AI/ML Capabilities", "subsection": "3.3 MLOps Maturity"},
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.2 Cost Reduction & Efficiency"},
        {"dimension": "06. Strategic Alignment", "subsection": "6.4 Innovation Management"},
        {"dimension": "04. Talent & Skills", "subsection": "4.4 Training & Development"}
    ],
    "mlflow.registry_hygiene_band": [
        {"dimension": "03. AI/ML Capabilities", "subsection": "3.4 Model Governance"},
        {"dimension": "08. Process Maturity", "subsection": "8.2 Documentation Practices"},
        {"dimension": "02. Data Management & Quality", "subsection": "2.3 Data Governance"},
        {"dimension": "03. AI/ML Capabilities", "subsection": "3.3 MLOps Maturity"}
    ],
    "mlflow.validation_artifacts_band": [
        {"dimension": "05. Governance & Ethics", "subsection": "5.1 Ethical Framework"},
        {"dimension": "03. AI/ML Capabilities", "subsection": "3.4 Model Governance"},
        {"dimension": "08. Process Maturity", "subsection": "8.3 Quality Assurance"},
        {"dimension": "11. Responsible AI & Social Impact", "subsection": "11.1 Algorithmic Fairness & Bias Mitigation"},
        {"dimension": "02. Data Management & Quality", "subsection": "2.2 Data Quality"}
    ],
    "mlflow.reproducibility_band": [
        {"dimension": "03. AI/ML Capabilities", "subsection": "3.3 MLOps Maturity"},
        {"dimension": "08. Process Maturity", "subsection": "8.3 Quality Assurance"},
        {"dimension": "02. Data Management & Quality", "subsection": "2.2 Data Quality"},
        {"dimension": "03. AI/ML Capabilities", "subsection": "3.1 Model Development"},
        {"dimension": "08. Process Maturity", "subsection": "8.5 Measurement & Metrics"}
    ],
    "aml.endpoint_slo_band": [
        {"dimension": "03. AI/ML Capabilities", "subsection": "3.2 Production Deployment"},
        {"dimension": "08. Process Maturity", "subsection": "8.3 Quality Assurance"},
        {"dimension": "13. AI Risk & Resilience", "subsection": "13.1 Model Reliability & Robustness"},
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.3 Customer Experience Enhancement"},
        {"dimension": "09. Foundation Model Operations", "subsection": "9.3 Performance Optimization"}
    ],
    "aml.jobs_flow_band": [
        {"dimension": "08. Process Maturity", "subsection": "8.4 Operational Excellence"},
        {"dimension": "03. AI/ML Capabilities", "subsection": "3.3 MLOps Maturity"},
        {"dimension": "01. Technical Infrastructure", "subsection": "1.4 Integration Architecture"},
        {"dimension": "13. AI Risk & Resilience", "subsection": "13.4 Operational Continuity"},
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.2 Cost Reduction & Efficiency"}
    ],
    "aml.monitoring_coverage_band": [
        {"dimension": "03. AI/ML Capabilities", "subsection": "3.4 Model Governance"},
        {"dimension": "08. Process Maturity", "subsection": "8.5 Measurement & Metrics"},
        {"dimension": "13. AI Risk & Resilience", "subsection": "13.1 Model Reliability & Robustness"},
        {"dimension": "05. Governance & Ethics", "subsection": "5.4 Accountability Structure"},
        {"dimension": "02. Data Management & Quality", "subsection": "2.3 Data Governance"}
    ],
    "aml.registry_governance_band": [
        {"dimension": "05. Governance & Ethics", "subsection": "5.2 Regulatory Compliance"},
        {"dimension": "05. Governance & Ethics", "subsection": "5.4 Accountability Structure"},
        {"dimension": "05. Governance & Ethics", "subsection": "5.5 Transparency Practices"},
        {"dimension": "03. AI/ML Capabilities", "subsection": "3.4 Model Governance"},
        {"dimension": "02. Data Management & Quality", "subsection": "2.3 Data Governance"}
    ],
    "aml.cost_correlation_band": [
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.2 Cost Reduction & Efficiency"},
        {"dimension": "01. Technical Infrastructure", "subsection": "1.2 Computing Resources"},
        {"dimension": "03. AI/ML Capabilities", "subsection": "3.3 MLOps Maturity"},
        {"dimension": "08. Process Maturity", "subsection": "8.5 Measurement & Metrics"}
    ],
    "sm.endpoint_slo_scaling_band": [
        {"dimension": "01. Technical Infrastructure", "subsection": "1.2 Computing Resources"},
        {"dimension": "03. AI/ML Capabilities", "subsection": "3.2 Production Deployment"},
        {"dimension": "08. Process Maturity", "subsection": "8.4 Operational Excellence"},
        {"dimension": "13. AI Risk & Resilience", "subsection": "13.1 Model Reliability & Robustness"},
        {"dimension": "09. Foundation Model Operations", "subsection": "9.5 Scaling & Distribution"}
    ],
    "sm.pipeline_flow_band": [
        {"dimension": "08. Process Maturity", "subsection": "8.4 Operational Excellence"},
        {"dimension": "03. AI/ML Capabilities", "subsection": "3.3 MLOps Maturity"},
        {"dimension": "01. Technical Infrastructure", "subsection": "1.4 Integration Architecture"},
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.2 Cost Reduction & Efficiency"},
        {"dimension": "13. AI Risk & Resilience", "subsection": "13.1 Model Reliability & Robustness"}
    ],
    "sm.experiments_lineage_band": [
        {"dimension": "02. Data Management & Quality", "subsection": "2.3 Data Governance"},
        {"dimension": "03. AI/ML Capabilities", "subsection": "3.3 MLOps Maturity"},
        {"dimension": "08. Process Maturity", "subsection": "8.2 Documentation Practices"},
        {"dimension": "05. Governance & Ethics", "subsection": "5.5 Transparency Practices"},
        {"dimension": "04. Talent & Skills", "subsection": "4.1 Technical Expertise"}
    ],
    "sm.clarify_coverage_band": [
        {"dimension": "11. Responsible AI & Social Impact", "subsection": "11.1 Algorithmic Fairness & Bias Mitigation"},
        {"dimension": "11. Responsible AI & Social Impact", "subsection": "11.2 Explainability & Interpretability"},
        {"dimension": "05. Governance & Ethics", "subsection": "5.1 Ethical Framework"},
        {"dimension": "05. Governance & Ethics", "subsection": "5.2 Regulatory Compliance"},
        {"dimension": "03. AI/ML Capabilities", "subsection": "3.4 Model Governance"}
    ],
    "sm.cost_efficiency_band": [
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.2 Cost Reduction & Efficiency"},
        {"dimension": "01. Technical Infrastructure", "subsection": "1.2 Computing Resources"},
        {"dimension": "03. AI/ML Capabilities", "subsection": "3.3 MLOps Maturity"},
        {"dimension": "08. Process Maturity", "subsection": "8.4 Operational Excellence"},
        {"dimension": "06. Strategic Alignment", "subsection": "6.3 Investment Strategy"}
    ],
    "cicd.deploy_frequency_band": [
        {"dimension": "03. AI/ML Capabilities", "subsection": "3.2 Production Deployment"},
        {"dimension": "03. AI/ML Capabilities", "subsection": "3.3 MLOps Maturity"},
        {"dimension": "08. Process Maturity", "subsection": "8.4 Operational Excellence"},
        {"dimension": "09. Foundation Model Operations", "subsection": "9.1 Model Integration & Deployment"},
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.2 Cost Reduction & Efficiency"}
    ],
    "cicd.lead_time_band": [
        {"dimension": "03. AI/ML Capabilities", "subsection": "3.2 Production Deployment"},
        {"dimension": "08. Process Maturity", "subsection": "8.4 Operational Excellence"},
        {"dimension": "03. AI/ML Capabilities", "subsection": "3.3 MLOps Maturity"},
        {"dimension": "08. Process Maturity", "subsection": "8.5 Measurement & Metrics"},
        {"dimension": "01. Technical Infrastructure", "subsection": "1.4 Integration Architecture"}
    ],
    "cicd.change_failure_rate_band": [
        {"dimension": "03. AI/ML Capabilities", "subsection": "3.2 Production Deployment"},
        {"dimension": "08. Process Maturity", "subsection": "8.3 Quality Assurance"},
        {"dimension": "08. Process Maturity", "subsection": "8.4 Operational Excellence"},
        {"dimension": "13. AI Risk & Resilience", "subsection": "13.1 Model Reliability & Robustness"},
        {"dimension": "03. AI/ML Capabilities", "subsection": "3.3 MLOps Maturity"}
    ],
    "cicd.policy_gates_band": [
        {"dimension": "08. Process Maturity", "subsection": "8.3 Quality Assurance"},
        {"dimension": "05. Governance & Ethics", "subsection": "5.2 Regulatory Compliance"},
        {"dimension": "03. AI/ML Capabilities", "subsection": "3.3 MLOps Maturity"},
        {"dimension": "01. Technical Infrastructure", "subsection": "1.4 Integration Architecture"},
        {"dimension": "08. Process Maturity", "subsection": "8.4 Operational Excellence"}
    ]
}