from __future__ import annotations
from typing import Dict, List

BI_TRACKER_METRIC_TO_AIMRI: Dict[str, List[dict]] = {
    "usage.dau_mau": [
        {"dimension": "02. Data Management & Quality", "subsection": "2.3 Data Governance"},
        {"dimension": "08. Process Maturity", "subsection": "8.5 Measurement & Metrics"},
        {"dimension": "06. Strategic Alignment", "subsection": "6.3 Investment Strategy"},
        {"dimension": "04. Talent & Skills", "subsection": "4.4 Training & Development"},
        {"dimension": "07. Cultural Readiness", "subsection": "7.3 Collaboration Culture"}
    ],
    "usage.creators_ratio": [
        {"dimension": "04. Talent & Skills", "subsection": "4.4 Training & Development"},
        {"dimension": "07. Cultural Readiness", "subsection": "7.3 Collaboration Culture"},
        {"dimension": "07. Cultural Readiness", "subsection": "7.4 Decision Making"},
        {"dimension": "06. Strategic Alignment", "subsection": "6.2 Leadership Support"},
        {"dimension": "02. Data Management & Quality", "subsection": "2.3 Data Governance"}
    ],
    "usage.session_depth": [
        {"dimension": "04. Talent & Skills", "subsection": "4.4 Training & Development"},
        {"dimension": "02. Data Management & Quality", "subsection": "2.3 Data Governance"},
        {"dimension": "08. Process Maturity", "subsection": "8.5 Measurement & Metrics"},
        {"dimension": "06. Strategic Alignment", "subsection": "6.3 Investment Strategy"},
        {"dimension": "07. Cultural Readiness", "subsection": "7.4 Decision Making"}
    ],
    "usage.drilldown": [
        {"dimension": "02. Data Management & Quality", "subsection": "2.4 Data Operations"},
        {"dimension": "04. Talent & Skills", "subsection": "4.1 Technical Expertise"},
        {"dimension": "07. Cultural Readiness", "subsection": "7.4 Decision Making"},
        {"dimension": "08. Process Maturity", "subsection": "8.5 Measurement & Metrics"}
    ],
    "reliability.refresh_timeliness": [
        {"dimension": "02. Data Management & Quality", "subsection": "2.3 Data Governance"},
        {"dimension": "02. Data Management & Quality", "subsection": "2.2 Data Quality"},
        {"dimension": "08. Process Maturity", "subsection": "8.3 Quality Assurance"},
        {"dimension": "08. Process Maturity", "subsection": "8.4 Operational Excellence"}
    ],
    "features.cross_links": [
        {"dimension": "02. Data Management & Quality", "subsection": "2.3 Data Governance"},
        {"dimension": "06. Strategic Alignment", "subsection": "6.1 Business Integration"},
        {"dimension": "07. Cultural Readiness", "subsection": "7.4 Decision Making"},
        {"dimension": "08. Process Maturity", "subsection": "8.5 Measurement & Metrics"}
    ],
    "governance.coverage": [
        {"dimension": "02. Data Management & Quality", "subsection": "2.3 Data Governance"},
        {"dimension": "05. Governance & Ethics", "subsection": "5.4 Accountability Structure"},
        {"dimension": "05. Governance & Ethics", "subsection": "5.2 Regulatory Compliance"},
        {"dimension": "08. Process Maturity", "subsection": "8.2 Documentation Practices"},
        {"dimension": "08. Process Maturity", "subsection": "8.3 Quality Assurance"}
    ],
    "data.source_diversity": [
        {"dimension": "02. Data Management & Quality", "subsection": "2.1 Data Architecture"},
        {"dimension": "02. Data Management & Quality", "subsection": "2.3 Data Governance"},
        {"dimension": "02. Data Management & Quality", "subsection": "2.2 Data Quality"},
        {"dimension": "06. Strategic Alignment", "subsection": "6.1 Business Integration"},
        {"dimension": "08. Process Maturity", "subsection": "8.5 Measurement & Metrics"}
    ],
    "democratization.self_service": [
        {"dimension": "02. Data Management & Quality", "subsection": "2.3 Data Governance"},
        {"dimension": "02. Data Management & Quality", "subsection": "2.5 Data Accessibility"},
        {"dimension": "07. Cultural Readiness", "subsection": "7.4 Decision Making"},
        {"dimension": "04. Talent & Skills", "subsection": "4.4 Training & Development"},
        {"dimension": "05. Governance & Ethics", "subsection": "5.4 Accountability Structure"}
    ],
    "decision.traceability": [
        {"dimension": "02. Data Management & Quality", "subsection": "2.3 Data Governance"},
        {"dimension": "05. Governance & Ethics", "subsection": "5.5 Transparency Practices"},
        {"dimension": "08. Process Maturity", "subsection": "8.5 Measurement & Metrics"},
        {"dimension": "07. Cultural Readiness", "subsection": "7.4 Decision Making"}
    ],
    "usage.weekly_active_trend": [
        {"dimension": "06. Strategic Alignment", "subsection": "6.2 Leadership Support"},
        {"dimension": "08. Process Maturity", "subsection": "8.5 Measurement & Metrics"},
        {"dimension": "07. Cultural Readiness", "subsection": "7.4 Decision Making"},
        {"dimension": "04. Talent & Skills", "subsection": "4.4 Training & Development"},
        {"dimension": "02. Data Management & Quality", "subsection": "2.3 Data Governance"}
    ],
    "usage.retention_4w": [
        {"dimension": "04. Talent & Skills", "subsection": "4.5 Recruitment & Retention"},
        {"dimension": "02. Data Management & Quality", "subsection": "2.3 Data Governance"},
        {"dimension": "06. Strategic Alignment", "subsection": "6.1 Business Integration"},
        {"dimension": "08. Process Maturity", "subsection": "8.5 Measurement & Metrics"},
        {"dimension": "07. Cultural Readiness", "subsection": "7.4 Decision Making"}
    ],
    "features.export_rate": [
        {"dimension": "02. Data Management & Quality", "subsection": "2.5 Data Accessibility"},
        {"dimension": "02. Data Management & Quality", "subsection": "2.3 Data Governance"},
        {"dimension": "08. Process Maturity", "subsection": "8.5 Measurement & Metrics"},
        {"dimension": "06. Strategic Alignment", "subsection": "6.3 Investment Strategy"}
    ],
    "features.alerts_usage": [
        {"dimension": "07. Cultural Readiness", "subsection": "7.4 Decision Making"},
        {"dimension": "04. Talent & Skills", "subsection": "4.4 Training & Development"},
        {"dimension": "08. Process Maturity", "subsection": "8.5 Measurement & Metrics"},
        {"dimension": "06. Strategic Alignment", "subsection": "6.1 Business Integration"},
        {"dimension": "02. Data Management & Quality", "subsection": "2.2 Data Quality"}
    ]
}
