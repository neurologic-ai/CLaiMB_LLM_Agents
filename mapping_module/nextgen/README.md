# NextGen AIMRI Mapping (Experimental)

Self-contained, optional reimplementation that does not modify existing code.

## Quick Start

1. Ensure `OPENAI_API_KEY` is set (e.g., in a `.env` file).
2. Run the CLI:

```
python -m mapping_module.nextgen.cli --csv mapping_module/csv/metrics.csv --taxonomy mapping_module/aimri_points.yaml --outdir mapping_module/outputs
```

This produces `*_nextgen_output.json` in the specified outdir.

## Design

- No dependency on `data_collection_agents` or existing `BaseMicroAgent`.
- Clear separation: `types.py`, `taxonomy.py`, `prompts.py`, `agent.py`, `cli.py`.
- Minimal taxonomy context is sent to the model for determinism and cost.

## Notes

- Uses `openai` SDK from `requirements.txt`.
- Maintains the two-hop flow: elaborate -> map.