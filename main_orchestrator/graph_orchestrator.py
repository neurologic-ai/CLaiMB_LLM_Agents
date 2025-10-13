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
from .gap_summarizer import GapSummarizer
from .recommendation_generator import RecommendationGenerator
import os
import re

@dataclass
class SurveyConfig:
    enabled: bool = True
    survey_path: Path | None = None
    yaml_paths: list[Path] = None
    existing_json: Path | None = None
    out_scores: Path | None = None
    out_audit: Path | None = None
    default_N: int = 5

@dataclass
class GapSummarizerConfig:
    enabled: bool = True
    model: str = "gpt-3.5-turbo"

@dataclass
class RecommendationGeneratorConfig:
    enabled: bool = True
    model: str = "gpt-4-turbo-preview"  # Better model for strategic recommendations

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
        survey_config: SurveyConfig | None = None,
        gap_summarizer_config: GapSummarizerConfig | None = None,
        recommendation_generator_config: RecommendationGeneratorConfig | None = None,
    ):
        self.bus = FeatureBus(bus_root)
        self.results_root = Path(results_root)
        self.results_root.mkdir(parents=True, exist_ok=True)

        self.agents_root = Path(agents_root)
        self.agents_root.mkdir(parents=True, exist_ok=True)

        # Configure survey from args or env
        self.survey_config = survey_config or self._load_survey_config_from_env()
        
        # Configure gap summarizer from args or env
        self.gap_summarizer_config = gap_summarizer_config or self._load_gap_summarizer_config_from_env()
        
        # Configure recommendation generator from args or env
        self.recommendation_generator_config = recommendation_generator_config or self._load_recommendation_generator_config_from_env()

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
    
    def _load_gap_summarizer_config_from_env(self) -> GapSummarizerConfig:
        """Build GapSummarizerConfig from environment variables."""
        enabled = os.getenv("GAP_SUMMARIZER_ENABLED", "true").lower() not in {"0", "false", "no"}
        model = os.getenv("GAP_SUMMARIZER_MODEL", "gpt-3.5-turbo")
        return GapSummarizerConfig(
            enabled=enabled,
            model=model,
        )
    
    def _load_recommendation_generator_config_from_env(self) -> RecommendationGeneratorConfig:
        """Build RecommendationGeneratorConfig from environment variables."""
        enabled = os.getenv("RECOMMENDATION_GENERATOR_ENABLED", "true").lower() not in {"0", "false", "no"}
        model = os.getenv("RECOMMENDATION_GENERATOR_MODEL", "gpt-4-turbo-preview")
        
        return RecommendationGeneratorConfig(
            enabled=enabled,
            model=model,
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
        # Save gap aggregation results
        (self.results_root / "category_gaps.json").write_text(
            json.dumps(out["result"].get("category_gaps", {}), indent=2)
        )
        
        # Generate comprehensive AIMRI structure with subsections
        self._generate_aimri_structure(out["result"])

        # --- Gap Summarizer (configurable) ---
        gap_cfg = self.gap_summarizer_config
        if gap_cfg and gap_cfg.enabled:
            try:
                print("▶ Running Gap Summarizer...")
                summarizer = GapSummarizer(model=gap_cfg.model)
                
                # Generate summaries for all categories
                gap_summaries = summarizer.summarize_all_categories(
                    save_output=True,
                    output_path=self.results_root / "gap_summaries.json"
                )
                
                print("✅ Gap Summarizer complete")
            except Exception as e:
                print(f"⚠️ Gap Summarizer failed: {e}")
                # Continue execution even if gap summarizer fails
        
        # --- Recommendation Generator (configurable) ---
        rec_cfg = self.recommendation_generator_config
        if rec_cfg and rec_cfg.enabled:
            try:
                print("▶ Running Recommendation Generator...")
                generator = RecommendationGenerator(model=rec_cfg.model)
                
                # Generate prioritized recommendations
                recommendations = generator.generate_recommendations(
                    save_output=True,
                    output_path=self.results_root / "prioritized_recommendations.json"
                )
                print("✅ Recommendation Generator complete")
            except Exception as e:
                print(f"⚠️ Recommendation Generator failed: {e}")
                # Continue execution even if recommendation generator fails

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

    def _generate_aimri_structure(self, result: Dict[str, Any]):
        """Generate comprehensive AIMRI structure with all 15 categories and their subsections."""
        # Load AIMRI canonical structure
        aimri_json_path = Path(__file__).parent / "aimri.json"
        try:
            with open(aimri_json_path, 'r') as f:
                aimri_canonical = json.load(f)
                aimri_points = aimri_canonical.get("aimri_points", [])
        except Exception:
            aimri_points = []
        
        # Build category to subsections mapping
        category_subsections_map = {}
        for point in aimri_points:
            cat = point.get("category")
            subsection_id = point.get("id")
            subsection_name = point.get("name")
            
            # Find matching category with number prefix
            for cat_key in ["01. Technical Infrastructure", "02. Data Management & Quality", 
                           "03. AI/ML Capabilities", "04. Talent & Skills", "05. Governance & Ethics",
                           "06. Strategic Alignment", "07. Cultural Readiness", "08. Process Maturity",
                           "09. Foundation Model Operations", "10. Generative AI Capabilities",
                           "11. Responsible AI & Social Impact", "12. AI Business Value & ROI",
                           "13. AI Risk & Resilience", "14. AI Ecosystem & External Integration",
                           "15. AI Leadership & Vision"]:
                if cat in cat_key:
                    if cat_key not in category_subsections_map:
                        category_subsections_map[cat_key] = []
                    category_subsections_map[cat_key].append({
                        "id": subsection_id,
                        "name": subsection_name,
                        "full_name": f"{subsection_id} {subsection_name}"
                    })
                    break
        
        # Get data from result details
        details = result.get("details", {})
        score_subsections = details.get("subsections", {})
        gap_subsections = details.get("gap_subsections", {})
        category_scores = result.get("category_scores", {})
        category_gaps = result.get("category_gaps", {})
        
        # Build comprehensive structure
        aimri_data = {}
        
        # All AIMRI categories
        ALL_CATEGORIES = [
            "01. Technical Infrastructure",
            "02. Data Management & Quality",
            "03. AI/ML Capabilities",
            "04. Talent & Skills",
            "05. Governance & Ethics",
            "06. Strategic Alignment",
            "07. Cultural Readiness",
            "08. Process Maturity",
            "09. Foundation Model Operations",
            "10. Generative AI Capabilities",
            "11. Responsible AI & Social Impact",
            "12. AI Business Value & ROI",
            "13. AI Risk & Resilience",
            "14. AI Ecosystem & External Integration",
            "15. AI Leadership & Vision"
        ]
        
        # Process each category
        for category in ALL_CATEGORIES:
            # Get category-level data
            category_score = category_scores.get(category, 0.0)
            category_gaps_data = category_gaps.get(category, {})
            
            if isinstance(category_gaps_data, dict):
                category_gap_list = category_gaps_data.get("gaps", [])
            else:
                category_gap_list = []
            
            # Build subsections list (just names)
            subsections_list = []
            canonical_subs = category_subsections_map.get(category, [])
            
            for sub_info in canonical_subs:
                subsections_list.append(sub_info["full_name"])
            
            aimri_data[category] = {
                "score": round(float(category_score), 2),
                "gaps": category_gap_list,
                "subsections": subsections_list
            }
        
        # Save to js.json
        js_file = self.results_root / "clubbed_result.json"
        js_file.write_text(json.dumps(aimri_data, indent=2, ensure_ascii=False))

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