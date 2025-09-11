from typing import Dict, List

MLOPS_METRIC_TO_AIMRI: Dict[str, List[Dict[str, str]]] = {
    "mlflow.experiment_completeness_band": [
        {
            "dimension": "03. AI/ML Capabilities",
            "subsection": "3.3 MLOps Maturity"
        },
        {
            "dimension": "08. Process Maturity",
            "subsection": "8.5 Measurement & Metrics"
        },
        {
            "dimension": "09. Foundation Model Operations",
            "subsection": "9.1 Model Integration & Deployment"
        }
    ],
    "mlflow.registry_hygiene_band": [
        {
            "dimension": "03. AI/ML Capabilities",
            "subsection": "3.3 MLOps Maturity"
        },
        {
            "dimension": "03. AI/ML Capabilities",
            "subsection": "3.4 Model Governance"
        },
        {
            "dimension": "08. Process Maturity",
            "subsection": "8.5 Measurement & Metrics"
        }
    ],
    "mlflow.validation_artifacts_band": [
        {
            "dimension": "03. AI/ML Capabilities",
            "subsection": "3.3 MLOps Maturity"
        },
        {
            "dimension": "03. AI/ML Capabilities",
            "subsection": "3.4 Model Governance"
        },
        {
            "dimension": "08. Process Maturity",
            "subsection": "8.5 Measurement & Metrics"
        }
    ],
    "mlflow.lineage_coverage_band": [
        {
            "dimension": "02. Data Management & Quality",
            "subsection": "2.2 Data Quality"
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
    "mlflow.experiment_velocity_band": [
        {
            "dimension": "03. AI/ML Capabilities",
            "subsection": "3.3 MLOps Maturity"
        },
        {
            "dimension": "08. Process Maturity",
            "subsection": "8.5 Measurement & Metrics"
        },
        {
            "dimension": "09. Foundation Model Operations",
            "subsection": "9.1 Model Integration & Deployment"
        }
    ],
    "aml.endpoint_slo_band": [
        {
            "dimension": "03. AI/ML Capabilities",
            "subsection": "3.2 Production Deployment"
        },
        {
            "dimension": "03. AI/ML Capabilities",
            "subsection": "3.3 MLOps Maturity"
        },
        {
            "dimension": "13. AI Risk & Resilience",
            "subsection": "13.1 Model Reliability & Robustness"
        }
    ],
    "aml.registry_governance_band": [
        {
            "dimension": "01. Technical Infrastructure",
            "subsection": "1.5 Security Infrastructure"
        },
        {
            "dimension": "03. AI/ML Capabilities",
            "subsection": "3.4 Model Governance"
        },
        {
            "dimension": "09. Foundation Model Operations",
            "subsection": "9.4 Risk & Compliance Management"
        }
    ],
    "mlflow.reproducibility_band": [
        {
            "dimension": "03. AI/ML Capabilities",
            "subsection": "3.3 MLOps Maturity"
        },
        {
            "dimension": "08. Process Maturity",
            "subsection": "8.5 Measurement & Metrics"
        },
        {
            "dimension": "13. AI Risk & Resilience",
            "subsection": "13.1 Model Reliability & Robustness"
        }
    ],
    "aml.jobs_flow_band": [
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
    "aml.monitoring_coverage_band": [
        {
            "dimension": "02. Data Management & Quality",
            "subsection": "2.2 Data Quality"
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
    "sm.pipeline_flow_band": [
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
    "aml.cost_correlation_band": [
        {
            "dimension": "03. AI/ML Capabilities",
            "subsection": "3.3 MLOps Maturity"
        },
        {
            "dimension": "08. Process Maturity",
            "subsection": "8.5 Measurement & Metrics"
        },
        {
            "dimension": "12. AI Business Value & ROI",
            "subsection": "12.2 Cost Reduction & Efficiency"
        }
    ],
    "sm.endpoint_slo_scaling_band": [
        {
            "dimension": "03. AI/ML Capabilities",
            "subsection": "3.3 MLOps Maturity"
        },
        {
            "dimension": "08. Process Maturity",
            "subsection": "8.5 Measurement & Metrics"
        },
        {
            "dimension": "09. Foundation Model Operations",
            "subsection": "9.5 Scaling & Distribution"
        }
    ],
    "sm.experiments_lineage_band": [
        {
            "dimension": "03. AI/ML Capabilities",
            "subsection": "3.3 MLOps Maturity"
        },
        {
            "dimension": "08. Process Maturity",
            "subsection": "8.5 Measurement & Metrics"
        },
        {
            "dimension": "09. Foundation Model Operations",
            "subsection": "9.1 Model Integration & Deployment"
        }
    ]
}