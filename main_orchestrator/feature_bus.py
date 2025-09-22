from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

def utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

class FeatureBus:
    
    def __init__(self, root: str | Path = "./bus"):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _adir(self, agent: str) -> Path:
        p = self.root / agent
        p.mkdir(parents=True, exist_ok=True)
        return p

    def publish(
        self,
        agent: str,
        scores: Dict[str, float],
        gaps: Optional[Dict[str, Any]] = None,
        run_id: Optional[str] = None,
    ) -> Dict[str, str]:
        adir = self._adir(agent)
        (adir / "scores.json").write_text(json.dumps(scores, indent=2, ensure_ascii=False))
        if gaps is not None:
            (adir / "gaps.json").write_text(json.dumps(gaps, indent=2, ensure_ascii=False))
        sign = {"agent": agent, "ts": utc_iso(), "run_id": run_id or f"{agent}-{datetime.utcnow().timestamp():.0f}"}
        (adir / "sign.json").write_text(json.dumps(sign, indent=2, ensure_ascii=False))
        return {
            "scores": str(adir / "scores.json"),
            "gaps": str(adir / "gaps.json"),
            "sign": str(adir / "sign.json"),
        }

    def read_json(self, agent: str, name: str) -> Any:
        p = self._adir(agent) / name
        return json.loads(p.read_text()) if p.exists() else None

    def read_sign_ts(self, agent: str) -> Optional[str]:
        sign = self.read_json(agent, "sign.json")
        return sign.get("ts") if sign else None

    def read_scores(self, agent: str) -> Dict[str, float]:
        return self.read_json(agent, "scores.json") or {}