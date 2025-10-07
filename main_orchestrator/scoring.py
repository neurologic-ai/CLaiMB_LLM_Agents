from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, Iterable, Tuple, Optional
import json
import re
from typing import List
from main_orchestrator.utils import _load_latest_inputs

CATEGORIES: Dict[str, Dict[str, List[str]]] = {
    "01. Technical Infrastructure": {"topics": [
        "cloud computing capabilities", "computing resources", "development environment",
        "integration architecture", "security infrastructure"
    ]},
    "02. Data Management & Quality": {"topics": [
        "data architecture", "data quality", "data governance", "data operations", "data accessibility"
    ]},
    "03. AI/ML Capabilities": {"topics": [
        "model development", "production deployment", "mlops maturity",
        "model governance", "advanced capabilities"
    ]},
    "04. Talent & Skills": {"topics": [
        "technical expertise", "domain knowledge", "team structure",
        "training and development", "recruitment and retention"
    ]},
    "05. Governance & Ethics": {"topics": [
        "ethical framework", "regulatory compliance", "risk management",
        "accountability structure", "transparency practices"
    ]},
    "06. Strategic Alignment": {"topics": [
        "business integration", "leadership support", "investment strategy",
        "innovation management", "partnership ecosystem"
    ]},
    "07. Cultural Readiness": {"topics": [
        "innovation mindset", "change management", "collaboration culture",
        "decision making", "learning environment"
    ]},
    "08. Process Maturity": {"topics": [
        "project management", "documentation practices", "quality assurance",
        "operational excellence", "measurement and metrics"
    ]},
    "09. Foundation Model Operations": {"topics": [
        "model integration and deployment", "domain adaptation and fine-tuning",
        "performance optimization", "risk and compliance management", "scaling and distribution"
    ]},
    "10. Generative AI Capabilities": {"topics": [
        "multi-modal generation", "quality control and validation", "creative workflow integration",
        "custom generation control", "domain-specific generation"
    ]},
    "11. Responsible AI & Social Impact": {"topics": [
        "algorithmic fairness and bias mitigation", "explainability and interpretability",
        "privacy and data protection", "ethical impact assessment", "human-AI collaboration"
    ]},
    "12. AI Business Value & ROI": {"topics": [
        "revenue generation and growth", "cost reduction and efficiency",
        "customer experience enhancement", "innovation and product development",
        "competitive advantage and market position"
    ]},
    "13. AI Risk & Resilience": {"topics": [
        "data reliability and robustness", "data dependency and vendor lock-in",
        "vendor and technology risks", "disaster recovery architecture",
        "regulatory and legal compliance"
    ]},
    "14. AI Ecosystem & External Integration": {"topics": [
        "supplier and vendor AI collaboration", "industry standards and consortiums",
        "academic and research partnerships", "regulatory and policy engagement"
    ]},
    "15. AI Leadership & Vision": {"topics": [
        "AI strategy and roadmap", "executive AI literacy", "organizational transformation",
        "future-proofing and adaptability", "thought leadership and industry influence"
    ]},
}

# ---------- AIMRI 15-category weights ----------
CATEGORY_WEIGHTS: Dict[str, float] = {
    "01. Technical Infrastructure": 10.0,
    "02. Data Management & Quality": 5.0,
    "03. AI/ML Capabilities": 20.0,
    "04. Talent & Skills": 5.0,
    "05. Governance & Ethics": 5.0,
    "06. Strategic Alignment": 5.0,
    "07. Cultural Readiness": 5.0,
    "08. Process Maturity": 5.0,
    "09. Foundation Model Operations": 5.0,
    "10. Generative AI Capabilities": 5.0,
    "11. Responsible AI & Social Impact": 5.0,
    "12. AI Business Value & ROI": 5.0,
    "13. AI Risk & Resilience": 5.0,
    "14. AI Ecosystem & External Integration": 5.0,
    "15. AI Leadership & Vision": 10.0,
}

# ---------- helpers  ----------
def _sort_key(label: str) -> tuple:
    if not isinstance(label, str):
        return (999, 999, str(label))
    nums = re.findall(r"\d+", label)
    if len(nums) == 0:
        return (999, 999, label)
    if len(nums) == 1:
        return (int(nums[0]), 0, label)
    if len(nums) >= 2:
        return (int(nums[0]), int(nums[1]), label)
    return (999, 999, label)

def _round2(x: float) -> float:
    return float(f"{x:.2f}")

def _is_metric_block(d: Any) -> bool:
    if not isinstance(d, dict):
        return False
    if "score" not in d:
        return False
    try:
        float(d["score"])
    except Exception:
        return False
    mappings = d.get("aimri") or d.get("aimri_mapping")
    return isinstance(mappings, list)

def _extract_metric_blocks_from_json(payload: Any) -> Iterable[Dict[str, Any]]:
    if isinstance(payload, dict):
        m = payload.get("metrics")
        if isinstance(m, dict):
            for v in m.values():
                if _is_metric_block(v):
                    yield v
        r = payload.get("results")
        if isinstance(r, dict):
            for v in r.values():
                if _is_metric_block(v):
                    yield v
        for v in payload.values():
            if _is_metric_block(v):
                yield v

def _normalize_mapping_item(item: Any) -> Tuple[str | None, str | None]:
    if not isinstance(item, dict):
        return (None, None)
    dim = item.get("dimension")
    sub = item.get("subsection")
    dim = dim.strip() if isinstance(dim, str) else None
    sub = sub.strip() if isinstance(sub, str) else None
    return (dim, sub)

def _aggregate_tree(inputs_root: Path) -> Dict[str, Any]:
    subsection_num: Dict[str, float] = {}
    subsection_den: Dict[str, float] = {}
    subsection_contribs: Dict[str, int] = {}

    dimension_num: Dict[str, float] = {}
    dimension_den: Dict[str, float] = {}
    dimension_contribs: Dict[str, int] = {}

    files = sorted(inputs_root.rglob("*.json"))
    metrics_seen = 0
    metrics_used = 0
    files_processed = 0

    for jf in files:
        try:
            data = json.loads(jf.read_text(encoding="utf-8", errors="ignore"))
            files_processed += 1
        except Exception:
            continue

        for metric in _extract_metric_blocks_from_json(data):
            metrics_seen += 1
            try:
                score = float(metric.get("score"))
            except Exception:
                continue

            mappings = metric.get("aimri") or metric.get("aimri_mapping")
            if not isinstance(mappings, list) or not mappings:
                continue

            subs_set = set()
            dims_set = set()
            for item in mappings:
                dim, sub = _normalize_mapping_item(item)
                if sub:
                    subs_set.add(sub)
                if dim:
                    dims_set.add(dim)

            k_subs = len(subs_set)
            k_dims = len(dims_set)

            if k_subs > 0:
                share = 1.0 / k_subs
                for sub in subs_set:
                    subsection_num[sub] = subsection_num.get(sub, 0.0) + score * share
                    subsection_den[sub] = subsection_den.get(sub, 0.0) + share
                    subsection_contribs[sub] = subsection_contribs.get(sub, 0) + 1

            if k_dims > 0:
                share = 1.0 / k_dims
                for dim in dims_set:
                    dimension_num[dim] = dimension_num.get(dim, 0.0) + score * share
                    dimension_den[dim] = dimension_den.get(dim, 0.0) + share
                    dimension_contribs[dim] = dimension_contribs.get(dim, 0) + 1

            if k_subs > 0 or k_dims > 0:
                metrics_used += 1

    subsections: Dict[str, Dict[str, float | int]] = {}
    for sub, den in subsection_den.items():
        if den > 0:
            score = subsection_num.get(sub, 0.0) / den
            subsections[sub] = {
                "score": _round2(score),
                "numerator": _round2(subsection_num.get(sub, 0.0)),
                "denominator": _round2(den),
                "metric_contributions": int(subsection_contribs.get(sub, 0)),
            }

    dimensions: Dict[str, Dict[str, float | int]] = {}
    for dim, den in dimension_den.items():
        if den > 0:
            score = dimension_num.get(dim, 0.0) / den
            dimensions[dim] = {
                "score": _round2(score),
                "numerator": _round2(dimension_num.get(dim, 0.0)),
                "denominator": _round2(den),
                "metric_contributions": int(dimension_contribs.get(dim, 0)),
            }

    return {
        "meta": {
            "inputs_root": str(inputs_root.resolve()),
            "files_processed": files_processed,
            "metrics_seen": metrics_seen,
            "metrics_used": metrics_used,
            "subsections_count": len(subsections),
            "dimensions_count": len(dimensions),
        },
        "subsections": {k: subsections[k] for k in sorted(subsections.keys(), key=_sort_key)},
        "dimensions":  {k: dimensions[k]  for k in sorted(dimensions.keys(),  key=_sort_key)},
    }

def _weighted_final(dimensions: Dict[str, Dict[str, Any]], weights: Dict[str, float]) -> Dict[str, Any]:
    final = 0.0
    breakdown = {}
    for dim, row in dimensions.items():
        s = float(row["score"])
        w = weights.get(dim, 0.0) / 100.0 
        final += s * w
        breakdown[dim] = {
            "score": s,
            "weight": round(w, 4),
            "weighted": round(s * w, 4),
        }
    return {"final_score": _round2(final), "breakdown": breakdown}

# ---------- Gap Aggregation Functions ----------
def _extract_gaps_from_metrics(payload: Any) -> Iterable[Tuple[str, str, List[str], str | None]]:
    """
    Extract gaps from agent metrics with their AIMRI mappings.
    Returns tuples of (dimension, subsection, gaps_list).
    """
    if isinstance(payload, dict):
        metrics = payload.get("metrics") or payload.get("results", {})
        if isinstance(metrics, dict):
            for metric in metrics.values():
                if not isinstance(metric, dict):
                    continue
                
                gaps = metric.get("gaps") or metric.get("gap")
                if not isinstance(gaps, list) or not gaps:
                    continue
                
                mappings = metric.get("aimri") or metric.get("aimri_mapping")
                if not isinstance(mappings, list) or not mappings:
                    continue
                metric_id = metric.get("metric_id") if isinstance(metric.get("metric_id"), str) else None
                
                for mapping in mappings:
                    dim, sub = _normalize_mapping_item(mapping)
                    if dim and gaps:
                        yield (dim, sub, gaps, metric_id)

def _aggregate_gaps_tree(inputs_root: Path) -> Dict[str, Any]:
    """
    Aggregate gaps by AIMRI dimension and subsection, similar to score aggregation.
    """
    dimension_gaps: Dict[str, List[str]] = {}
    subsection_gaps: Dict[str, List[str]] = {}
    dimension_contribs: Dict[str, int] = {}
    subsection_contribs: Dict[str, int] = {}
    # Track unique contributing metrics per dimension/subsection to avoid inflation across files/mappings
    dimension_seen_metrics: Dict[str, set] = {}
    subsection_seen_metrics: Dict[str, set] = {}
    
    files = sorted(inputs_root.rglob("*.json"))
    gaps_seen = 0
    gaps_used = 0
    files_processed = 0
    
    for jf in files:
        try:
            data = json.loads(jf.read_text(encoding="utf-8", errors="ignore"))
            files_processed += 1
        except Exception:
            continue
        
        # Try to infer agent name from file path: .../agents/<agent>/<artifact>.json
        try:
            agent_name = jf.parent.name
        except Exception:
            agent_name = None

        for dimension, subsection, gaps, metric_id in _extract_gaps_from_metrics(data):
            gaps_seen += len(gaps)
            
            # Clean and validate gaps
            clean_gaps = []
            for gap in gaps:
                if isinstance(gap, str) and gap.strip():
                    clean_gaps.append(gap.strip()[:300])  # Limit length
            
            if not clean_gaps:
                continue
            
            # Aggregate by dimension
            if dimension not in dimension_gaps:
                dimension_gaps[dimension] = []
                dimension_contribs[dimension] = 0
                dimension_seen_metrics[dimension] = set()
            dimension_gaps[dimension].extend(clean_gaps)
            # Increment contributor count only once per unique (agent:metric_id)
            if metric_id:
                key = f"{agent_name}:{metric_id}" if agent_name else metric_id
                if key not in dimension_seen_metrics[dimension]:
                    dimension_seen_metrics[dimension].add(key)
                    dimension_contribs[dimension] += 1
            
            # Aggregate by subsection
            if subsection:
                if subsection not in subsection_gaps:
                    subsection_gaps[subsection] = []
                    subsection_contribs[subsection] = 0
                    subsection_seen_metrics[subsection] = set()
                subsection_gaps[subsection].extend(clean_gaps)
                if metric_id:
                    key = f"{agent_name}:{metric_id}" if agent_name else metric_id
                    if key not in subsection_seen_metrics[subsection]:
                        subsection_seen_metrics[subsection].add(key)
                        subsection_contribs[subsection] += 1
            
            gaps_used += len(clean_gaps)
    
    # Deduplicate and sort gaps
    def _dedupe_and_sort(gaps_list: List[str]) -> List[str]:
        # Remove duplicates while preserving order
        seen = set()
        unique_gaps = []
        for gap in gaps_list:
            if gap not in seen:
                seen.add(gap)
                unique_gaps.append(gap)
        return unique_gaps[:10]  # Limit to top 10 gaps per category
    
    subsections: Dict[str, Dict[str, Any]] = {}
    for sub, gaps in subsection_gaps.items():
        if gaps:
            subsections[sub] = {
                "gaps": _dedupe_and_sort(gaps),
                "total_gaps": len(gaps),
                "metric_contributions": subsection_contribs.get(sub, 0),
            }
    
    dimensions: Dict[str, Dict[str, Any]] = {}
    for dim, gaps in dimension_gaps.items():
        if gaps:
            dimensions[dim] = {
                "gaps": _dedupe_and_sort(gaps),
                "total_gaps": len(gaps),
                "metric_contributions": dimension_contribs.get(dim, 0),
            }
    
    return {
        "meta": {
            "inputs_root": str(inputs_root.resolve()),
            "files_processed": files_processed,
            "gaps_seen": gaps_seen,
            "gaps_used": gaps_used,
            "subsections_count": len(subsections),
            "dimensions_count": len(dimensions),
        },
        "subsections": {k: subsections[k] for k in sorted(subsections.keys(), key=_sort_key)},
        "dimensions": {k: dimensions[k] for k in sorted(dimensions.keys(), key=_sort_key)},
    }

# ---------- Public scorer API (drop-in) ----------
class ScoringAgent:
    def __init__(self, *, category_weights: Dict[str, float] | None = None):
        self.category_weights = self._load_weights() or CATEGORY_WEIGHTS

    def _normalize_weights(self, w: Dict[str, Any]) -> Optional[Dict[str, float]]:
        try:
            cleaned: Dict[str, float] = {}
            for cat in CATEGORY_WEIGHTS.keys():
                if cat in w:
                    cleaned[cat] = float(w[cat])
                else:
                    cleaned[cat] = float(CATEGORY_WEIGHTS[cat])

            if any(v < 0 for v in cleaned.values()):
                return None

            total = sum(cleaned.values())
            if total == 0:
                return None

            # normalize to 100
            normalized = {k: (v / total) * 100.0 for k, v in cleaned.items()}
            return normalized
        except Exception:
            return None

    def _load_weights(self) -> Optional[Dict[str, float]]:
        latest = _load_latest_inputs() or {}
        rec = latest.get("category_weights")
        if not rec:
            return None

        path = rec.get("input_path")
        if not path or not Path(path).exists():
            return None

        try:
            raw = json.loads(Path(path).read_text(encoding="utf-8"))
        except Exception:
            return None

        normalized = self._normalize_weights(raw) if isinstance(raw, dict) else None
        return normalized

    def run_gaps(self, inputs_root: str | Path) -> Dict[str, Any]:
        """Run gap aggregation by AIMRI category."""
        root = Path(inputs_root)
        gaps_tree = _aggregate_gaps_tree(root)
        return gaps_tree



    def run(self, inputs_root: str | Path) -> Dict[str, Any]:
        self.category_weights = self._load_weights() or self.category_weights or CATEGORY_WEIGHTS
        root = Path(inputs_root)
        tree = _aggregate_tree(root)
        gaps_tree = _aggregate_gaps_tree(root)
        category_scores = {k: float(v["score"]) for k, v in tree["dimensions"].items()}
        wf = _weighted_final(tree["dimensions"], self.category_weights)
        overall = float(wf["final_score"])
        return {
            "overall_score": overall,
            "category_scores": category_scores,
            "category_gaps": gaps_tree["dimensions"],
            "details": {
                "weights_used": self.category_weights,
                "weighted_breakdown": wf["breakdown"],
                "subsections": tree["subsections"],
                "dimensions": tree["dimensions"],
                "gap_subsections": gaps_tree["subsections"],
                "meta": tree["meta"],
                "gaps_meta": gaps_tree["meta"],
            },
        }