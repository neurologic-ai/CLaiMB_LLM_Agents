# workflows/code_repo_workflow.py
from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple
from loguru import logger
import os
import sys

# --- import bootstrap ---
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Use the improved orchestrator (unchanged)
from agent_layer.dev_env_scanner.orchestrator import CodeRepoOrchestrator, now_utc_iso  # noqa: E402
from data_collection_agents.dev_env_scanner_agent.logging_utils import setup_logger  # noqa: E402

from data_collection_agents.dev_env_scanner_agent.utils.file_utils import list_all_files, list_source_files #noqa: E402

ARTIFACT_DIR = Path(os.getenv("CODE_REPO_ARTIFACT_DIR", "runs_code_repo_mvp"))
LOGS_DIR     = Path(os.getenv("CODE_REPO_LOGS_DIR", "logs"))

# Tunables (can be overridden via env)
MAX_FILES_PER_REPO = int(os.getenv("CODE_REPO_MAX_FILES", "80"))
MAX_SNIPPET_BYTES  = int(os.getenv("CODE_REPO_MAX_BYTES", "3000"))

_PROTO_SUFFIXES = ("_pb2.py", "_pb2_grpc.py")
_PROTO_HINTS    = ("/generated/", "/gen/", "/proto/", "/protos/", "/bazel-")

def _is_generated_or_proto(p: Path) -> bool:
    s = str(p).replace("\\", "/").lower()
    return s.endswith(_PROTO_SUFFIXES) or any(h in s for h in _PROTO_HINTS)

def _read_snippets(paths: Iterable[Path]) -> List[str]:
    out: List[str] = []
    half = max(1, MAX_SNIPPET_BYTES // 2)
    for p in paths:
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            text = ""
        if len(text) <= MAX_SNIPPET_BYTES:
            out.append(text)
        else:
            out.append(text[:half] + "\n# ...\n" + text[-half:])
    return out

def collect_snapshot(repo_dir: Path) -> Dict[str, Any]:
    """
    Layout-agnostic: uses the new list_source_files (no 'src/' or repo-name assumptions).
    Also lightly prioritizes likely-interesting files before capping to MAX_FILES_PER_REPO.
    """
    # all python files (already excludes docs/tests/etc in list_source_files)
    src = list(list_source_files(str(repo_dir)))
    src = [p for p in src if not _is_generated_or_proto(p)]

    # simple prioritization (does not filter out others):
    keywords = ("src/", "train", "eval", "serve", "api", "pipeline", "dag", "flow", "inference")
    pri = [p for p in src if any(k in str(p).lower() for k in keywords)]
    seen = set()
    ordered: List[Path] = []
    for p in pri + src:
        if p not in seen:
            seen.add(p)
            ordered.append(p)

    picked = ordered[:MAX_FILES_PER_REPO]

    snapshot = {
        "code_snippets": _read_snippets(picked),
        "file_paths": list(list_all_files(str(repo_dir))),  # full list (used by fs.* metrics)
    }
    return snapshot

class CodeRepoWorkflow:
    """
    - sets up per-run logging (logs/<run_id>.log)
    - builds snapshot from a repo path
    - runs the CodeRepoOrchestrator
    - writes artifact json (runs_code_repo_mvp/<run_id>.json)
    """
    def __init__(self, artifact_dir: Path | None = None, logs_dir: Path | None = None) -> None:
        self.artifact_dir = artifact_dir or ARTIFACT_DIR
        self.logs_dir = logs_dir or LOGS_DIR
        self.artifact_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.orchestrator = CodeRepoOrchestrator()

    def run(self, repo_path: str, run_id: str | None = None) -> Tuple[Path, Dict[str, Any]]:
        rid = run_id or f"code-repo-{now_utc_iso()}"

        # per-run file + console; single file (no rotation)
        per_run_log = (self.logs_dir / f"{rid}.log").resolve()
        setup_logger(log_path=str(per_run_log), level="INFO", serialize=False)
        logger.info(f"Starting CodeRepoWorkflow.run (run_id={rid})")

        repo_dir = Path(repo_path).resolve()
        if not repo_dir.exists():
            raise FileNotFoundError(f"repo_path does not exist: {repo_dir}")

        snapshot = collect_snapshot(repo_dir)
        result = self.orchestrator.run(snapshot, out_dir=self.artifact_dir)

        out_path = Path(result["artifact_path"]).resolve()
        logger.info(f"Artifact written → {out_path}")
        return out_path, result

# ---- Backwards-compatible functional entrypoint ----
def run_workflow(repo_path: str) -> Dict[str, Any]:
    wf = CodeRepoWorkflow()
    _, result = wf.run(repo_path=repo_path, run_id=None)
    return result