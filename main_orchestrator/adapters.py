# orchestrator/adapters.py
from pathlib import Path
import subprocess
from urllib.parse import urlparse
from workflows.bi_tracker_workflow import run_workflow as run_bi
from workflows.code_repo_workflow import run_workflow
from agent_layer.cloud_infra_agent.orchestrator import CloudInfraOrchestrator
from workflows.AGENT_DATA_PLATFORM_ANALYZER.mvp_data_platform_scanner import MVPDataPlatformScanner
from workflows.enterprise_workflow import run_workflow as run_enterprise
from workflows.ml_ops_workflow import run_workflow as run_mlops
import json
import time

from orchestrator.utils import now_utc_str, write_json

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

def run_bi_adapter(out_dir: Path):
    res = run_bi()
    artifact = str(out_dir / f"bi_tracker_{now_utc_str()}.json")
    write_json(Path(artifact), res)
    return artifact, res.get("aggregates"), res.get("metrics")

def run_code_repo_adapter(out_dir: Path, repo_path_or_url: str):

    base_dir = Path("input_repos").resolve()
    base_dir.mkdir(parents=True, exist_ok=True)

    if _is_url(repo_path_or_url):
        repo_dir = _clone_one(repo_path_or_url, base_dir=base_dir, update_existing=True, depth=1)
    else:
        repo_dir = Path(repo_path_or_url).resolve()
        if not repo_dir.exists():
            raise FileNotFoundError(f"repo_path does not exist: {repo_dir}")

    res = run_workflow(str(repo_dir))
    artifact = str(out_dir / f"code_repo_{int(time.time())}.json")
    out_dir.mkdir(parents=True, exist_ok=True)
    Path(artifact).write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
    return artifact, res.get("aggregates"), res.get("metrics"), {"raw_keys": list(res.keys())}

def run_cloud_infra_adapter(out_dir: Path, batch_dir: str):
    orch = CloudInfraOrchestrator(
        batch_dir=batch_dir,
        runs_dir=str(out_dir),
        log_dir="logs/cloud_infra",
        log_level="INFO",
        serialize_logs=False,
        max_workers=8,
    )
    res = orch.run_once()

    if not isinstance(res, dict):
        res = {"status": "ok"}

    artifact = str(out_dir / f"cloud_infra_{now_utc_str()}.json")
    Path(artifact).write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")

    return artifact, res.get("aggregates"), res.get("metrics")

def run_data_platform_adapter(out_dir: Path):
    scanner = MVPDataPlatformScanner()  
    obj = scanner.run()

    if not isinstance(obj, dict):
        raise RuntimeError("Data Platform Analyzer produced no artifact dict. Check OPENAI_API_KEY and inputs.")

    artifact = str(out_dir / f"data_platform_{int(time.time())}.json")
    out_dir.mkdir(parents=True, exist_ok=True)
    Path(artifact).write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")
    return artifact, obj.get("aggregates"), obj.get("results") or obj.get("metrics"), {"raw_keys": list(obj.keys())}

def run_enterprise_adapter(out_dir: Path):
    out_path, scores = run_enterprise()
    metrics = None
    try:
        if out_path and Path(out_path).exists():
            data = json.loads(Path(out_path).read_text(encoding="utf-8"))
            metrics = data.get("results") or data.get("metrics")
    except Exception as e:
        metrics = {"error": f"failed to load metrics: {e}"}
    payload = {
        "artifact_path": str(out_path) if out_path else None,
        "scores": scores,
        "metrics": metrics,
    }
    artifact = str(out_dir / f"enterprise_{now_utc_str()}.json")
    write_json(Path(artifact), payload)
    return payload["artifact_path"] or artifact, scores, metrics

def run_mlops_adapter(out_dir: Path):
    artifact_path, aggregates, metrics = run_mlops()
    payload = {"artifact_path": str(artifact_path), "aggregates": aggregates, "metrics": metrics}
    artifact = str(out_dir / f"mlops_{now_utc_str()}.json")
    write_json(Path(artifact), payload)
    return artifact, aggregates, metrics