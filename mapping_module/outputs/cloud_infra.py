from __future__ import annotations
from typing import Dict, List

CLOUD_INFRA_METRIC_TO_AIMRI: Dict[str, List[dict]] = {
    "tagging.coverage": [
        {"dimension": "5.4 — Governance & Ethics", "subsection": "Accountability Structure"},
        {"dimension": "2.3 — Data Management & Quality", "subsection": "Data Governance"},
        {"dimension": "1.1 — Technical Infrastructure", "subsection": "Cloud Computing Capabilities"},
        {"dimension": "12.2 — AI Business Value & ROI", "subsection": "Cost Reduction & Efficiency"},
        {"dimension": "8.5 — Process Maturity", "subsection": "Measurement & Metrics"}
    ],
    "compute.utilization": [
        {"dimension": "1.2", "subsection": "Technical Infrastructure / Computing Resources"},
        {"dimension": "1.1", "subsection": "Technical Infrastructure / Cloud Computing Capabilities"},
        {"dimension": "8.5", "subsection": "Process Maturity / Measurement & Metrics"},
        {"dimension": "12.2", "subsection": "AI Business Value & ROI / Cost Reduction & Efficiency"},
        {"dimension": "6.4", "subsection": "Strategic Alignment / Innovation Management"}
    ],
    "k8s.utilization": [
        {"dimension": "1.2", "subsection": "Technical Infrastructure / Computing Resources"},
        {"dimension": "1.1", "subsection": "Technical Infrastructure / Cloud Computing Capabilities"},
        {"dimension": "8.5", "subsection": "Process Maturity / Measurement & Metrics"},
        {"dimension": "12.2", "subsection": "AI Business Value & ROI / Cost Reduction & Efficiency"},
        {"dimension": "6.4", "subsection": "Strategic Alignment / Innovation Management"}
    ],
    "scaling.effectiveness": [
        {"dimension": "1.1", "subsection": "Technical Infrastructure / Cloud Computing Capabilities"},
        {"dimension": "1.2", "subsection": "Technical Infrastructure / Computing Resources"},
        {"dimension": "8.4", "subsection": "Process Maturity / Operational Excellence"},
        {"dimension": "12.2", "subsection": "AI Business Value & ROI / Cost Reduction & Efficiency"},
        {"dimension": "13.4", "subsection": "AI Risk & Resilience / Operational Continuity"}
    ],
    "db.utilization": [
        {"dimension": "1.2", "subsection": "1.2 Technical Infrastructure / Computing Resources"},
        {"dimension": "2.4", "subsection": "2.4 Data Management & Quality / Data Operations"},
        {"dimension": "8.5", "subsection": "8.5 Process Maturity / Measurement & Metrics"}
    ],
    "lb.performance": [
        {"dimension": "1.1", "subsection": "Technical Infrastructure / Cloud Computing Capabilities"},
        {"dimension": "1.2", "subsection": "Technical Infrastructure / Computing Resources"},
        {"dimension": "8.5", "subsection": "Process Maturity / Measurement & Metrics"},
        {"dimension": "12.3", "subsection": "AI Business Value & ROI / Customer Experience Enhancement"},
        {"dimension": "13.4", "subsection": "AI Risk & Resilience / Operational Continuity"}
    ],
    "storage.efficiency": [
        {"dimension": "12.2", "subsection": "AI Business Value & ROI / Cost Reduction & Efficiency"},
        {"dimension": "1.1", "subsection": "Technical Infrastructure / Cloud Computing Capabilities"},
        {"dimension": "2.4", "subsection": "Data Management & Quality / Data Operations"},
        {"dimension": "8.4", "subsection": "Process Maturity / Operational Excellence"},
        {"dimension": "6.4", "subsection": "Strategic Alignment / Innovation Management"}
    ],
    "iac.coverage_drift": [
        {"dimension": "1.1", "subsection": "Technical Infrastructure / Cloud Computing Capabilities"},
        {"dimension": "1.2", "subsection": "Technical Infrastructure / Computing Resources"},
        {"dimension": "5.3", "subsection": "Governance & Ethics / Risk Management"},
        {"dimension": "8.4", "subsection": "Process Maturity / Operational Excellence"},
        {"dimension": "2.3", "subsection": "Data Management & Quality / Data Governance"}
    ],
    "availability.incidents": [
        {"dimension": "13. AI Risk & Resilience", "subsection": "13.4 Operational Continuity"},
        {"dimension": "1. Technical Infrastructure", "subsection": "1.1 Cloud Computing Capabilities"},
        {"dimension": "8. Process Maturity", "subsection": "8.4 Operational Excellence"},
        {"dimension": "5. Governance & Ethics", "subsection": "5.3 Risk Management"},
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.2 Cost Reduction & Efficiency"}
    ],
    "cost.idle_underutilized": [
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.2 Cost Reduction & Efficiency"},
        {"dimension": "1. Technical Infrastructure", "subsection": "1.2 Computing Resources"},
        {"dimension": "8. Process Maturity", "subsection": "8.5 Measurement & Metrics"},
        {"dimension": "6. Strategic Alignment", "subsection": "6.3 Investment Strategy"},
        {"dimension": "4. Talent & Skills", "subsection": "4.1 Technical Expertise"}
    ],
    "cost.commit_coverage": [
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.2 Cost Reduction & Efficiency"},
        {"dimension": "1. Technical Infrastructure", "subsection": "1.2 Computing Resources"},
        {"dimension": "8. Process Maturity", "subsection": "8.5 Measurement & Metrics"}
    ],
    "cost.allocation_quality": [
        {"dimension": "12.2", "subsection": "AI Business Value & ROI / Cost Reduction & Efficiency"},
        {"dimension": "5.4", "subsection": "Governance & Ethics / Accountability Structure"},
        {"dimension": "6.1", "subsection": "Strategic Alignment / Business Integration"},
        {"dimension": "8.5", "subsection": "Process Maturity / Measurement & Metrics"},
        {"dimension": "2.2", "subsection": "Data Management & Quality / Data Quality"}
    ],
    "security.public_exposure": [
        {"dimension": "1.5 - Technical Infrastructure", "subsection": "Security Infrastructure"},
        {"dimension": "5.3 - Governance & Ethics", "subsection": "Risk Management"},
        {"dimension": "5.2 - Governance & Ethics", "subsection": "Regulatory Compliance"},
        {"dimension": "2.5 - Data Management & Quality", "subsection": "Data Accessibility"},
        {"dimension": "8.4 - Process Maturity", "subsection": "Operational Excellence"}
    ],
    "security.encryption": [
        {"dimension": "1.5. Security Infrastructure", "subsection": "1.5 Title"},
        {"dimension": "5.3. Risk Management", "subsection": "5.3 Title"},
        {"dimension": "11.3. Privacy & Data Protection", "subsection": "11.3 Title"},
        {"dimension": "2.1. Data Architecture", "subsection": "2.1 Title"},
        {"dimension": "2.4. Data Operations", "subsection": "2.4 Title"}
    ],
    "security.iam_risk": [
        {"dimension": "1.5 — Technical Infrastructure / Security Infrastructure", "subsection": "1.5 Title"},
        {"dimension": "5.3 — Governance & Ethics / Risk Management", "subsection": "5.3 Title"},
        {"dimension": "5.2 — Governance & Ethics / Regulatory Compliance", "subsection": "5.2 Title"},
        {"dimension": "13.4 — AI Risk & Resilience / Operational Continuity", "subsection": "13.4 Title"},
        {"dimension": "5.4 — Governance & Ethics / Accountability Structure", "subsection": "5.4 Title"}
    ],
    "security.vuln_patch": [
        {"dimension": "1.5 — Technical Infrastructure / Security Infrastructure", "subsection": "1.5 Title"},
        {"dimension": "5.3 — Governance & Ethics / Risk Management", "subsection": "5.3 Title"},
        {"dimension": "8.4 — Process Maturity / Operational Excellence", "subsection": "8.4 Title"},
        {"dimension": "8.5 — Process Maturity / Measurement & Metrics", "subsection": "8.5 Title"},
        {"dimension": "2.4 — Data Management & Quality / Data Operations", "subsection": "2.4 Title"}
    ]
}
