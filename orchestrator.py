# #!/usr/bin/env python3

# from __future__ import annotations
# import argparse
# import json
# import os
# import sys
# import time
# import traceback
# from dataclasses import dataclass
# from datetime import datetime, timezone
# from pathlib import Path
# from typing import Any, Callable, Dict, Optional, Tuple
# from concurrent.futures import ThreadPoolExecutor, Future, as_completed

# # --- Repo root on path so imports work when run as a file ---
# ROOT = Path(__file__).resolve().parents[0]
# REPO = ROOT.parents[0] if ROOT.name == "mvp" else ROOT.parents[1]
# if str(REPO) not in sys.path:
#     sys.path.insert(0, str(REPO))

# # ---- Agent imports (call workflow APIs directly; no subprocess) ----
# from workflows.bi_tracker_workflow import run_workflow as run_bi            # noqa: E402
# from workflows.code_repo_workflow import run_workflow as run_code_repo      # noqa: E402
# from agent_layer.cloud_infra_agent.orchestrator import CloudInfraOrchestrator  # noqa: E402
# from workflows.AGENT_DATA_PLATFORM_ANALYZER.mvp_data_platform_scanner import run_once as run_data_platform_once  # noqa: E402
# from workflows.enterprise_workflow import run_workflow as run_enterprise     # noqa: E402
# from workflows.ml_ops_workflow import run_workflow as run_mlops              # noqa: E402


# # ============================
# # Configuration & Data Models
# # ============================

# @dataclass(frozen=True)
# class AgentSpec:
#     name: str
#     enabled: bool
#     timeout_sec: int
#     retries: int

# @dataclass
# class AgentResult:
#     name: str
#     ok: bool
#     artifact_path: Optional[str]
#     aggregates: Any
#     metrics: Any
#     extra: Dict[str, Any]
#     error: Optional[str]
#     duration_sec: float


# # =====================
# # Logging & Utilities
# # =====================

# def now_utc_str() -> str:
#     return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

# def ensure_dir(p: Path) -> None:
#     p.mkdir(parents=True, exist_ok=True)

# def log(msg: str, *, run_id: str, level: str = "INFO") -> None:
#     # simple, CI-friendly logging
#     print(f"[{level}] [{run_id}] {msg}", flush=True)

# def _sanitize(obj: Any) -> Any:
#     from pathlib import Path as _Path
#     if isinstance(obj, _Path):
#         return str(obj)
#     if isinstance(obj, dict):
#         return {k: _sanitize(v) for k, v in obj.items()}
#     if isinstance(obj, (list, tuple, set)):
#         return [_sanitize(v) for v in obj]
#     return obj

# def write_json(path: Path, payload: Any) -> None:
#     ensure_dir(path.parent)
#     payload = _sanitize(payload)
#     path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


# # =====================
# # Agent Adapters
# # =====================

# def run_bi_adapter(out_dir: Path) -> Tuple[Optional[str], Any, Any, Dict[str, Any]]:
#     """BI Tracker: returns (artifact_path, aggregates, metrics, extra)."""
#     res = run_bi()  # expected dict: {artifact_path?, aggregates?, metrics?}
#     artifact = res.get("artifact_path")
#     if artifact:
#         artifact = str(artifact)
#     else:
#         artifact = str(out_dir / f"bi_tracker_{now_utc_str()}.json")
#         write_json(Path(artifact), res)  # persist if workflow didn't
#     return artifact, res.get("aggregates"), res.get("metrics"), {"raw_keys": list(res.keys())}

# def run_code_repo_adapter(out_dir: Path, repo_path_or_url: str) -> Tuple[Optional[str], Any, Any, Dict[str, Any]]:
#     """Code Repo Agent."""
#     res = run_code_repo(repo_path_or_url)
#     artifact = str(out_dir / f"code_repo_{now_utc_str()}.json")
#     write_json(Path(artifact), res)
#     return artifact, res.get("aggregates"), res.get("metrics"), {"raw_keys": list(res.keys())}

# def run_cloud_infra_adapter(out_dir: Path, batch_dir: str) -> Tuple[Optional[str], Any, Any, Dict[str, Any]]:
#     """
#     Cloud Infra Agent: run internal orchestrator.
#     NOTE: Do not log under orchestrator_output. Use a separate logs/ folder.
#     """
#     orch = CloudInfraOrchestrator(
#         batch_dir=batch_dir,
#         runs_dir=str(out_dir / "cloud_infra"),              # artifacts go under orchestrator_output
#         log_dir=str(Path("logs") / "cloud_infra"),          # logs kept OUTSIDE orchestrator_output
#         log_level=os.getenv("CLOUD_LOG_LEVEL", "INFO"),
#         serialize_logs=bool(int(os.getenv("CLOUD_SERIALIZE_LOGS", "0"))),
#         max_workers=int(os.getenv("CLOUD_MAX_WORKERS", "8")),
#     )
#     run_id = os.getenv("CLOUD_RUN_ID")  # or None
#     orch.run_once(run_id=run_id)
#     # Drop a small marker artifact so combined file always references something
#     marker = {"note": "CloudInfraOrchestrator executed. See runs_dir for artifacts."}
#     artifact = str(out_dir / f"cloud_infra_marker_{now_utc_str()}.json")
#     write_json(Path(artifact), marker)
#     return artifact, None, None, marker

# def run_data_platform_adapter(out_dir: Path) -> Tuple[Optional[str], Any, Any, Dict[str, Any]]:
#     """
#     Data Platform Analyzer: run_once() should return a dict with 'aggregates' and 'results'.
#     Defensive guard to avoid NoneType errors.
#     """
#     obj = run_data_platform_once()
#     if not isinstance(obj, dict):
#         raise RuntimeError(
#             "Data Platform Analyzer returned no artifact (None or non-dict). "
#             "Check OPENAI_API_KEY, snapshot inputs, and config paths."
#         )
#     artifact = str(out_dir / f"data_platform_{now_utc_str()}.json")
#     write_json(Path(artifact), obj)
#     aggregates = obj.get("aggregates")
#     metrics = obj.get("results") or obj.get("metrics")
#     return artifact, aggregates, metrics, {"raw_keys": list(obj.keys())}

# def run_enterprise_adapter(out_dir: Path) -> Tuple[Optional[str], Any, Any, Dict[str, Any]]:
#     """
#     Enterprise Systems Agent: workflow usually returns (artifact_path, scores).
#     Normalize and persist a small join file.
#     """
#     out_path, scores = run_enterprise()
#     payload = {"artifact_path": str(out_path) if out_path else None, "scores": scores}
#     artifact = str(out_dir / f"enterprise_{now_utc_str()}.json")
#     write_json(Path(artifact), payload)
#     return payload["artifact_path"] or artifact, scores, None, {"raw_keys": list(payload.keys())}

# def run_mlops_adapter(out_dir: Path) -> Tuple[Optional[str], Any, Any, Dict[str, Any]]:
#     """
#     ML Ops Agent: returns (artifact_path, aggregates, metrics).
#     Run exclusively to avoid logger handler collisions.
#     """
#     artifact_path, aggregates, metrics = run_mlops()
#     payload = {"artifact_path": str(artifact_path) if artifact_path else None,
#                "aggregates": aggregates, "metrics": metrics}
#     artifact = str(out_dir / f"ml_ops_{now_utc_str()}.json")
#     write_json(Path(artifact), payload)
#     return payload["artifact_path"] or artifact, aggregates, metrics, {"raw_keys": list(payload.keys())}


# # =====================
# # Orchestration Engine
# # =====================

# def run_with_retries(
#     fn: Callable[[], Tuple[Optional[str], Any, Any, Dict[str, Any]]],
#     spec: AgentSpec,
#     run_id: str,
# ) -> AgentResult:
#     start = time.time()
#     last_err: Optional[str] = None
#     for attempt in range(1, spec.retries + 2):  # retries=N → N+1 attempts total
#         try:
#             log(f"{spec.name}: attempt {attempt}", run_id=run_id)
#             with ThreadPoolExecutor(max_workers=1) as ex:
#                 fut: Future = ex.submit(fn)
#                 artifact, aggregates, metrics, extra = fut.result(timeout=spec.timeout_sec)

#             dur = round(time.time() - start, 2)
#             log(f"{spec.name}: completed in {dur}s", run_id=run_id)
#             return AgentResult(
#                 name=spec.name,
#                 ok=True,
#                 artifact_path=artifact,
#                 aggregates=aggregates,
#                 metrics=metrics,
#                 extra=extra,
#                 error=None,
#                 duration_sec=dur,
#             )
#         except Exception as e:
#             last_err = f"{type(e).__name__}: {e}"
#             tb = traceback.format_exc(limit=5)
#             log(f"{spec.name}: failure on attempt {attempt}: {last_err}\n{tb}", run_id=run_id, level="ERROR")
#             time.sleep(min(2 * attempt, 6))  # small backoff

#     dur = round(time.time() - start, 2)
#     return AgentResult(
#         name=spec.name, ok=False, artifact_path=None, aggregates=None, metrics=None,
#         extra={}, error=last_err, duration_sec=dur
#     )


# def orchestrate(args: argparse.Namespace) -> Path:
#     run_id = args.run_id or f"mvp-{now_utc_str()}"
#     out_root = Path(args.out_dir).resolve()
#     ensure_dir(out_root)
#     per_agent_dir = out_root / "agents"
#     ensure_dir(per_agent_dir)

#     log("==== MVP Orchestration START ====", run_id=run_id)

#     specs: Dict[str, AgentSpec] = {
#         "bi_tracker": AgentSpec("bi_tracker", args.bi_enabled, args.timeout_bi, args.retries),
#         "code_repo": AgentSpec("code_repo", args.code_enabled, args.timeout_code, args.retries),
#         "cloud_infra": AgentSpec("cloud_infra", args.cloud_enabled, args.timeout_cloud, args.retries),
#         "data_platform": AgentSpec("data_platform", args.data_enabled, args.timeout_data, args.retries),
#         "enterprise": AgentSpec("enterprise", args.enterprise_enabled, args.timeout_enterprise, args.retries),
#         "ml_ops": AgentSpec("ml_ops", args.mlops_enabled, args.timeout_mlops, args.retries),
#     }

#     # Build callables with parameters wired in
#     callables: Dict[str, Callable[[], Tuple[Optional[str], Any, Any, Dict[str, Any]]]] = {}

#     if specs["bi_tracker"].enabled:
#         callables["bi_tracker"] = lambda: run_bi_adapter(per_agent_dir / "bi_tracker")

#     if specs["code_repo"].enabled:
#         if not args.code_repo:
#             raise SystemExit("--code-enabled requires --code-repo <URL-or-path>")
#         callables["code_repo"] = lambda: run_code_repo_adapter(per_agent_dir / "code_repo", args.code_repo)

#     if specs["cloud_infra"].enabled:
#         if not args.cloud_batch:
#             raise SystemExit("--cloud-enabled requires --cloud-batch <dir>")
#         callables["cloud_infra"] = lambda: run_cloud_infra_adapter(per_agent_dir / "cloud_infra", args.cloud_batch)

#     if specs["data_platform"].enabled:
#         callables["data_platform"] = lambda: run_data_platform_adapter(per_agent_dir / "data_platform")

#     if specs["enterprise"].enabled:
#         callables["enterprise"] = lambda: run_enterprise_adapter(per_agent_dir / "enterprise")

#     if specs["ml_ops"].enabled:
#         callables["ml_ops"] = lambda: run_mlops_adapter(per_agent_dir / "ml_ops")

#     # Execute everyone EXCEPT ML Ops in a threadpool
#     futures: Dict[Future, str] = {}
#     results: Dict[str, AgentResult] = {}

#     with ThreadPoolExecutor(max_workers=args.max_workers) as ex:
#         for name, spec in specs.items():
#             if not spec.enabled:
#                 log(f"{name}: disabled — skipping", run_id=run_id, level="WARN")
#                 continue
#             if name == "ml_ops":
#                 # run ML Ops exclusively afterwards to avoid global logger handler collision
#                 continue
#             fut = ex.submit(run_with_retries, callables[name], spec, run_id)
#             futures[fut] = name

#         for fut in as_completed(futures):
#             name = futures[fut]
#             try:
#                 result: AgentResult = fut.result()
#             except Exception as e:
#                 err = f"{type(e).__name__}: {e}"
#                 result = AgentResult(name=name, ok=False, artifact_path=None, aggregates=None, metrics=None,
#                                      extra={}, error=err, duration_sec=0.0)
#             results[name] = result

#     # Run ML Ops exclusively (if enabled)
#     if specs["ml_ops"].enabled:
#         log("ml_ops: running exclusively to avoid logger collisions", run_id=run_id, level="WARN")
#         results["ml_ops"] = run_with_retries(callables["ml_ops"], specs["ml_ops"], run_id)

#     # Build combined payload
#     combined = {
#         "run_id": run_id,
#         "started_at_utc": now_utc_str(),
#         "out_dir": str(out_root),
#         "agents": {
#             name: {
#                 "ok": r.ok,
#                 "artifact_path": r.artifact_path,
#                 "aggregates": r.aggregates,
#                 "metrics_summary": None if r.metrics is None else (
#                     list(r.metrics.keys())[:10] if isinstance(r.metrics, dict) else f"type={type(r.metrics).__name__}"
#                 ),
#                 "extra": r.extra,
#                 "error": r.error,
#                 "duration_sec": r.duration_sec,
#             }
#             for name, r in results.items()
#         },
#     }

#     # Persist combined master artifact
#     combined_path = out_root / f"all_agents_{run_id}.json"
#     write_json(combined_path, combined)

#     ok_count = sum(1 for r in results.values() if r.ok)
#     log(f"==== DONE: {ok_count}/{len(results)} agents succeeded. Combined: {combined_path}", run_id=run_id)
#     return combined_path


# # =====================
# # CLI
# # =====================

# def build_parser() -> argparse.ArgumentParser:
#     p = argparse.ArgumentParser(description="Run all MVP agents and produce a combined JSON artifact.")
#     # enable/disable
#     p.add_argument("--bi-enabled", action="store_true", help="Enable BI Tracker Agent")
#     p.add_argument("--code-enabled", action="store_true", help="Enable Code Repo Agent")
#     p.add_argument("--cloud-enabled", action="store_true", help="Enable Cloud Infra Agent")
#     p.add_argument("--data-enabled", action="store_true", help="Enable Data Platform Analyzer Agent")
#     p.add_argument("--enterprise-enabled", action="store_true", help="Enable Enterprise Systems Agent")
#     p.add_argument("--mlops-enabled", action="store_true", help="Enable ML Ops Agent")

#     # shared
#     p.add_argument("--out-dir", default="orchestrator_output",
#                    help="Where to write combined + per-agent artifacts (no logs here)")
#     p.add_argument("--run-id", default="", help="Optional run ID (defaults to UTC timestamp)")
#     p.add_argument("--max-workers", type=int, default=4, help="Parallel workers for non-ML Ops agents")
#     p.add_argument("--retries", type=int, default=1, help="Number of retries per agent on failure")

#     # timeouts
#     p.add_argument("--timeout-bi", type=int, default=900, help="Seconds before timing out BI agent")
#     p.add_argument("--timeout-code", type=int, default=1800, help="Seconds before timing out Code Repo agent")
#     p.add_argument("--timeout-cloud", type=int, default=1800, help="Seconds before timing out Cloud Infra agent")
#     p.add_argument("--timeout-data", type=int, default=1800, help="Seconds before timing out Data Platform agent")
#     p.add_argument("--timeout-enterprise", type=int, default=1200, help="Seconds before timing out Enterprise agent")
#     p.add_argument("--timeout-mlops", type=int, default=1800, help="Seconds before timing out ML Ops agent")

#     # per-agent params
#     p.add_argument("--code-repo", default="", help="Git URL or local path for Code Repo Agent")
#     p.add_argument("--cloud-batch", default="", help="Input batch directory for Cloud Infra Agent")
#     return p


# def main() -> None:
#     args = build_parser().parse_args()
#     combined = orchestrate(args)
#     print(str(combined))

# if __name__ == "__main__":
#     main()