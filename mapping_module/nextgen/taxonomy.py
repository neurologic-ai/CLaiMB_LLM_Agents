from __future__ import annotations
import json
from pathlib import Path
from typing import List
import yaml

from .types import AimriPoint


def load_taxonomy(path: str) -> List[AimriPoint]:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    points: List[AimriPoint] = []
    for p in data.get("points", []):
        points.append(
            AimriPoint(
                id=str(p["id"]),
                name=p["name"],
                dimension=p.get("dimension", ""),
                aliases=[a.lower() for a in (p.get("aliases") or [])],
            )
        )
    return points


def compact_taxonomy(points: List[AimriPoint]) -> str:
    minimal = [{"id": p.id, "name": p.name, "aliases": p.aliases} for p in points]
    return json.dumps(minimal, ensure_ascii=False, separators=(",", ":"))

