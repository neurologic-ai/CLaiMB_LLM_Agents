# main_orchestrator/input_schemas.py
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Any, Dict, List, Optional
import re

class CategoryWeightsModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    technical_infrastructure: float = Field(..., alias="01. Technical Infrastructure")
    data_management_quality: float = Field(..., alias="02. Data Management & Quality")
    ai_ml_capabilities: float = Field(..., alias="03. AI/ML Capabilities")
    talent_skills: float = Field(..., alias="04. Talent & Skills")
    governance_ethics: float = Field(..., alias="05. Governance & Ethics")
    strategic_alignment: float = Field(..., alias="06. Strategic Alignment")
    cultural_readiness: float = Field(..., alias="07. Cultural Readiness")
    process_maturity: float = Field(..., alias="08. Process Maturity")
    foundation_model_ops: float = Field(..., alias="09. Foundation Model Operations")
    generative_ai: float = Field(..., alias="10. Generative AI Capabilities")
    responsible_ai: float = Field(..., alias="11. Responsible AI & Social Impact")
    ai_business_value: float = Field(..., alias="12. AI Business Value & ROI")
    ai_risk_resilience: float = Field(..., alias="13. AI Risk & Resilience")
    ai_ecosystem: float = Field(..., alias="14. AI Ecosystem & External Integration")
    ai_leadership: float = Field(..., alias="15. AI Leadership & Vision")

_ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

class BIInputsModel(BaseModel):
    # allow extras (we'll ignore them later)
    model_config = ConfigDict(extra="allow")

    today_utc: Optional[str] = None
    activity_events: List[Dict[str, Any]] = Field(default_factory=list)
    user_directory:  List[Dict[str, Any]] = Field(default_factory=list)
    session_logs:    List[Dict[str, Any]] = Field(default_factory=list)
    usage_logs:      List[Dict[str, Any]] = Field(default_factory=list)
    interaction_logs: List[Dict[str, Any]] = Field(default_factory=list)

    governance_data: List[Dict[str, Any]] = Field(default_factory=list)
    dashboard_metadata: List[Dict[str, Any]] = Field(default_factory=list)
    dashboard_link_data: List[Dict[str, Any]] = Field(default_factory=list)

    source_catalog: List[str] = Field(default_factory=list)
    user_roles: List[Dict[str, Any]] = Field(default_factory=list)

    decision_logs: List[Dict[str, Any]] = Field(default_factory=list)

    @field_validator(
        "activity_events","user_directory","session_logs","usage_logs",
        "interaction_logs","governance_data","dashboard_metadata",
        "dashboard_link_data","user_roles","decision_logs"
    )
    @classmethod
    def list_of_dicts(cls, v):
        if not isinstance(v, list):
            raise ValueError("must be a list")
        for i, item in enumerate(v):
            if not isinstance(item, dict):
                raise ValueError(f"index {i}: must be an object")
        return v

    @field_validator("source_catalog")
    @classmethod
    def list_of_strings(cls, v):
        if not isinstance(v, list):
            raise ValueError("must be a list")
        for i, item in enumerate(v):
            if not isinstance(item, str):
                raise ValueError(f"index {i}: must be a string")
        return v

    @field_validator("today_utc")
    @classmethod
    def iso_date_or_none(cls, v: Optional[str]):
        if v in (None, ""):
            return None
        if not _ISO_DATE.match(v):
            raise ValueError("today_utc must be YYYY-MM-DD")
        return v
    
class EnterpriseInputsModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    process_automation_coverage: Dict[str, Any] = Field(default_factory=dict)
    workflow_sla_adherence: Dict[str, Any] = Field(default_factory=dict)
    lead_to_oppty_cycle_time: Dict[str, Any] = Field(default_factory=dict)
    case_resolution_time_sn: Dict[str, Any] = Field(default_factory=dict)
    incident_reopen_rate_sn: Dict[str, Any] = Field(default_factory=dict)
    hr_onboarding_cycle_time: Dict[str, Any] = Field(default_factory=dict)
    procure_to_pay_cycle_time: Dict[str, Any] = Field(default_factory=dict)
    q2c_throughput: Dict[str, Any] = Field(default_factory=dict)
    backlog_aging: Dict[str, Any] = Field(default_factory=dict)
    rpa_success_rate: Dict[str, Any] = Field(default_factory=dict)

    data_sync_latency: Dict[str, Any] = Field(default_factory=dict)
    api_reliability: Dict[str, Any] = Field(default_factory=dict)
    integration_topology_health: Dict[str, Any] = Field(default_factory=dict)
    duplicate_record_rate: Dict[str, Any] = Field(default_factory=dict)
    dq_exceptions_rate: Dict[str, Any] = Field(default_factory=dict)

    ai_integration_penetration: Dict[str, Any] = Field(default_factory=dict)
    ai_outcome_uplift: Dict[str, Any] = Field(default_factory=dict)
    ai_governance_coverage: Dict[str, Any] = Field(default_factory=dict)

    customization_debt_index: Dict[str, Any] = Field(default_factory=dict)
    change_failure_rate: Dict[str, Any] = Field(default_factory=dict)


class MLOpsInputsModel(BaseModel):
    model_config = ConfigDict(extra="forbid")  # reject unknowns

    # all keys from your dataclass, with Optional[Dict[str, Any]]
    mlflow_experiment_completeness: Optional[Dict[str, Any]] = None
    mlflow_lineage_coverage: Optional[Dict[str, Any]] = None
    mlflow_best_run_trend: Optional[Dict[str, Any]] = None
    mlflow_registry_hygiene: Optional[Dict[str, Any]] = None
    mlflow_validation_artifacts: Optional[Dict[str, Any]] = None
    mlflow_reproducibility: Optional[Dict[str, Any]] = None

    aml_endpoint_slo: Optional[Dict[str, Any]] = None
    aml_jobs_flow: Optional[Dict[str, Any]] = None
    aml_monitoring_coverage: Optional[Dict[str, Any]] = None
    aml_registry_governance: Optional[Dict[str, Any]] = None
    aml_cost_correlation: Optional[Dict[str, Any]] = None

    sm_endpoint_slo_scaling: Optional[Dict[str, Any]] = None
    sm_pipeline_stats: Optional[Dict[str, Any]] = None
    sm_experiments_lineage: Optional[Dict[str, Any]] = None
    sm_clarify_coverage: Optional[Dict[str, Any]] = None
    sm_cost_efficiency: Optional[Dict[str, Any]] = None

    cicd_deploy_frequency: Optional[Dict[str, Any]] = None
    cicd_lead_time: Optional[Dict[str, Any]] = None
    cicd_change_failure_rate: Optional[Dict[str, Any]] = None
    cicd_policy_gates: Optional[Dict[str, Any]] = None
    cicd_artifact_lineage: Optional[Dict[str, Any]] = None

    declared_slo: Optional[Dict[str, Any]] = None
    policy_required_checks: Optional[List[str]] = None