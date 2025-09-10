# mvp/run_once.py
from __future__ import annotations
import os
import json
from dotenv import load_dotenv

from workflows.bi_tracker_workflow import run_workflow 
from data_collection_agents.bi_tracker_agent.logging_utils import setup_logger


def main() -> None:

    load_dotenv()
    setup_logger("logs/agent_layer.log", level="INFO", serialize=False)

    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found in environment (.env). Please check your .env file.")
        return
    result = run_workflow()

    artifact = result.get("artifact_path") or "(not saved)"
    aggregates = result.get("aggregates") or {}
    metrics = result.get("metrics") or {}

    print("\n=== BI Tracker MVP Run ===")
    print(f"Artifact: {artifact}")

    if aggregates:
        print("Scores:")
        print(json.dumps(aggregates, indent=2))
    else:
        print("Scores: (none)")

    print(f"Metrics computed: {len(metrics) if isinstance(metrics, dict) else 0}")

    # Optional: show a quick preview of a few metric ids
    if isinstance(metrics, dict) and metrics:
        preview_ids = list(metrics.keys())[:5]
        print(f"Preview metrics: {', '.join(preview_ids)}")


if __name__ == "__main__":
    main()