# from __future__ import annotations
# import json
# from pathlib import Path
# from typing import List, Dict, Any, Tuple
# import yaml

# def load_aimri_points(path: str | Path) -> List[Dict[str, str]]:
#     data = json.loads(Path(path).read_text(encoding="utf-8"))
#     return data.get("aimri_points", [])

# def load_metric_yaml(path: str | Path) -> List[Dict[str, Any]]:
#     content = Path(path).read_text(encoding="utf-8")
#     items = list(yaml.safe_load_all(content))
#     if len(items) == 1 and isinstance(items[0], list):
#         return items[0]
#     out: List[Dict[str, Any]] = []
#     for it in items:
#         if isinstance(it, list):
#             out.extend(it)
#         elif isinstance(it, dict):
#             out.append(it)
#     return out

# def ensure_dir(p: str | Path) -> Path:
#     path = Path(p)
#     path.mkdir(parents=True, exist_ok=True)
#     return path

# def write_python_mapping(out_path: str | Path, var_name: str, mapping: Dict[str, List[Dict[str,str]]]) -> None:
#     content = [
#         "from __future__ import annotations",
#         "from typing import Dict, List",
#         "",
#         f"{var_name}: Dict[str, List[dict]] = {{"
#     ]
#     for mid, lst in mapping.items():
#         content.append(f'    "{mid}": [')
#         for m in lst:
#             dim = m.get("dimension","").replace('"','\"')
#             sub = m.get("subsection","").replace('"','\"')
#             content.append(f'        {{"dimension": "{dim}",   "subsection": "{sub}"}},')
#         if lst:
#             content[-1] = content[-1].rstrip(",")
#         content.append("    ],")
#     if mapping:
#         content[-1] = content[-1].rstrip(",")
#     content.append("}")
#     Path(out_path).write_text("\n".join(content) + "\n", encoding="utf-8")

# def var_name_for_agent(agent_key: str) -> str:
#     key = agent_key.strip().upper().replace("-", "_")
#     return f"{key}_METRIC_TO_AIMRI"

# def build_labels(aimri_item: Dict[str, str]) -> Tuple[str, str]:
#     ident = aimri_item.get("id","")
#     category = aimri_item.get("category","").strip()
#     name = aimri_item.get("name","").strip()
#     try:
#         major = int(float(ident.split(".")[0]))
#         minor = ident.split(".")[1]
#     except Exception:
#         major, minor = 0, "0"
#     dim = f"{major:02d}. {category}"
#     sub = f"{major}.{minor} {name}"
#     return dim, sub
# mapping_module2/io_utils.py
# mapping_module2/io_utils.py
from __future__ import annotations
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple
import yaml

# ---------- AIMRI (JSON) ----------
def load_aimri_points(path: str | Path) -> List[Dict[str, str]]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return data.get("aimri_points", [])

# ---------- Metrics (YAML) ----------
def load_metric_yaml(path: str | Path) -> List[Dict[str, Any]]:
    """
    Load metrics YAML. Supports two shapes (NO recursion, no double-counting):
      1) { metrics: [ {id, name, description, ...}, ... ] }
      2) [ {id, name, description, ...}, ... ]
    """
    content = Path(path).read_text(encoding="utf-8")
    doc = yaml.safe_load(content)

    # Case 1: dict with 'metrics'
    if isinstance(doc, dict) and "metrics" in doc:
        lst = doc["metrics"]
        if isinstance(lst, list):
            return lst

    # Case 2: top-level list
    if isinstance(doc, list):
        return doc

    # Nothing recognized
    return []

# ---------- FS helpers ----------
def ensure_dir(p: str | Path) -> Path:
    path = Path(p)
    path.mkdir(parents=True, exist_ok=True)
    return path

def write_python_mapping(out_path: str | Path, var_name: str,
                         mapping: Dict[str, List[Dict[str, str]]]) -> None:
    """
    Write output in the same format as your sample: a top-level CONST dict of
    metric_id -> [{dimension, subsection}, ...]
    """
    lines: List[str] = []
    lines.append("from __future__ import annotations")
    lines.append("from typing import Dict, List")
    lines.append("")
    lines.append(f"{var_name}: Dict[str, List[dict]] = {{")
    for mid, lst in mapping.items():
        lines.append(f'    "{mid}": [')
        for m in lst:
            dim = (m.get("dimension") or "").replace('"', '\\"')
            sub = (m.get("subsection") or "").replace('"', '\\"')
            lines.append(f'        {{"dimension": "{dim}", "subsection": "{sub}"}},')
        if lst:
            # remove trailing comma from last entry
            lines[-1] = lines[-1].rstrip(",")
        lines.append("    ],")
    if mapping:
        lines[-1] = lines[-1].rstrip(",")
    lines.append("}")
    Path(out_path).write_text("\n".join(lines) + "\n", encoding="utf-8")

def var_name_for_agent(agent_key: str) -> str:
    key = agent_key.strip().upper().replace("-", "_")
    return f"{key}_METRIC_TO_AIMRI"

def build_labels(aimri_item: Dict[str, str]) -> Tuple[str, str]:
    """
    Build:
      - dimension: "02. Data Management & Quality"
      - subsection: "2.3 Data Governance"
    from an AIMRI item with fields: id="2.3", category="Data Management & Quality", name="Data Governance"
    """
    ident = (aimri_item.get("id") or "").strip()
    category = (aimri_item.get("category") or "").strip()
    name = (aimri_item.get("name") or "").strip()
    try:
        major = int(float(ident.split(".")[0]))
        minor = ident.split(".")[1]
    except Exception:
        major, minor = 0, "0"
    dim = f"{major:02d}. {category}"
    sub = f"{major}.{minor} {name}"
    return dim, sub
