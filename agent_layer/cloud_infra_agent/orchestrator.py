# agent_layer/orchestrator.py

from __future__ import annotations
import os
import json
import uuid
from typing import Dict, Any, Optional, Callable
from pathlib import Path
from datetime import datetime, timezone

from loguru import logger

# ── your existing modules ──────────────────────────────────────────────────────
from data_collection_agents.cloud_infra_agent.config import Input_File_For_Metric_map
from data_collection_agents.cloud_infra_agent.logging_utils import setup_logger, timed
from workflows.cloud_infra_workflow import run_workflow


def _load_metric_files_via_map(batch_dir: str) -> Dict[str, Any]:
    """
    Load inputs using the explicit Input_File_For_Metric_map.
    Produces context keyed by **dotted** metric_id: {"params": <json>}.
    """
    ctx: Dict[str, Any] = {}
    loaded, missing = [], []

    for metric_id, fname in Input_File_For_Metric_map.items():
        path = os.path.join(batch_dir, fname)
        if os.path.isfile(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                ctx[metric_id] = {"params": data}
                loaded.append((metric_id, fname))
            except Exception as e:
                logger.warning(f"[engine_adapter] failed to load {fname} for {metric_id}: {e}")
        else:
            missing.append((metric_id, fname))

    if missing:
        miss_pretty = ", ".join([f"{m}→{f}" for m, f in missing])
        logger.info(f"[engine_adapter] Missing mapped files (ok if intentional): {miss_pretty}")

    logger.info("[engine_adapter] context keys: " + ", ".join(sorted(ctx.keys())))
    return ctx


def _make_run_id(prefix: str = "cloud-infra") -> str:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    return f"{prefix}-{ts}"


def _context_from_snapshot(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    """
    Accepts a snapshot like { 'metric.id': {...}, ... }.
    We can pass it through as-is: the workflow will wrap to {'params': ...} when needed.
    """
    if not isinstance(snapshot, dict) or not snapshot:
        raise ValueError("snapshot must be a non-empty dict keyed by metric_id")
    logger.info("[engine_adapter] Using context from snapshot function")
    logger.info("[engine_adapter] context keys: " + ", ".join(sorted(snapshot.keys())))
    return snapshot


class CloudInfraOrchestrator:
    def __init__(
        self,
        batch_dir: str,
        runs_dir: str = "agent_layer_outputs/cloud_infra",
        *,
        log_dir: str = "logs",
        log_level: str = "INFO",
        serialize_logs: bool = False,
        max_workers: int = 8,
        snapshot_fn: Optional[Callable[[], Dict[str, Any]]] = None,  # ← NEW
    ) -> None:
        self.batch_dir = os.path.abspath(batch_dir)
        self.runs_dir = os.path.abspath(runs_dir)
        self.log_dir = os.path.abspath(log_dir)
        self.max_workers = max_workers

        os.makedirs(self.runs_dir, exist_ok=True)
        os.makedirs(self.log_dir, exist_ok=True)

        self.log_level = log_level
        self.serialize_logs = serialize_logs

        # NEW: optional function that returns a snapshot dict
        self._snapshot_fn = snapshot_fn

    def _build_config(self, run_id: str) -> Dict[str, Any]:
        """Build the config dict for run_workflow."""
        return {
            "save_dir": self.runs_dir,
            "output_path": str(Path(self.runs_dir) / f"{run_id}.json"),
            "max_workers": self.max_workers,
            "run_id": run_id,  # include in workflow logs
        }

    def _load_context(self) -> Dict[str, Any]:
        """
        Two options:
          1) If snapshot_fn is provided → call it and use that dict.
          2) Else → load legacy inputs from files via Input_File_For_Metric_map.
        """
        if self._snapshot_fn is not None:
            try:
                snap = self._snapshot_fn()
                return _context_from_snapshot(snap)
            except Exception as e:
                logger.exception(f"[engine_adapter] snapshot_fn raised: {e}")
                raise

        logger.info("[engine_adapter] No snapshot_fn provided → loading mapped files")
        return _load_metric_files_via_map(self.batch_dir)

    def run_once(self, *, run_id: Optional[str] = None) -> Dict[str, Any]:
        rid = run_id or _make_run_id()

        # Make per-run log path
        log_path = str(Path(self.log_dir) / f"{rid}.log")

        # Setup logger with per-run file
        setup_logger(
            log_path=log_path,
            level=self.log_level,
            serialize=self.serialize_logs,
        )

        logger.info(f"[orchestrator] Starting run_id={rid}")

        # Load inputs
        with timed("Load inputs"):
            context = self._load_context()

        # Run workflow
        cfg = self._build_config(rid)
        try:
            with timed("Run workflow"):
                final = run_workflow(cfg, context) or {}
        except Exception as e:
            logger.exception(f"[orchestrator] run_workflow failed: {e}")
            final = {"error": str(e), "echo": {"run_id": rid, "count_inputs": len(context)}}

        # Ensure output file
        out_path = Path(cfg["output_path"])
        out_path.write_text(json.dumps(final, indent=2), encoding="utf-8")
        logger.info(f"[orchestrator] ✅ Output saved: {out_path}")

        logger.info(f"[orchestrator] Finished run_id={rid}")
        return final



# # Optional: simple CLI entrypoint
# if __name__ == "__main__":
#     import argparse

#     parser = argparse.ArgumentParser(description="Cloud Infra Orchestrator (single run)")
#     parser.add_argument("--batch-dir", required=True, help="Directory containing input JSON files")
#     parser.add_argument("--runs-dir", default="runs", help="Directory to write <run_id>.json")
#     parser.add_argument("--log-dir", default="logs", help="Directory to write per-run <run_id>.log")
#     parser.add_argument("--log-level", default="INFO", help="Log level (DEBUG, INFO, WARNING, ERROR)")
#     parser.add_argument("--serialize-logs", action="store_true", help="Write JSON-serialized logs")
#     parser.add_argument("--max-workers", type=int, default=8, help="Parallel workers for metrics")
#     parser.add_argument("--run-id", default=None, help="Override generated run id")

#     args = parser.parse_args()

#     orch = CloudInfraOrchestrator(
#         batch_dir=args.batch_dir,
#         runs_dir=args.runs_dir,
#         log_dir=args.log_dir,            # <-- per-run logs directory
#         log_level=args.log_level,
#         serialize_logs=args.serialize_logs,
#         max_workers=args.max_workers,
#     )
#     orch.run_once(run_id=args.run_id)
