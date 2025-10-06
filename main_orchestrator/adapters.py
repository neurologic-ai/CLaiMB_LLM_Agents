from pathlib import Path
import subprocess
from urllib.parse import urlparse
from workflows.code_repo_workflow import run_workflow
from agent_layer.cloud_infra_agent.orchestrator import CloudInfraOrchestrator
from workflows.AGENT_DATA_PLATFORM_ANALYZER.mvp_data_platform_scanner import MVPDataPlatformScanner
from agent_layer.bi_tracker_agent.orchestrator import BIOrchestrator
from agent_layer.enterprise_systems.orchestrator_enterprise import EnterpriseOrchestrator
from agent_layer.ml_ops_agent.orchestrator_mlops import run as run_mlops_agent
from data_collection_agents.bi_tracker_agent.logging_utils import timed
from typing import Optional, Dict, Any
from loguru import logger
import json
import time
from .utils import now_utc_str, write_json

def _is_url(s: str) -> bool:
    try:
        u = urlparse(s)
        return bool(u.scheme and u.netloc)
    except Exception:
        return False

def _split_owner_repo(path: str) -> str:
    parts = [p for p in path.strip("/").split("/") if p]
    repo = parts[-1] if parts else "repo"
    if repo.endswith(".git"):
        repo = repo[:-4]
    return repo

def _clone_one(url: str, base_dir: Path, update_existing: bool = True, depth: int = 1) -> Path:
    parsed = urlparse(url)
    host = (parsed.hostname or "unknown").lower()
    repo = _split_owner_repo(parsed.path or "")
    dest = base_dir / host / repo
    dest.parent.mkdir(parents=True, exist_ok=True)

    if (dest / ".git").exists():
        if update_existing:
            subprocess.run(
                ["git", "-C", str(dest), "pull", "--rebase", "--autostash"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
        return dest

    cmd = ["git", "clone"]
    if depth and depth > 0:
        cmd.extend(["--depth", str(depth)])
    cmd.extend([url, str(dest)])
    subprocess.run(cmd, check=True)
    return dest

def run_bi_adapter(
    out_dir: Path,
    *,
    snapshot: Optional[Dict[str, Any]] = None,
    snapshot_path: Optional[str] = None,
) -> tuple[str, Dict[str, Any] | None, Dict[str, Any] | None]:

    if snapshot is None and snapshot_path is None:
        raise ValueError("BI adapter: no snapshot provided")

    if snapshot is None:
        snapshot = json.loads(Path(snapshot_path).read_text(encoding="utf-8"))
    
    with timed("bi_tracker_agent"):
        orch = BIOrchestrator()
        res = orch.run(snapshot, out_dir=Path("agent_layer_outputs/bi_tracker"))

    artifact = str(out_dir / f"bi_tracker_{now_utc_str()}.json")
    write_json(Path(artifact), res)
    return artifact, res.get("aggregates"), res.get("metrics")

def run_code_repo_adapter(
    out_dir: Path,
    *,
    repo_url: Optional[str] = None,
    repo_path: Optional[str] = None,
):
    if not repo_url and not repo_path:
        raise ValueError("CodeRepo adapter: either repo_url or repo_path must be provided")

    base_dir = Path("input_repos").resolve()
    base_dir.mkdir(parents=True, exist_ok=True)

    with timed("agent.code_repo"):
        if repo_url:
            repo_dir = _clone_one(repo_url, base_dir=base_dir, update_existing=True, depth=1)
        else:
            repo_dir = Path(repo_path).resolve()
            if not repo_dir.exists():
                raise FileNotFoundError(f"repo_path does not exist: {repo_dir}")
            
        res = run_workflow(str(repo_dir))

    out_dir.mkdir(parents=True, exist_ok=True)
    artifact = str(out_dir / f"code_repo_{now_utc_str()}.json")
    Path(artifact).write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")

    mcount = len((res or {}).get("metrics") or {})
    logger.info(f"[code_repo] metrics={mcount} repo_dir={repo_dir}")

    return artifact, res.get("aggregates"), res.get("metrics"), {"raw_keys": list(res.keys())}


def run_cloud_infra_adapter(
    out_dir: Path,
    *,
    snapshot_path: str,
):
    p = Path(snapshot_path)
    if not p.exists():
        raise FileNotFoundError(f"cloud_infra snapshot not found: {p}")

    try:
        snapshot = json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        raise ValueError(f"Invalid cloud_infra JSON at {p}: {e}")

    with timed("agent.cloud_infra"):
        orch = CloudInfraOrchestrator(
            batch_dir="unused",
            runs_dir=str(out_dir),
            log_dir="logs/cloud_infra",
            log_level="INFO",
            serialize_logs=False,
            max_workers=8,
            snapshot_fn=lambda: snapshot,
        )
        res = orch.run_once()
        if not isinstance(res, dict):
            res = {"status": "ok"}

    out_dir.mkdir(parents=True, exist_ok=True)
    artifact = str(out_dir / f"cloud_infra_{now_utc_str()}.json")
    Path(artifact).write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")

    mcount = len((res or {}).get("metrics") or {})
    logger.info(f"[cloud_infra] metrics={mcount}")

    return artifact, res.get("aggregates"), res.get("metrics")

# ---------- Data Platform ----------
def run_data_platform_adapter(
    out_dir: Path,
    *,
    snapshot: Optional[Dict[str, Any]] = None,
    snapshot_path: Optional[str] = None,
):
    if snapshot is None and snapshot_path is None:
        raise ValueError("Data Platform adapter: no snapshot provided")

    if snapshot is None:
        snapshot = json.loads(Path(snapshot_path).read_text(encoding="utf-8"))

    with timed("agent.data_platform"):
        scanner = MVPDataPlatformScanner()
        obj = scanner.run(ctx=snapshot)
        if not isinstance(obj, dict):
            raise RuntimeError("Data Platform Analyzer produced no artifact dict.")

    out_dir.mkdir(parents=True, exist_ok=True)
    artifact = str(out_dir / f"data_platform_{int(time.time())}.json")
    Path(artifact).write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")

    mcount = len((obj or {}).get("results") or (obj or {}).get("metrics") or {})
    logger.info(f"[data_platform] metrics={mcount}")

    return artifact, obj.get("aggregates"), obj.get("results") or obj.get("metrics"), {"raw_keys": list(obj.keys())}


# ---------- Enterprise ----------
def run_enterprise_adapter(
    out_dir: Path,
    *,
    snapshot: Optional[Dict[str, Any]] = None,
    snapshot_path: Optional[str] = None,
):
    if snapshot is None and snapshot_path is None:
        raise ValueError("Enterprise adapter: no snapshot provided")

    if snapshot is None:
        snapshot = json.loads(Path(snapshot_path).read_text(encoding="utf-8"))

    with timed("agent.enterprise_systems"):
        orch = EnterpriseOrchestrator()
        results, scores, waves = orch.run(snapshot, verbose=True)
        artifact_obj = {
            "run": {"waves": waves},
            "scores": scores,
            "metrics": results,
        }

    out_dir.mkdir(parents=True, exist_ok=True)
    artifact_path = str(out_dir / f"enterprise_{now_utc_str()}.json")
    Path(artifact_path).write_text(json.dumps(artifact_obj, indent=2, ensure_ascii=False), encoding="utf-8")

    mcount = len((results or {}))
    logger.info(f"[enterprise_systems] metrics={mcount}")

    return artifact_path, scores, results


# ---------- MLOps ----------
def run_mlops_adapter(
    out_dir: Path,
    *,
    snapshot: Optional[Dict[str, Any]] = None,
    snapshot_path: Optional[str] = None,
):
    if snapshot is None and snapshot_path is None:
        raise ValueError("MLOps adapter: no snapshot provided")

    if snapshot is None:
        snapshot = json.loads(Path(snapshot_path).read_text(encoding="utf-8"))

    with timed("agent.ml_ops"):
        res = run_mlops_agent(snapshot, out_dir=Path("agent_layer_outputs/mlops_monitor"))

    artifact_path = res["artifact_path"]
    aggregates    = res.get("aggregates")
    metrics       = res.get("metrics")

    out_dir.mkdir(parents=True, exist_ok=True)
    payload_artifact = str(out_dir / f"mlops_{now_utc_str()}.json")
    Path(payload_artifact).write_text(
        json.dumps({"artifact_path": artifact_path, "aggregates": aggregates, "metrics": metrics}, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    mcount = len((metrics or {}))
    logger.info(f"[ml_ops] metrics={mcount}")

    return payload_artifact, aggregates, metrics