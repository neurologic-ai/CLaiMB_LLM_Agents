from __future__ import annotations
from typing import Dict, List

CLOUD_INFRA_METRIC_TO_AIMRI: Dict[str, List[dict]] = {
    "tagging.coverage": [
        {"dimension": "05. Governance & Ethics", "subsection": "5.4 Accountability Structure"},
        {"dimension": "02. Data Management & Quality", "subsection": "2.3 Data Governance"},
        {"dimension": "08. Process Maturity", "subsection": "8.4 Operational Excellence"},
        {"dimension": "01. Technical Infrastructure", "subsection": "1.1 Cloud Computing Capabilities"},
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.2 Cost Reduction & Efficiency"}
    ],
    "compute.utilization": [
        {"dimension": "01. Technical Infrastructure", "subsection": "1.2 Computing Resources"},
        {"dimension": "08. Process Maturity", "subsection": "8.5 Measurement & Metrics"},
        {"dimension": "06. Strategic Alignment", "subsection": "6.3 Investment Strategy"},
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.2 Cost Reduction & Efficiency"}
    ],
    "k8s.utilization": [
        {"dimension": "01. Technical Infrastructure", "subsection": "1.2 Computing Resources"},
        {"dimension": "08. Process Maturity", "subsection": "8.5 Measurement & Metrics"},
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.2 Cost Reduction & Efficiency"},
        {"dimension": "04. Talent & Skills", "subsection": "4.1 Technical Expertise"}
    ],
    "scaling.effectiveness": [
        {"dimension": "01. Technical Infrastructure", "subsection": "1.2 Computing Resources"},
        {"dimension": "08. Process Maturity", "subsection": "8.5 Measurement & Metrics"},
        {"dimension": "09. Foundation Model Operations", "subsection": "9.5 Scaling & Distribution"},
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.2 Cost Reduction & Efficiency"},
        {"dimension": "13. AI Risk & Resilience", "subsection": "13.4 Operational Continuity"}
    ],
    "db.utilization": [
        {"dimension": "01. Technical Infrastructure", "subsection": "1.2 Computing Resources"},
        {"dimension": "02. Data Management & Quality", "subsection": "2.4 Data Operations"},
        {"dimension": "08. Process Maturity", "subsection": "8.5 Measurement & Metrics"},
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.2 Cost Reduction & Efficiency"}
    ],
    "lb.performance": [
        {"dimension": "01. Technical Infrastructure", "subsection": "1.1 Cloud Computing Capabilities"},
        {"dimension": "08. Process Maturity", "subsection": "8.5 Measurement & Metrics"},
        {"dimension": "04. Talent & Skills", "subsection": "4.1 Technical Expertise"},
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.3 Customer Experience Enhancement"},
        {"dimension": "13. AI Risk & Resilience", "subsection": "13.4 Operational Continuity"}
    ],
    "storage.efficiency": [
        {"dimension": "02. Data Management & Quality", "subsection": "2.4 Data Operations"},
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.2 Cost Reduction & Efficiency"},
        {"dimension": "01. Technical Infrastructure", "subsection": "1.1 Cloud Computing Capabilities"},
        {"dimension": "08. Process Maturity", "subsection": "8.4 Operational Excellence"},
        {"dimension": "05. Governance & Ethics", "subsection": "5.3 Risk Management"}
    ],
    "iac.coverage_drift": [
        {"dimension": "01. Technical Infrastructure", "subsection": "1.1 Cloud Computing Capabilities"},
        {"dimension": "05. Governance & Ethics", "subsection": "5.2 Regulatory Compliance"},
        {"dimension": "08. Process Maturity", "subsection": "8.4 Operational Excellence"},
        {"dimension": "05. Governance & Ethics", "subsection": "5.3 Risk Management"}
    ],
    "availability.incidents": [
        {"dimension": "13. AI Risk & Resilience", "subsection": "13.4 Operational Continuity"},
        {"dimension": "08. Process Maturity", "subsection": "8.4 Operational Excellence"},
        {"dimension": "01. Technical Infrastructure", "subsection": "1.1 Cloud Computing Capabilities"},
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.3 Customer Experience Enhancement"},
        {"dimension": "05. Governance & Ethics", "subsection": "5.3 Risk Management"}
    ],
    "cost.idle_underutilized": [
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.2 Cost Reduction & Efficiency"},
        {"dimension": "01. Technical Infrastructure", "subsection": "1.2 Computing Resources"},
        {"dimension": "08. Process Maturity", "subsection": "8.4 Operational Excellence"},
        {"dimension": "06. Strategic Alignment", "subsection": "6.3 Investment Strategy"},
        {"dimension": "04. Talent & Skills", "subsection": "4.1 Technical Expertise"}
    ],
    "cost.commit_coverage": [
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.2 Cost Reduction & Efficiency"},
        {"dimension": "6. Strategic Alignment", "subsection": "6.3 Investment Strategy"},
        {"dimension": "8. Process Maturity", "subsection": "8.5 Measurement & Metrics"},
        {"dimension": "1.1", "subsection": "01. Technical Infrastructure"}
    ],
    "cost.allocation_quality": [
        {"dimension": "02. Data Management & Quality", "subsection": "2.3 Data Governance"},
        {"dimension": "05. Governance & Ethics", "subsection": "5.4 Accountability Structure"},
        {"dimension": "08. Process Maturity", "subsection": "8.5 Measurement & Metrics"},
        {"dimension": "06. Strategic Alignment", "subsection": "6.3 Investment Strategy"},
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.2 Cost Reduction & Efficiency"}
    ],
    "security.public_exposure": [
        {"dimension": "01. Technical Infrastructure", "subsection": "1.5 Security Infrastructure"},
        {"dimension": "05. Governance & Ethics", "subsection": "5.3 Risk Management"},
        {"dimension": "05. Governance & Ethics", "subsection": "5.2 Regulatory Compliance"},
        {"dimension": "02. Data Management & Quality", "subsection": "2.3 Data Governance"}
    ],
    "security.encryption": [
        {"dimension": "01. Technical Infrastructure", "subsection": "1.5 Security Infrastructure"},
        {"dimension": "05. Governance & Ethics", "subsection": "5.2 Regulatory Compliance"},
        {"dimension": "11. Responsible AI & Social Impact", "subsection": "11.3 Privacy & Data Protection"},
        {"dimension": "02. Data Management & Quality", "subsection": "2.3 Data Governance"}
    ],
    "security.iam_risk": [
        {"dimension": "01. Technical Infrastructure", "subsection": "1.5 Security Infrastructure"},
        {"dimension": "05. Governance & Ethics", "subsection": "5.3 Risk Management"},
        {"dimension": "05. Governance & Ethics", "subsection": "5.2 Regulatory Compliance"},
        {"dimension": "04. Talent & Skills", "subsection": "4.1 Technical Expertise"}
    ],
    "security.vuln_patch": [
        {"dimension": "01. Technical Infrastructure", "subsection": "1.5 Security Infrastructure"},
        {"dimension": "05. Governance & Ethics", "subsection": "5.3 Risk Management"},
        {"dimension": "08. Process Maturity", "subsection": "8.4 Operational Excellence"},
        {"dimension": "05. Governance & Ethics", "subsection": "5.2 Regulatory Compliance"}
    ]
}
