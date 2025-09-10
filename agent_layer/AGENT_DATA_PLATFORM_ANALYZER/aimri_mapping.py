from typing import Dict, List

MLOPS_METRIC_TO_AIMRI: Dict[str, List[Dict[str, str]]] = {
    "check_schema_consistency": [
        {"dimension": "02. Data Management & Quality", "subsection": "2.1 Data Architecture"},
        {"dimension": "02. Data Management & Quality", "subsection": "2.2 Data Quality"},
    ],
    "evaluate_data_freshness": [
        {"dimension": "02. Data Management & Quality", "subsection": "2.1 Data Architecture"},
        {"dimension": "02. Data Management & Quality", "subsection": "2.4 Data Operations"},
    ],
    "evaluate_data_quality": [
        {"dimension": "02. Data Management & Quality", "subsection": "2.2 Data Quality"},
    ],
    "evaluate_governance_compliance": [
        {"dimension": "02. Data Management & Quality", "subsection": "2.3 Data Governance"},
        {"dimension": "03. AI/ML Capabilities",        "subsection": "3.4 Model Governance"},
        {"dimension": "05. Governance & Ethics",      "subsection": "5.1 Ethical Framework"},
        {"dimension": "05. Governance & Ethics",      "subsection": "5.2 Regulatory Compliance"},
        {"dimension": "05. Governance & Ethics",      "subsection": "5.3 Risk Management"},
        {"dimension": "13. AI Risk & Resilience",     "subsection": "13.5 Regulatory & Legal Compliance"},
    ],
    "evaluate_data_lineage": [
        {"dimension": "02. Data Management & Quality", "subsection": "2.1 Data Architecture"},
    ],
    "evaluate_metadata_coverage": [
        {"dimension": "02. Data Management & Quality", "subsection": "2.5 Data Accessibility"},
    ],
    "evaluate_sensitive_tagging": [
        {"dimension": "02. Data Management & Quality", "subsection": "2.3 Data Governance"},
        {"dimension": "13. AI Risk & Resilience",      "subsection": "13.5 Regulatory & Legal Compliance"},
        {"dimension": "09. Foundation Model Operations","subsection": "9.4 Risk & Compliance Management"},
        {"dimension": "11. Responsible AI & Social Impact", "subsection": "11.3 Privacy & Data Protection"},
    ],
    "evaluate_duplication": [
        {"dimension": "02. Data Management & Quality", "subsection": "2.2 Data Quality"},
        {"dimension": "02. Data Management & Quality", "subsection": "2.5 Data Accessibility"},
    ],
    "evaluate_backup_recovery": [
        {"dimension": "01. Technical Infrastructure", "subsection": "1.5 Security Infrastructure"},
        {"dimension": "05. Governance & Ethics",      "subsection": "5.3 Risk Management"},
    ],
    "evaluate_security_config": [
        {"dimension": "01. Technical Infrastructure", "subsection": "1.5 Security Infrastructure"},
        {"dimension": "05. Governance & Ethics",      "subsection": "5.3 Risk Management"},
    ],
    "compute_pipeline_success_rate": [
        {"dimension": "02. Data Management & Quality", "subsection": "2.4 Data Operations"},
        {"dimension": "11. Responsible AI & Social Impact", "subsection": "11.5 Human-AI Collaboration"},
        {"dimension": "03. AI/ML Capabilities",        "subsection": "3.1 Model Development"},
        {"dimension": "03. AI/ML Capabilities",        "subsection": "3.3 MLOps Maturity"},
    ],
    "compute_pipeline_latency_throughput": [
        {"dimension": "02. Data Management & Quality", "subsection": "2.4 Data Operations"},
        {"dimension": "03. AI/ML Capabilities",        "subsection": "3.2 Production Deployment"},
        {"dimension": "03. AI/ML Capabilities",        "subsection": "3.3 MLOps Maturity"},
    ],
    "evaluate_resource_utilization": [
        {"dimension": "01. Technical Infrastructure", "subsection": "1.1 Cloud Computing Capabilities"},
        {"dimension": "01. Technical Infrastructure", "subsection": "1.2 Computing Resources"},
        {"dimension": "01. Technical Infrastructure", "subsection": "1.4 Integration Architecture"},
    ],
    "assess_query_performance": [
        {"dimension": "02. Data Management & Quality", "subsection": "2.5 Data Accessibility"},
        {"dimension": "02. Data Management & Quality", "subsection": "2.4 Data Operations"},
    ],
    "compute_analytics_adoption": [
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.1 Revenue Generation & Growth"},
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.2 Cost Reduction & Efficiency"},
    ],
}
