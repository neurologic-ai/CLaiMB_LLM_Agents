from __future__ import annotations
from typing import Dict, List

ENTERPRISE_SYSTEM_METRIC_TO_AIMRI: Dict[str, List[dict]] = {
    "process.automation.coverage": [
        {"dimension": "08. Process Maturity", "subsection": "8.4 Operational Excellence"},
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.2 Cost Reduction & Efficiency"},
        {"dimension": "06. Strategic Alignment", "subsection": "6.1 Business Integration"},
        {"dimension": "04. Talent & Skills", "subsection": "4.4 Training & Development"},
        {"dimension": "05. Governance & Ethics", "subsection": "5.3 Risk Management"}
    ],
    "workflow.sla_adherence": [
        {"dimension": "08. Process Maturity", "subsection": "8.4 Operational Excellence"},
        {"dimension": "08. Process Maturity", "subsection": "8.5 Measurement & Metrics"},
        {"dimension": "05. Governance & Ethics", "subsection": "5.4 Accountability Structure"},
        {"dimension": "05. Governance & Ethics", "subsection": "5.5 Transparency Practices"},
        {"dimension": "06. Strategic Alignment", "subsection": "6.1 Business Integration"}
    ],
    "sales.lead_to_oppty_cycle_time": [
        {"dimension": "08. Process Maturity", "subsection": "8.4 Operational Excellence"},
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.1 Revenue Generation & Growth"},
        {"dimension": "06. Strategic Alignment", "subsection": "6.1 Business Integration"},
        {"dimension": "04. Talent & Skills", "subsection": "4.4 Training & Development"},
        {"dimension": "08. Process Maturity", "subsection": "8.5 Measurement & Metrics"}
    ],
    "itsm.case_resolution_time": [
        {"dimension": "08. Process Maturity", "subsection": "8.4 Operational Excellence"},
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.3 Customer Experience Enhancement"},
        {"dimension": "08. Process Maturity", "subsection": "8.5 Measurement & Metrics"},
        {"dimension": "06. Strategic Alignment", "subsection": "6.1 Business Integration"},
        {"dimension": "04. Talent & Skills", "subsection": "4.1 Technical Expertise"}
    ],
    "itsm.incident_reopen_rate": [
        {"dimension": "08. Process Maturity", "subsection": "8.3 Quality Assurance"},
        {"dimension": "08. Process Maturity", "subsection": "8.4 Operational Excellence"},
        {"dimension": "02. Data Management & Quality", "subsection": "2.2 Data Quality"},
        {"dimension": "06. Strategic Alignment", "subsection": "6.1 Business Integration"},
        {"dimension": "04. Talent & Skills", "subsection": "4.4 Training & Development"}
    ],
    "hr.onboarding_cycle_time": [
        {"dimension": "04. Talent & Skills", "subsection": "4.4 Training & Development"},
        {"dimension": "04. Talent & Skills", "subsection": "4.5 Recruitment & Retention"},
        {"dimension": "08. Process Maturity", "subsection": "8.4 Operational Excellence"},
        {"dimension": "06. Strategic Alignment", "subsection": "6.1 Business Integration"},
        {"dimension": "05. Governance & Ethics", "subsection": "5.2 Regulatory Compliance"}
    ],
    "sap.procure_to_pay_cycle": [
        {"dimension": "08. Process Maturity", "subsection": "8.4 Operational Excellence"},
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.2 Cost Reduction & Efficiency"},
        {"dimension": "05. Governance & Ethics", "subsection": "5.2 Regulatory Compliance"},
        {"dimension": "06. Strategic Alignment", "subsection": "6.1 Business Integration"},
        {"dimension": "04. Talent & Skills", "subsection": "4.4 Training & Development"}
    ],
    "q2c.throughput": [
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.1 Revenue Generation & Growth"},
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.2 Cost Reduction & Efficiency"},
        {"dimension": "8. Process Maturity", "subsection": "8.4 Operational Excellence"},
        {"dimension": "6. Strategic Alignment", "subsection": "6.1 Business Integration"},
        {"dimension": "4. Talent & Skills", "subsection": "4.2 Domain Knowledge"}
    ],
    "backlog.aging": [
        {"dimension": "08. Process Maturity", "subsection": "8.4 Operational Excellence"},
        {"dimension": "08. Process Maturity", "subsection": "8.5 Measurement & Metrics"},
        {"dimension": "06. Strategic Alignment", "subsection": "6.1 Business Integration"},
        {"dimension": "04. Talent & Skills", "subsection": "4.4 Training & Development"},
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.2 Cost Reduction & Efficiency"}
    ],
    "rpa.success_rate": [
        {"dimension": "08. Process Maturity", "subsection": "8.3 Quality Assurance"},
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.2 Cost Reduction & Efficiency"},
        {"dimension": "04. Talent & Skills", "subsection": "4.1 Technical Expertise"},
        {"dimension": "01. Technical Infrastructure", "subsection": "1.4 Integration Architecture"},
        {"dimension": "06. Strategic Alignment", "subsection": "6.1 Business Integration"}
    ],
    "integration.data_sync_latency": [
        {"dimension": "02. Data Management & Quality", "subsection": "2.2 Data Quality"},
        {"dimension": "01. Technical Infrastructure", "subsection": "1.4 Integration Architecture"},
        {"dimension": "02. Data Management & Quality", "subsection": "2.4 Data Operations"},
        {"dimension": "08. Process Maturity", "subsection": "8.4 Operational Excellence"},
        {"dimension": "06. Strategic Alignment", "subsection": "6.1 Business Integration"}
    ],
    "api.reliability": [
        {"dimension": "01. Technical Infrastructure", "subsection": "1.4 Integration Architecture"},
        {"dimension": "08. Process Maturity", "subsection": "8.3 Quality Assurance"},
        {"dimension": "02. Data Management & Quality", "subsection": "2.4 Data Operations"},
        {"dimension": "13. AI Risk & Resilience", "subsection": "13.4 Operational Continuity"},
        {"dimension": "06. Strategic Alignment", "subsection": "6.1 Business Integration"}
    ],
    "integration.topology_health": [
        {"dimension": "01. Technical Infrastructure", "subsection": "1.4 Integration Architecture"},
        {"dimension": "02. Data Management & Quality", "subsection": "2.1 Data Architecture"},
        {"dimension": "08. Process Maturity", "subsection": "8.4 Operational Excellence"},
        {"dimension": "06. Strategic Alignment", "subsection": "6.1 Business Integration"}
    ],
    "mdm.duplicate_rate": [
        {"dimension": "02. Data Management & Quality", "subsection": "2.2 Data Quality"},
        {"dimension": "02. Data Management & Quality", "subsection": "2.3 Data Governance"},
        {"dimension": "02. Data Management & Quality", "subsection": "2.1 Data Architecture"},
        {"dimension": "08. Process Maturity", "subsection": "8.3 Quality Assurance"},
        {"dimension": "08. Process Maturity", "subsection": "8.5 Measurement & Metrics"}
    ],
    "dq.exceptions_rate": [
        {"dimension": "02. Data Management & Quality", "subsection": "2.2 Data Quality"},
        {"dimension": "02. Data Management & Quality", "subsection": "2.3 Data Governance"},
        {"dimension": "02. Data Management & Quality", "subsection": "2.4 Data Operations"},
        {"dimension": "08. Process Maturity", "subsection": "8.3 Quality Assurance"},
        {"dimension": "05. Governance & Ethics", "subsection": "5.2 Regulatory Compliance"}
    ],
    "ai.penetration": [
        {"dimension": "03. AI/ML Capabilities", "subsection": "3.1 Model Development"},
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.2 Cost Reduction & Efficiency"},
        {"dimension": "06. Strategic Alignment", "subsection": "6.1 Business Integration"},
        {"dimension": "08. Process Maturity", "subsection": "8.4 Operational Excellence"},
        {"dimension": "15. AI Leadership & Vision", "subsection": "15.1 AI Strategy & Roadmap"}
    ],
    "ai.outcome_uplift": [
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.1 Revenue Generation & Growth"},
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.2 Cost Reduction & Efficiency"},
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.3 Customer Experience Enhancement"},
        {"dimension": "3. AI/ML Capabilities", "subsection": "3.1 Model Development"},
        {"dimension": "8. Process Maturity", "subsection": "8.4 Operational Excellence"}
    ],
    "ai.governance_coverage": [
        {"dimension": "05. Governance & Ethics", "subsection": "5.1 Ethical Framework"},
        {"dimension": "05. Governance & Ethics", "subsection": "5.2 Regulatory Compliance"},
        {"dimension": "05. Governance & Ethics", "subsection": "5.3 Risk Management"},
        {"dimension": "03. AI/ML Capabilities", "subsection": "3.4 Model Governance"},
        {"dimension": "13. AI Risk & Resilience", "subsection": "13.5 Regulatory & Legal Compliance"}
    ],
    "platform.customization_debt": [
        {"dimension": "08. Process Maturity", "subsection": "8.2 Documentation Practices"},
        {"dimension": "08. Process Maturity", "subsection": "8.4 Operational Excellence"},
        {"dimension": "05. Governance & Ethics", "subsection": "5.3 Risk Management"},
        {"dimension": "06. Strategic Alignment", "subsection": "6.4 Innovation Management"},
        {"dimension": "04. Talent & Skills", "subsection": "4.1 Technical Expertise"}
    ],
    "change.failure_rate": [
        {"dimension": "07. Cultural Readiness", "subsection": "7.2 Change Management"},
        {"dimension": "08. Process Maturity", "subsection": "8.3 Quality Assurance"},
        {"dimension": "08. Process Maturity", "subsection": "8.1 Project Management"},
        {"dimension": "05. Governance & Ethics", "subsection": "5.3 Risk Management"},
        {"dimension": "06. Strategic Alignment", "subsection": "6.4 Innovation Management"}
    ]
}
