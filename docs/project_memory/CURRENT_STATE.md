# Current State

## Release identity

| Field | Current value |
|---|---|
| Version | `0.3.4` |
| Release date | 2026-06-20 |
| Stage | Research demo / ranked safe landing zone list |
| Input | One aerial RGB image |
| Model | Locally trained SegFormer-B0 semantic segmentation model |
| Runtime | Python, PyTorch, Hugging Face Transformers, Streamlit |

For full implementation and verification history, see `VERSION.md`.

## Implemented capabilities

- Local-only SegFormer-B0 model and processor loading with strict 24-label validation.
- Streamlit application and CLI inference entry point.
- Semantic mask and overlay generation at source-image resolution.
- Five-factor landing-risk map with probability-aware hazard override and hazard dilation.
- Temporary probability/RGB water safety override while preserving the raw semantic prediction.
- Overlapping tiled inference for large images.
- Circular footprint-aware landing-center selection using safe-distance transforms.
- Full-resolution confidence, uncertainty, and top-1/top-2 margin maps.
- Optional confidence-aware risk, enabled by default.
- Labeled presentation outputs alongside plain machine-friendly images.
- Race-safe sequential `outputs/Sample-XX/` folders that do not overwrite earlier runs.
- Complete, deterministic, valid-only ranked safe-zone list.
- Candidate, rejection, ranked-zone, landing-target, and metadata CSV/JSON exports.
- Optional probability, hazard, class-coverage, confidence, uncertainty, margin, footprint, and water debug outputs.

## Version 0.3.4 behavior

Valid zones are sorted by score descending, mean risk ascending, maximum inscribed radius descending, and area descending. They receive stable identifiers beginning with `Zone-01`.

```text
best_landing_zone = ranked_safe_zones[0]
```

`Zone-01` is the only source for `best_landing_zone.png`, `best_landing_zone_labeled.png`, and `landing_target.json`. Rejected regions remain outside `ranked_safe_zones.csv` and `ranked_safe_zones.json`; their reasons continue to be recorded in `rejected_regions.csv`.

Landing targets are image-pixel coordinates. Optional scale-based values are local image-plane offsets only, not GPS, georeferenced, or UAV-planner coordinates.

## Current limitations

- Input is RGB-only.
- Physical terrain slope and surface roughness are not measured; current layers are semantic proxies.
- Depth and elevation are not integrated.
- Wind, hidden obstacles, load-bearing capacity, and UAV dynamics are not modeled.
- No georeferenced or GPS coordinate output exists.
- The water override is temporary, heuristic/probability-based, and can produce misses or false positives.
- A hazard receiving almost zero model probability cannot be recovered reliably without better training data, retraining, or a separate detector.
- Thresholds and confidence cutoffs require calibration against representative validation data.
- The system is not certified for real autonomous landing or flight-safety decisions.
