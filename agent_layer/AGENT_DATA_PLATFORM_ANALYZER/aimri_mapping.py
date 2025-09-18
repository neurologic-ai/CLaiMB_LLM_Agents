from typing import Dict, List

DATA_METRIC_TO_AIMRI: Dict[str, List[Dict[str, str]]] = {
    "evaluate_governance_compliance": [
        {
            "dimension": "02. Data Management & Quality",
            "subsection": "2.3 Data Governance"
        },
        {
            "dimension": "05. Governance & Ethics",
            "subsection": "5.2 Regulatory Compliance"
        },
        {
            "dimension": "09. Foundation Model Operations",
            "subsection": "9.4 Risk & Compliance Management"
        }
    ],
    "evaluate_data_lineage": [
        {
            "dimension": "02. Data Management & Quality",
            "subsection": "2.3 Data Governance"
        },
        {
            "dimension": "02. Data Management & Quality",
            "subsection": "2.4 Data Operations"
        },
        {
            "dimension": "13. AI Risk & Resilience",
            "subsection": "13.2 Data Dependency & Availability"
        }
    ],
    "evaluate_data_freshness": [
        {
            "dimension": "02. Data Management & Quality",
            "subsection": "2.2 Data Quality"
        },
        {
            "dimension": "02. Data Management & Quality",
            "subsection": "2.4 Data Operations"
        },
        {
            "dimension": "13. AI Risk & Resilience",
            "subsection": "13.2 Data Dependency & Availability"
        }
    ],
    "evaluate_data_quality": [
        {
            "dimension": "02. Data Management & Quality",
            "subsection": "2.2 Data Quality"
        },
        {
            "dimension": "02. Data Management & Quality",
            "subsection": "2.4 Data Operations"
        },
        {
            "dimension": "08. Process Maturity",
            "subsection": "8.3 Quality Assurance"
        }
    ],
    "check_schema_consistency": [
        {
            "dimension": "02. Data Management & Quality",
            "subsection": "2.4 Data Operations"
        },
        {
            "dimension": "03. AI/ML Capabilities",
            "subsection": "3.3 MLOps Maturity"
        },
        {
            "dimension": "08. Process Maturity",
            "subsection": "8.5 Measurement & Metrics"
        }
    ],
    "evaluate_duplication": [
        {
            "dimension": "02. Data Management & Quality",
            "subsection": "2.2 Data Quality"
        },
        {
            "dimension": "02. Data Management & Quality",
            "subsection": "2.4 Data Operations"
        },
        {
            "dimension": "03. AI/ML Capabilities",
            "subsection": "3.3 MLOps Maturity"
        }
    ],
    "evaluate_metadata_coverage": [
        {
            "dimension": "02. Data Management & Quality",
            "subsection": "2.3 Data Governance"
        },
        {
            "dimension": "02. Data Management & Quality",
            "subsection": "2.4 Data Operations"
        },
        {
            "dimension": "08. Process Maturity",
            "subsection": "8.2 Documentation Practices"
        }
    ],
    "evaluate_backup_recovery": [
        {
            "dimension": "02. Data Management & Quality",
            "subsection": "2.4 Data Operations"
        },
        {
            "dimension": "03. AI/ML Capabilities",
            "subsection": "3.3 MLOps Maturity"
        },
        {
            "dimension": "13. AI Risk & Resilience",
            "subsection": "13.4 Operational Continuity"
        }
    ],
    "evaluate_sensitive_tagging": [
        {
            "dimension": "02. Data Management & Quality",
            "subsection": "2.5 Data Accessibility"
        },
        {
            "dimension": "05. Governance & Ethics",
            "subsection": "5.2 Regulatory Compliance"
        },
        {
            "dimension": "11. Responsible AI & Social Impact",
            "subsection": "11.3 Privacy & Data Protection"
        }
    ],
    "evaluate_security_config": [
        {
            "dimension": "01. Technical Infrastructure",
            "subsection": "1.5 Security Infrastructure"
        },
        {
            "dimension": "02. Data Management & Quality",
            "subsection": "2.3 Data Governance"
        },
        {
            "dimension": "09. Foundation Model Operations",
            "subsection": "9.4 Risk & Compliance Management"
        }
    ],
    "compute_pipeline_success_rate": [
        {
            "dimension": "02. Data Management & Quality",
            "subsection": "2.4 Data Operations"
        },
        {
            "dimension": "03. AI/ML Capabilities",
            "subsection": "3.3 MLOps Maturity"
        },
        {
            "dimension": "08. Process Maturity",
            "subsection": "8.5 Measurement & Metrics"
        }
    ],
    "assess_query_performance": [
        {
            "dimension": "02. Data Management & Quality",
            "subsection": "2.4 Data Operations"
        },
        {
            "dimension": "03. AI/ML Capabilities",
            "subsection": "3.3 MLOps Maturity"
        },
        {
            "dimension": "08. Process Maturity",
            "subsection": "8.5 Measurement & Metrics"
        }
    ],
    "compute_pipeline_latency_throughput": [
        {
            "dimension": "01. Technical Infrastructure",
            "subsection": "1.2 Computing Resources"
        },
        {
            "dimension": "03. AI/ML Capabilities",
            "subsection": "3.3 MLOps Maturity"
        },
        {
            "dimension": "08. Process Maturity",
            "subsection": "8.5 Measurement & Metrics"
        }
    ],
    "evaluate_resource_utilization": [
        {
            "dimension": "01. Technical Infrastructure",
            "subsection": "1.2 Computing Resources"
        },
        {
            "dimension": "03. AI/ML Capabilities",
            "subsection": "3.3 MLOps Maturity"
        },
        {
            "dimension": "12. AI Business Value & ROI",
            "subsection": "12.2 Cost Reduction & Efficiency"
        }
    ],
    "compute_analytics_adoption": [
        {
            "dimension": "04. Talent & Skills",
            "subsection": "4.4 Training & Development"
        },
        {
            "dimension": "07. Cultural Readiness",
            "subsection": "7.4 Decision Making"
        },
        {
            "dimension": "08. Process Maturity",
            "subsection": "8.5 Measurement & Metrics"
        }
    ]
}