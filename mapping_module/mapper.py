from __future__ import annotations
import json
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


# --- PATCH START: helper to write aggregated raw files per agent ---
def _write_agent_raw_files(pkg_root: Path, agent_key: str, raw_elab: List[Dict[str, Any]], raw_map: List[Dict[str, Any]]) -> None:
    out_dir = pkg_root / "raw_llm_outputs" / agent_key
    out_dir.mkdir(parents=True, exist_ok=True)

    elab_path = out_dir / "elaboration.json"
    map_path = out_dir / "mapping.json"

    # Save EXACT model JSON objects if available; if parsing failed, we keep 'raw_text' for that item.
    elab_payload = {
        "agent": agent_key,
        "kind": "elaboration",
        "items": raw_elab,  # list of {"metric_id", "model", "system", "user", "json"|{}, "raw_text"|None}
    }
    map_payload = {
        "agent": agent_key,
        "kind": "mapping",
        "items": raw_map,
    }

    elab_path.write_text(json.dumps(elab_payload, indent=2, ensure_ascii=False), encoding="utf-8")
    map_path.write_text(json.dumps(map_payload, indent=2, ensure_ascii=False), encoding="utf-8")
# --- PATCH END ---


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
    def __init__(self, model: str = "gpt-4o-mini", agent_key: str = "generic", raw_dir: Optional[Path] = None):
        self.agent = _AdapterAgent(model=model)
        self.agent_key = agent_key
        self.raw_dir = raw_dir
        # --- PATCH START: holder for raw LLM output (per call) ---
        self.last_raw: Optional[Dict[str, Any]] = None
        # --- PATCH END ---

    def elaborate(self, metric: Dict[str, Any]) -> str:
        metric_id = metric.get("id","?")
        name = metric.get("name","")
        desc = metric.get("description","")

        sys = prompts.get_elaborate_system(self.agent_key)
        # fn = metric.get("function")
        # if hasattr(prompts, "elaborate_user_code_repo") and self.agent_key == "code_repo" and fn:
        #     user = prompts.elaborate_user_code_repo(metric_id, name, desc, fn)
        # else:
        #     user = prompts.elaborate_user(metric_id, name, desc)
        user = prompts.elaborate_user(metric_id, name, desc)

        # Get raw text from LLM (exact output text)
        raw_text = self.agent.call(system=sys, user=user, expect_json=False)
        parsed = self.agent._parse_json_response(raw_text) if isinstance(raw_text, str) else {}

        # --- PATCH START: store raw packet for aggregation ---
        self.last_raw = {
            "metric_id": metric_id,
            "model": self.agent.model,
            "system": sys,
            "user": user,
            # exact JSON as parsed object if possible; if parsing failed, keep raw_text
            "json": parsed if isinstance(parsed, (dict, list)) else {},
            "raw_text": raw_text if not isinstance(parsed, (dict, list)) else None,
        }
        # --- PATCH END ---

        if isinstance(parsed, dict):
            return parsed.get("elaborated_description", desc or name)
        return str(parsed).strip() or desc or name


class AimriMapper:
    def __init__(self, aimri_points: List[Dict[str, str]], model: str = "gpt-4o-mini", agent_key: str = "generic", raw_dir: Optional[Path] = None):
        self.agent = _AdapterAgent(model=model)
        self._index: Dict[str, Dict[str, str]] = {p["id"]: p for p in aimri_points}
        self.agent_key = agent_key
        self.raw_dir = raw_dir
        # --- PATCH START: holder for raw LLM output (per call) ---
        self.last_raw: Optional[Dict[str, Any]] = None
        # --- PATCH END ---

    def map_metric(self, metric_id: str, name: str, elaborated: str) -> List[Dict[str,str]]:
        sys = prompts.get_map_system(self.agent_key)
        catalog = list(self._index.values())
        user = prompts.map_user(metric_id, name, elaborated, catalog)

        # Get raw text from LLM (exact output text)
        raw_text = self.agent.call(system=sys, user=user, expect_json=False)
        parsed = self.agent._parse_json_response(raw_text)

        # --- PATCH START: store raw packet for aggregation ---
        self.last_raw = {
            "metric_id": metric_id,
            "model": self.agent.model,
            "system": sys,
            "user": user,
            "json": parsed if isinstance(parsed, (dict, list)) else {},
            "raw_text": raw_text if not isinstance(parsed, (dict, list)) else None,
        }
        # --- PATCH END ---

        mappings: List[Dict[str,str]] = []
        if isinstance(parsed, dict):
            raw = parsed.get("mappings") or []
            try:
                raw = sorted(raw, key=lambda x: float(x.get("confidence", 0.0)), reverse=True)
            except Exception:
                pass
            for entry in raw:
                dim = entry.get("dimension")
                sub = entry.get("subsection")
                if dim and sub:
                    mappings.append({"dimension": dim, "subsection": sub})

        if not mappings:
            text = str(parsed)
            hinted_ids = [k for k in self._index.keys() if k in text][:5]
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

    agent_key = Path(yaml_path).stem  # cloud_infra / bi_tracker / enterprise_system / code_repo

    # --- PATCH START: prepare aggregation lists + raw output dir ---
    pkg_root = Path(yaml_path).resolve().parent.parent  # <pkg>
    raw_dir = ensure_dir(pkg_root / "raw_llm_outputs" / agent_key)
    raw_elab_items: List[Dict[str, Any]] = []
    raw_map_items: List[Dict[str, Any]] = []
    # --- PATCH END ---

    elaborator = DescriptionElaborator(model=model, agent_key=agent_key)
    mapper = AimriMapper(aimri, model=model, agent_key=agent_key)

    out_map: Dict[str, List[Dict[str,str]]] = {}
    for m in metrics:
        mid = m.get("id")
        if not mid:
            continue
        name = m.get("name","")

        elaborated = elaborator.elaborate(m)
        # --- PATCH START: collect raw elaboration packet ---
        if elaborator.last_raw:
            raw_elab_items.append(elaborator.last_raw)
        # --- PATCH END ---

        mappings = mapper.map_metric(mid, name, elaborated)
        out_map[mid] = mappings
        logger.debug(f"{mid} → {mappings}")

        # --- PATCH START: collect raw mapping packet ---
        if mapper.last_raw:
            raw_map_items.append(mapper.last_raw)
        # --- PATCH END ---

    var_name = var_name_for_agent(agent_key)
    ensure_dir(out_dir)
    out_path = Path(out_dir) / f"{agent_key}.py"
    write_python_mapping(out_path, var_name, out_map)
    logger.info(f"Wrote {out_path}")

    # --- PATCH START: write one raw file per agent for elaboration & mapping ---
    (raw_dir / "elaboration.json").write_text(
        json.dumps({"agent": agent_key, "kind": "elaboration", "items": raw_elab_items}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (raw_dir / "mapping.json").write_text(
        json.dumps({"agent": agent_key, "kind": "mapping", "items": raw_map_items}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    logger.info(f"Wrote raw LLM outputs → {raw_dir}/elaboration.json and {raw_dir}/mapping.json")
    # --- PATCH END ---

    return out_path
