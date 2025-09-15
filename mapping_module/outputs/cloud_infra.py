from __future__ import annotations
from typing import Dict, List

CLOUD_INFRA_METRIC_TO_AIMRI: Dict[str, List[dict]] = {
    "tagging.coverage": [
        {"dimension": "02. Data Management & Quality", "subsection": "2.3 Data Governance"},
        {"dimension": "05. Governance & Ethics", "subsection": "5.4 Accountability Structure"},
        {"dimension": "08. Process Maturity", "subsection": "8.4 Operational Excellence"},
        {"dimension": "01. Technical Infrastructure", "subsection": "1.1 Cloud Computing Capabilities"},
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.2 Cost Reduction & Efficiency"}
    ],
    "compute.utilization": [
        {"dimension": "01. Technical Infrastructure", "subsection": "1.2 Computing Resources"},
        {"dimension": "08. Process Maturity", "subsection": "8.5 Measurement & Metrics"},
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.2 Cost Reduction & Efficiency"},
        {"dimension": "06. Strategic Alignment", "subsection": "6.3 Investment Strategy"}
    ],
    "k8s.utilization": [
        {"dimension": "01. Technical Infrastructure", "subsection": "1.2 Computing Resources"},
        {"dimension": "08. Process Maturity", "subsection": "8.4 Operational Excellence"},
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.2 Cost Reduction & Efficiency"},
        {"dimension": "06. Strategic Alignment", "subsection": "6.4 Innovation Management"}
    ],
    "scaling.effectiveness": [
        {"dimension": "01. Technical Infrastructure", "subsection": "1.2 Computing Resources"},
        {"dimension": "08. Process Maturity", "subsection": "8.4 Operational Excellence"},
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.2 Cost Reduction & Efficiency"},
        {"dimension": "13. AI Risk & Resilience", "subsection": "13.4 Operational Continuity"}
    ],
    "db.utilization": [
        {"dimension": "01. Technical Infrastructure", "subsection": "1.2 Computing Resources"},
        {"dimension": "02. Data Management & Quality", "subsection": "2.4 Data Operations"},
        {"dimension": "08. Process Maturity", "subsection": "8.5 Measurement & Metrics"},
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.2 Cost Reduction & Efficiency"},
        {"dimension": "13. AI Risk & Resilience", "subsection": "13.4 Operational Continuity"}
    ],
    "lb.performance": [
        {"dimension": "01. Technical Infrastructure", "subsection": "1.4 Integration Architecture"},
        {"dimension": "08. Process Maturity", "subsection": "8.3 Quality Assurance"},
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.3 Customer Experience Enhancement"},
        {"dimension": "13. AI Risk & Resilience", "subsection": "13.4 Operational Continuity"},
        {"dimension": "05. Governance & Ethics", "subsection": "5.3 Risk Management"}
    ],
    "storage.efficiency": [
        {"dimension": "02. Data Management & Quality", "subsection": "2.4 Data Operations"},
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.2 Cost Reduction & Efficiency"},
        {"dimension": "01. Technical Infrastructure", "subsection": "1.1 Cloud Computing Capabilities"},
        {"dimension": "08. Process Maturity", "subsection": "8.4 Operational Excellence"},
        {"dimension": "06. Strategic Alignment", "subsection": "6.3 Investment Strategy"}
    ],
    "iac.coverage_drift": [
        {"dimension": "01. Technical Infrastructure", "subsection": "1.5 Security Infrastructure"},
        {"dimension": "08. Process Maturity", "subsection": "8.4 Operational Excellence"},
        {"dimension": "05. Governance & Ethics", "subsection": "5.2 Regulatory Compliance"},
        {"dimension": "04. Talent & Skills", "subsection": "4.1 Technical Expertise"},
        {"dimension": "06. Strategic Alignment", "subsection": "6.1 Business Integration"}
    ],
    "availability.incidents": [
        {"dimension": "01. Technical Infrastructure", "subsection": "1.1 Cloud Computing Capabilities"},
        {"dimension": "08. Process Maturity", "subsection": "8.4 Operational Excellence"},
        {"dimension": "13. AI Risk & Resilience", "subsection": "13.4 Operational Continuity"},
        {"dimension": "05. Governance & Ethics", "subsection": "5.3 Risk Management"},
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.3 Customer Experience Enhancement"}
    ],
    "cost.idle_underutilized": [
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.2 Cost Reduction & Efficiency"},
        {"dimension": "01. Technical Infrastructure", "subsection": "1.2 Computing Resources"},
        {"dimension": "08. Process Maturity", "subsection": "8.5 Measurement & Metrics"},
        {"dimension": "06. Strategic Alignment", "subsection": "6.3 Investment Strategy"},
        {"dimension": "04. Talent & Skills", "subsection": "4.1 Technical Expertise"}
    ],
    "cost.commit_coverage": [
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.2 Cost Reduction & Efficiency"},
        {"dimension": "6. Strategic Alignment", "subsection": "6.3 Investment Strategy"},
        {"dimension": "8. Process Maturity", "subsection": "8.5 Measurement & Metrics"},
        {"dimension": "1.1 Technical Infrastructure", "subsection": "1.1 Cloud Computing Capabilities"}
    ],
    "cost.allocation_quality": [
        {"dimension": "05. Governance & Ethics", "subsection": "5.4 Accountability Structure"},
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.2 Cost Reduction & Efficiency"},
        {"dimension": "08. Process Maturity", "subsection": "8.5 Measurement & Metrics"},
        {"dimension": "06. Strategic Alignment", "subsection": "6.3 Investment Strategy"},
        {"dimension": "02. Data Management & Quality", "subsection": "2.2 Data Quality"}
    ],
    "security.public_exposure": [
        {"dimension": "01. Technical Infrastructure", "subsection": "1.5 Security Infrastructure"},
        {"dimension": "05. Governance & Ethics", "subsection": "5.3 Risk Management"},
        {"dimension": "13. AI Risk & Resilience", "subsection": "13.5 Regulatory & Legal Compliance"},
        {"dimension": "02. Data Management & Quality", "subsection": "2.3 Data Governance"},
        {"dimension": "08. Process Maturity", "subsection": "8.3 Quality Assurance"}
    ],
    "security.encryption": [
        {"dimension": "01. Technical Infrastructure", "subsection": "1.5 Security Infrastructure"},
        {"dimension": "05. Governance & Ethics", "subsection": "5.2 Regulatory Compliance"},
        {"dimension": "11. Responsible AI & Social Impact", "subsection": "11.3 Privacy & Data Protection"},
        {"dimension": "13. AI Risk & Resilience", "subsection": "13.5 Regulatory & Legal Compliance"},
        {"dimension": "02. Data Management & Quality", "subsection": "2.3 Data Governance"}
    ],
    "security.iam_risk": [
        {"dimension": "01. Technical Infrastructure", "subsection": "1.5 Security Infrastructure"},
        {"dimension": "05. Governance & Ethics", "subsection": "5.3 Risk Management"},
        {"dimension": "05. Governance & Ethics", "subsection": "5.2 Regulatory Compliance"},
        {"dimension": "13. AI Risk & Resilience", "subsection": "13.5 Regulatory & Legal Compliance"},
        {"dimension": "08. Process Maturity", "subsection": "8.3 Quality Assurance"}
    ],
    "security.vuln_patch": [
        {"dimension": "01. Technical Infrastructure", "subsection": "1.5 Security Infrastructure"},
        {"dimension": "05. Governance & Ethics", "subsection": "5.3 Risk Management"},
        {"dimension": "08. Process Maturity", "subsection": "8.3 Quality Assurance"},
        {"dimension": "13. AI Risk & Resilience", "subsection": "13.5 Regulatory & Legal Compliance"},
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.2 Cost Reduction & Efficiency"}
    ]
}
