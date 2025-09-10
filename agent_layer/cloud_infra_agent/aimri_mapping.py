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



CLOUD_INFRA_METRIC_TO_AIMRI: Dict[str, List[dict]] = {
    "tagging.coverage": [
        {"dimension": "02. Data Management & Quality", "subsection": "2.3 Data Governance"},
        {"dimension": "02. Data Management & Quality", "subsection": "2.4 Data Operations"},
    ],
    "compute.utilization": [
        {"dimension": "08. Process Maturity",           "subsection": "8.4 Operational Excellence"},
        {"dimension": "01. Technical Infrastructure",   "subsection": "1.2 Computing Resources"},
    ],
    "k8s.utilization": [
        {"dimension": "08. Process Maturity",           "subsection": "8.4 Operational Excellence"},
    ],
    "scaling.effectiveness": [
        {"dimension": "03. AI/ML Capabilities",         "subsection": "3.3 MLOps Maturity"},
        {"dimension": "08. Process Maturity",           "subsection": "8.4 Operational Excellence"},
        {"dimension": "09. Foundation Model Operations","subsection": "9.5 Scaling & Distribution"},
    ],
    "db.utilization": [
        {"dimension": "08. Process Maturity",           "subsection": "8.4 Operational Excellence"},
        {"dimension": "01. Technical Infrastructure",   "subsection": "1.2 Computing Resources"},
        {"dimension": "02. Data Management & Quality",  "subsection": "2.4 Data Operations"},
    ],
    "lb.performance": [
        {"dimension": "08. Process Maturity",           "subsection": "8.3 Quality Assurance"},
        {"dimension": "08. Process Maturity",           "subsection": "8.4 Operational Excellence"},
        {"dimension": "08. Process Maturity",           "subsection": "8.2 Reliability Engineering"},
    ],
    "storage.efficiency": [
        {"dimension": "08. Process Maturity",           "subsection": "8.4 Operational Excellence"},
        {"dimension": "02. Data Management & Quality",  "subsection": "2.4 Data Operations"},
    ],
    "iac.coverage_drift": [
        {"dimension": "03. AI/ML Capabilities",         "subsection": "3.3 MLOps Maturity"},
        {"dimension": "08. Process Maturity",           "subsection": "8.4 Operational Excellence"},
    ],
    "availability.incidents": [
        {"dimension": "08. Process Maturity",           "subsection": "8.3 Quality Assurance"},
        {"dimension": "08. Process Maturity",           "subsection": "8.4 Operational Excellence"},
        {"dimension": "08. Process Maturity",           "subsection": "8.2 Reliability Engineering"},
    ],
    "cost.idle_underutilized": [
        {"dimension": "12. AI Business Value & ROI",    "subsection": "12.2 Cost Reduction & Efficiency"},
        {"dimension": "08. Process Maturity",           "subsection": "8.4 Operational Excellence"},
    ],
    "cost.commit_coverage": [
        {"dimension": "12. AI Business Value & ROI",    "subsection": "12.2 Cost Reduction & Efficiency"},
        {"dimension": "08. Process Maturity",           "subsection": "8.4 Operational Excellence"},
    ],
    "cost.allocation_quality": [
        {"dimension": "02. Data Management & Quality",  "subsection": "2.3 Data Governance"},
        {"dimension": "12. AI Business Value & ROI",    "subsection": "12.2 Cost Reduction & Efficiency"},
    ],
    "security.public_exposure": [
        {"dimension": "01. Technical Infrastructure",   "subsection": "1.5 Security Infrastructure"},
    ],
    "security.encryption": [
        {"dimension": "01. Technical Infrastructure",   "subsection": "1.5 Security Infrastructure"},
    ],
    "security.iam_risk": [
        {"dimension": "01. Technical Infrastructure",   "subsection": "1.5 Security Infrastructure"},
    ],
    "security.vuln_patch": [
        {"dimension": "01. Technical Infrastructure",   "subsection": "1.5 Security Infrastructure"},
    ],
}
