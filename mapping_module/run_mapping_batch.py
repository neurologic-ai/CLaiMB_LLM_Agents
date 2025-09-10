import csv
import json
import os
import sys
import argparse
from pathlib import Path

from mapping_module.mapper import AimriMapperAgent
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

def main():
    parser = argparse.ArgumentParser(description="Run AIMRI mapping for metrics CSV")
    parser.add_argument(
        "--csv",
        default="mapping_module/csv/metrics.csv",
        help="Path to input CSV (default: csv/metrics.csv)",
    )
    parser.add_argument(
        "--taxonomy",
        default="mapping_module/aimri_points.yaml",
        help="Path to AIMRI taxonomy YAML (default: mapping_module/aimri_points.yaml)",
    )
    parser.add_argument(
        "--outdir",
        default="mapping_module/outputs",
        help="Folder for outputs (default: outputs/)",
    )

    args = parser.parse_args()

    in_csv = Path(args.csv)
    taxonomy_yaml = Path(args.taxonomy)
    out_dir = Path(args.outdir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # output file name based on csv name
    out_name = f"{in_csv.stem}_output.json"
    out_path = out_dir / out_name

    agent = AimriMapperAgent(taxonomy_path=str(taxonomy_yaml),api_key=api_key)
    results = []

    with in_csv.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            metric_id = row["Metrics for Computation"].strip()
            short_desc = row["Function Description"].strip()
            results.append(agent.map_metric(metric_id, short_desc))

    with out_path.open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"✅ Done. Output written to {out_path}")


if __name__ == "__main__":
    main()
