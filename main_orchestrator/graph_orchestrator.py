from __future__ import annotations
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from main_orchestrator import survey_recalibrator
from .feature_bus import FeatureBus, utc_iso
from .scoring import ScoringAgent
from .survey_recalibrator import Args as SRArgs, main_with_args as run_survey_recalibration
import os

@dataclass
class SurveyConfig:
    enabled: bool = True
    survey_path: Path | None = None
    yaml_paths: list[Path] = None
    existing_json: Path | None = None
    out_scores: Path | None = None
    out_audit: Path | None = None
    default_N: int = 5

AGENTS_LIST = [
    "cloud_infra",        # 6h
    "data_platform",      # 12h
    "ml_ops",             # 4h
    "bi_tracker",         # daily
    "enterprise_systems", # 8h
    "code_repo",          # daily
]

TRIGGER_K_OF_N = 1

def run_recalibration(
    survey_path: str = "./surveys/_Survey_QA_samples.yaml",
    yaml_paths: list[str] = [],
    existing_json: str = "./results/category_scores.json",
    out_scores: str = "./results/survey_metric_scores.json",
    out_audit: str = "./results/survey_recalibration_audit.json",
):
    args = survey_recalibrator.Args(
        survey=Path(survey_path),
        yamls=[Path(y) for y in yaml_paths],
        out_scores=Path(out_scores),
        out_audit=Path(out_audit),
        existing_json=Path(existing_json),
        default_N=5,
    )
    return survey_recalibrator.main_with_args(args)

@dataclass
class OrchestratorState:
    global_scores: Dict[str, float] = field(default_factory=dict)
    latest_sign_ts: Dict[str, Optional[str]] = field(default_factory=dict)
    updated_count: int = 0
    changed_agents: List[str] = field(default_factory=list)
    last_scored_ts: Optional[str] = None
    last_result: Optional[Dict[str, Any]] = None


class Orchestrator:
    def __init__(
        self,
        bus_root: str = "./bus",
        results_root: str = "./results",
        agents_root: str = "./orchestrator_output/agents",
        survey_config: SurveyConfig | None = None,   # <— NEW
    ):
        self.bus = FeatureBus(bus_root)
        self.results_root = Path(results_root)
        self.results_root.mkdir(parents=True, exist_ok=True)

        self.agents_root = Path(agents_root)
        self.agents_root.mkdir(parents=True, exist_ok=True)

        # NEW: configure survey from args or env
        self.survey_config = survey_config or self._load_survey_config_from_env()

        self.scorer = ScoringAgent(category_weights=None)
        self.graph = self._build_graph()

    def _load_survey_config_from_env(self) -> SurveyConfig:
        """Build SurveyConfig from environment variables (with sensible defaults)."""
        def _csv_paths(env_key: str) -> list[Path]:
            raw = os.getenv(env_key, "")
            parts = [p.strip() for p in raw.split(",") if p.strip()]
            return [Path(p) for p in parts]

        enabled = os.getenv("SURVEY_ENABLED", "true").lower() not in {"0", "false", "no"}
        survey_path = Path(os.getenv("SURVEY_FILE", "./surveys/_Survey_QA_samples.yaml"))
        yaml_paths  = _csv_paths("SURVEY_YAMLS") or [
            Path("./metric_descriptions/bi_tracker.yaml"),
            Path("./metric_descriptions/cloud_infra.yaml"),
            Path("./metric_descriptions/code_repo.yaml"),
            Path("./metric_descriptions/data_platform_scanner.yaml"),
            Path("./metric_descriptions/enterprise_system.yaml"),
            Path("./metric_descriptions/ml_ops.yaml"),
        ]

        # existing_json defaults to the file we write in persist_results
        existing_json = Path(os.getenv("SURVEY_EXISTING_JSON", str(self.results_root / "category_scores.json")))
        out_scores    = Path(os.getenv("SURVEY_OUT_SCORES", str(self.results_root / "survey_metric_scores.json")))
        out_audit     = Path(os.getenv("SURVEY_OUT_AUDIT",  str(self.results_root / "survey_recalibration_audit.json")))
        default_N     = int(os.getenv("SURVEY_DEFAULT_N", "5"))

        return SurveyConfig(
            enabled=enabled,
            survey_path=survey_path,
            yaml_paths=yaml_paths,
            existing_json=existing_json,
            out_scores=out_scores,
            out_audit=out_audit,
            default_N=default_N,
        )

    # ---- nodes ----
    def ingest_signs(self, state: OrchestratorState) -> OrchestratorState:
        latest, changed = dict(state.latest_sign_ts), []
        for a in AGENTS_LIST:
            ts = self.bus.read_sign_ts(a)
            if ts and (latest.get(a) is None or ts > latest.get(a)):
                latest[a] = ts
                changed.append(a)
        state.latest_sign_ts = latest
        state.changed_agents = changed
        state.updated_count = len(changed)
        return state

    def update_cache(self, state: OrchestratorState) -> OrchestratorState:
        scores = dict(state.global_scores)
        for a in state.changed_agents:
            frag = self.bus.read_scores(a)
            for k, v in frag.items():
                try:
                    scores[k] = float(v)
                except Exception:
                    pass
        state.global_scores = scores
        return state

    def should_score(self, state: OrchestratorState) -> str:
        return "do_score" if state.updated_count >= TRIGGER_K_OF_N else "skip"

    def score_agent(self, state: OrchestratorState) -> OrchestratorState:
        self.scorer = ScoringAgent()
        res = self.scorer.run(self.agents_root)
        state.last_result = res
        state.last_scored_ts = utc_iso()
        state.updated_count = 0
        state.changed_agents = []
        return state

    def persist_results(self, state: OrchestratorState) -> OrchestratorState:
        ts = state.last_scored_ts or utc_iso()
        out = {
            "ts": ts,
            "result": state.last_result or {},
            "latest_sign_ts": state.latest_sign_ts,
        }
        (self.results_root / f"scoring_{ts}.json").write_text(json.dumps(out, indent=2))
        (self.results_root / "latest_overall.json").write_text(
            json.dumps({"overall": out["result"].get("overall_score")}, indent=2)
        )
        (self.results_root / "category_scores.json").write_text(
            json.dumps(out["result"].get("category_scores", {}), indent=2)
        )

        # --- Survey recalibration (configurable) ---
        cfg = self.survey_config
        if cfg and cfg.enabled:
            sr_args = SRArgs(
                survey=cfg.survey_path,
                yamls=cfg.yaml_paths or [],
                existing_json=cfg.existing_json or (self.results_root / "category_scores.json"),
                out_scores=cfg.out_scores or (self.results_root / "survey_metric_scores.json"),
                out_audit=cfg.out_audit or (self.results_root / "survey_recalibration_audit.json"),
                default_N=cfg.default_N,
            )
            run_survey_recalibration(sr_args)

        return state

    # ---- graph ----
    def _build_graph(self):
        g = StateGraph(OrchestratorState)
        g.add_node("ingest_signs", self.ingest_signs)
        g.add_node("update_cache", self.update_cache)
        g.add_node("score_agent", self.score_agent)
        g.add_node("persist_results", self.persist_results)
        g.set_entry_point("ingest_signs")
        g.add_edge("ingest_signs", "update_cache")
        g.add_conditional_edges("update_cache", self.should_score, {"do_score": "score_agent", "skip": END})
        g.add_edge("score_agent", "persist_results")
        g.add_edge("persist_results", END)
        return g.compile(checkpointer=MemorySaver())

    # ---- one tick ----
    def tick(self, state: OrchestratorState, *, thread_id: str = "default") -> OrchestratorState:
        cfg = {"configurable": {"thread_id": thread_id}}
        return self.graph.invoke(state, config=cfg)