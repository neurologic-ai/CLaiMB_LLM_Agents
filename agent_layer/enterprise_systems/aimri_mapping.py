from __future__ import annotations
from typing import Dict, List

"""
AIMRI mapping for Enterprise Systems metrics.

Each metric id maps to a list of dicts:
  {"dimension": "<NN. Dimension Name>", "subsection": "<NN.M Title>"}

Dimension names follow the AIMRI board:
01 Technical Infrastructure
02 Data Management & Quality
03 AI/ML Capabilities
04 Talent & Skills
05 Governance & Ethics
06 Strategic Alignment
07 Cultural Readiness
08 Process Maturity
09 Foundation Model Operations
10 Generative AI Capabilities
11 Responsible AI & Social Impact
12 AI Business Value & ROI
13 AI Risk & Resilience
14 AI Ecosystem & External Integration
15 AI Leadership & Vision
"""

ENTERPRISE_METRIC_TO_AIMRI: Dict[str, List[Dict[str, str]]] = {
    # ---- Business Process & Workflow ----
    "process.automation.coverage": [
        {"dimension": "08. Process Maturity",           "subsection": "8.4 Operational Excellence"},
        {"dimension": "10. Generative AI Capabilities", "subsection": "10.2 Quality Control & Validation"},
    ],
    "workflow.sla_adherence": [
        {"dimension": "09. Foundation Model Operations", "subsection": "9.1 Model Integration & Deployment"},
        {"dimension": "13. AI Risk & Resilience",        "subsection": "13.4 Operational Continuity"},
    ],
    "sales.lead_to_oppty_cycle_time": [
        {"dimension": "12. AI Business Value & ROI",    "subsection": "12.1 Revenue Generation & Growth"},
        {"dimension": "08. Process Maturity",           "subsection": "8.5 Measurement & Metrics"},
    ],
    "itsm.case_resolution_time": [
        {"dimension": "13. AI Risk & Resilience",       "subsection": "13.4 Operational Continuity"},
        {"dimension": "08. Process Maturity",           "subsection": "8.4 Operational Excellence"},
    ],
    "itsm.incident_reopen_rate": [
        {"dimension": "13. AI Risk & Resilience",       "subsection": "13.1 Model Reliability & Robustness"},
        {"dimension": "08. Process Maturity",           "subsection": "8.3 Quality Assurance"},
    ],
    "hr.onboarding_cycle_time": [
        {"dimension": "04. Talent & Skills",            "subsection": "4.5 Recruitment & Retention"},
        {"dimension": "07. Cultural Readiness",         "subsection": "7.2 Change Management"},
    ],
    "sap.procure_to_pay_cycle": [
        {"dimension": "08. Process Maturity",           "subsection": "8.4 Operational Excellence"},
        {"dimension": "12. AI Business Value & ROI",    "subsection": "12.2 Cost Reduction & Efficiency"},
    ],
    "q2c.throughput": [
        {"dimension": "12. AI Business Value & ROI",    "subsection": "12.3 Customer Experience Enhancement"},
        {"dimension": "08. Process Maturity",           "subsection": "8.4 Operational Excellence"},
    ],
    "backlog.aging": [
        {"dimension": "08. Process Maturity",           "subsection": "8.5 Measurement & Metrics"},
        {"dimension": "13. AI Risk & Resilience",       "subsection": "13.4 Operational Continuity"},
    ],
    "rpa.success_rate": [
        {"dimension": "10. Generative AI Capabilities", "subsection": "10.2 Quality Control & Validation"},
        {"dimension": "08. Process Maturity",           "subsection": "8.4 Operational Excellence"},
    ],

    # ---- Integration & Data Health ----
    "integration.data_sync_latency": [
        {"dimension": "01. Technical Infrastructure",    "subsection": "1.5 Integration Architecture"},
        {"dimension": "14. AI Ecosystem & External Integration", "subsection": "14.1 Customer AI Integration"},
    ],
    "api.reliability": [
        {"dimension": "01. Technical Infrastructure",    "subsection": "1.5 Integration Architecture"},
        {"dimension": "13. AI Risk & Resilience",        "subsection": "13.1 Model Reliability & Robustness"},
    ],
    "integration.topology_health": [
        {"dimension": "01. Technical Infrastructure",    "subsection": "1.5 Integration Architecture"},
        {"dimension": "14. AI Ecosystem & External Integration", "subsection": "14.2 Supplier & Vendor AI Collaboration"},
    ],
    "mdm.duplicate_rate": [
        {"dimension": "02. Data Management & Quality",   "subsection": "2.2 Data Quality"},
        {"dimension": "02. Data Management & Quality",   "subsection": "2.5 Data Accessibility"},
    ],
    "dq.exceptions_rate": [
        {"dimension": "02. Data Management & Quality",   "subsection": "2.2 Data Quality"},
        {"dimension": "05. Governance & Ethics",         "subsection": "5.2 Regulatory Compliance"},
    ],

    # ---- AI Integration & Outcomes ----
    "ai.penetration": [
        {"dimension": "03. AI/ML Capabilities",          "subsection": "3.4 Advanced Capabilities"},
        {"dimension": "12. AI Business Value & ROI",     "subsection": "12.1 Revenue Generation & Growth"},
    ],
    "ai.outcome_uplift": [
        {"dimension": "12. AI Business Value & ROI",     "subsection": "12.1 Revenue Generation & Growth"},
        {"dimension": "12. AI Business Value & ROI",     "subsection": "12.3 Customer Experience Enhancement"},
    ],
    "ai.governance_coverage": [
        {"dimension": "05. Governance & Ethics",         "subsection": "5.1 Ethical Framework"},
        {"dimension": "05. Governance & Ethics",         "subsection": "5.2 Regulatory Compliance"},
    ],

    # ---- Platform Health, Change & Risk ----
    "platform.customization_debt": [
        {"dimension": "01. Technical Infrastructure",    "subsection": "1.4 Development Environment"},
        {"dimension": "13. AI Risk & Resilience",        "subsection": "13.2 Data Dependency Risks"},
    ],
    "change.failure_rate": [
        {"dimension": "08. Process Maturity",           "subsection": "8.3 Quality Assurance"},
        {"dimension": "13. AI Risk & Resilience",       "subsection": "13.4 Operational Continuity"},
    ],
}