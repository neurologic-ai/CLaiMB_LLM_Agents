import csv
import json
import os
from pathlib import Path
import argparse
from dotenv import load_dotenv

from .agent import NextGenAimriMapper


def main() -> None:
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")

    parser = argparse.ArgumentParser(description="Run AIMRI mapping (nextgen) for metrics CSV")
    parser.add_argument("--csv", default="mapping_module/csv/metrics.csv", help="Path to input CSV")
    parser.add_argument(
        "--taxonomy",
        default="mapping_module/aimri_points.yaml",
        help="Path to AIMRI taxonomy YAML",
    )
    parser.add_argument(
        "--outdir",
        default="mapping_module/outputs",
        help="Folder for outputs (will be created)",
    )

    args = parser.parse_args()

    in_csv = Path(args.csv)
    taxonomy_yaml = Path(args.taxonomy)
    out_dir = Path(args.outdir)
    out_dir.mkdir(parents=True, exist_ok=True)

    out_name = f"{in_csv.stem}_nextgen_output.json"
    out_path = out_dir / out_name

    agent = NextGenAimriMapper(taxonomy_path=str(taxonomy_yaml), api_key=api_key)
    results = []

    with in_csv.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            metric_id = row["Metrics for Computation"].strip()
            short_desc = row["Function Description"].strip()
            results.append(agent.map_metric(metric_id, short_desc))

    with out_path.open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"✅ Done (nextgen). Output written to {out_path}")


if __name__ == "__main__":
    main()

