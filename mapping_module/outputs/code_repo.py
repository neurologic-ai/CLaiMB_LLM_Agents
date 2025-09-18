from __future__ import annotations
from typing import Dict, List

CODE_REPO_METRIC_TO_AIMRI: Dict[str, List[dict]] = {
    "code.cyclomatic_complexity_band": [
        {"dimension": "08. Process Maturity", "subsection": "8.3 Quality Assurance"},
        {"dimension": "08. Process Maturity", "subsection": "8.5 Measurement & Metrics"},
        {"dimension": "04. Talent & Skills", "subsection": "4.1 Technical Expertise"},
        {"dimension": "06. Strategic Alignment", "subsection": "6.4 Innovation Management"},
        {"dimension": "07. Cultural Readiness", "subsection": "7.5 Learning Environment"}
    ],
    "code.maintainability_band": [
        {"dimension": "08. Process Maturity", "subsection": "8.3 Quality Assurance"},
        {"dimension": "08. Process Maturity", "subsection": "8.2 Documentation Practices"},
        {"dimension": "04. Talent & Skills", "subsection": "4.1 Technical Expertise"},
        {"dimension": "06. Strategic Alignment", "subsection": "6.4 Innovation Management"},
        {"dimension": "07. Cultural Readiness", "subsection": "7.3 Collaboration Culture"}
    ],
    "code.docstring_coverage_band": [
        {"dimension": "08. Process Maturity", "subsection": "8.2 Documentation Practices"},
        {"dimension": "04. Talent & Skills", "subsection": "4.1 Technical Expertise"},
        {"dimension": "06. Strategic Alignment", "subsection": "6.1 Business Integration"},
        {"dimension": "03. AI/ML Capabilities", "subsection": "3.1 Model Development"}
    ],
    "code.nested_loops_band": [
        {"dimension": "08. Process Maturity", "subsection": "8.3 Quality Assurance"},
        {"dimension": "04. Talent & Skills", "subsection": "4.1 Technical Expertise"},
        {"dimension": "08. Process Maturity", "subsection": "8.4 Operational Excellence"},
        {"dimension": "06. Strategic Alignment", "subsection": "6.4 Innovation Management"}
    ],
    "repo.tests_presence": [
        {"dimension": "08. Process Maturity", "subsection": "8.3 Quality Assurance"},
        {"dimension": "04. Talent & Skills", "subsection": "4.1 Technical Expertise"},
        {"dimension": "08. Process Maturity", "subsection": "8.2 Documentation Practices"},
        {"dimension": "06. Strategic Alignment", "subsection": "6.4 Innovation Management"}
    ],
    "repo.env_config_hygiene": [
        {"dimension": "01. Technical Infrastructure", "subsection": "1.3 Development Environment"},
        {"dimension": "08. Process Maturity", "subsection": "8.2 Documentation Practices"},
        {"dimension": "02. Data Management & Quality", "subsection": "2.2 Data Quality"},
        {"dimension": "08. Process Maturity", "subsection": "8.3 Quality Assurance"},
        {"dimension": "06. Strategic Alignment", "subsection": "6.1 Business Integration"}
    ],
    "repo.cicd_presence": [
        {"dimension": "08. Process Maturity", "subsection": "8.3 Quality Assurance"},
        {"dimension": "08. Process Maturity", "subsection": "8.4 Operational Excellence"},
        {"dimension": "01. Technical Infrastructure", "subsection": "1.4 Integration Architecture"},
        {"dimension": "08. Process Maturity", "subsection": "8.5 Measurement & Metrics"},
        {"dimension": "01. Technical Infrastructure", "subsection": "1.3 Development Environment"}
    ],
    "repo.deployment_readiness": [
        {"dimension": "08. Process Maturity", "subsection": "8.3 Quality Assurance"},
        {"dimension": "08. Process Maturity", "subsection": "8.2 Documentation Practices"},
        {"dimension": "09. Foundation Model Operations", "subsection": "9.1 Model Integration & Deployment"},
        {"dimension": "04. Talent & Skills", "subsection": "4.1 Technical Expertise"},
        {"dimension": "06. Strategic Alignment", "subsection": "6.1 Business Integration"}
    ],
    "repo.experiments_management": [
        {"dimension": "08. Process Maturity", "subsection": "8.2 Documentation Practices"},
        {"dimension": "03. AI/ML Capabilities", "subsection": "3.3 MLOps Maturity"},
        {"dimension": "02. Data Management & Quality", "subsection": "2.1 Data Architecture"},
        {"dimension": "03. AI/ML Capabilities", "subsection": "3.1 Model Development"},
        {"dimension": "08. Process Maturity", "subsection": "8.1 Project Management"}
    ],
    "repo.project_structure": [
        {"dimension": "08. Process Maturity", "subsection": "8.2 Documentation Practices"},
        {"dimension": "04. Talent & Skills", "subsection": "4.3 Team Structure"},
        {"dimension": "01. Technical Infrastructure", "subsection": "1.3 Development Environment"},
        {"dimension": "06. Strategic Alignment", "subsection": "6.1 Business Integration"}
    ],
    "parallel_patterns": [
        {"dimension": "01. Technical Infrastructure", "subsection": "1.4 Integration Architecture"},
        {"dimension": "08. Process Maturity", "subsection": "8.3 Quality Assurance"},
        {"dimension": "13. AI Risk & Resilience", "subsection": "13.1 Model Reliability & Robustness"},
        {"dimension": "04. Talent & Skills", "subsection": "4.1 Technical Expertise"},
        {"dimension": "06. Strategic Alignment", "subsection": "6.4 Innovation Management"}
    ],
    "inference_endpoint": [
        {"dimension": "03. AI/ML Capabilities", "subsection": "3.2 Production Deployment"},
        {"dimension": "08. Process Maturity", "subsection": "8.3 Quality Assurance"},
        {"dimension": "01. Technical Infrastructure", "subsection": "1.4 Integration Architecture"},
        {"dimension": "13. AI Risk & Resilience", "subsection": "13.1 Model Reliability & Robustness"},
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.3 Customer Experience Enhancement"}
    ],
    "model_export": [
        {"dimension": "03. AI/ML Capabilities", "subsection": "3.2 Production Deployment"},
        {"dimension": "03. AI/ML Capabilities", "subsection": "3.1 Model Development"},
        {"dimension": "09. Foundation Model Operations", "subsection": "9.1 Model Integration & Deployment"},
        {"dimension": "08. Process Maturity", "subsection": "8.2 Documentation Practices"},
        {"dimension": "13. AI Risk & Resilience", "subsection": "13.1 Model Reliability & Robustness"}
    ],
    "data_pipeline": [
        {"dimension": "02. Data Management & Quality", "subsection": "2.4 Data Operations"},
        {"dimension": "08. Process Maturity", "subsection": "8.4 Operational Excellence"},
        {"dimension": "13. AI Risk & Resilience", "subsection": "13.1 Model Reliability & Robustness"},
        {"dimension": "05. Governance & Ethics", "subsection": "5.5 Transparency Practices"}
    ],
    "feature_engineering": [
        {"dimension": "02. Data Management & Quality", "subsection": "2.2 Data Quality"},
        {"dimension": "03. AI/ML Capabilities", "subsection": "3.1 Model Development"},
        {"dimension": "03. AI/ML Capabilities", "subsection": "3.3 MLOps Maturity"},
        {"dimension": "08. Process Maturity", "subsection": "8.3 Quality Assurance"},
        {"dimension": "13. AI Risk & Resilience", "subsection": "13.1 Model Reliability & Robustness"}
    ],
    "security_hygiene": [
        {"dimension": "01. Technical Infrastructure", "subsection": "1.5 Security Infrastructure"},
        {"dimension": "05. Governance & Ethics", "subsection": "5.3 Risk Management"},
        {"dimension": "13. AI Risk & Resilience", "subsection": "13.5 Regulatory & Legal Compliance"},
        {"dimension": "03. AI/ML Capabilities", "subsection": "3.4 Model Governance"}
    ],
    "ml.framework_maturity": [
        {"dimension": "03. AI/ML Capabilities", "subsection": "3.1 Model Development"},
        {"dimension": "03. AI/ML Capabilities", "subsection": "3.3 MLOps Maturity"},
        {"dimension": "08. Process Maturity", "subsection": "8.3 Quality Assurance"},
        {"dimension": "04. Talent & Skills", "subsection": "4.1 Technical Expertise"},
        {"dimension": "08. Process Maturity", "subsection": "8.2 Documentation Practices"}
    ],
    "ml.experiment_tracking": [
        {"dimension": "03. AI/ML Capabilities", "subsection": "3.3 MLOps Maturity"},
        {"dimension": "08. Process Maturity", "subsection": "8.2 Documentation Practices"},
        {"dimension": "02. Data Management & Quality", "subsection": "2.2 Data Quality"},
        {"dimension": "03. AI/ML Capabilities", "subsection": "3.1 Model Development"},
        {"dimension": "08. Process Maturity", "subsection": "8.5 Measurement & Metrics"}
    ],
    "ml.hpo_practice": [
        {"dimension": "03. AI/ML Capabilities", "subsection": "3.1 Model Development"},
        {"dimension": "03. AI/ML Capabilities", "subsection": "3.3 MLOps Maturity"},
        {"dimension": "08. Process Maturity", "subsection": "8.3 Quality Assurance"},
        {"dimension": "12. AI Business Value & ROI", "subsection": "12.2 Cost Reduction & Efficiency"},
        {"dimension": "13. AI Risk & Resilience", "subsection": "13.1 Model Reliability & Robustness"}
    ],
    "ml.data_validation": [
        {"dimension": "02. Data Management & Quality", "subsection": "2.2 Data Quality"},
        {"dimension": "02. Data Management & Quality", "subsection": "2.1 Data Architecture"},
        {"dimension": "03. AI/ML Capabilities", "subsection": "3.3 MLOps Maturity"},
        {"dimension": "08. Process Maturity", "subsection": "8.3 Quality Assurance"}
    ],
    "ml.training_practice": [
        {"dimension": "03. AI/ML Capabilities", "subsection": "3.3 MLOps Maturity"},
        {"dimension": "13. AI Risk & Resilience", "subsection": "13.1 Model Reliability & Robustness"},
        {"dimension": "08. Process Maturity", "subsection": "8.3 Quality Assurance"},
        {"dimension": "04. Talent & Skills", "subsection": "4.4 Training & Development"},
        {"dimension": "09. Foundation Model Operations", "subsection": "9.1 Model Integration & Deployment"}
    ],
    "ml.evaluation_practice": [
        {"dimension": "11. Responsible AI & Social Impact", "subsection": "11.1 Algorithmic Fairness & Bias Mitigation"},
        {"dimension": "5. Governance & Ethics", "subsection": "5.1 Ethical Framework"},
        {"dimension": "3. AI/ML Capabilities", "subsection": "3.4 Model Governance"},
        {"dimension": "8. Process Maturity", "subsection": "8.3 Quality Assurance"},
        {"dimension": "8. Process Maturity", "subsection": "8.5 Measurement & Metrics"}
    ]
}
