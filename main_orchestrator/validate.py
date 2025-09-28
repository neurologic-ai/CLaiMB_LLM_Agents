from data_collection_agents.bi_tracker_agent.canonical import BIInputs

from data_collection_agents.enterprise_systems_agent.canonical import EnterpriseInputs

from data_collection_agents.ml_ops_agent.canonical import MLOpsInputs

_BI_ALLOWED = {
    "today_utc","activity_events","user_directory","session_logs","usage_logs",
    "interaction_logs","governance_data","dashboard_metadata","dashboard_link_data",
    "source_catalog","user_roles","decision_logs",
}

def _normalize_and_check_bi(payload: dict) -> tuple[dict, list[str]]:

    ignored = [k for k in payload.keys() if k not in _BI_ALLOWED]

    snap = BIInputs.from_dict(payload)
    normalized = {
        "today_utc": snap.today_utc,
        "activity_events": snap.activity_events,
        "user_directory": snap.user_directory,
        "session_logs": snap.session_logs,
        "usage_logs": snap.usage_logs,
        "interaction_logs": snap.interaction_logs,
        "governance_data": snap.governance_data,
        "dashboard_metadata": snap.dashboard_metadata,
        "dashboard_link_data": snap.dashboard_link_data,
        "source_catalog": snap.source_catalog,
        "user_roles": snap.user_roles,
        "decision_logs": snap.decision_logs,
    }

    has_any = any(
        bool(normalized[k])
        for k in normalized.keys()
        if k != "today_utc"
    )
    if not has_any:
        raise ValueError("No valid BI inputs provided (all canonical fields are empty).")

    return normalized, ignored

_ENTERPRISE_FIELDS = [
    # --- Business Process & Workflow (1–10) ---
    "process_automation_coverage",
    "workflow_sla_adherence",
    "lead_to_oppty_cycle_time",
    "case_resolution_time_sn",
    "incident_reopen_rate_sn",
    "hr_onboarding_cycle_time",
    "procure_to_pay_cycle_time",
    "q2c_throughput",
    "backlog_aging",
    "rpa_success_rate",

    # --- Integration & Data Health (11–15) ---
    "data_sync_latency",
    "api_reliability",
    "integration_topology_health",
    "duplicate_record_rate",
    "dq_exceptions_rate",

    # --- AI Integration & Outcomes (16–18) ---
    "ai_integration_penetration",
    "ai_outcome_uplift",
    "ai_governance_coverage",

    # --- Platform Health, Change & Risk (19–20) ---
    "customization_debt_index",
    "change_failure_rate",
]
_ENTERPRISE_ALLOWED = set(_ENTERPRISE_FIELDS)


def _normalize_and_check_enterprise(payload: dict) -> tuple[dict, list[str]]:


    ignored = [k for k in payload.keys() if k not in _ENTERPRISE_ALLOWED]

    snap = EnterpriseInputs.from_dict(payload)

    normalized = {field: getattr(snap, field) for field in _ENTERPRISE_FIELDS}


    has_any = any(bool(v) for v in normalized.values())
    if not has_any:
        raise ValueError("No valid Enterprise inputs provided (all canonical fields are empty).")

    return normalized, ignored

# Allow all canonical fields (taken directly from MLOpsInputs dataclass)
_MLOPS_ALLOWED = set(MLOpsInputs.__dataclass_fields__.keys())


def _normalize_and_check_mlops(payload: dict) -> tuple[dict, list[str]]:
    """
    Normalize raw UI payload into canonical MLOpsInputs shape.
    Returns (normalized_dict, ignored_fields).
    Raises ValueError if all canonical fields are empty.
    """

    ignored = [k for k in payload.keys() if k not in _MLOPS_ALLOWED]

    # Canonical object will filter out anything not allowed
    snap = MLOpsInputs.from_json(payload)

    # Convert back to dict for storage/forwarding
    normalized = snap.as_dict()

    # Check: at least one canonical field has data (not counting declared defaults)
    has_any = any(
        bool(v)
        for k, v in normalized.items()
        if k not in ("declared_slo", "policy_required_checks")
    )
    if not has_any:
        raise ValueError("No valid MLOps inputs provided (all canonical fields are empty).")

    return normalized, ignored