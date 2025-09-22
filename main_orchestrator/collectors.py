# main_orchestrator/collectors.py
from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from .feature_bus import FeatureBus

# Reuse your production adapters (they already normalize outputs & paths)
from main_orchestrator.adapters import (
    run_bi_adapter,
    run_code_repo_adapter,
    run_cloud_infra_adapter,
    run_data_platform_adapter,
    run_enterprise_adapter,
    run_mlops_adapter,
)

# ---------- Base ----------
class BaseCollector:
    def __init__(self, agent_name: str, bus: FeatureBus, artifacts_root: Path):
        self.agent_name = agent_name
        self.bus = bus
        self.artifacts_root = Path(artifacts_root)
        (self.artifacts_root / agent_name).mkdir(parents=True, exist_ok=True)

    def compute(self) -> Tuple[Dict[str, float], Optional[Dict[str, Any]]]:
        raise NotImplementedError

    def run(self) -> Dict[str, str]:
        scores, gaps = self.compute()
        if gaps is None:
            gaps = {}
        return self.bus.publish(self.agent_name, scores, gaps)
   
# ---------- Helpers ----------
def _is_num(x: Any) -> bool:
    try:
        float(x)
        return True
    except Exception:
        return False

def _scores_from_aggregates_or_payload(obj: Dict[str, Any]) -> Dict[str, float]:
    """
    Try to find category-level scores the same way your old orchestrator did.
    Supports shapes:
      - {"aggregates": {"per_category_1to5": {...}}}
      - {"aggregates": {"<cat>": number, ...}}
      - {"scores": {"categories": {...}}}  # Enterprise
    """
    if not isinstance(obj, dict):
        return {}

    # 1) Standard: aggregates.per_category_1to5
    agg = obj.get("aggregates")
    if isinstance(agg, dict):
        per_cat = agg.get("per_category_1to5")
        if isinstance(per_cat, dict):
            return {k: float(v) for k, v in per_cat.items() if _is_num(v)}
        # sometimes aggregates is already flat numbers
        if all(_is_num(v) for v in agg.values()):
            return {k: float(v) for k, v in agg.items()}

    # 2) Enterprise: scores.categories
    sc = obj.get("scores")
    if isinstance(sc, dict) and isinstance(sc.get("categories"), dict):
        return {k: float(v) for k, v in sc["categories"].items() if _is_num(v)}

    return {}

def _collect_gaps_from_metrics(metrics: Any, limit_per_key: int = 3, max_total: int = 20) -> Dict[str, list]:
    """
    Try to extract gap recommendations from agent metrics/results.
    Always return a dict (possibly empty) so gaps.json is written.
    """
    gaps: Dict[str, list] = {}

    # 1) Deep metric-level gaps
    if isinstance(metrics, dict):
        for mid, mv in metrics.items():
            if isinstance(mv, dict):
                gp = mv.get("gap") or mv.get("gaps")
                if isinstance(gp, list) and gp:
                    gaps[mid] = [str(x)[:200] for x in gp[:limit_per_key]]
                    if len(gaps) >= max_total:
                        break

    # 2) Top-level keys like BI's "gaps" or "recommendations"
    if not gaps and isinstance(metrics, dict):
        for k in ("gaps", "recommendations", "improvements"):
            gp = metrics.get(k)
            if isinstance(gp, list) and gp:
                gaps[k] = [str(x)[:200] for x in gp[:min(limit_per_key, len(gp))]]
                break

    return gaps 


# ---------- Concrete collectors (call your adapters) ----------
class CloudInfraCollector(BaseCollector):
    """Every 6h"""
    def __init__(self, bus: FeatureBus, artifacts_root: Path, *, batch_dir: str):
        super().__init__("cloud_infra", bus, artifacts_root)
        self.batch_dir = batch_dir

    def compute(self) -> Tuple[Dict[str, float], Optional[Dict[str, Any]]]:
        # Adapter writes a marker + the orchestrator writes detailed run files under runs_dir
        artifact, aggregates, metrics = run_cloud_infra_adapter(self.artifacts_root / self.agent_name, self.batch_dir)
        payload = {"artifact_path": artifact, "aggregates": aggregates, "metrics": metrics}
        scores = _scores_from_aggregates_or_payload(payload)
        gaps = _collect_gaps_from_metrics(metrics)
        return scores, gaps


class DataPlatformCollector(BaseCollector):
    """Every 12h"""
    def __init__(self, bus: FeatureBus, artifacts_root: Path):
        super().__init__("data_platform", bus, artifacts_root)

    def compute(self) -> Tuple[Dict[str, float], Optional[Dict[str, Any]]]:
        artifact, aggregates, metrics, *_maybe_extra = _safe_call_4(run_data_platform_adapter, self.artifacts_root / self.agent_name)
        payload = {"artifact_path": artifact, "aggregates": aggregates, "metrics": metrics}
        scores = _scores_from_aggregates_or_payload(payload)
        gaps = _collect_gaps_from_metrics(metrics)
        return scores, gaps


class MLOpsCollector(BaseCollector):
    """Every 4h"""
    def __init__(self, bus: FeatureBus, artifacts_root: Path):
        super().__init__("ml_ops", bus, artifacts_root)

    def compute(self) -> Tuple[Dict[str, float], Optional[Dict[str, Any]]]:
        artifact, aggregates, metrics = run_mlops_adapter(self.artifacts_root / self.agent_name)
        payload = {"artifact_path": artifact, "aggregates": aggregates, "metrics": metrics}
        scores = _scores_from_aggregates_or_payload(payload)
        gaps = _collect_gaps_from_metrics(metrics)
        return scores, gaps


class BITrackerCollector(BaseCollector):
    """Daily"""
    def __init__(self, bus: FeatureBus, artifacts_root: Path):
        super().__init__("bi_tracker", bus, artifacts_root)

    def compute(self) -> Tuple[Dict[str, float], Optional[Dict[str, Any]]]:
        artifact, aggregates, metrics, *_maybe_extra = _safe_call_4(run_bi_adapter, self.artifacts_root / self.agent_name)
        payload = {"artifact_path": artifact, "aggregates": aggregates, "metrics": metrics}
        scores = _scores_from_aggregates_or_payload(payload)
        gaps = _collect_gaps_from_metrics(metrics)
        return scores, gaps


class EnterpriseSystemsCollector(BaseCollector):
    """Every 8h"""
    def __init__(self, bus: FeatureBus, artifacts_root: Path):
        super().__init__("enterprise_systems", bus, artifacts_root)

    def compute(self) -> Tuple[Dict[str, float], Optional[Dict[str, Any]]]:
        artifact, aggregates_like, metrics = run_enterprise_adapter(self.artifacts_root / self.agent_name)
        payload = {"artifact_path": artifact, "scores": aggregates_like, "metrics": metrics}
        scores = _scores_from_aggregates_or_payload(payload)
        gaps = _collect_gaps_from_metrics(metrics)
        return scores, gaps


class CodeRepoCollector(BaseCollector):
    """Daily"""
    def __init__(self, bus: FeatureBus, artifacts_root: Path, *, repo_path_or_url: str):
        super().__init__("code_repo", bus, artifacts_root)
        self.repo = repo_path_or_url

    def compute(self) -> Tuple[Dict[str, float], Optional[Dict[str, Any]]]:
        artifact, aggregates, metrics, *_maybe_extra = _safe_call_4(
            run_code_repo_adapter, self.artifacts_root / self.agent_name, self.repo
        )
        payload = {"artifact_path": artifact, "aggregates": aggregates, "metrics": metrics}
        scores = _scores_from_aggregates_or_payload(payload)
        gaps = _collect_gaps_from_metrics(metrics)
        return scores, gaps


# --- small adapter-result helper: tolerate 3-tuple or 4-tuple returns
def _safe_call_4(fn, *args):
    out = fn(*args)
    if isinstance(out, tuple) and len(out) == 3:
        a, b, c = out
        return a, b, c, {}
    return out


# ---------- Factory ----------
def build_collectors(
    bus: FeatureBus,
    *,
    artifacts_root: str | Path,
    cloud_batch_dir: str,
    code_repo: str,
) -> Dict[str, BaseCollector]:
    root = Path(artifacts_root)
    return {
        "cloud_infra": CloudInfraCollector(bus, root, batch_dir=cloud_batch_dir),
        "data_platform": DataPlatformCollector(bus, root),
        "ml_ops": MLOpsCollector(bus, root),
        "bi_tracker": BITrackerCollector(bus, root),
        "enterprise_systems": EnterpriseSystemsCollector(bus, root),
        "code_repo": CodeRepoCollector(bus, root, repo_path_or_url=code_repo),
    }