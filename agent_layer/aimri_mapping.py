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

# Canonical dimension names (used to construct the mapping consistently)
DIM = {
    1:  "1. Algorithmic Fairness & Bias Mitigation",
    2:  "2. Data Management & Quality",
    5:  "5. Governance & Ethics",
    6:  "6. Strategic Alignment",
    7:  "7. Cultural Readiness",
    8:  "8. Process Maturity",
    12: "12. Business Impact",
    13: "13. AI Risk & Resilience",
    14: "14. External Ecosystem",
}

METRIC_TO_AIMRI: Dict[str, List[Dict[str, str]]] = {
    # usage.*
    "usage.dau_mau": [
        {"dimension": DIM[7],  "subsection": "7.4 Decision Making"},
        {"dimension": DIM[12], "subsection": "12.1 Revenue Generation & Growth"},
    ],
    "usage.creators_ratio": [
        {"dimension": "4. Talent & Skills", "subsection": "4.1 Technical Expertise"},
        {"dimension": DIM[7],               "subsection": "7.3 Collaboration Culture"},
    ],
    "usage.session_depth": [
        {"dimension": DIM[7],  "subsection": "7.1 Innovation Mindset"},
        {"dimension": DIM[12], "subsection": "12.3 Customer Experience Enhancement"},
    ],
    "usage.drilldown": [
        {"dimension": DIM[7], "subsection": "7.4 Decision Making"},
        {"dimension": DIM[8], "subsection": "8.4 Operational Excellence"},
    ],
    "usage.weekly_active_trend": [
        {"dimension": DIM[12], "subsection": "12.1 Revenue Generation & Growth"},
        {"dimension": DIM[7],  "subsection": "7.1 Innovation Mindset"},
    ],
    "usage.retention_4w": [
        {"dimension": DIM[12], "subsection": "12.2 Cost Reduction & Efficiency"},
        {"dimension": DIM[7],  "subsection": "7.4 Decision Making"},
    ],

    # reliability.*
    "reliability.refresh_timeliness": [
        {"dimension": DIM[13], "subsection": "13.4 Operational Continuity"},
        {"dimension": DIM[2],  "subsection": "2.2 Data Quality"},
    ],
    "reliability.sla_breach_streaks": [
        {"dimension": DIM[13], "subsection": "13.4 Operational Continuity"},
        {"dimension": DIM[2],  "subsection": "2.2 Data Quality"},
    ],
    "reliability.error_rate_queries": [
        {"dimension": DIM[13], "subsection": "13.1 Model Reliability & Robustness"},
        {"dimension": DIM[2],  "subsection": "2.2 Data Quality"},
    ],

    # features.*
    "features.cross_links": [
        {"dimension": DIM[6],  "subsection": "6.1 Business Integration"},
        {"dimension": DIM[14], "subsection": "14.1 Customer AI Integration"},
    ],
    "features.export_rate": [
        {"dimension": DIM[8],  "subsection": "8.1 Project Management"},
        {"dimension": DIM[6],  "subsection": "6.5 Innovation Management"},
    ],
    "features.alerts_usage": [
        {"dimension": DIM[13], "subsection": "13.4 Operational Continuity"},
        {"dimension": DIM[8],  "subsection": "8.4 Operational Excellence"},
    ],

    # governance.*
    "governance.coverage": [
        {"dimension": DIM[5], "subsection": "5.2 Regulatory Compliance"},
        {"dimension": DIM[2], "subsection": "2.3 Data Governance"},
    ],
    "governance.pii_coverage": [
        {"dimension": DIM[5],  "subsection": "5.2 Regulatory Compliance"},
        {"dimension": DIM[13], "subsection": "13.5 Regulatory & Legal Compliance"},
    ],
    "governance.lineage_coverage": [
        {"dimension": DIM[5], "subsection": "5.4 Transparency Practices"},
        {"dimension": DIM[2], "subsection": "2.3 Data Governance"},
    ],

    # data.*
    "data.source_diversity": [
        {"dimension": DIM[2],  "subsection": "2.1 Data Architecture"},
        {"dimension": DIM[14], "subsection": "14.2 Supplier & Vendor AI Collaboration"},
    ],
    "data.cost_efficiency": [
        {"dimension": DIM[12], "subsection": "12.2 Cost Reduction & Efficiency"},
        {"dimension": DIM[13], "subsection": "13.2 Data Dependability & Trust"},
    ],

    # democratization.*
    "democratization.self_service": [
        {"dimension": DIM[7], "subsection": "7.2 Change Management"},
        {"dimension": DIM[6], "subsection": "6.1 Business Integration"},
    ],
    "decision.traceability": [
        {"dimension": DIM[5], "subsection": "5.4 Transparency Practices"},
        {"dimension": DIM[7], "subsection": "7.4 Decision Making"},
    ],
    "democratization.dept_coverage": [
        {"dimension": DIM[7], "subsection": "7.3 Collaboration Culture"},
        {"dimension": DIM[6], "subsection": "6.1 Business Integration"},
    ],
}