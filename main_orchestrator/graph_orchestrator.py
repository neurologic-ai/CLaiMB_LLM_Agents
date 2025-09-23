from __future__ import annotations
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from .feature_bus import FeatureBus, utc_iso
from .scoring import ScoringAgent
AGENTS_LIST = [
    "cloud_infra",        # 6h
    "data_platform",      # 12h
    "ml_ops",             # 4h
    "bi_tracker",         # daily
    "enterprise_systems", # 8h
    "code_repo",          # daily
]

TRIGGER_K_OF_N = 2

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
    ):
        self.bus = FeatureBus(bus_root)
        self.results_root = Path(results_root)
        self.results_root.mkdir(parents=True, exist_ok=True)

        self.agents_root = Path(agents_root)
        self.agents_root.mkdir(parents=True, exist_ok=True)
        self.scorer = ScoringAgent(category_weights=None)
        self.graph = self._build_graph()

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
            "global_scores": state.global_scores,
            "latest_sign_ts": state.latest_sign_ts,
        }
        (self.results_root / f"scoring_{ts}.json").write_text(json.dumps(out, indent=2))
        (self.results_root / "latest_overall.json").write_text(
            json.dumps({"overall": out["result"].get("overall_score")}, indent=2)
        )
        (self.results_root / "category_scores.json").write_text(
            json.dumps(out["result"].get("category_scores", {}), indent=2)
        )
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