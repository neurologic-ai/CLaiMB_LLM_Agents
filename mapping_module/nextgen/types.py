from __future__ import annotations
from dataclasses import dataclass
from typing import List


@dataclass
class AimriPoint:
    id: str
    name: str
    dimension: str
    aliases: List[str]

