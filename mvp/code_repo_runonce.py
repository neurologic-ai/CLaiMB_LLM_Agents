#!/usr/bin/env python3
"""Run the Code Repo Agent once on a repo (URL or local path) and write one JSON."""

from __future__ import annotations
import argparse
import json
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse
from datetime import datetime, timezone

# make imports work as module
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from workflows.code_repo_workflow import run_workflow  # noqa: E402


# ---------------- Helpers ----------------
def _is_url(s: str) -> bool:
    try:
        u = urlparse(s)
        return bool(u.scheme and u.netloc)
    except Exception:
        return False


def _split_owner_repo(path: str) -> str:
    """Extract repo name from a Git URL path."""
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
            print(f"🔄 Updated: {dest}")
        else:
            print(f"⏭️  Skipping update (exists): {dest}")
        return dest

    cmd = ["git", "clone"]
    if depth and depth > 0:
        cmd.extend(["--depth", str(depth)])
    cmd.extend([url, str(dest)])
    subprocess.run(cmd, check=True)
    print(f"📥 Cloned {url} → {dest}")
    return dest


def _default_out_path(repo_arg: str, repo_dir: Path) -> Path:
    if _is_url(repo_arg):
        repo = _split_owner_repo(urlparse(repo_arg).path or "")
    else:
        repo = repo_dir.name or "repo"
    safe_repo = repo.replace("/", "_")
    out_dir = Path("runs_code_repo_mvp")
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return out_dir / f"{safe_repo}_{ts}.json"


# ---------------- Main ----------------
def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run Code Repo Agent once on a repo (URL or local path).")
    p.add_argument("--repo", required=True, help="Git URL or local path to the repository root.")
    p.add_argument("--out", default="", help="Exact JSON file path to write. If omitted, a default is used.")
    p.add_argument("--clone-base", default="input_repos", help="Where to place the cloned repo if --repo is a URL.")
    p.add_argument("--no-update-existing", action="store_true", help="Skip git pull if repo already exists locally.")
    p.add_argument("--clone-depth", type=int, default=1, help="Shallow clone depth (default=1).")
    return p.parse_args()


def main() -> None:
    args = parse_args()

    # 1) Resolve repo location (clone if URL, else use local path)
    if _is_url(args.repo):
        base_dir = Path(args.clone_base).resolve()
        repo_dir = _clone_one(
            url=args.repo,
            base_dir=base_dir,
            update_existing=(not args.no_update_existing),
            depth=args.clone_depth,
        )
    else:
        repo_dir = Path(args.repo).resolve()
        if not repo_dir.exists():
            raise FileNotFoundError(f"Repo path not found: {repo_dir}")

    # 2) Run your workflow
    result = run_workflow(str(repo_dir))

    # 3) Determine output path
    out_file = Path(args.out).resolve() if args.out else _default_out_path(args.repo, repo_dir)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    print("\n=== Code Repo Agent MVP Run ===")
    print(f"Repo: {repo_dir}")
    print(f"Artifact: {out_file}")
    aggregates = result.get("aggregates") or {}
    metrics = result.get("metrics") or {}
    print("Scores:" if aggregates else "Scores: (none)")
    if aggregates:
        print(json.dumps(aggregates, indent=2))
    print(f"Metrics computed: {len(metrics) if isinstance(metrics, dict) else 0}")


if __name__ == "__main__":
    main()