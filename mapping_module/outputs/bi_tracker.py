from __future__ import annotations
from typing import Dict, List

BI_TRACKER_METRIC_TO_AIMRI: Dict[str, List[dict]] = {
    "usage.dau_mau": [
        {"dimension": "07. Cultural Readiness", "subsection": "7.4 Decision Making"},
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.3 Customer Experience Enhancement"},
        {"dimension": "08. Process Maturity", "subsection": "8.5 Measurement & Metrics"},
        {"dimension": "06. Strategic Alignment", "subsection": "6.1 Business Integration"}
    ],
    "usage.creators_ratio": [
        {"dimension": "04. Talent & Skills", "subsection": "4.4 Training & Development"},
        {"dimension": "07. Cultural Readiness", "subsection": "7.3 Collaboration Culture"},
        {"dimension": "02. Data Management & Quality", "subsection": "2.3 Data Governance"},
        {"dimension": "06. Strategic Alignment", "subsection": "6.2 Leadership Support"},
        {"dimension": "08. Process Maturity", "subsection": "8.5 Measurement & Metrics"}
    ],
    "usage.session_depth": [
        {"dimension": "08. Process Maturity", "subsection": "8.5 Measurement & Metrics"},
        {"dimension": "02. Data Management & Quality", "subsection": "2.4 Data Operations"},
        {"dimension": "06. Strategic Alignment", "subsection": "6.1 Business Integration"},
        {"dimension": "07. Cultural Readiness", "subsection": "7.4 Decision Making"},
        {"dimension": "05. Governance & Ethics", "subsection": "5.4 Accountability Structure"}
    ],
    "usage.drilldown": [
        {"dimension": "06. Strategic Alignment", "subsection": "6.4 Innovation Management"},
        {"dimension": "07. Cultural Readiness", "subsection": "7.4 Decision Making"},
        {"dimension": "02. Data Management & Quality", "subsection": "2.5 Data Accessibility"},
        {"dimension": "08. Process Maturity", "subsection": "8.5 Measurement & Metrics"},
        {"dimension": "04. Talent & Skills", "subsection": "4.1 Technical Expertise"}
    ],
    "reliability.refresh_timeliness": [
        {"dimension": "02. Data Management & Quality", "subsection": "2.3 Data Governance"},
        {"dimension": "02. Data Management & Quality", "subsection": "2.2 Data Quality"},
        {"dimension": "08. Process Maturity", "subsection": "8.4 Operational Excellence"},
        {"dimension": "08. Process Maturity", "subsection": "8.5 Measurement & Metrics"}
    ],
    "features.cross_links": [
        {"dimension": "01. Technical Infrastructure", "subsection": "1.4 Integration Architecture"},
        {"dimension": "02. Data Management & Quality", "subsection": "2.1 Data Architecture"},
        {"dimension": "06. Strategic Alignment", "subsection": "6.1 Business Integration"},
        {"dimension": "08. Process Maturity", "subsection": "8.5 Measurement & Metrics"}
    ],
    "governance.coverage": [
        {"dimension": "02. Data Management & Quality", "subsection": "2.3 Data Governance"},
        {"dimension": "05. Governance & Ethics", "subsection": "5.4 Accountability Structure"},
        {"dimension": "05. Governance & Ethics", "subsection": "5.2 Regulatory Compliance"},
        {"dimension": "08. Process Maturity", "subsection": "8.2 Documentation Practices"}
    ],
    "data.source_diversity": [
        {"dimension": "02. Data Management & Quality", "subsection": "2.1 Data Architecture"},
        {"dimension": "02. Data Management & Quality", "subsection": "2.2 Data Quality"},
        {"dimension": "02. Data Management & Quality", "subsection": "2.3 Data Governance"},
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
        {"dimension": "05. Governance & Ethics", "subsection": "5.5 Transparency Practices"},
        {"dimension": "02. Data Management & Quality", "subsection": "2.3 Data Governance"},
        {"dimension": "08. Process Maturity", "subsection": "8.2 Documentation Practices"},
        {"dimension": "07. Cultural Readiness", "subsection": "7.4 Decision Making"},
        {"dimension": "06. Strategic Alignment", "subsection": "6.1 Business Integration"}
    ],
    "usage.weekly_active_trend": [
        {"dimension": "06. Strategic Alignment", "subsection": "6.2 Leadership Support"},
        {"dimension": "07. Cultural Readiness", "subsection": "7.4 Decision Making"},
        {"dimension": "08. Process Maturity", "subsection": "8.5 Measurement & Metrics"},
        {"dimension": "04. Talent & Skills", "subsection": "4.4 Training & Development"},
        {"dimension": "02. Data Management & Quality", "subsection": "2.5 Data Accessibility"}
    ],
    "usage.retention_4w": [
        {"dimension": "04. Talent & Skills", "subsection": "4.5 Recruitment & Retention"},
        {"dimension": "06. Strategic Alignment", "subsection": "6.3 Investment Strategy"},
        {"dimension": "02. Data Management & Quality", "subsection": "2.3 Data Governance"},
        {"dimension": "07. Cultural Readiness", "subsection": "7.4 Decision Making"},
        {"dimension": "08. Process Maturity", "subsection": "8.5 Measurement & Metrics"}
    ],
    "features.export_rate": [
        {"dimension": "02. Data Management & Quality", "subsection": "2.5 Data Accessibility"},
        {"dimension": "04. Talent & Skills", "subsection": "4.4 Training & Development"},
        {"dimension": "08. Process Maturity", "subsection": "8.5 Measurement & Metrics"},
        {"dimension": "06. Strategic Alignment", "subsection": "6.1 Business Integration"}
    ],
    "features.alerts_usage": [
        {"dimension": "02. Data Management & Quality", "subsection": "2.4 Data Operations"},
        {"dimension": "07. Cultural Readiness", "subsection": "7.4 Decision Making"},
        {"dimension": "08. Process Maturity", "subsection": "8.5 Measurement & Metrics"},
        {"dimension": "06. Strategic Alignment", "subsection": "6.1 Business Integration"}
    ],
    "reliability.sla_breach_streaks": [
        {"dimension": "02. Data Management & Quality", "subsection": "2.2 Data Quality"},
        {"dimension": "02. Data Management & Quality", "subsection": "2.4 Data Operations"},
        {"dimension": "05. Governance & Ethics", "subsection": "5.3 Risk Management"},
        {"dimension": "08. Process Maturity", "subsection": "8.3 Quality Assurance"},
        {"dimension": "13. AI Risk & Resilience", "subsection": "13.4 Operational Continuity"}
    ],
    "reliability.error_rate_queries": [
        {"dimension": "02. Data Management & Quality", "subsection": "2.2 Data Quality"},
        {"dimension": "02. Data Management & Quality", "subsection": "2.3 Data Governance"},
        {"dimension": "08. Process Maturity", "subsection": "8.3 Quality Assurance"},
        {"dimension": "01. Technical Infrastructure", "subsection": "1.4 Integration Architecture"},
        {"dimension": "08. Process Maturity", "subsection": "8.5 Measurement & Metrics"}
    ],
    "governance.pii_coverage": [
        {"dimension": "02. Data Management & Quality", "subsection": "2.3 Data Governance"},
        {"dimension": "05. Governance & Ethics", "subsection": "5.2 Regulatory Compliance"},
        {"dimension": "05. Governance & Ethics", "subsection": "5.3 Risk Management"},
        {"dimension": "11. Responsible AI & Social Impact", "subsection": "11.3 Privacy & Data Protection"}
    ],
    "governance.lineage_coverage": [
        {"dimension": "02. Data Management & Quality", "subsection": "2.3 Data Governance"},
        {"dimension": "02. Data Management & Quality", "subsection": "2.2 Data Quality"},
        {"dimension": "05. Governance & Ethics", "subsection": "5.2 Regulatory Compliance"},
        {"dimension": "05. Governance & Ethics", "subsection": "5.3 Risk Management"},
        {"dimension": "08. Process Maturity", "subsection": "8.2 Documentation Practices"}
    ],
    "data.cost_efficiency": [
        {"dimension": "02. Data Management & Quality", "subsection": "2.2 Data Quality"},
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.2 Cost Reduction & Efficiency"},
        {"dimension": "08. Process Maturity", "subsection": "8.3 Quality Assurance"},
        {"dimension": "06. Strategic Alignment", "subsection": "6.1 Business Integration"},
        {"dimension": "02. Data Management & Quality", "subsection": "2.4 Data Operations"}
    ],
    "democratization.dept_coverage": [
        {"dimension": "07. Cultural Readiness", "subsection": "7.3 Collaboration Culture"},
        {"dimension": "06. Strategic Alignment", "subsection": "6.1 Business Integration"},
        {"dimension": "04. Talent & Skills", "subsection": "4.4 Training & Development"},
        {"dimension": "05. Governance & Ethics", "subsection": "5.4 Accountability Structure"},
        {"dimension": "02. Data Management & Quality", "subsection": "2.5 Data Accessibility"}
    ]
}
