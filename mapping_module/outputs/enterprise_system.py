from __future__ import annotations
from typing import Dict, List

ENTERPRISE_SYSTEM_METRIC_TO_AIMRI: Dict[str, List[dict]] = {
    "process.automation.coverage": [
        {"dimension": "08. Process Maturity", "subsection": "8.4 Operational Excellence"},
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.2 Cost Reduction & Efficiency"},
        {"dimension": "06. Strategic Alignment", "subsection": "6.1 Business Integration"},
        {"dimension": "04. Talent & Skills", "subsection": "4.4 Training & Development"},
        {"dimension": "07. Cultural Readiness", "subsection": "7.2 Change Management"}
    ],
    "workflow.sla_adherence": [
        {"dimension": "08. Process Maturity", "subsection": "8.4 Operational Excellence"},
        {"dimension": "08. Process Maturity", "subsection": "8.5 Measurement & Metrics"},
        {"dimension": "05. Governance & Ethics", "subsection": "5.3 Risk Management"},
        {"dimension": "06. Strategic Alignment", "subsection": "6.1 Business Integration"},
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.2 Cost Reduction & Efficiency"}
    ],
    "sales.lead_to_oppty_cycle_time": [
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.1 Revenue Generation & Growth"},
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.2 Cost Reduction & Efficiency"},
        {"dimension": "8.5 Process Maturity", "subsection": "8.5 Measurement & Metrics"},
        {"dimension": "6.1 Strategic Alignment", "subsection": "6.1 Business Integration"},
        {"dimension": "4.4 Talent & Skills", "subsection": "4.4 Training & Development"}
    ],
    "itsm.case_resolution_time": [
        {"dimension": "08. Process Maturity", "subsection": "8.4 Operational Excellence"},
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.2 Cost Reduction & Efficiency"},
        {"dimension": "06. Strategic Alignment", "subsection": "6.1 Business Integration"},
        {"dimension": "04. Talent & Skills", "subsection": "4.1 Technical Expertise"},
        {"dimension": "08. Process Maturity", "subsection": "8.5 Measurement & Metrics"}
    ],
    "itsm.incident_reopen_rate": [
        {"dimension": "08. Process Maturity", "subsection": "8.3 Quality Assurance"},
        {"dimension": "08. Process Maturity", "subsection": "8.4 Operational Excellence"},
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.3 Customer Experience Enhancement"},
        {"dimension": "06. Strategic Alignment", "subsection": "6.1 Business Integration"},
        {"dimension": "04. Talent & Skills", "subsection": "4.1 Technical Expertise"}
    ],
    "hr.onboarding_cycle_time": [
        {"dimension": "04. Talent & Skills", "subsection": "4.4 Training & Development"},
        {"dimension": "08. Process Maturity", "subsection": "8.4 Operational Excellence"},
        {"dimension": "06. Strategic Alignment", "subsection": "6.1 Business Integration"},
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.2 Cost Reduction & Efficiency"},
        {"dimension": "07. Cultural Readiness", "subsection": "7.3 Collaboration Culture"}
    ],
    "sap.procure_to_pay_cycle": [
        {"dimension": "08. Process Maturity", "subsection": "8.4 Operational Excellence"},
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.2 Cost Reduction & Efficiency"},
        {"dimension": "06. Strategic Alignment", "subsection": "6.1 Business Integration"},
        {"dimension": "05. Governance & Ethics", "subsection": "5.3 Risk Management"},
        {"dimension": "02. Data Management & Quality", "subsection": "2.4 Data Operations"}
    ],
    "q2c.throughput": [
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.1 Revenue Generation & Growth"},
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.2 Cost Reduction & Efficiency"},
        {"dimension": "8. Process Maturity", "subsection": "8.4 Operational Excellence"},
        {"dimension": "6. Strategic Alignment", "subsection": "6.1 Business Integration"},
        {"dimension": "8. Process Maturity", "subsection": "8.5 Measurement & Metrics"}
    ],
    "backlog.aging": [
        {"dimension": "08. Process Maturity", "subsection": "8.4 Operational Excellence"},
        {"dimension": "08. Process Maturity", "subsection": "8.5 Measurement & Metrics"},
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.3 Customer Experience Enhancement"},
        {"dimension": "06. Strategic Alignment", "subsection": "6.4 Innovation Management"},
        {"dimension": "04. Talent & Skills", "subsection": "4.4 Training & Development"}
    ],
    "rpa.success_rate": [
        {"dimension": "08. Process Maturity", "subsection": "8.3 Quality Assurance"},
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.2 Cost Reduction & Efficiency"},
        {"dimension": "13. AI Risk & Resilience", "subsection": "13.1 Model Reliability & Robustness"},
        {"dimension": "06. Strategic Alignment", "subsection": "6.1 Business Integration"},
        {"dimension": "08. Process Maturity", "subsection": "8.5 Measurement & Metrics"}
    ],
    "integration.data_sync_latency": [
        {"dimension": "01. Technical Infrastructure", "subsection": "1.4 Integration Architecture"},
        {"dimension": "02. Data Management & Quality", "subsection": "2.4 Data Operations"},
        {"dimension": "02. Data Management & Quality", "subsection": "2.2 Data Quality"},
        {"dimension": "08. Process Maturity", "subsection": "8.4 Operational Excellence"},
        {"dimension": "13. AI Risk & Resilience", "subsection": "13.4 Operational Continuity"}
    ],
    "api.reliability": [
        {"dimension": "01. Technical Infrastructure", "subsection": "1.4 Integration Architecture"},
        {"dimension": "08. Process Maturity", "subsection": "8.3 Quality Assurance"},
        {"dimension": "13. AI Risk & Resilience", "subsection": "13.4 Operational Continuity"},
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.2 Cost Reduction & Efficiency"}
    ],
    "integration.topology_health": [
        {"dimension": "01. Technical Infrastructure", "subsection": "1.4 Integration Architecture"},
        {"dimension": "02. Data Management & Quality", "subsection": "2.4 Data Operations"},
        {"dimension": "06. Strategic Alignment", "subsection": "6.1 Business Integration"},
        {"dimension": "08. Process Maturity", "subsection": "8.4 Operational Excellence"}
    ],
    "mdm.duplicate_rate": [
        {"dimension": "02. Data Management & Quality", "subsection": "2.2 Data Quality"},
        {"dimension": "02. Data Management & Quality", "subsection": "2.3 Data Governance"},
        {"dimension": "02. Data Management & Quality", "subsection": "2.4 Data Operations"},
        {"dimension": "08. Process Maturity", "subsection": "8.3 Quality Assurance"},
        {"dimension": "05. Governance & Ethics", "subsection": "5.4 Accountability Structure"}
    ],
    "dq.exceptions_rate": [
        {"dimension": "02. Data Management & Quality", "subsection": "2.2 Data Quality"},
        {"dimension": "02. Data Management & Quality", "subsection": "2.3 Data Governance"},
        {"dimension": "02. Data Management & Quality", "subsection": "2.1 Data Architecture"},
        {"dimension": "08. Process Maturity", "subsection": "8.3 Quality Assurance"}
    ],
    "ai.penetration": [
        {"dimension": "03. AI/ML Capabilities", "subsection": "3.1 Model Development"},
        {"dimension": "06. Strategic Alignment", "subsection": "6.1 Business Integration"},
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.2 Cost Reduction & Efficiency"},
        {"dimension": "08. Process Maturity", "subsection": "8.4 Operational Excellence"},
        {"dimension": "04. Talent & Skills", "subsection": "4.1 Technical Expertise"}
    ],
    "ai.outcome_uplift": [
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.1 Revenue Generation & Growth"},
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.2 Cost Reduction & Efficiency"},
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.3 Customer Experience Enhancement"},
        {"dimension": "6. Strategic Alignment", "subsection": "6.1 Business Integration"},
        {"dimension": "8. Process Maturity", "subsection": "8.4 Operational Excellence"}
    ],
    "ai.governance_coverage": [
        {"dimension": "05. Governance & Ethics", "subsection": "5.1 Ethical Framework"},
        {"dimension": "05. Governance & Ethics", "subsection": "5.2 Regulatory Compliance"},
        {"dimension": "05. Governance & Ethics", "subsection": "5.3 Risk Management"},
        {"dimension": "11. Responsible AI & Social Impact", "subsection": "11.1 Algorithmic Fairness & Bias Mitigation"},
        {"dimension": "11. Responsible AI & Social Impact", "subsection": "11.3 Privacy & Data Protection"}
    ],
    "platform.customization_debt": [
        {"dimension": "01. Technical Infrastructure", "subsection": "1.4 Integration Architecture"},
        {"dimension": "08. Process Maturity", "subsection": "8.5 Measurement & Metrics"},
        {"dimension": "05. Governance & Ethics", "subsection": "5.3 Risk Management"},
        {"dimension": "06. Strategic Alignment", "subsection": "6.4 Innovation Management"},
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.2 Cost Reduction & Efficiency"}
    ],
    "change.failure_rate": [
        {"dimension": "08. Process Maturity", "subsection": "8.3 Quality Assurance"},
        {"dimension": "07. Cultural Readiness", "subsection": "7.2 Change Management"},
        {"dimension": "06. Strategic Alignment", "subsection": "6.1 Business Integration"},
        {"dimension": "08. Process Maturity", "subsection": "8.5 Measurement & Metrics"},
        {"dimension": "05. Governance & Ethics", "subsection": "5.3 Risk Management"}
    ]
}
