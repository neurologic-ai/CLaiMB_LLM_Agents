import os
from pathlib import Path
from typing import Iterator, Optional, Iterable

def list_all_files(repo_path: str) -> Iterator[str]:
    """Yield every file under repo_path."""
    for root, _, files in os.walk(repo_path):
        for fname in files:
            yield os.path.join(root, fname)

_EXCLUDE_DIRS_DEFAULT = {
    "docs", "examples", "templates", ".github", "tests", "__pycache__",
    ".venv", "venv", ".tox", ".mypy_cache", ".pytest_cache",
    "build", "dist", "site-packages", "third_party", "thirdparty", "vendor",
    "bazel-bin", "bazel-out", "bazel-genfiles", "generated", "gen", "_generated",
    "protobuf", "protos", "proto", ".eggs", ".nox", ".cache"
}
_EXCLUDE_SUFFIXES = (
    "_pb2.py",
    "_pb2_grpc.py",
)
_EXCLUDE_CONTAINS = (
    "/generated/",
    "/gen/",
    "/protos/",
    "/proto/",
    "/bazel-",
)

def list_source_files(
    root: str,
    include_dirs: Optional[Iterable[str]] = None,
    exclude_dirs: Optional[Iterable[str]] = None,
) -> Iterator[Path]:
    """
    Yield all .py files anywhere under `root`, skipping non-source & generated trees.
    No 'src/' or repo-name assumptions.
    """
    root_path = Path(root)
    excludes = set(exclude_dirs or _EXCLUDE_DIRS_DEFAULT)

    for path in root_path.rglob("*.py"):
        parts = path.parts

       
        if any(p in excludes for p in parts):
            continue

        s = str(path).replace("\\", "/")
        if s.endswith(_EXCLUDE_SUFFIXES) or any(tok in s for tok in _EXCLUDE_CONTAINS):
            continue

        yield path