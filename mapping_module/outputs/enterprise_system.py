from __future__ import annotations
from typing import Dict, List

ENTERPRISE_SYSTEM_METRIC_TO_AIMRI: Dict[str, List[dict]] = {
    "process.automation.coverage": [
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.2 Cost Reduction & Efficiency"},
        {"dimension": "8. Process Maturity", "subsection": "8.4 Operational Excellence"},
        {"dimension": "6. Strategic Alignment", "subsection": "6.1 Business Integration"},
        {"dimension": "4. Talent & Skills", "subsection": "4.4 Training & Development"},
        {"dimension": "3. AI/ML Capabilities", "subsection": "3.1 Model Development"}
    ],
    "workflow.sla_adherence": [
        {"dimension": "8.4 — Process Maturity", "subsection": "Operational Excellence"},
        {"dimension": "8.5 — Process Maturity", "subsection": "Measurement & Metrics"},
        {"dimension": "5.3 — Governance & Ethics", "subsection": "Risk Management"},
        {"dimension": "12.3 — AI Business Value & ROI", "subsection": "Customer Experience Enhancement"},
        {"dimension": "6.4 — Strategic Alignment", "subsection": "Innovation Management"}
    ],
    "sales.lead_to_oppty_cycle_time": [
        {"dimension": "8.5", "subsection": "Process Maturity / Measurement & Metrics"},
        {"dimension": "12.2", "subsection": "AI Business Value & ROI / Cost Reduction & Efficiency"},
        {"dimension": "6.1", "subsection": "Strategic Alignment / Business Integration"},
        {"dimension": "4.4", "subsection": "Talent & Skills / Training & Development"},
        {"dimension": "8.4", "subsection": "Process Maturity / Operational Excellence"}
    ],
    "itsm.case_resolution_time": [
        {"dimension": "8.5", "subsection": "Process Maturity / Measurement & Metrics"},
        {"dimension": "12.2", "subsection": "AI Business Value & ROI / Cost Reduction & Efficiency"},
        {"dimension": "6.4", "subsection": "Strategic Alignment / Innovation Management"},
        {"dimension": "4.4", "subsection": "Talent & Skills / Training & Development"},
        {"dimension": "8.4", "subsection": "Process Maturity / Operational Excellence"}
    ],
    "itsm.incident_reopen_rate": [
        {"dimension": "8.1", "subsection": "Process Maturity / Project Management"},
        {"dimension": "8.3", "subsection": "Process Maturity / Quality Assurance"},
        {"dimension": "8.4", "subsection": "Process Maturity / Operational Excellence"},
        {"dimension": "8.5", "subsection": "Process Maturity / Measurement & Metrics"},
        {"dimension": "4.4", "subsection": "Talent & Skills / Training & Development"}
    ],
    "hr.onboarding_cycle_time": [
        {"dimension": "4.4 — Talent & Skills", "subsection": "Training & Development"},
        {"dimension": "4.5 — Talent & Skills", "subsection": "Recruitment & Retention"},
        {"dimension": "8.4 — Process Maturity", "subsection": "Operational Excellence"},
        {"dimension": "8.5 — Process Maturity", "subsection": "Measurement & Metrics"}
    ],
    "sap.procure_to_pay_cycle": [
        {"dimension": "8.1 — Process Maturity", "subsection": "8.4 Operational Excellence"},
        {"dimension": "8.1 — Process Maturity", "subsection": "8.5 Measurement & Metrics"},
        {"dimension": "6.1 — Strategic Alignment", "subsection": "6.1 Business Integration"},
        {"dimension": "12.2 — AI Business Value & ROI", "subsection": "12.2 Cost Reduction & Efficiency"},
        {"dimension": "4.1 — Talent & Skills", "subsection": "4.2 Domain Knowledge"}
    ],
    "q2c.throughput": [
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.2 Cost Reduction & Efficiency"},
        {"dimension": "8. Process Maturity", "subsection": "8.4 Operational Excellence"},
        {"dimension": "6. Strategic Alignment", "subsection": "6.1 Business Integration"},
        {"dimension": "4. Talent & Skills", "subsection": "4.2 Domain Knowledge"},
        {"dimension": "5. Governance & Ethics", "subsection": "5.3 Risk Management"}
    ],
    "backlog.aging": [
        {"dimension": "8.4 — Process Maturity", "subsection": "Operational Excellence"},
        {"dimension": "8.5 — Process Maturity", "subsection": "Measurement & Metrics"},
        {"dimension": "6.4 — Strategic Alignment", "subsection": "Innovation Management"},
        {"dimension": "12.2 — AI Business Value & ROI", "subsection": "Cost Reduction & Efficiency"},
        {"dimension": "4.4 — Talent & Skills", "subsection": "Training & Development"}
    ],
    "rpa.success_rate": [
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.2 Cost Reduction & Efficiency"},
        {"dimension": "8. Process Maturity", "subsection": "8.4 Operational Excellence"},
        {"dimension": "8. Process Maturity", "subsection": "8.5 Measurement & Metrics"},
        {"dimension": "13. AI Risk & Resilience", "subsection": "13.1 Model Reliability & Robustness"},
        {"dimension": "6. Strategic Alignment", "subsection": "6.1 Business Integration"}
    ],
    "integration.data_sync_latency": [
        {"dimension": "2.1", "subsection": "Data Management & Quality / Data Architecture"},
        {"dimension": "2.2", "subsection": "Data Management & Quality / Data Quality"},
        {"dimension": "2.4", "subsection": "Data Management & Quality / Data Operations"},
        {"dimension": "4.1", "subsection": "Talent & Skills / Technical Expertise"},
        {"dimension": "6.1", "subsection": "Strategic Alignment / Business Integration"}
    ],
    "api.reliability": [
        {"dimension": "1.4", "subsection": "Technical Infrastructure / Integration Architecture"},
        {"dimension": "8.4", "subsection": "Process Maturity / Operational Excellence"},
        {"dimension": "2.2", "subsection": "Data Management & Quality / Data Quality"},
        {"dimension": "6.1", "subsection": "Strategic Alignment / Business Integration"},
        {"dimension": "13.1", "subsection": "AI Risk & Resilience / Model Reliability & Robustness"}
    ],
    "integration.topology_health": [
        {"dimension": "1.4 — Technical Infrastructure", "subsection": "Integration Architecture"},
        {"dimension": "8.4 — Process Maturity", "subsection": "Operational Excellence"},
        {"dimension": "6.1 — Strategic Alignment", "subsection": "Business Integration"},
        {"dimension": "2.1 — Data Management & Quality", "subsection": "Data Architecture"}
    ],
    "mdm.duplicate_rate": [
        {"dimension": "2.2", "subsection": "Data Quality"},
        {"dimension": "2.3", "subsection": "Data Governance"},
        {"dimension": "2.1", "subsection": "Data Architecture"},
        {"dimension": "2.4", "subsection": "Data Operations"},
        {"dimension": "8.3", "subsection": "Quality Assurance"}
    ],
    "dq.exceptions_rate": [
        {"dimension": "2.2", "subsection": "Data Quality"},
        {"dimension": "2.3", "subsection": "Data Governance"},
        {"dimension": "2.4", "subsection": "Data Operations"},
        {"dimension": "8.3", "subsection": "Quality Assurance"},
        {"dimension": "5.3", "subsection": "Risk Management"}
    ],
    "ai.penetration": [
        {"dimension": "3.1 AI/ML Capabilities", "subsection": "Model Development"},
        {"dimension": "3.2 AI/ML Capabilities", "subsection": "Production Deployment"},
        {"dimension": "6.1 Strategic Alignment", "subsection": "Business Integration"},
        {"dimension": "12.2 AI Business Value & ROI", "subsection": "Cost Reduction & Efficiency"},
        {"dimension": "4.1 Talent & Skills", "subsection": "Technical Expertise"}
    ],
    "ai.outcome_uplift": [
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.1 Revenue Generation & Growth"},
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.2 Cost Reduction & Efficiency"},
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.3 Customer Experience Enhancement"},
        {"dimension": "6. Strategic Alignment", "subsection": "6.1 Business Integration"},
        {"dimension": "8. Process Maturity", "subsection": "8.4 Operational Excellence"}
    ],
    "ai.governance_coverage": [
        {"dimension": "5.1 — Governance & Ethics", "subsection": "Ethical Framework"},
        {"dimension": "5.2 — Governance & Ethics", "subsection": "Regulatory Compliance"},
        {"dimension": "5.3 — Governance & Ethics", "subsection": "Risk Management"},
        {"dimension": "5.4 — Governance & Ethics", "subsection": "Accountability Structure"},
        {"dimension": "5.5 — Governance & Ethics", "subsection": "Transparency Practices"}
    ],
    "platform.customization_debt": [
        {"dimension": "1.4 — Technical Infrastructure", "subsection": "Integration Architecture"},
        {"dimension": "1.3 — Technical Infrastructure", "subsection": "Development Environment"},
        {"dimension": "5.3 — Governance & Ethics", "subsection": "Risk Management"},
        {"dimension": "6.4 — Strategic Alignment", "subsection": "Innovation Management"},
        {"dimension": "8.4 — Process Maturity", "subsection": "Operational Excellence"}
    ],
    "change.failure_rate": [
        {"dimension": "7.2 — Cultural Readiness", "subsection": "Change Management"},
        {"dimension": "8.3 — Process Maturity", "subsection": "Quality Assurance"},
        {"dimension": "8.5 — Process Maturity", "subsection": "Measurement & Metrics"},
        {"dimension": "6.4 — Strategic Alignment", "subsection": "Innovation Management"},
        {"dimension": "3.3 — AI/ML Capabilities", "subsection": "MLOps Maturity"}
    ]
}
