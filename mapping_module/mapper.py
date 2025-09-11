from __future__ import annotations
from typing import Dict, List, Any, Optional
from pathlib import Path
from loguru import logger

from .base_agent import BaseMicroAgent
from .io_utils import load_aimri_points, load_metric_yaml, ensure_dir, write_python_mapping, var_name_for_agent, build_labels
from . import prompts
# --- add near the top of mapper.py, after imports ---
from .base_agent import BaseMicroAgent
import os
from dotenv import load_dotenv
load_dotenv()

api_key=os.getenv("OPENAI_API_KEY")

class _AdapterAgent(BaseMicroAgent):
    """Concrete wrapper exposing .call(...) while using env OPENAI_API_KEY via BaseMicroAgent."""
    def __init__(self, model: str = "gpt-4o-mini"):
        super().__init__(model=model,api_key=api_key)  # DO NOT pass api_key; BaseMicroAgent will use env

    def evaluate(self, code_snippets: List[str], context: Optional[Dict] = None) -> Dict[str, Any]:
        # Not used by this pipeline; required to satisfy ABC.
        return {}

    def call(self, *, system: str, user: str, expect_json: bool = False, max_tokens: int = 900):
        text = self._call_llm(prompt=user, system_prompt=system, max_tokens=max_tokens)
        return self._parse_json_response(text) if expect_json else text

class DescriptionElaborator:
    def __init__(self, model: str = "gpt-4o-mini", agent_key: str = "generic"):
        # self.agent = BaseMicroAgent(model=model)
        self.agent = _AdapterAgent(model=model)
        self.agent_key = agent_key

    def elaborate(self, metric: Dict[str, Any]) -> str:
        metric_id = metric.get("id","?")
        name = metric.get("name","")
        desc = metric.get("description","")
        sys = prompts.get_elaborate_system(self.agent_key)
        user = prompts.elaborate_user(metric_id, name, desc)
        out = self.agent.call(system=sys, user=user, expect_json=True)
        logger.debug(out)
        if isinstance(out, dict):
            return out.get("elaborated_description", desc or name)
        return str(out).strip() or desc or name

class AimriMapper:
    def __init__(self, aimri_points: List[Dict[str, str]], model: str = "gpt-4o-mini", agent_key: str = "generic"):
        # self.agent = BaseMicroAgent(model=model)
        self.agent = _AdapterAgent(model=model)
        self._index: Dict[str, Dict[str, str]] = {p["id"]: p for p in aimri_points}
        self.agent_key = agent_key

    def map_metric(self, metric_id: str, name: str, elaborated: str) -> List[Dict[str,str]]:
        sys = prompts.get_map_system(self.agent_key)
        catalog = list(self._index.values())
        user = prompts.map_user(metric_id, name, elaborated, catalog)
        result = self.agent.call(system=sys, user=user, expect_json=True)

        # Expected shape:
        # {"metric_id": "...", "mappings": [{"dimension": "...", "subsection": "...", "confidence": 0.0, "rationale": "..."}]}
        mappings: List[Dict[str,str]] = []
        if isinstance(result, dict):
            raw = result.get("mappings") or []
            # Sort by confidence desc if present
            try:
                raw = sorted(raw, key=lambda x: float(x.get("confidence", 0.0)), reverse=True)
            except Exception:
                pass
            # Log confidence & rationale, but DO NOT change output format
            for entry in raw:
                dim = entry.get("dimension")
                sub = entry.get("subsection")
                conf = entry.get("confidence")
                rat = entry.get("rationale")
                if conf is not None or rat is not None:
                    logger.debug(f"[{metric_id}] candidate: {dim} / {sub} | conf={conf} | why={rat}")
                if dim and sub:
                    mappings.append({"dimension": dim, "subsection": sub})
        if not mappings:
            text = str(result)
            hinted_ids = []
            for k in self._index.keys():
                if k in text:
                    hinted_ids.append(k)
            hinted_ids = hinted_ids[:5]
            for hid in hinted_ids:
                dim, sub = build_labels(self._index[hid])
                mappings.append({"dimension": dim, "subsection": sub})
        return mappings[:5]

def process_yaml(
    yaml_path: str | Path,
    aimri_path: str | Path,
    out_dir: str | Path,
    model: str = "gpt-4o-mini"
) -> Path:
    logger.info(f"Processing YAML: {yaml_path}")
    aimri = load_aimri_points(aimri_path)
    metrics = load_metric_yaml(yaml_path)

    agent_key = Path(yaml_path).stem  # cloud_infra / bi_tracker / enterprise_system
    elaborator = DescriptionElaborator(model=model, agent_key=agent_key)
    mapper = AimriMapper(aimri, model=model, agent_key=agent_key)

    out_map: Dict[str, List[Dict[str,str]]] = {}
    for m in metrics:
        mid = m.get("id")
        if not mid:
            continue
        name = m.get("name","")
        elaborated = elaborator.elaborate(m)
        mappings = mapper.map_metric(mid, name, elaborated)
        out_map[mid] = mappings
        logger.debug(f"{mid} → {mappings}")

    var_name = var_name_for_agent(agent_key)
    ensure_dir(out_dir)
    out_path = Path(out_dir) / f"{agent_key}.py"
    write_python_mapping(out_path, var_name, out_map)
    logger.info(f"Wrote {out_path}")
    return out_path
