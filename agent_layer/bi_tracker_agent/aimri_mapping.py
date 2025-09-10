# agent_layer/aimri_mapping.py
from __future__ import annotations
from typing import Dict, List

"""
AIMRI mapping for BI Tracker metrics.

Schema expected by orchestrator:
    METRIC_TO_AIMRI = {
        "<metric_id>": [
            {"dimension": "<Dimension Name>", "subsection": "<code title>"},
            ...
        ]
    }

Where:
- "dimension" is the top-level AIMRI dimension name (e.g., "7. Cultural Readiness").
- "subsection" is the specific code and title (e.g., "7.4 Decision Making").
"""

METRIC_TO_AIMRI: Dict[str, List[Dict[str, str]]] = {
    # usage.*
    "usage.dau_mau": [
        {"dimension": "7. Cultural Readiness",  "subsection": "7.4 Decision Making"},
        {"dimension": "12. Business Impact", "subsection": "12.1 Revenue Generation & Growth"},
    ],
    "usage.creators_ratio": [
        {"dimension": "4. Talent & Skills", "subsection": "4.1 Technical Expertise"},
        {"dimension": "7. Cultural Readiness",               "subsection": "7.3 Collaboration Culture"},
    ],
    "usage.session_depth": [
        {"dimension": "7. Cultural Readiness",  "subsection": "7.1 Innovation Mindset"},
        {"dimension": "12. Business Impact", "subsection": "12.3 Customer Experience Enhancement"},
    ],
    "usage.drilldown": [
        {"dimension": "7. Cultural Readiness", "subsection": "7.4 Decision Making"},
        {"dimension": "8. Process Maturity", "subsection": "8.4 Operational Excellence"},
    ],
    "usage.weekly_active_trend": [
        {"dimension": "12. Business Impact", "subsection": "12.1 Revenue Generation & Growth"},
        {"dimension": "7. Cultural Readiness",  "subsection": "7.1 Innovation Mindset"},
    ],
    "usage.retention_4w": [
        {"dimension": "12. Business Impact", "subsection": "12.2 Cost Reduction & Efficiency"},
        {"dimension": "7. Cultural Readiness",  "subsection": "7.4 Decision Making"},
    ],

    # reliability.*
    "reliability.refresh_timeliness": [
        {"dimension": "13. AI Risk & Resilience", "subsection": "13.4 Operational Continuity"},
        {"dimension":  "2. Data Management & Quality",  "subsection": "2.2 Data Quality"},
    ],
    "reliability.sla_breach_streaks": [
        {"dimension": "13. AI Risk & Resilience", "subsection": "13.4 Operational Continuity"},
        {"dimension":  "2. Data Management & Quality",  "subsection": "2.2 Data Quality"},
    ],
    "reliability.error_rate_queries": [
        {"dimension": "13. AI Risk & Resilience", "subsection": "13.1 Model Reliability & Robustness"},
        {"dimension":  "2. Data Management & Quality",  "subsection": "2.2 Data Quality"},
    ],

    # features.*
    "features.cross_links": [
        {"dimension":  "6. Strategic Alignment",  "subsection": "6.1 Business Integration"},
        {"dimension": "14. External Ecosystem", "subsection": "14.1 Customer AI Integration"},
    ],
    "features.export_rate": [
        {"dimension": "8. Process Maturity",  "subsection": "8.1 Project Management"},
        {"dimension":  "6. Strategic Alignment",  "subsection": "6.4 Innovation Management"},
    ],
    "features.alerts_usage": [
        {"dimension": "13. AI Risk & Resilience", "subsection": "13.4 Operational Continuity"},
        {"dimension": "8. Process Maturity",  "subsection": "8.4 Operational Excellence"},
    ],

    # governance.*
    "governance.coverage": [
        {"dimension": "5. Governance & Ethics", "subsection": "5.2 Regulatory Compliance"},
        {"dimension":  "2. Data Management & Quality", "subsection": "2.3 Data Governance"},
    ],
    "governance.pii_coverage": [
        {"dimension": "5. Governance & Ethics",  "subsection": "5.2 Regulatory Compliance"},
        {"dimension": "13. AI Risk & Resilience", "subsection": "13.5 Regulatory & Legal Compliance"},
    ],
    "governance.lineage_coverage": [
        {"dimension": "5. Governance & Ethics", "subsection": "5.5 Transparency Practices"},
        {"dimension":  "2. Data Management & Quality", "subsection": "2.3 Data Governance"},
    ],

    # data.*
    "data.source_diversity": [
        {"dimension":  "2. Data Management & Quality",  "subsection": "2.1 Data Architecture"},
        {"dimension": "14. External Ecosystem", "subsection": "14.2 Supplier & Vendor AI Collaboration"},
    ],
    "data.cost_efficiency": [
        {"dimension": "12. Business Impact", "subsection": "12.2 Cost Reduction & Efficiency"},
        {"dimension": "13. AI Risk & Resilience", "subsection": "13.2 Data Dependability & Trust"},
    ],

    # democratization.*
    "democratization.self_service": [
        {"dimension": "7. Cultural Readiness", "subsection": "7.2 Change Management"},
        {"dimension":  "6. Strategic Alignment", "subsection": "6.1 Business Integration"},
    ],
    "decision.traceability": [
        {"dimension": "5. Governance & Ethics", "subsection": "5.5 Transparency Practices"},
        {"dimension": "7. Cultural Readiness", "subsection": "7.4 Decision Making"},
    ],
    "democratization.dept_coverage": [
        {"dimension": "7. Cultural Readiness", "subsection": "7.3 Collaboration Culture"},
        {"dimension":  "6. Strategic Alignment", "subsection": "6.1 Business Integration"},
    ],
}