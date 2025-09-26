# main_orchestrator/tick_cli.py
from __future__ import annotations
from dotenv import load_dotenv
from pathlib import Path

from main_orchestrator.graph_orchestrator import Orchestrator, OrchestratorState
from main_orchestrator.feature_bus import FeatureBus
from main_orchestrator.collectors import build_collectors

def main():
    load_dotenv()

    BUS = FeatureBus("./bus")
    ORCH = Orchestrator(bus_root="./bus", results_root="./results")
    state = OrchestratorState()

    # one-shot: run any agent you want, then tick orchestrator
    artifacts_root = Path("orchestrator_output/agents")
    collectors = build_collectors(
        BUS,
        artifacts_root=artifacts_root,
        cloud_batch_dir="cloud_infra_inputs/Sample2",
        code_repo="https://github.com/deepakpadhi986/AI-Resume-Analyzer.git",
    )

   
    for name, collector in collectors.items():
        print(f"▶ Running {name}")
        collector.run()

    state = ORCH.tick(state, thread_id="cli")
    print("✅ Tick complete. See ./results and orchestrator_output/agents/*")

if __name__ == "__main__":
    main()