# orchestrator/orchestrator.py
import argparse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Optional

from orchestrator.models import AgentSpec, AgentResult
from orchestrator.adapters import (
    run_bi_adapter, run_code_repo_adapter, run_cloud_infra_adapter,
    run_data_platform_adapter, run_enterprise_adapter, run_mlops_adapter
)
from orchestrator.utils import now_utc_str, write_json
from orchestrator.scoring import aggregate_tree, weighted_final
from orchestrator.utils import _parse_weights_arg

class Orchestrator:
    def __init__(self, out_dir: str = "orchestrator_output", max_workers: int = 4):
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.max_workers = max_workers

    def run_all(
        self,
        specs: Dict[str, AgentSpec],
        repo: str = "",
        batch: str = "",
        weights_raw: Optional[str] = None,
    ) -> Dict[str, str]:
        run_id = f"mvp-{now_utc_str()}"
        per_agent_dir = self.out_dir / "agents"
        per_agent_dir.mkdir(parents=True, exist_ok=True)

        results: Dict[str, AgentResult] = {}

        # --- Run the 5 non-mlops agents in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as ex:
            futures = {}
            if specs.get("bi_tracker", AgentSpec("bi_tracker", False, 0, 0)).enabled:
                futures[ex.submit(run_bi_adapter, per_agent_dir / "bi_tracker")] = "bi_tracker"
            if specs.get("code_repo", AgentSpec("code_repo", False, 0, 0)).enabled:
                futures[ex.submit(run_code_repo_adapter, per_agent_dir / "code_repo", repo)] = "code_repo"
            if specs.get("cloud_infra", AgentSpec("cloud_infra", False, 0, 0)).enabled:
                futures[ex.submit(run_cloud_infra_adapter, per_agent_dir / "cloud_infra", batch)] = "cloud_infra"
            if specs.get("data_platform", AgentSpec("data_platform", False, 0, 0)).enabled:
                futures[ex.submit(run_data_platform_adapter, per_agent_dir / "data_platform")] = "data_platform"
            if specs.get("enterprise", AgentSpec("enterprise", False, 0, 0)).enabled:
                futures[ex.submit(run_enterprise_adapter, per_agent_dir / "enterprise")] = "enterprise"

            for fut in as_completed(futures):
                name = futures[fut]
                try:
                    artifact, aggregates, metrics = fut.result()
                    results[name] = AgentResult(
                        name=name, ok=True, artifact_path=artifact, aggregates=aggregates,
                        metrics=metrics, error=None, duration_sec=0.0
                    )
                except Exception as e:
                    results[name] = AgentResult(
                        name=name, ok=False, artifact_path=None, aggregates=None,
                        metrics=None, error=str(e), duration_sec=0.0
                    )

        # --- Run ml_ops last (avoids logger collisions)
        if specs.get("ml_ops", AgentSpec("ml_ops", False, 0, 0)).enabled:
            try:
                artifact, aggregates, metrics = run_mlops_adapter(per_agent_dir / "ml_ops")
                results["ml_ops"] = AgentResult(
                    name="ml_ops", ok=True, artifact_path=artifact, aggregates=aggregates,
                    metrics=metrics, error=None, duration_sec=0.0
                )
            except Exception as e:
                results["ml_ops"] = AgentResult(
                    name="ml_ops", ok=False, artifact_path=None, aggregates=None,
                    metrics=None, error=str(e), duration_sec=0.0
                )

        # --- SCORING
        scoring_result = aggregate_tree(per_agent_dir)
        dims = scoring_result.get("dimensions", {})
        weights = _parse_weights_arg(weights_raw, dims)

        if dims:
            final = weighted_final(dims, weights)
            scoring_result["aimri_weighted"] = final
            scoring_result["weights"] = weights
        else:
            # No dimensions found → produce a minimal scoring artifact
            scoring_result["aimri_weighted"] = {"final_score": 0.0, "breakdown": {}}
            scoring_result["weights"] = {}

        scoring_path = self.out_dir / f"aimri_scores_{run_id}.json"
        write_json(scoring_path, scoring_result)

        # --- COMBINED MASTER
        combined = {
            "run_id": run_id,
            "started_at": now_utc_str(),
            "agents": {k: vars(v) for k, v in results.items()},
            "scoring_path": str(scoring_path),
        }
        combined_path = self.out_dir / f"all_agents_{run_id}.json"
        write_json(combined_path, combined)

        return {
            "combined_path": str(combined_path),
            "scoring_path": str(scoring_path),
        }


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Run all MVP agents and produce a combined JSON artifact + weighted AIMRI score.")
    # enable/disable
    p.add_argument("--bi-enabled", action="store_true")
    p.add_argument("--code-enabled", action="store_true")
    p.add_argument("--cloud-enabled", action="store_true")
    p.add_argument("--data-enabled", action="store_true")
    p.add_argument("--enterprise-enabled", action="store_true")
    p.add_argument("--mlops-enabled", action="store_true")
    # params
    p.add_argument("--code-repo", default="", help="Git URL or local repo path")
    p.add_argument("--cloud-batch", default="", help="Batch dir for Cloud Infra")
    p.add_argument("--out-dir", default="orchestrator_output", help="Where to save outputs")
    p.add_argument("--max-workers", type=int, default=4, help="Parallel workers for non-mlops agents")
    # NEW: user weights
    p.add_argument(
        "--weights",
        default="",
        help="Optional weights like '01. Technical Infrastructure=10,02. Data Management & Quality=20'. "
             "Keys must match the 'dimensions' names discovered in outputs.",
    )
    return p


def main():
    args = build_parser().parse_args()
    specs = {
        "bi_tracker":  AgentSpec("bi_tracker", args.bi_enabled,        900,  1),
        "code_repo":   AgentSpec("code_repo", args.code_enabled,       1800, 1),
        "cloud_infra": AgentSpec("cloud_infra", args.cloud_enabled,    1800, 1),
        "data_platform": AgentSpec("data_platform", args.data_enabled, 1800, 1),
        "enterprise":  AgentSpec("enterprise", args.enterprise_enabled, 1200, 1),
        "ml_ops":      AgentSpec("ml_ops", args.mlops_enabled,         1800, 1),
    }

    orch = Orchestrator(out_dir=args.out_dir, max_workers=args.max_workers)
    paths = orch.run_all(
        specs,
        repo=args.code_repo,
        batch=args.cloud_batch,
        weights_raw=args.weights,
    )
    print(f"✅ Orchestration complete.\n  Combined: {paths['combined_path']}\n  Scoring:  {paths['scoring_path']}")


if __name__ == "__main__":
    main()