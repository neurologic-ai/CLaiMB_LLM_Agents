# Data_Collection_Agents/bi_tracker/llm_engine.py
from __future__ import annotations
import json
import time
import random
from typing import Any, Dict, List, Optional
from loguru import logger
from .logging_utils import timed
from .base_agent import BaseMicroAgent

"""
BI Metric Prompt Builder — Per-metric expert prompts (score-only contract)

Output JSON (for every metric):
{
  "metric_id": "<id>",
  "score": 1..5,
  "rationale": "<1–3 sentences: name strongest positive(s) + the single biggest limiter>",
  "flags": ["optional","short","machine-readable","hints"],
  "gaps": ["<limiter> → <what to add/change> → <target threshold> (unlocks score X)"]
}

Design goals
- Treat the LLM as a domain analyst, not a calculator.
- Make explicit how each input key affects the judgement.
- Prefer conservative scoring when critical evidence is missing; record it in `gaps`.
- Be robust to sparse or partial inputs.
"""

# ---------------------------------------------------------------------------
# Shared blocks & helpers
# ---------------------------------------------------------------------------

UNIVERSAL_RESPONSE_FORMAT = (
    '{"metric_id":"<id>",'
    '"score":<1-5>,'
    '"rationale":"<1–3 sentences: strongest positive(s) + single biggest limiter>",'
    '"flags":[],'
    '"gaps":[]}'
)

IMPROVEMENT_GUIDANCE_EXAMPLES = [
    "Trend stability not demonstrated → include 7d/28d DAU series with seasonality notes → ≥4 weeks stable/increasing (unlocks score 5).",
    "Department spread unknown → report creators by department and coverage % → reach ≥60% dept coverage (unlocks score 4).",
    "Export governance unclear → add export policy status + exception rate → ≥95% governed exports (unlocks score 5).",
    "Refresh lateness tail unknown → add p95/p99 lateness across assets → keep p95 within SLA for ≥95% assets (unlocks score 5).",
]

def _section(title: str, body: str) -> str:
    return f"{title}:\n{body.strip()}\n\n"

def _bullets(title: str, items: List[str]) -> str:
    return f"{title}:\n- " + "\n- ".join(items) + "\n\n"


# ---------------------------------------------------------------------------
# Metric prompts (20) — upgraded rubrics with explicit key-to-score link
# ---------------------------------------------------------------------------

METRIC_PROMPTS: Dict[str, Dict[str, Any]] = {
    # 1) DAU/MAU stickiness
    "usage.dau_mau": {
        "system": (
            _section("ROLE", "Product analytics specialist focusing on engagement quality, seasonality, and stability.")
            + _section("CONTEXT", "Stickiness ≈ DAU/MAU. Reliable interpretation needs enough daily coverage and 4-week stability.")
            + _section("GOAL", "Explain if stickiness is healthy and *reliable* given evidence. Name strongest positive and main limiter. Output score 1–5.")
            + _bullets("INSTRUCTIONS", [
                "From activity_events, infer DAU and MAU (distinct user_id per day vs last 30d). If evidence is too sparse, say so.",
                "Check stability across the last 4 ISO weeks; call out growth/flat/decline.",
                "Account for seasonality (weekday/weekend).",
                "Prefer conservative scoring if denominators or stability evidence are weak.",
            ])
            + _section("INPUT DESCRIPTIONS",
                "- today (YYYY-MM-DD): Anchor date to bound 'last 30 days' and ISO-week bucketing.\n"
                "- activity_events[]: User events for distinct counts.\n"
                "  • ts: ISO timestamp (use only events within last 30 days from 'today').\n"
                "  • user_id: Stable identifier for distinct DAU/MAU.\n"
                "  • action: view/explore/edit (useful for volume context; do not filter by action unless stated)."
            )
            + _bullets("RUBRIC — How inputs affect score", [
                "5: Stickiness ≥0.60 AND 4-week pattern is stable or improving with sufficient daily coverage (events across most days).",
                "4: 0.45–0.59 with stable week pattern; minor gaps (e.g., a few sparse days).",
                "3: 0.30–0.44 OR unstable weeks OR unclear daily coverage (denominators weak).",
                "2: 0.15–0.29 OR sustained decline across weeks.",
                "1: <0.15 OR severe data sparsity preventing trustworthy computation.",
            ])
            + _section("RESPONSE FORMAT (JSON ONLY)", UNIVERSAL_RESPONSE_FORMAT)
        ),
        "example_input": {
            "today": "2025-08-01",
            "activity_events": [
                {"ts": "2025-08-01T10:00:00Z", "user_id": "u1", "action": "view", "content_id": "d1"},
                {"ts": "2025-07-22T10:00:00Z", "user_id": "u2", "action": "view", "content_id": "d2"}
            ]
        },
        "input_key_meanings": {
            "today": "ISO date for 'today' (YYYY-MM-DD)",
            "activity_events": "Events in last 30d to compute DAU/MAU (distinct user_id by day/month)",
            "activity_events[].user_id": "User identifier",
            "activity_events[].ts": "Event timestamp (ISO)",
            "activity_events[].action": "view/explore/edit"
        },
        "response_format": UNIVERSAL_RESPONSE_FORMAT,
        "example_output": {
            "metric_id": "usage.dau_mau",
            "band": 4,
            "rationale": "Stickiness ~0.55 is solid; lack of explicit 7d stability and 4w trend limits to 4.",
            "flags": ["trend_unknown"],
            "gaps": [
                "Trend stability not demonstrated → provide 7d DAU and 4-week DAU trend with seasonality notes → show stable/non-declining trend (unlocks band 5)."
            ]
        }
    },

    # 2) Active viewers vs creators
    "usage.creators_ratio": {
        "system": (
            _section("ROLE", "Self-service BI reviewer emphasizing enablement and authoring capacity.")
            + _section("CONTEXT", "Higher creator share among actives and broad departmental spread indicate democratization.")
            + _section("GOAL", "Assess creator share and breadth; highlight concentration risks; output score 1–5.")
            + _bullets("INSTRUCTIONS", [
                "Compute creator% among active users from usage_logs[].role.",
                "If dept_map is present, estimate breadth: % departments with ≥1 creator; call out concentration (creators clustered in 1–2 teams).",
                "Prefer cautious scoring if breadth is unknown.",
            ])
            + _section("INPUT DESCRIPTIONS",
                "- usage_logs[]: Active users during the window.\n"
                "  • role: 'creator' / 'viewer'.\n"
                "- dept_map {user_id->department}: Optional — establishes breadth and concentration."
            )
            + _bullets("RUBRIC — How inputs affect score", [
                "5: Creator% ≥35% AND creators distributed across many departments (broad coverage).",
                "4: 25–34% creators with fair breadth OR clear improving trend.",
                "3: 15–24% creators OR heavy concentration in a couple of teams.",
                "2: 8–14% creators (limited enablement).",
                "1: <8% creators OR unknown creator% due to missing roles.",
            ])
            + _section("RESPONSE FORMAT (JSON ONLY)", UNIVERSAL_RESPONSE_FORMAT)
        ),
        "example_input": {
            "usage_logs": [
                {"user": "u1", "role": "viewer"},
                {"user": "u2", "role": "creator"}
            ],
            "dept_map": {"u1": "Sales", "u2": "Ops"}
        },
        "input_key_meanings": {
            "usage_logs": "Array of active users with effective roles",
            "usage_logs[].role": "'creator' or 'viewer'",
            "dept_map": "Optional mapping user->department to assess spread"
        },
        "response_format": UNIVERSAL_RESPONSE_FORMAT,
        "example_output": {
            "metric_id": "usage.creators_ratio",
            "band": 4,
            "rationale": "Creator share near 30% is healthy; department coverage not fully proven keeps it at 4.",
            "flags": ["dept_spread_unknown"],
            "gaps": [
                "Department spread unknown → publish creators per department and % coverage → achieve ≥60% departments with ≥1 creator (unlocks band 5)."
            ]
        }
    },

    # 3) Session depth & repeatability
    "usage.session_depth": {
        "system": (
            _section("ROLE", "Engagement quality analyst focusing on time-on-task, page breadth, and repeat cadence.")
            + _section("CONTEXT", "Depth is multi-dimensional: duration, pages per session, and repeat frequency.")
            + _section("GOAL", "Summarize depth and its reliability; name top driver and limiter; score 1–5.")
            + _bullets("INSTRUCTIONS", [
                "Use central tendency (mean/median) across users; avoid outlier bias.",
                "Incorporate repeats_per_week where available; if sparse, mark as a gap.",
            ])
            + _section("INPUT DESCRIPTIONS",
                "- session_logs[]:\n"
                "  • duration (seconds) — time-on-task\n"
                "  • pages — page breadth per session\n"
                "  • repeats_per_week (optional) — repeat cadence"
            )
            + _bullets("RUBRIC — How inputs affect score", [
                "5: ≥300s avg, ≥4 pages, and weekly repeats for majority (evidence present).",
                "4: 250–299s with ~3–4 pages; repeat cadence partially evidenced.",
                "3: 150–249s and ~2–3 pages; repeat cadence unknown/sparse.",
                "2: 90–149s and ≤2 pages; weak repeatability.",
                "1: <90s and ≤1 page; no evidence of repeat use.",
            ])
            + _section("RESPONSE FORMAT (JSON ONLY)", UNIVERSAL_RESPONSE_FORMAT)
        ),
        "example_input": {
            "session_logs": [
                {"user": "u1", "duration": 320, "pages": 4, "repeats_per_week": 2},
                {"user": "u2", "duration": 180, "pages": 3}
            ]
        },
        "input_key_meanings": {
            "session_logs": "Per-user session aggregates for recent period",
            "session_logs[].duration": "Average seconds per session",
            "session_logs[].pages": "Average pages per session",
            "session_logs[].repeats_per_week": "Approx repeat sessions / week"
        },
        "response_format": UNIVERSAL_RESPONSE_FORMAT,
        "example_output": {
            "metric_id": "usage.session_depth",
            "band": 4,
            "rationale": "Avg ~270s and ~3.6 pages are strong; repeat cadence missing for many users caps at 4.",
            "flags": ["repeat_freq_sparse"],
            "gaps": [
                "Repeat cadence missing for many users → instrument repeats_per_week for ≥80% actives → verify weekly repeats for majority (unlocks band 5)."
            ]
        }
    },

    # 4) Drill-down usage
    "usage.drilldown": {
        "system": (
            _section("ROLE", "Exploration behavior analyst focusing on diagnostic depth across teams.")
            + _section("CONTEXT", "Drill-down indicates investigative analysis beyond viewing.")
            + _section("GOAL", "Estimate adoption rate, breadth across BUs, and 4-week stability; then score 1–5.")
            + _bullets("INSTRUCTIONS", [
                "Identify drill actions; relate to sessions/users for adoption.",
                "Discuss breadth by BU/department if user or ts exist; else record a gap.",
                "Comment on 4-week stability where timestamps allow.",
            ])
            + _section("INPUT DESCRIPTIONS",
                "- interaction_logs[]:\n"
                "  • user: enables breadth by dept (with mapping)\n"
                "  • action: look for 'drill'/'drilldown'\n"
                "  • ts (optional): enables stability check"
            )
            + _bullets("RUBRIC — How inputs affect score", [
                "5: ≥35% sessions use drill, broad spread across ≥3 BUs, and stable over 4 weeks.",
                "4: 25–34% with fair spread; stability mostly fine.",
                "3: 15–24% OR narrow spread OR stability unknown.",
                "2: 8–14% with limited breadth.",
                "1: <8% or highly concentrated usage.",
            ])
            + _section("RESPONSE FORMAT (JSON ONLY)", UNIVERSAL_RESPONSE_FORMAT)
        ),
        "example_input": {"interaction_logs": [{"user": "u1", "action": "drill"}]},
        "input_key_meanings": {
            "interaction_logs": "Interactions where 'action' includes 'drill'/'drilldown'",
            "interaction_logs[].user": "User performing drilldown",
            "interaction_logs[].ts": "Optional timestamp to assess stability"
        },
        "response_format": UNIVERSAL_RESPONSE_FORMAT,
        "example_output": {
            "metric_id": "usage.drilldown",
            "band": 3,
            "rationale": "About 18% of sessions include drill; lack of multi-BU spread limits the score.",
            "flags": ["spread_limited"],
            "gaps": [
                "Spread by BU unknown → report drilldown usage by dept/team → show broad spread across ≥3 BUs (unlocks band 4).",
                "Stability unverified → include 4-week drilldown time series → demonstrate non-declining trend (supports band 4–5)."
            ]
        }
    },

    # 5) Refresh timeliness
    "reliability.refresh_timeliness": {
        "system": (
            _section("ROLE", "Freshness/SLA reviewer focusing on impact on critical assets.")
            + _section("CONTEXT", "Late refresh on high-priority content erodes trust most.")
            + _section("GOAL", "Explain within-SLA posture and staleness concentration; score 1–5.")
            + _bullets("INSTRUCTIONS", [
                "Weigh 'priority' dashboards more in your reasoning.",
                "Call out lateness tails (p95/p99) if available; otherwise record a gap.",
            ])
            + _section("INPUT DESCRIPTIONS",
                "- dashboards[]:\n"
                "  • last_refresh (YYYY-MM-DD)\n"
                "  • sla (daily/weekly/monthly)\n"
                "  • priority (high/medium/low)\n"
                "- today (YYYY-MM-DD): reference date for staleness"
            )
            + _bullets("RUBRIC — How inputs affect score", [
                "5: ≥95% within SLA across estate; 0 critical stale (priority=high).",
                "4: 85–94% within SLA; stales are low-impact.",
                "3: 70–84% OR some high-impact stales.",
                "2: 50–69% within SLA OR many stales.",
                "1: <50% OR chronic stales; evidence insufficient.",
            ])
            + _section("RESPONSE FORMAT (JSON ONLY)", UNIVERSAL_RESPONSE_FORMAT)
        ),
        "example_input": {
            "dashboards": [
                {"id": "d1", "last_refresh": "2025-07-31", "sla": "daily", "priority": "high"},
                {"id": "d2", "last_refresh": "2025-07-28", "sla": "weekly", "priority": "low"}
            ],
            "today": "2025-08-01"
        },
        "input_key_meanings": {
            "dashboards": "Freshness entries with SLA cadence and (optional) priority",
            "dashboards[].sla": "daily/weekly/monthly",
            "dashboards[].priority": "high/medium/low to weight impact",
            "today": "ISO date for comparison"
        },
        "response_format": UNIVERSAL_RESPONSE_FORMAT,
        "example_output": {
            "metric_id": "reliability.refresh_timeliness",
            "band": 4,
            "rationale": "≈88% within SLA and no critical stales; missing p95 lateness limits confidence.",
            "flags": ["lateness_distribution_unknown"],
            "gaps": [
                "Tail lateness unknown → add p95/p99 lateness across assets → keep p95 within SLA for ≥95% dashboards (unlocks band 5)."
            ]
        }
    },

    # 6) Cross-dashboard links
    "features.cross_links": {
        "system": (
            _section("ROLE", "Navigation design reviewer focusing on discovery and user journeys.")
            + _section("CONTEXT", "Cross-links reduce dead-ends and improve analysis flow between dashboards.")
            + _section("GOAL", "Judge link coverage, traversal usage, and concentration; score 1–5.")
            + _bullets("INSTRUCTIONS", [
                "Assess % dashboards with links and link_usage.",
                "Flag skew if a few dashboards account for most traversals.",
            ])
            + _section("INPUT DESCRIPTIONS",
                "- dashboards[]:\n"
                "  • links[]: IDs of target dashboards\n"
                "  • link_usage: traversal/click count"
            )
            + _bullets("RUBRIC — How inputs affect score", [
                "5: ≥60% dashboards linked; high traversal; broad spread (no heavy skew).",
                "4: 45–59% linked with moderate traversal.",
                "3: 30–44% or usage concentrated on few nodes.",
                "2: 15–29% linked.",
                "1: <15% linked or negligible traversal.",
            ])
            + _section("RESPONSE FORMAT (JSON ONLY)", UNIVERSAL_RESPONSE_FORMAT)
        ),
        "example_input": {
            "dashboards": [
                {"id": "d1", "links": ["d2"], "link_usage": 15},
                {"id": "d2", "links": [], "link_usage": 0}
            ]
        },
        "input_key_meanings": {
            "dashboards": "Dashboards with 'links' array and 'link_usage' counter",
            "dashboards[].links": "Target dashboard IDs",
            "dashboards[].link_usage": "Clicks or traversals over period"
        },
        "response_format": UNIVERSAL_RESPONSE_FORMAT,
        "example_output": {
            "metric_id": "features.cross_links",
            "band": 3,
            "rationale": "~1/3 of dashboards are linked; usage is moderate but uneven.",
            "flags": ["distribution_skewed"],
            "gaps": [
                "Distribution uneven → raise link enablement and usage across low-adoption BUs → reach ≥45% dashboards with links and balanced usage (unlocks band 4)."
            ]
        }
    },

    # 7) Governance coverage
    "governance.coverage": {
        "system": (
            _section("ROLE", "Governance and stewardship reviewer.")
            + _section("CONTEXT", "Certification, clear owners, and complete metadata underpin trust.")
            + _section("GOAL", "Describe coverage, highlight owner & metadata gaps; score 1–5.")
            + _bullets("INSTRUCTIONS", [
                "Weigh owner and certification higher than minor metadata fields.",
                "Explicitly call out missing owner/lineage as critical gaps.",
            ])
            + _section("INPUT DESCRIPTIONS",
                "- dashboards[]:\n"
                "  • certified (bool)\n"
                "  • owner (str/None)\n"
                "  • metadata[]: list of fields present (e.g., description, SLA, lineage, glossary)"
            )
            + _bullets("RUBRIC — How inputs affect score", [
                "5: ≥95% certified & owned with complete metadata (incl. lineage).",
                "4: 85–94% coverage; minor metadata gaps.",
                "3: 70–84% coverage; noticeable metadata gaps.",
                "2: 50–69% coverage OR many owners missing.",
                "1: <50% coverage OR widespread lack of owners.",
            ])
            + _section("RESPONSE FORMAT (JSON ONLY)", UNIVERSAL_RESPONSE_FORMAT)
        ),
        "example_input": {
            "dashboards": [
                {"id": "d1", "certified": True, "owner": "teamA", "metadata": ["description", "refresh_rate"]},
                {"id": "d2", "certified": False, "owner": None, "metadata": []}
            ]
        },
        "input_key_meanings": {
            "dashboards": "Certification/owner/metadata flags per dashboard",
            "dashboards[].metadata": "List of metadata fields present"
        },
        "response_format": UNIVERSAL_RESPONSE_FORMAT,
        "example_output": {
            "metric_id": "governance.coverage",
            "band": 3,
            "rationale": "Owners assigned on most assets; incomplete metadata limits quality.",
            "flags": ["metadata_gaps"],
            "gaps": [
                "Metadata incomplete → enforce template (description, owner, SLA, lineage) → reach ≥85% full profiles (unlocks band 4)."
            ]
        }
    },

    # 8) Data source diversity
    "data.source_diversity": {
        "system": (
            _section("ROLE", "Platform breadth reviewer with domain coverage lens.")
            + _section("CONTEXT", "Variety across domains (ERP/CRM/Support/etc.) reduces blind spots and vendor risk.")
            + _section("GOAL", "Assess source count and domain balance; score 1–5.")
            + _bullets("INSTRUCTIONS", [
                "Consider both number of sources and diversity of domains.",
                "If domain tags are missing, mark it as a gap and score conservatively.",
            ])
            + _section("INPUT DESCRIPTIONS",
                "- source_catalog[]: distinct upstream systems (warehouse/DB/SaaS/etc.)."
            )
            + _bullets("RUBRIC — How inputs affect score", [
                "5: ≥8 sources across ≥3 domains with recent additions.",
                "4: 6–7 sources across ≥3 domains.",
                "3: 4–5 sources or only 2 domains.",
                "2: 2–3 sources within 1–2 domains.",
                "1: Single source or unknown variety.",
            ])
            + _section("RESPONSE FORMAT (JSON ONLY)", UNIVERSAL_RESPONSE_FORMAT)
        ),
        "example_input": {"source_catalog": ["Snowflake", "Postgres", "Salesforce"]},
        "input_key_meanings": {
            "source_catalog": "Distinct source systems (warehouse/DB/SaaS/etc.)"
        },
        "response_format": UNIVERSAL_RESPONSE_FORMAT,
        "example_output": {
            "metric_id": "data.source_diversity",
            "band": 3,
            "rationale": "Three sources suggest some variety; unclear domain coverage restricts score.",
            "flags": ["domain_mix_unknown"],
            "gaps": [
                "Domain mix unknown → tag each source to domain (ERP/CRM/Support) → show ≥3 domains represented (unlocks band 4)."
            ]
        }
    },

    # 9) Self-service adoption
    "democratization.self_service": {
        "system": (
            _section("ROLE", "Adoption & enablement reviewer.")
            + _section("CONTEXT", "Creator share + breadth + momentum indicate self-service maturity.")
            + _section("GOAL", "Explain adoption posture and missing proof points; score 1–5.")
            + _bullets("INSTRUCTIONS", [
                "Estimate creator% among actives from user_roles.",
                "Discuss breadth via dept_map if present; comment on momentum if trend data exists.",
            ])
            + _section("INPUT DESCRIPTIONS",
                "- user_roles[]: {id, role='creator'|'viewer'}.\n"
                "- dept_map {user_id->department}: optional breadth evidence."
            )
            + _bullets("RUBRIC — How inputs affect score", [
                "5: ≥35% creators with broad, growing footprint across departments.",
                "4: 25–34% creators; breadth fair, some signs of growth.",
                "3: 15–24% creators OR breadth unknown.",
                "2: 8–14% creators.",
                "1: <8% creators or roles unknown.",
            ])
            + _section("RESPONSE FORMAT (JSON ONLY)", UNIVERSAL_RESPONSE_FORMAT)
        ),
        "example_input": {
            "user_roles": [{"id": "u1", "role": "creator"}, {"id": "u2", "role": "viewer"}],
            "dept_map": {"u1": "Finance", "u2": "Ops"}
        },
        "input_key_meanings": {
            "user_roles": "Users and their roles ('creator'/'viewer')",
            "dept_map": "Optional mapping user->department for coverage"
        },
        "response_format": UNIVERSAL_RESPONSE_FORMAT,
        "example_output": {
            "metric_id": "democratization.self_service",
            "band": 3,
            "rationale": "Creator share ~22% shows traction; unclear growth and department breadth cap it.",
            "flags": ["growth_unknown", "coverage_unknown"],
            "gaps": [
                "Growth and breadth unclear → add 3-month creator trend + creators per department → reach ≥25% creators with ≥3 BUs active (unlocks band 4)."
            ]
        }
    },

    # 10) Decision traceability
    "decision.traceability": {
        "system": (
            _section("ROLE", "Decision hygiene reviewer emphasizing evidence-based practice.")
            + _section("CONTEXT", "Decisions should reference dashboards with evidence and be recent.")
            + _section("GOAL", "Summarize traceability coverage and recency; score 1–5.")
            + _bullets("INSTRUCTIONS", [
                "Compute/estimate % decisions with linked dashboards + evidence.",
                "Emphasize last 30–60d coverage; if unclear, mark a gap.",
            ])
            + _section("INPUT DESCRIPTIONS",
                "- decision_logs[]:\n"
                "  • linked_dash (optional)\n"
                "  • evidence (screenshot/URL/etc.)\n"
                "  • date (ISO)"
            )
            + _bullets("RUBRIC — How inputs affect score", [
                "5: ≥70% recent decisions (≤60d) are linked with strong evidence.",
                "4: 55–69% linked with evidence.",
                "3: 35–54% or evidence mixed; recency partial.",
                "2: 15–34% linked.",
                "1: <15% or evidence absent.",
            ])
            + _section("RESPONSE FORMAT (JSON ONLY)", UNIVERSAL_RESPONSE_FORMAT)
        ),
        "example_input": {
            "decision_logs": [
                {"id": "dec1", "linked_dash": "sales_forecast", "evidence": "screenshot", "date": "2025-07-25"},
                {"id": "dec2", "linked_dash": None, "evidence": None, "date": "2025-07-10"}
            ]
        },
        "input_key_meanings": {
            "decision_logs": "Decisions with optional dashboard references and evidence markers",
            "decision_logs[].date": "Used to judge recency/freshness of decisions"
        },
        "response_format": UNIVERSAL_RESPONSE_FORMAT,
        "example_output": {
            "metric_id": "decision.traceability",
            "band": 3,
            "rationale": "About half of decisions reference dashboards; evidence exists but recency is mixed.",
            "flags": ["recency_mixed"],
            "gaps": [
                "Coverage unclear → compute exact % decisions linked with evidence in last 30–60d → achieve ≥55% recent linked decisions (unlocks band 4)."
            ]
        }
    },

    # 11) Weekly active trend (4w)
    "usage.weekly_active_trend": {
        "system": (
            _section("ROLE", "Adoption trend analyst.")
            + _section("CONTEXT", "Four ISO weeks reveal momentum (growth/flat/decline).")
            + _section("GOAL", "Characterize WAU trajectory and reliability; score 1–5.")
            + _bullets("INSTRUCTIONS", [
                "Bucket events to ISO weeks via ts and 'today'.",
                "State sample/coverage caveats and seasonality.",
            ])
            + _section("INPUT DESCRIPTIONS",
                "- today (YYYY-MM-DD): anchor for week windows.\n"
                "- activity_events[]: ts + user_id to compute distinct WAU per week."
            )
            + _bullets("RUBRIC — How inputs affect score", [
                "5: clear consistent growth across 4 weeks; sample adequate each week.",
                "4: mild growth or high-level stability.",
                "3: flat with noise; no material drop; some sample caveats.",
                "2: sustained decline.",
                "1: sharp drop or very low activity; evidence sparse.",
            ])
            + _section("RESPONSE FORMAT (JSON ONLY)", UNIVERSAL_RESPONSE_FORMAT)
        ),
        "example_input": {
            "today": "2025-08-21",
            "activity_events": [
                {"ts": "2025-08-21T09:00:00Z", "user_id": "u1", "action": "view"},
                {"ts": "2025-08-05T10:00:00Z", "user_id": "u2", "action": "view"}
            ]
        },
        "input_key_meanings": {
            "today": "ISO date used to bucket events into ISO weeks",
            "activity_events": "Events with ts + user_id to compute distinct WAU per week"
        },
        "response_format": UNIVERSAL_RESPONSE_FORMAT,
        "example_output": {
            "metric_id": "usage.weekly_active_trend",
            "band": 4,
            "rationale": "WAU shows mild week-over-week growth; lack of denominators per week limits certainty.",
            "flags": ["denominator_unknown"],
            "gaps": [
                "Denominators unknown → provide WAU counts + total actives per week for last 4 weeks → verify consistent growth (solidifies band 4–5)."
            ]
        }
    },

    # 12) 4-week retention
    "usage.retention_4w": {
        "system": (
            _section("ROLE", "Retention analyst focusing on cohort behavior.")
            + _section("CONTEXT", "Measures % of week-1 actives who return in weeks 2–4.")
            + _section("GOAL", "Explain retention posture and key gaps; score 1–5.")
            + _bullets("INSTRUCTIONS", [
                "Identify week-1 cohort and returns in weeks 2–4 from activity_events.",
                "If persona/BU splits exist, reference them; otherwise mark a gap.",
            ])
            + _section("INPUT DESCRIPTIONS",
                "- today (YYYY-MM-DD): anchor.\n"
                "- activity_events[]: ts + user_id for cohorting and returns."
            )
            + _bullets("RUBRIC — How inputs affect score", [
                "5: ≥60% retention with clear cohort evidence.",
                "4: 45–59% with stable returning patterns.",
                "3: 30–44% or cohort composition unknown.",
                "2: 15–29% retention.",
                "1: <15% or evidence too sparse.",
            ])
            + _section("RESPONSE FORMAT (JSON ONLY)", UNIVERSAL_RESPONSE_FORMAT)
        ),
        "example_input": {
            "today": "2025-08-21",
            "activity_events": [
                {"ts":"2025-08-01T10:00:00Z","user_id":"u1","action":"view"},
                {"ts":"2025-08-15T09:00:00Z","user_id":"u1","action":"view"}
            ]
        },
        "input_key_meanings": {
            "today": "Reference date",
            "activity_events": "Distinct users by ISO week to compute returns for W2–W4"
        },
        "response_format": UNIVERSAL_RESPONSE_FORMAT,
        "example_output": {
            "metric_id": "usage.retention_4w",
            "band": 3,
            "rationale": "Retention ~35% is moderate; absence of cohort split by persona limits insight.",
            "flags": ["cohort_mix_unknown"],
            "gaps": [
                "Cohort composition unknown → report cohort size and retention by persona/BU → reach ≥45% overall with clear segment drivers (unlocks band 4)."
            ]
        }
    },

    # 13) Export / download rate (egress)
    "features.export_rate": {
        "system": (
            _section("ROLE", "Egress and offline-use reviewer with governance lens.")
            + _section("CONTEXT", "Exports imply data leaving governed surfaces; policy coverage matters.")
            + _section("GOAL", "Explain egress posture and governance clarity; score 1–5.")
            + _bullets("INSTRUCTIONS", [
                "Approximate export session share via 'export'/'download' actions.",
                "Discuss governance (policy enforcement, exception rate); if unknown, mark a gap.",
            ])
            + _section("INPUT DESCRIPTIONS",
                "- activity_events[]: actions including 'export'/'download' to infer egress share."
            )
            + _bullets("RUBRIC — How inputs affect score", [
                "5: ≥30% exports with strong governance (policies enforced, low exceptions).",
                "4: 20–29% with decent governance.",
                "3: 10–19% or governance unclear.",
                "2: 5–9% exports; weak governance.",
                "1: <5% or no meaningful evidence.",
            ])
            + _section("RESPONSE FORMAT (JSON ONLY)", UNIVERSAL_RESPONSE_FORMAT)
        ),
        "example_input": {
            "activity_events": [
                {"ts":"2025-08-21T09:00:00Z","user_id":"u1","action":"export"},
                {"ts":"2025-08-21T09:05:00Z","user_id":"u2","action":"view"}
            ]
        },
        "input_key_meanings": {
            "activity_events": "Session-level actions; 'export'/'download' indicate file egress"
        },
        "response_format": UNIVERSAL_RESPONSE_FORMAT,
        "example_output": {
            "metric_id": "features.export_rate",
            "band": 2,
            "rationale": "Exports near 8% indicate low offline usage; policy coverage for exports is unknown.",
            "flags": ["governance_unknown"],
            "gaps": [
                "Export governance unknown → add policy enforcement status + exception rate → demonstrate ≥95% governed exports (unlocks band 4–5)."
            ]
        }
    },

    # 14) Alerts / subscriptions usage
    "features.alerts_usage": {
        "system": (
            _section("ROLE", "Operationalization reviewer for push analytics.")
            + _section("CONTEXT", "Alerts/subscriptions move insights into workflows; delivery reliability matters.")
            + _section("GOAL", "Describe adoption breadth and delivery success; score 1–5.")
            + _bullets("INSTRUCTIONS", [
                "Identify alert/subscription events; estimate unique users and BU spread.",
                "Call out delivery reliability if failures/bounces are present; otherwise mark gap.",
            ])
            + _section("INPUT DESCRIPTIONS",
                "- activity_events[]: 'alert_*' and 'subscription_*' actions."
            )
            + _bullets("RUBRIC — How inputs affect score", [
                "5: Broad adoption across BUs with high delivery success.",
                "4: Moderate adoption; mostly successful deliveries.",
                "3: Limited adoption; breadth unclear.",
                "2: Very low adoption.",
                "1: Near zero or no evidence.",
            ])
            + _section("RESPONSE FORMAT (JSON ONLY)", UNIVERSAL_RESPONSE_FORMAT)
        ),
        "example_input": {
            "activity_events": [
                {"ts":"2025-08-21T07:00:00Z","user_id":"u1","action":"alert_delivered"},
                {"ts":"2025-08-21T07:00:01Z","user_id":"u2","action":"subscription_email"}
            ]
        },
        "input_key_meanings": {
            "activity_events": "'alert_*' and 'subscription_*' actions to infer adoption and delivery"
        },
        "response_format": UNIVERSAL_RESPONSE_FORMAT,
        "example_output": {
            "metric_id": "features.alerts_usage",
            "band": 3,
            "rationale": "Meaningful but small cohort uses alerts; delivery looks reliable but BU spread is unknown.",
            "flags": ["coverage_unknown"],
            "gaps": [
                "BU spread unknown → count unique alert/subscription users per BU and delivery success → reach moderate adoption across ≥3 BUs (unlocks band 4)."
            ]
        }
    },

    # 15) SLA breach streaks
    "reliability.sla_breach_streaks": {
        "system": (
            _section("ROLE", "Reliability analyst focusing on chronicity and impact.")
            + _section("CONTEXT", "Consecutive SLA breaches erode trust, especially for critical assets.")
            + _section("GOAL", "Characterize streak length and concentration; score 1–5.")
            + _bullets("INSTRUCTIONS", [
                "Reconstruct breach streaks from last_refresh vs SLA.",
                "Weigh priority=high dashboards more in reasoning.",
                "If max/median streaks are unknown, record a gap.",
            ])
            + _section("INPUT DESCRIPTIONS",
                "- dashboards[]: {last_refresh, sla, priority}.\n"
                "- today (YYYY-MM-DD): reference date."
            )
            + _bullets("RUBRIC — How inputs affect score", [
                "5: Zero breaches on critical dashboards; very short/none elsewhere.",
                "4: Rare/short breaches, low impact.",
                "3: Occasional moderate streaks.",
                "2: Frequent or long streaks.",
                "1: Chronic breaches or insufficient evidence.",
            ])
            + _section("RESPONSE FORMAT (JSON ONLY)", UNIVERSAL_RESPONSE_FORMAT)
        ),
        "example_input": {
            "dashboards": [
                {"id":"d1","last_refresh":"2025-08-21","sla":"daily","priority":"high"},
                {"id":"d2","last_refresh":"2025-08-15","sla":"daily","priority":"high"}
            ],
            "today": "2025-08-21"
        },
        "input_key_meanings": {
            "dashboards[].last_refresh": "Used with SLA to compute breach streak length",
            "dashboards[].priority": "High/medium/low to identify critical breaches",
            "today": "Reference date"
        },
        "response_format": UNIVERSAL_RESPONSE_FORMAT,
        "example_output": {
            "metric_id": "reliability.sla_breach_streaks",
            "band": 4,
            "rationale": "Only brief breaches observed; absence of streak length distribution limits certainty.",
            "flags": ["streak_tail_unknown"],
            "gaps": [
                "Streak tail unknown → provide max/median breach days and count on high-priority dashboards → keep max streak at 0 for critical assets (unlocks band 5)."
            ]
        }
    },

    # 16) Query/visual error rate
    "reliability.error_rate_queries": {
        "system": (
            _section("ROLE", "Runtime stability reviewer considering both frequency and impact.")
            + _section("CONTEXT", "Low error rates can mask high-impact incidents; severity matters.")
            + _section("GOAL", "Explain observed error posture and missing impact data; score 1–5.")
            + _bullets("INSTRUCTIONS", [
                "Approximate error rate from 'error' actions vs total activity when feasible.",
                "Call out severity/affected-users if available; otherwise record as a gap.",
            ])
            + _section("INPUT DESCRIPTIONS",
                "- activity_events[]: contains 'error' when failures happen; other actions provide denominator."
            )
            + _bullets("RUBRIC — How inputs affect score", [
                "5: <0.1% errors and no Sev1/Sev2 incidents.",
                "4: 0.1–0.5% errors with low impact.",
                "3: 0.5–1.5% or impact unknown.",
                "2: 1.5–3% or occasional higher-impact failures.",
                "1: >3% or repeated high-impact issues.",
            ])
            + _section("RESPONSE FORMAT (JSON ONLY)", UNIVERSAL_RESPONSE_FORMAT)
        ),
        "example_input": {
            "activity_events": [
                {"ts":"2025-08-21T09:00:00Z","user_id":"u1","action":"error"},
                {"ts":"2025-08-21T09:01:00Z","user_id":"u2","action":"view"}
            ]
        },
        "input_key_meanings": {
            "activity_events": "'error' actions approximate query/visualization failures; consider volume for rate"
        },
        "response_format": UNIVERSAL_RESPONSE_FORMAT,
        "example_output": {
            "metric_id": "reliability.error_rate_queries",
            "band": 4,
            "rationale": "Estimated error rate is low; lack of incident severity data prevents a 5.",
            "flags": ["impact_unknown"],
            "gaps": [
                "Incident impact unknown → attach severity and affected-user counts for each incident → show no Sev1/Sev2 in last 30d (unlocks band 5)."
            ]
        }
    },

    # 17) PII coverage
    "governance.pii_coverage": {
        "system": (
            _section("ROLE", "Data protection reviewer focusing on labeling and access control.")
            + _section("CONTEXT", "Consistent PII tagging + enforced access policies reduce regulatory risk.")
            + _section("GOAL", "Describe coverage and hotspots; score 1–5.")
            + _bullets("INSTRUCTIONS", [
                "Look for explicit PII tags and access policy presence; call out missing controls.",
            ])
            + _section("INPUT DESCRIPTIONS",
                "- dashboards[]:\n"
                "  • metadata[] includes 'pii' and/or 'access_policy' when present\n"
                "  • certified/owner (optional) useful context"
            )
            + _bullets("RUBRIC — How inputs affect score", [
                "5: Comprehensive labeling and enforced access policies across estate.",
                "4: Strong coverage; minor gaps.",
                "3: Partial coverage; inconsistent controls.",
                "2: Many gaps; weak control posture.",
                "1: Poor or absent labeling/policy evidence.",
            ])
            + _section("RESPONSE FORMAT (JSON ONLY)", UNIVERSAL_RESPONSE_FORMAT)
        ),
        "example_input": {
            "dashboards": [
                {"id":"d1","certified":True,"owner":"fin","metadata":["description","pii","access_policy"]},
                {"id":"d2","certified":False,"owner":None,"metadata":[]}
            ]
        },
        "input_key_meanings": {
            "dashboards": "Governance signals per asset",
            "dashboards[].metadata": "Presence of 'pii'/'access_policy' used as proxy"
        },
        "response_format": UNIVERSAL_RESPONSE_FORMAT,
        "example_output": {
            "metric_id": "governance.pii_coverage",
            "band": 3,
            "rationale": "Key assets appear labeled; inconsistent coverage across estate limits score.",
            "flags": ["coverage_inconsistent"],
            "gaps": [
                "Coverage inconsistent → roll out automated PII detection + policy tagging → reach ≥85% assets with PII tag and enforced access policy (unlocks band 4)."
            ]
        }
    },

    # 18) Lineage / owner documentation
    "governance.lineage_coverage": {
        "system": (
            _section("ROLE", "Documentation hygiene reviewer.")
            + _section("CONTEXT", "Owners, lineage, and glossary improve auditability and reuse.")
            + _section("GOAL", "Explain coverage posture and most consequential gaps; score 1–5.")
            + _bullets("INSTRUCTIONS", [
                "Call out owner gaps separately from lineage/glossary gaps.",
                "Request precise coverage when unknown.",
            ])
            + _section("INPUT DESCRIPTIONS",
                "- dashboards[]:\n"
                "  • owner (str/None)\n"
                "  • metadata[] includes 'lineage' and/or 'glossary'"
            )
            + _bullets("RUBRIC — How inputs affect score", [
                "5: Near-complete coverage across estate (owners + lineage/glossary).",
                "4: Strong with minor holes.",
                "3: Moderate coverage; noticeable gaps.",
                "2: Sparse documentation.",
                "1: Minimal or unclear evidence.",
            ])
            + _section("RESPONSE FORMAT (JSON ONLY)", UNIVERSAL_RESPONSE_FORMAT)
        ),
        "example_input": {
            "dashboards": [
                {"id":"d1","owner":"bi_ops","metadata":["lineage","glossary"]},
                {"id":"d2","owner":None,"metadata":[]}
            ]
        },
        "input_key_meanings": {
            "dashboards": "Ownership + metadata proxies for lineage/glossary completeness"
        },
        "response_format": UNIVERSAL_RESPONSE_FORMAT,
        "example_output": {
            "metric_id": "governance.lineage_coverage",
            "band": 3,
            "rationale": "Lineage documented on a subset; owner gaps limit confidence.",
            "flags": ["owner_missing"],
            "gaps": [
                "Owners/lineage missing on many assets → enforce owner assignment and lineage links → achieve ≥85% coverage (unlocks band 4)."
            ]
        }
    },

    # 19) Cost efficiency
    "data.cost_efficiency": {
        "system": (
            _section("ROLE", "Cost posture reviewer balancing efficiency and waste signals.")
            + _section("CONTEXT", "Healthy source mix + low egress + minimal staleness → efficient posture.")
            + _section("GOAL", "Synthesize efficiency posture; list positives and limiters; score 1–5.")
            + _bullets("INSTRUCTIONS", [
                "Balance source diversity (healthy) vs egress (exports) and stale refresh (waste).",
                "Request specifics when partial evidence.",
            ])
            + _section("INPUT DESCRIPTIONS",
                "- source_catalog[]: architectural breadth.\n"
                "- activity_events[]: 'export'/'download' as egress proxy.\n"
                "- dashboards[]: staleness via last_refresh vs SLA."
            )
            + _bullets("RUBRIC — How inputs affect score", [
                "5: Strong platform mix, low egress, minimal staleness (esp. on critical assets).",
                "4: Minor inefficiencies (some egress or a small stale set).",
                "3: Mixed signals (diversity OK but egress/stales present).",
                "2: Inefficient: heavy egress and/or many stale assets.",
                "1: Wasteful posture across dimensions; unclear evidence.",
            ])
            + _section("RESPONSE FORMAT (JSON ONLY)", UNIVERSAL_RESPONSE_FORMAT)
        ),
        "example_input": {
            "source_catalog": ["Snowflake","BigQuery","Salesforce"],
            "activity_events": [{"ts":"2025-08-21T09:00:00Z","user_id":"u1","action":"export"}],
            "dashboards": [{"id":"d1","last_refresh":"2025-07-01","sla":"monthly"}]
        },
        "input_key_meanings": {
            "source_catalog": "Warehouse/DB/SaaS balance",
            "activity_events": "Exports as proxy for data egress",
            "dashboards": "Stale content as proxy for wasted refresh"
        },
        "response_format": UNIVERSAL_RESPONSE_FORMAT,
        "example_output": {
            "metric_id": "data.cost_efficiency",
            "band": 3,
            "rationale": "Diverse sources but moderate egress and some staleness create mixed efficiency.",
            "flags": ["egress_present","stale_assets_present"],
            "gaps": [
                "Egress and staleness present → quantify export session % and stale share by priority → reduce exports <15% and stale critical assets to 0 (unlocks band 4–5)."
            ]
        }
    },

    # 20) Department coverage (creators per dept)
    "democratization.dept_coverage": {
        "system": (
            _section("ROLE", "Org-wide empowerment reviewer.")
            + _section("CONTEXT", "Creators present across departments indicate sustainable democratization.")
            + _section("GOAL", "Describe breadth of creator presence and blind spots; score 1–5.")
            + _bullets("INSTRUCTIONS", [
                "Compute/estimate % departments with ≥1 creator using user_directory if available.",
                "If denominator (total departments) is unknown, ask for it and score cautiously.",
            ])
            + _section("INPUT DESCRIPTIONS",
                "- user_roles[]: identify creators\n"
                "- user_directory[]: {user_id, department} mapping for coverage"
            )
            + _bullets("RUBRIC — How inputs affect score", [
                "5: ≥80% departments have ≥1 creator (denominator clear).",
                "4: 60–79% coverage, or strong evidence of breadth.",
                "3: 40–59% or denominator unknown.",
                "2: 20–39% coverage.",
                "1: <20% or no breadth evidence.",
            ])
            + _section("RESPONSE FORMAT (JSON ONLY)", UNIVERSAL_RESPONSE_FORMAT)
        ),
        "example_input": {
            "user_roles": [{"id":"u1","role":"creator"},{"id":"u2","role":"viewer"}],
            "user_directory": [{"user_id":"u1","department":"Finance"},{"user_id":"u2","department":"Ops"}]
        },
        "input_key_meanings": {
            "user_roles": "Role mapping to identify creators",
            "user_directory": "Map users to departments for coverage calculation"
        },
        "response_format": UNIVERSAL_RESPONSE_FORMAT,
        "example_output": {
            "metric_id": "democratization.dept_coverage",
            "band": 4,
            "rationale": "Creators appear in most departments; lack of distinct creator counts by dept limits certainty.",
            "flags": ["creator_counts_unknown"],
            "gaps": [
                "Per-dept counts unknown → publish creators per department and total departments considered → reach ≥80% dept coverage (unlocks band 5)."
            ]
        }
    }
}

# ---------------------------------------------------------------------------
# Prompt builder (kept compatible with your pipeline)
# ---------------------------------------------------------------------------

def build_prompt(metric_id: str, task_input: dict) -> str:
    meta = METRIC_PROMPTS.get(metric_id)
    if not meta:
        raise ValueError(f"Unknown metric_id: {metric_id}")
    meanings = meta.get("input_key_meanings", {})
    key_meanings_str = "\n".join([f"- {k}: {v}" for k, v in meanings.items()]) if meanings else ""
    improvement_block = (
        "IMPROVEMENT GUIDANCE EXAMPLES:\n- "
        + "\n- ".join(IMPROVEMENT_GUIDANCE_EXAMPLES)
        + "\n\n"
    )
    return (
        f"SYSTEM:\n{meta['system']}\n"
        f"INPUT JSON KEYS AND MEANINGS:\n{key_meanings_str}\n\n"
        f"RESPONSE FORMAT (JSON only):\n{meta['response_format']}\n\n"
        f"{improvement_block}"
        f"TASK INPUT (USER EVIDENCE):\n{json.dumps(task_input, indent=2)}\n\n"
        f"EXAMPLE INPUT:\n{json.dumps(meta['example_input'], indent=2)}\n\n"
        f"EXAMPLE OUTPUT:\n{json.dumps(meta['example_output'], indent=2)}"
    )

# ---------------------------------------------------------------------------
# LLM wrapper — score-only normalization (no band in outputs)
# ---------------------------------------------------------------------------

class BIUsageLLM(BaseMicroAgent):
    def _ask(self, user_prompt: str, max_tokens: int = 800) -> Dict[str, Any]:
        time.sleep(random.uniform(0.02, 0.07))
        with timed("LLM.call"):
            raw = self._call_llm(system_prompt="", prompt=user_prompt, max_tokens=max_tokens)
        try:
            out = self._parse_json_response(raw) or {}
        except Exception:
            out = {}

        # Normalize to single score (1..5)
        try:
            score_val = out.get("score", out.get("band", 3))
            out["score"] = max(1, min(5, int(score_val)))
        except Exception:
            out["score"] = 3

        # Remove any band to avoid leaking it downstream
        if "band" in out:
            del out["band"]

        # Ensure required fields
        out.setdefault("rationale", "Strong signal; limited by missing supporting detail.")
        out.setdefault("flags", [])
        out.setdefault("gaps", [])
        out.setdefault("metric_id", "unknown.metric")

        return out

    def score_metric(self, metric_id: str, task_input: Dict[str, Any]) -> Dict[str, Any]:
        _ = METRIC_PROMPTS[metric_id]  # raises if unknown
        prompt = build_prompt(metric_id, task_input)

        #logger.debug(f"Built prompt for {metric_id} (len={len(prompt)})")

        with timed(f"metric.{metric_id}"):
            out = self._ask(prompt)
            out["metric_id"] = metric_id

        logger.info(f"[{metric_id}] score={out['score']}")
        # if out.get("flags"):
        #     logger.info(f"[{metric_id}] flags={out['flags']}")
        if out.get("gaps"):
            logger.info(f"[{metric_id}] gaps={out['gaps']}")
        return out

    # -------- metric helpers --------
    def score_dau_mau(self, activity_events: List[Dict[str, Any]], today: str) -> Dict[str, Any]:
        return self.score_metric("usage.dau_mau", {"activity_events": activity_events, "today": today})

    def score_active_creators(self, usage_logs: List[Dict[str, Any]], dept_map: Optional[Dict[str,str]]=None) -> Dict[str, Any]:
        payload: Dict[str,Any] = {"usage_logs": usage_logs}
        if dept_map is not None:
            payload["dept_map"] = dept_map
        return self.score_metric("usage.creators_ratio", payload)

    def score_session_depth(self, session_logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        return self.score_metric("usage.session_depth", {"session_logs": session_logs})

    def score_drilldown(self, interaction_logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        return self.score_metric("usage.drilldown", {"interaction_logs": interaction_logs})

    def score_refresh_timeliness(self, dashboards: List[Dict[str, Any]], today: str) -> Dict[str, Any]:
        return self.score_metric("reliability.refresh_timeliness", {"dashboards": dashboards, "today": today})

    def score_cross_links(self, link_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        return self.score_metric("features.cross_links", {"dashboards": link_data})

    def score_governance_coverage(self, gov: List[Dict[str, Any]]) -> Dict[str, Any]:
        return self.score_metric("governance.coverage", {"dashboards": gov})

    def score_source_diversity(self, sources: List[str]) -> Dict[str, Any]:
        return self.score_metric("data.source_diversity", {"source_catalog": sources})

    def score_self_service_adoption(self, user_roles: List[Dict[str, Any]], dept_map: Optional[Dict[str,str]]=None) -> Dict[str, Any]:
        payload: Dict[str,Any] = {"user_roles": user_roles}
        if dept_map is not None:
            payload["dept_map"] = dept_map
        return self.score_metric("democratization.self_service", payload)

    def score_decision_traceability(self, decision_logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        return self.score_metric("decision.traceability", {"decision_logs": decision_logs})

    def score_weekly_active_trend(self, activity_events: List[Dict[str, Any]], today: str) -> Dict[str, Any]:
        return self.score_metric("usage.weekly_active_trend", {"activity_events": activity_events, "today": today})

    def score_retention_4w(self, activity_events: List[Dict[str, Any]], today: str) -> Dict[str, Any]:
        return self.score_metric("usage.retention_4w", {"activity_events": activity_events, "today": today})

    def score_export_rate(self, activity_events: List[Dict[str, Any]]) -> Dict[str, Any]:
        return self.score_metric("features.export_rate", {"activity_events": activity_events})

    def score_alerts_usage(self, activity_events: List[Dict[str, Any]]) -> Dict[str, Any]:
        return self.score_metric("features.alerts_usage", {"activity_events": activity_events})

    def score_sla_breach_streaks(self, dashboards: List[Dict[str, Any]], today: str) -> Dict[str, Any]:
        return self.score_metric("reliability.sla_breach_streaks", {"dashboards": dashboards, "today": today})

    def score_error_rate_queries(self, activity_events: List[Dict[str, Any]]) -> Dict[str, Any]:
        return self.score_metric("reliability.error_rate_queries", {"activity_events": activity_events})

    def score_pii_coverage(self, gov_dashboards: List[Dict[str, Any]]) -> Dict[str, Any]:
        return self.score_metric("governance.pii_coverage", {"dashboards": gov_dashboards})

    def score_lineage_coverage(self, gov_dashboards: List[Dict[str, Any]]) -> Dict[str, Any]:
        return self.score_metric("governance.lineage_coverage", {"dashboards": gov_dashboards})

    def score_cost_efficiency(self, source_catalog: List[str], activity_events: List[Dict[str, Any]], dashboards: List[Dict[str, Any]]) -> Dict[str, Any]:
        return self.score_metric("data.cost_efficiency", {"source_catalog": source_catalog, "activity_events": activity_events, "dashboards": dashboards})

    def score_dept_coverage(self, user_roles: List[Dict[str, Any]], user_directory: List[Dict[str, Any]]) -> Dict[str, Any]:
        return self.score_metric("democratization.dept_coverage", {"user_roles": user_roles, "user_directory": user_directory})

    # Optional parity hook
    def evaluate(self, code_snippets: List[str], context: Optional[Dict] = None) -> Dict[str, Any]:
        return {"status": "ok"}