from __future__ import annotations
import argparse
from pathlib import Path
import sys

# Ensure repo root is on sys.path when running as a file
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent_layer.cloud_infra_agent.orchestrator import CloudInfraOrchestrator #noqa:E402



def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Cloud Infra Orchestrator (single run)")
    p.add_argument("--batch-dir", required=True, help="Directory containing input JSON files")
    p.add_argument("--runs-dir", default="agent_layer_outputs/cloud_infra", help="Directory to write <run_id>.json")
    p.add_argument("--log-dir", default="logs/cloud_infra", help="Directory to write per-run <run_id>.log")
    p.add_argument("--log-level", default="INFO", help="Log level (DEBUG, INFO, WARNING, ERROR)")
    p.add_argument("--serialize-logs", action="store_true", help="Write JSON-serialized logs")
    p.add_argument("--max-workers", type=int, default=8, help="Parallel workers for metrics")
    p.add_argument("--run-id", default=None, help="Override generated run id")
    return p.parse_args()

def main() -> None:
    args = parse_args()
    orch = CloudInfraOrchestrator(
        batch_dir=args.batch_dir,
        runs_dir=args.runs_dir,
        log_dir=args.log_dir,
        log_level=args.log_level,
        serialize_logs=args.serialize_logs,
        max_workers=args.max_workers,
    )
    orch.run_once(run_id=args.run_id)

if __name__ == "__main__":
    main()
