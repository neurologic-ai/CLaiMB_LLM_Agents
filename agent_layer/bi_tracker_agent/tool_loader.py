# agent_layer/tool_loader.py
from __future__ import annotations
import os
from typing import Any, Callable, Dict
from dotenv import load_dotenv

load_dotenv()

from data_collection_agents.bi_tracker_agent.llm_engine import BIUsageLLM  # noqa: E402

class BITrackerToolLoader:
    """
    Class wrapper around the original module-level loader.
    Behavior is intentionally identical to the prior implementation.
    """

    def __init__(self) -> None:
        self._llm = BIUsageLLM(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.0")),
        )

    @staticmethod
    def _clamp_1to5(v: Any, default: int = 3) -> int:
        try:
            x = int(v)
            return 1 if x < 1 else 5 if x > 5 else x
        except Exception:
            return default

    @staticmethod
    def _sanitize(raw: Dict[str, Any], metric_id: str) -> Dict[str, Any]:
        out = dict(raw or {})
        out["metric_id"] = metric_id

        # --- single source of truth: SCORE (1..5) ---
        score = out.get("score", out.get("band", 3))
        out["score"] = BITrackerToolLoader._clamp_1to5(score, 3)
        # remove any band remnants so artifacts never show it
        if "band" in out:
            del out["band"]

        # required fields
        out.setdefault("rationale", "Strong signal; limited by missing detail.")
        out.setdefault("gaps", [])
        out.setdefault("flags", [])

        # hygiene limits
        out["rationale"] = str(out["rationale"])[:600]
        out["gaps"] = [str(g)[:280] for g in (out.get("gaps") or [])][:6]
        out["flags"] = [str(f)[:80] for f in (out.get("flags") or [])][:10]

        return out

    def load_tool(self, metric_id: str) -> Callable[[Dict[str, Any]], Dict[str, Any]]:
        """
        Returns a callable(snapshot) that computes the metric for the given metric_id.
        Behavior mirrors the original module-level load_tool.
        """
        def _score(_mid: str, snapshot: Dict[str, Any]) -> Dict[str, Any]:
            s = snapshot or {}

            if _mid == "usage.dau_mau":
                return self._sanitize(self._llm.score_dau_mau(s.get("activity_events", []), s.get("today_utc", "")), _mid)
            if _mid == "usage.creators_ratio":
                return self._sanitize(self._llm.score_active_creators(s.get("usage_logs", [])), _mid)
            if _mid == "usage.session_depth":
                return self._sanitize(self._llm.score_session_depth(s.get("session_logs", [])), _mid)
            if _mid == "usage.drilldown":
                return self._sanitize(self._llm.score_drilldown(s.get("interaction_logs", [])), _mid)
            if _mid == "usage.weekly_active_trend":
                return self._sanitize(self._llm.score_weekly_active_trend(s.get("activity_events", []), s.get("today_utc", "")), _mid)
            if _mid == "usage.retention_4w":
                return self._sanitize(self._llm.score_retention_4w(s.get("activity_events", []), s.get("today_utc", "")), _mid)

            if _mid == "features.cross_links":
                return self._sanitize(self._llm.score_cross_links(s.get("dashboard_link_data", [])), _mid)
            if _mid == "features.export_rate":
                return self._sanitize(self._llm.score_export_rate(s.get("activity_events", [])), _mid)
            if _mid == "features.alerts_usage":
                return self._sanitize(self._llm.score_alerts_usage(s.get("activity_events", [])), _mid)

            if _mid == "democratization.dept_coverage":
                return self._sanitize(self._llm.score_dept_coverage(s.get("user_roles", []), s.get("user_directory", [])), _mid)
            if _mid == "democratization.self_service":
                return self._sanitize(self._llm.score_self_service_adoption(s.get("user_roles", [])), _mid)

            if _mid == "reliability.refresh_timeliness":
                return self._sanitize(self._llm.score_refresh_timeliness(s.get("dashboard_metadata", []), s.get("today_utc", "")), _mid)
            if _mid == "reliability.sla_breach_streaks":
                return self._sanitize(self._llm.score_sla_breach_streaks(s.get("dashboard_metadata", []), s.get("today_utc", "")), _mid)
            if _mid == "reliability.error_rate_queries":
                return self._sanitize(self._llm.score_error_rate_queries(s.get("activity_events", [])), _mid)

            if _mid == "governance.coverage":
                return self._sanitize(self._llm.score_governance_coverage(s.get("governance_data", [])), _mid)
            if _mid == "governance.pii_coverage":
                return self._sanitize(self._llm.score_pii_coverage(s.get("governance_data", [])), _mid)
            if _mid == "governance.lineage_coverage":
                return self._sanitize(self._llm.score_lineage_coverage(s.get("governance_data", [])), _mid)

            if _mid == "data.source_diversity":
                return self._sanitize(self._llm.score_source_diversity(s.get("source_catalog", [])), _mid)
            if _mid == "data.cost_efficiency":
                return self._sanitize(self._llm.score_cost_efficiency(
                    s.get("source_catalog", []),
                    s.get("activity_events", []),
                    s.get("dashboard_metadata", []),
                ), _mid)

            return self._sanitize({"score": 3, "rationale": "Unknown metric_id."}, _mid)

        return lambda snapshot: _score(metric_id, snapshot)


# ---- Backwards-compatible module-level API (unchanged for callers) ----
_LOADER = BITrackerToolLoader()

def load_tool(metric_id: str) -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    return _LOADER.load_tool(metric_id)