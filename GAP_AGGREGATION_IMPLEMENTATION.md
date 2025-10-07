# Gap Aggregation Implementation

## Overview
This implementation adds gap aggregation functionality to the main orchestrator, similar to how scores are aggregated by AIMRI category. The system now collects gaps from all agent metrics and aggregates them by AIMRI dimension and subsection.

## Key Features

### 1. Gap Extraction and Aggregation
- **Source**: Extracts gaps from agent metrics using the same `aimri_mapping` logic as scores
- **Processing**: Groups gaps by AIMRI dimension and subsection
- **Deduplication**: Removes duplicate gaps while preserving order
- **Limiting**: Caps at 10 gaps per category to maintain readability

### 2. Integration with Existing System
- **ScoringAgent**: Extended with `run_gaps()` method and integrated gap aggregation into main `run()` method
- **Graph Orchestrator**: Updated to persist gap aggregation results to `category_gaps.json`
- **API Endpoint**: Enhanced `/results/latest` to include gap information
- **File Structure**: Maintains consistency with existing score aggregation patterns

## Implementation Details

### New Functions in `scoring.py`

#### `_extract_gaps_from_metrics(payload)`
- Extracts gaps from agent metrics with their AIMRI mappings
- Returns tuples of (dimension, subsection, gaps_list)
- Handles both `gaps` and `gap` fields in metrics

#### `_aggregate_gaps_tree(inputs_root)`
- Aggregates gaps by AIMRI dimension and subsection
- Similar structure to existing `_aggregate_tree()` for scores
- Includes metadata about gaps processed and contributions

#### `ScoringAgent.run_gaps(inputs_root)`
- Standalone method to run only gap aggregation
- Returns gap aggregation results without score computation

#### Enhanced `ScoringAgent.run(inputs_root)`
- Now includes gap aggregation alongside score computation
- Returns both `category_scores` and `category_gaps` in results
- Maintains backward compatibility

### Updated Components

#### `graph_orchestrator.py`
- `persist_results()` method now saves gap aggregation to `category_gaps.json`
- Maintains same file naming and structure patterns as scores

#### `app_main.py`
- `/results/latest` endpoint now includes gaps in response
- Returns `gaps` field alongside `overall` and `categories`

## Data Structure

### Gap Aggregation Output
```json
{
  "01. Technical Infrastructure": {
    "gaps": [
      "Link usage is concentrated on a few dashboards; increase link enablement...",
      "1. Onboard unmanaged resources to IaC management",
      "2. Address the critical policy finding regarding the network security group"
    ],
    "total_gaps": 238,
    "metric_contributions": 75
  },
  "02. Data Management & Quality": {
    "gaps": [...],
    "total_gaps": 260,
    "metric_contributions": 134
  }
}
```

### Metadata
- `total_gaps`: Total number of gaps found for this category
- `metric_contributions`: Number of metrics that contributed gaps to this category
- `gaps`: Array of unique, deduplicated gaps (max 10 per category)

## API Usage

### Get Latest Results (including gaps)
```bash
GET /results/latest
```

Response:
```json
{
  "overall": {"overall": 2.49},
  "categories": {
    "01. Technical Infrastructure": 2.55,
    "02. Data Management & Quality": 2.42
  },
  "gaps": {
    "01. Technical Infrastructure": {
      "gaps": [...],
      "total_gaps": 238,
      "metric_contributions": 75
    }
  }
}
```