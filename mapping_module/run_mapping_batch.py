from __future__ import annotations
import argparse
from pathlib import Path
from loguru import logger

from .logging_utils import setup_logger
from .mapper import process_yaml


def _anchors() -> tuple[Path, Path, Path, Path]:
    """
    Anchor all defaults relative to this file's directory:
      <pkg_dir>/aimri_points.json
      <pkg_dir>/metric_descriptions/
      <pkg_dir>/outputs/
      <pkg_dir>/logs/
    """
    pkg_dir = Path(__file__).resolve().parent
    logger.debug(pkg_dir)
    aimri_path = pkg_dir / "aimri_points.json"
    metrics_dir = pkg_dir / "metric_descriptions"
    out_dir = pkg_dir / "outputs"
    logs_dir = pkg_dir / "logs"
    return aimri_path, metrics_dir, out_dir, logs_dir


def main() -> None:
    p = argparse.ArgumentParser(
        description="Run AIMRI mapping for metric YAMLs (single file, single agent, or batch). "
                    "All paths are anchored relative to this script's directory."
    )
    # Optional overrides if you ever need them
    p.add_argument("--aimri", default=None, help="Override path to aimri_points.json")
    p.add_argument("--metrics-dir", default=None, help="Override directory containing YAMLs")
    p.add_argument("--out-dir", default=None, help="Override output directory")
    p.add_argument("--model", default="gpt-4o-mini", help="OpenAI model name")

    # Single-target options (mutually exclusive)
    group = p.add_mutually_exclusive_group()
    group.add_argument("--file", default=None,
                       help="Process a specific YAML file (absolute or relative). Overrides --agent and batch.")
    group.add_argument("--agent", default=None,
                       help="Process a specific agent by stem name (e.g., 'cloud_infra' -> cloud_infra.yaml).")

    args = p.parse_args()

    # Anchors (relative to this script)
    default_aimri, default_metrics_dir, default_out_dir, logs_dir = _anchors()

    aimri_path = Path(args.aimri).resolve() if args.aimri else default_aimri
    metrics_dir = Path(args.metrics_dir).resolve() if args.metrics_dir else default_metrics_dir
    out_dir = Path(args.out_dir).resolve() if args.out_dir else default_out_dir

    setup_logger(logs_dir / "mapping.log", level="INFO")

    # Validate anchor files/dirs
    if not aimri_path.exists():
        raise FileNotFoundError(f"AIMRI file not found: {aimri_path}")
    if not metrics_dir.exists():
        raise FileNotFoundError(f"metrics dir not found: {metrics_dir}")
    out_dir.mkdir(parents=True, exist_ok=True)

    # Resolve targets
    yaml_files: list[Path] = []

    if args.file:
        target = Path(args.file).resolve()
        if not target.exists():
            raise FileNotFoundError(f"--file not found: {target}")
        if target.suffix.lower() != ".yaml":
            raise ValueError(f"--file must be a .yaml file: {target}")
        yaml_files = [target]
        logger.info(f"Single-file mode: {target}")

    elif args.agent:
        candidate = (metrics_dir / f"{args.agent}.yaml").resolve()
        if not candidate.exists():
            raise FileNotFoundError(f"--agent '{args.agent}' not found at: {candidate}")
        yaml_files = [candidate]
        logger.info(f"Single-agent mode: {candidate.name}")

    else:
        yaml_files = sorted(metrics_dir.glob("*.yaml"))
        if not yaml_files:
            logger.warning(f"No YAML files found in {metrics_dir}.")
            return
        logger.info(f"Batch mode: {len(yaml_files)} YAML(s) under {metrics_dir}")

    # Process
    for yf in yaml_files:
        try:
            process_yaml(yf, aimri_path, out_dir, model=args.model)
        except Exception as e:
            logger.exception(f"Failed to process {yf}: {e}")


if __name__ == "__main__":
    main()
