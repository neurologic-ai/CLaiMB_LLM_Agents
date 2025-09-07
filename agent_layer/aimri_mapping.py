# agent_layer/aimri_mapping.py
from __future__ import annotations
from typing import Dict, List

"""
AIMRI mapping for BI Tracker metrics.

Each metric id maps to a list of AIMRI dimension entries:
    {"dimension": "<major number>. <name>", "subsection": "<subnumber> <title>"}

Example: {"dimension": "7. Decision Making & Culture", "subsection": "7.4 Decision Making"}

"""

METRIC_TO_AIMRI: Dict[str, List[Dict[str, str]]] = {
    # Header / umbrella line you provided (kept under a special key in case you want to surface it in the UI)
    "__metrics_for_computation__": [
        {"dimension": "7. Decision Making & Culture", "subsection": "7.4 Decision Making"},
        {"dimension": "12. Business Impact",         "subsection": "12.1 Revenue Generation & Growth"},
    ],

    # usage.* ------------------------------------------------------------------
    "usage.dau_mau": [
        {"dimension": "4. Talent & Skills",              "subsection": "4.1 Technical Expertise"},
        {"dimension": "7. Decision Making & Culture",    "subsection": "7.3 Collaboration Culture"},
    ],
    "usage.creators_ratio": [
        {"dimension": "7. Decision Making & Culture",    "subsection": "7.1 Innovation Mindset"},
        {"dimension": "12. Business Impact",             "subsection": "12.3 Customer Experience Enhancement"},
    ],
    "usage.session_depth": [
        {"dimension": "7. Decision Making & Culture",    "subsection": "7.4 Decision Making"},
        {"dimension": "8. Process Maturity",             "subsection": "8.4 Operational Excellence"},
    ],
    "usage.drilldown": [
        {"dimension": "13. AI Risk & Resilience",        "subsection": "13.4 Operational Continuity"},
        {"dimension": "2. Data Management & Quality",    "subsection": "2.2 Data Quality"},
    ],
    "usage.weekly_active_trend": [
        {"dimension": "12. Business Impact",             "subsection": "12.2 Cost Reduction & Efficiency"},
        {"dimension": "7. Decision Making & Culture",    "subsection": "7.4 Decision Making"},
    ],
    "usage.retention_4w": [
        {"dimension": "8. Process Maturity",             "subsection": "8.1 Project Management"},
        {"dimension": "6. Strategic Alignment",          "subsection": "6.5 Innovation Management"},
    ],

    # reliability.* ------------------------------------------------------------
    "reliability.refresh_timeliness": [
        {"dimension": "6. Strategic Alignment",          "subsection": "6.1 Business Integration"},
        {"dimension": "14. External Ecosystem",          "subsection": "14.1 Customer AI Integration"},
    ],
    "reliability.sla_breach_streaks": [
        {"dimension": "13. AI Risk & Resilience",        "subsection": "13.1 Model Reliability & Robustness"},
        {"dimension": "2. Data Management & Quality",    "subsection": "2.2 Data Quality"},
    ],
    "reliability.error_rate_queries": [
        {"dimension": "5. Governance & Ethics",          "subsection": "5.2 Regulatory Compliance"},
        {"dimension": "13. AI Risk & Resilience",        "subsection": "13.5 Regulatory & Legal Compliance"},
    ],

    # features.* ---------------------------------------------------------------
    "features.cross_links": [
        {"dimension": "5. Governance & Ethics",          "subsection": "5.2 Regulatory Compliance"},
        {"dimension": "2. Data Management & Quality",    "subsection": "2.3 Data Governance"},
    ],
    "features.export_rate": [
        {"dimension": "13. AI Risk & Resilience",        "subsection": "13.4 Operational Continuity"},
        {"dimension": "8. Process Maturity",             "subsection": "8.4 Operational Excellence"},
    ],
    "features.alerts_usage": [
        {"dimension": "13. AI Risk & Resilience",        "subsection": "13.4 Operational Continuity"},
        {"dimension": "2. Data Management & Quality",    "subsection": "2.2 Data Quality"},
    ],

    # governance.* -------------------------------------------------------------
    "governance.coverage": [
        {"dimension": "2. Data Management & Quality",    "subsection": "2.1 Data Architecture"},
        {"dimension": "14. External Ecosystem",          "subsection": "14.2 Supplier & Vendor AI Collaboration"},
    ],
    "governance.pii_coverage": [
        {"dimension": "5. Governance & Ethics",          "subsection": "5.4 Transparency Practices"},
        {"dimension": "2. Data Management & Quality",    "subsection": "2.3 Data Governance"},
    ],
    "governance.lineage_coverage": [
        {"dimension": "12. Business Impact",             "subsection": "12.2 Cost Reduction & Efficiency"},
        {"dimension": "13. AI Risk & Resilience",        "subsection": "13.2 Data Dependability & Trust"},
    ],

    # data.* -------------------------------------------------------------------
    "data.source_diversity": [
        {"dimension": "7. Decision Making & Culture",    "subsection": "7.2 Change Management"},
        {"dimension": "6. Strategic Alignment",          "subsection": "6.1 Business Integration"},
    ],
    "data.cost_efficiency": [
        {"dimension": "7. Decision Making & Culture",    "subsection": "7.3 Collaboration Culture"},
        {"dimension": "6. Strategic Alignment",          "subsection": "6.1 Business Integration"},
    ],

    # democratization.* --------------------------------------------------------
    "democratization.self_service": [
        {"dimension": "5. Governance & Ethics",          "subsection": "5.4 Transparency Practices"},
        {"dimension": "7. Decision Making & Culture",    "subsection": "7.4 Decision Making"},
    ],
    "decision.traceability": [
        {"dimension": "12. Business Impact",             "subsection": "12.1 Revenue Generation & Growth"},
        {"dimension": "7. Decision Making & Culture",    "subsection": "7.1 Innovation Mindset"},
    ],
    "democratization.dept_coverage": [
        # Intentionally left empty per your original mapping.
    ],
}