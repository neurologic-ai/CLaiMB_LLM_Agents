from __future__ import annotations
from typing import Dict, List

BI_TRACKER_METRIC_TO_AIMRI: Dict[str, List[dict]] = {
    "usage.dau_mau": [
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.3 Customer Experience Enhancement"},
        {"dimension": "8. Process Maturity", "subsection": "8.5 Measurement & Metrics"},
        {"dimension": "6. Strategic Alignment", "subsection": "6.1 Business Integration"},
        {"dimension": "4. Talent & Skills", "subsection": "4.5 Recruitment & Retention"},
        {"dimension": "7. Cultural Readiness", "subsection": "7.4 Decision Making"}
    ],
    "usage.creators_ratio": [
        {"dimension": "7.3 Cultural Readiness", "subsection": "Collaboration Culture"},
        {"dimension": "4.4 Talent & Skills", "subsection": "Training & Development"},
        {"dimension": "6.4 Strategic Alignment", "subsection": "Innovation Management"},
        {"dimension": "8.5 Process Maturity", "subsection": "Measurement & Metrics"},
        {"dimension": "12.3 AI Business Value & ROI", "subsection": "Customer Experience Enhancement"}
    ],
    "usage.session_depth": [
        {"dimension": "6.1", "subsection": "Strategic Alignment / Business Integration"},
        {"dimension": "12.3", "subsection": "AI Business Value & ROI / Customer Experience Enhancement"},
        {"dimension": "8.5", "subsection": "Process Maturity / Measurement & Metrics"},
        {"dimension": "4.1", "subsection": "Talent & Skills / Technical Expertise"},
        {"dimension": "7.4", "subsection": "Cultural Readiness / Decision Making"}
    ],
    "usage.drilldown": [
        {"dimension": "6.1", "subsection": "Strategic Alignment / Business Integration"},
        {"dimension": "7.1", "subsection": "Cultural Readiness / Innovation Mindset"},
        {"dimension": "8.5", "subsection": "Process Maturity / Measurement & Metrics"},
        {"dimension": "2.1", "subsection": "Data Management & Quality / Data Architecture"},
        {"dimension": "4.4", "subsection": "Talent & Skills / Training & Development"}
    ],
    "reliability.refresh_timeliness": [
        {"dimension": "2.2", "subsection": "Data Management & Quality / Data Quality"},
        {"dimension": "2.4", "subsection": "Data Management & Quality / Data Operations"},
        {"dimension": "2.1", "subsection": "Data Management & Quality / Data Architecture"},
        {"dimension": "8.5", "subsection": "Process Maturity / Measurement & Metrics"},
        {"dimension": "6.1", "subsection": "Strategic Alignment / Business Integration"}
    ],
    "features.cross_links": [
        {"dimension": "1.4", "subsection": "Integration Architecture"},
        {"dimension": "6.1", "subsection": "Business Integration"},
        {"dimension": "2.1", "subsection": "Data Architecture"},
        {"dimension": "4.3", "subsection": "Team Structure"},
        {"dimension": "8.4", "subsection": "Operational Excellence"}
    ],
    "governance.coverage": [
        {"dimension": "2.1 — Data Management & Quality", "subsection": "2.3 Data Governance"},
        {"dimension": "5.1 — Governance & Ethics", "subsection": "5.4 Accountability Structure"},
        {"dimension": "5.2 — Governance & Ethics", "subsection": "5.2 Regulatory Compliance"},
        {"dimension": "2.2 — Data Management & Quality", "subsection": "2.2 Data Quality"}
    ],
    "data.source_diversity": [
        {"dimension": "2.1", "subsection": "Data Management & Quality / Data Architecture"},
        {"dimension": "2.3", "subsection": "Data Management & Quality / Data Governance"},
        {"dimension": "2.4", "subsection": "Data Management & Quality / Data Operations"},
        {"dimension": "6.1", "subsection": "Strategic Alignment / Business Integration"},
        {"dimension": "1.4", "subsection": "Technical Infrastructure / Integration Architecture"}
    ],
    "democratization.self_service": [
        {"dimension": "7.1 — Cultural Readiness", "subsection": "Innovation Mindset"},
        {"dimension": "2.5 — Data Management & Quality", "subsection": "Data Accessibility"},
        {"dimension": "4.4 — Talent & Skills", "subsection": "Training & Development"},
        {"dimension": "5.3 — Governance & Ethics", "subsection": "Risk Management"},
        {"dimension": "6.1 — Strategic Alignment", "subsection": "Business Integration"}
    ],
    "decision.traceability": [
        {"dimension": "5.4 Governance & Ethics", "subsection": "Accountability Structure"},
        {"dimension": "5.5 Governance & Ethics", "subsection": "Transparency Practices"},
        {"dimension": "2.3 Data Management & Quality", "subsection": "Data Governance"},
        {"dimension": "2.5 Data Management & Quality", "subsection": "Data Accessibility"},
        {"dimension": "8.5 Process Maturity", "subsection": "Measurement & Metrics"}
    ],
    "usage.weekly_active_trend": [
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.3 Customer Experience Enhancement"},
        {"dimension": "8. Process Maturity", "subsection": "8.5 Measurement & Metrics"},
        {"dimension": "4. Talent & Skills", "subsection": "4.4 Training & Development"},
        {"dimension": "6. Strategic Alignment", "subsection": "6.1 Business Integration"},
        {"dimension": "7. Cultural Readiness", "subsection": "7.1 Innovation Mindset"}
    ],
    "usage.retention_4w": [
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.3 Customer Experience Enhancement"},
        {"dimension": "4. Talent & Skills", "subsection": "4.5 Recruitment & Retention"},
        {"dimension": "8. Process Maturity", "subsection": "8.5 Measurement & Metrics"},
        {"dimension": "6. Strategic Alignment", "subsection": "6.1 Business Integration"},
        {"dimension": "7. Cultural Readiness", "subsection": "7.4 Decision Making"}
    ],
    "features.export_rate": [
        {"dimension": "2.5 — Data Management & Quality", "subsection": "Data Accessibility"},
        {"dimension": "12.3 — AI Business Value & ROI", "subsection": "Customer Experience Enhancement"},
        {"dimension": "8.5 — Process Maturity", "subsection": "Measurement & Metrics"},
        {"dimension": "6.1 — Strategic Alignment", "subsection": "Business Integration"},
        {"dimension": "4.1 — Talent & Skills", "subsection": "Technical Expertise"}
    ],
    "features.alerts_usage": [
        {"dimension": "6.1", "subsection": "Strategic Alignment / Business Integration"},
        {"dimension": "8.5", "subsection": "Process Maturity / Measurement & Metrics"},
        {"dimension": "4.1", "subsection": "Talent & Skills / Technical Expertise"},
        {"dimension": "7.1", "subsection": "Cultural Readiness / Innovation Mindset"},
        {"dimension": "12.3", "subsection": "AI Business Value & ROI / Customer Experience Enhancement"}
    ]
}
