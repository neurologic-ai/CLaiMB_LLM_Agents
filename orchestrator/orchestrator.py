# orchestrator/orchestrator.py
import argparse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict

from orchestrator.models import AgentSpec, AgentResult
from orchestrator.adapters import (
    run_bi_adapter, run_code_repo_adapter, run_cloud_infra_adapter,
    run_data_platform_adapter, run_enterprise_adapter, run_mlops_adapter
)
from orchestrator.utils import now_utc_str, write_json
from orchestrator.scoring import aggregate_tree, weighted_final

class Orchestrator:
    def __init__(self, out_dir="orchestrator_output"):
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)

    def run_all(self, specs: Dict[str, AgentSpec], repo: str="", batch: str="") -> Path:
        run_id = f"mvp-{now_utc_str()}"
        per_agent_dir = self.out_dir / "agents"
        per_agent_dir.mkdir(parents=True, exist_ok=True)

        results: Dict[str, AgentResult] = {}

        with ThreadPoolExecutor(max_workers=4) as ex:
            futures = {}
            if specs["bi_tracker"].enabled:
                futures[ex.submit(run_bi_adapter, per_agent_dir / "bi_tracker")] = "bi_tracker"
            if specs["code_repo"].enabled:
                futures[ex.submit(run_code_repo_adapter, per_agent_dir / "code_repo", repo)] = "code_repo"
            if specs["cloud_infra"].enabled:
                futures[ex.submit(run_cloud_infra_adapter, per_agent_dir / "cloud_infra", batch)] = "cloud_infra"
            if specs["data_platform"].enabled:
                futures[ex.submit(run_data_platform_adapter, per_agent_dir / "data_platform")] = "data_platform"
            if specs["enterprise"].enabled:
                futures[ex.submit(run_enterprise_adapter, per_agent_dir / "enterprise")] = "enterprise"

            for fut in as_completed(futures):
                name = futures[fut]
                try:
                    artifact, aggregates, metrics = fut.result()
                    results[name] = AgentResult(name, True, artifact, aggregates, metrics, None, 0.0)
                except Exception as e:
                    results[name] = AgentResult(name, False, None, None, None, str(e), 0.0)

        # Run mlops last (logger collisions)
        if specs["ml_ops"].enabled:
            try:
                artifact, aggregates, metrics = run_mlops_adapter(per_agent_dir / "ml_ops")
                results["ml_ops"] = AgentResult("ml_ops", True, artifact, aggregates, metrics, None, 0.0)
            except Exception as e:
                results["ml_ops"] = AgentResult("ml_ops", False, None, None, None, str(e), 0.0)
        
        # ---- SCORING ----
        scoring_result = aggregate_tree(per_agent_dir)

        # equal weights unless configured
        weights = {dim: 1.0 for dim in scoring_result["dimensions"].keys()}
        final = weighted_final(scoring_result["dimensions"], weights)
        scoring_result["aimri_weighted"] = final
        scoring_result["weights"] = weights

        # Persist scoring JSON
        scoring_path = self.out_dir / f"aimri_scores_{run_id}.json"
        write_json(scoring_path, scoring_result)

        # ---- COMBINED MASTER ----
        combined = {
            "run_id": run_id,
            "started_at": now_utc_str(),
            "agents": {k: vars(v) for k, v in results.items()},
            "scoring": str(scoring_path),   # path to AIMRI scoring
        }
        combined_path = self.out_dir / f"all_agents_{run_id}.json"
        write_json(combined_path, combined)

        return combined_path


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Run all MVP agents and produce a combined JSON artifact.")
    p.add_argument("--bi-enabled", action="store_true")
    p.add_argument("--code-enabled", action="store_true")
    p.add_argument("--cloud-enabled", action="store_true")
    p.add_argument("--data-enabled", action="store_true")
    p.add_argument("--enterprise-enabled", action="store_true")
    p.add_argument("--mlops-enabled", action="store_true")
    p.add_argument("--code-repo", default="", help="Git URL or local repo path")
    p.add_argument("--cloud-batch", default="", help="Batch dir for Cloud Infra")
    p.add_argument("--out-dir", default="orchestrator_output", help="Where to save outputs")
    return p

def main():
    args = build_parser().parse_args()
    specs = {
        "bi_tracker": AgentSpec("bi_tracker", args.bi_enabled, 900, 1),
        "code_repo": AgentSpec("code_repo", args.code_enabled, 1800, 1),
        "cloud_infra": AgentSpec("cloud_infra", args.cloud_enabled, 1800, 1),
        "data_platform": AgentSpec("data_platform", args.data_enabled, 1800, 1),
        "enterprise": AgentSpec("enterprise", args.enterprise_enabled, 1200, 1),
        "ml_ops": AgentSpec("ml_ops", args.mlops_enabled, 1800, 1),
    }

    orch = Orchestrator(out_dir=args.out_dir)
    combined_path = orch.run_all(specs, repo=args.code_repo, batch=args.cloud_batch)
    print(f"✅ Orchestration complete. Results saved at: {combined_path}")

if __name__ == "__main__":
    main()