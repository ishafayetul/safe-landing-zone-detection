# Research Packet Resource Manifest

## Source selection

Selected source folder: `outputs/Sample-28/`.

The preferred folder existed and contained all requested labeled/ranked figures and reports. No fallback sample was needed. Assets in this packet are copies; the existing output folder was not changed.

## Copied figures

| Packet file | Dimensions | Recommended use |
|---|---:|---|
| `figures/input_image.png` | 3375×2250 | Opening scene; poster/slide/paper input figure. |
| `figures/semantic_mask_labeled.png` | 3809×2332 | Semantic result and present-class legend. |
| `figures/overlay_labeled.png` | 3809×2332 | Connects the prediction to the original scene. |
| `figures/risk_map_labeled.png` | 3605×2402 | Explains low-to-high landing risk. |
| `figures/all_safe_zones_labeled.png` | 3604×2426 | Shows all valid ranked zones and the footprint context. |
| `figures/top_safe_zones_labeled.png` | 3604×2426 | Shows the configured Top-N result; this sample has one valid zone. |
| `figures/best_landing_zone_labeled.png` | 3604×2474 | Strongest final-decision visual with Rank-1 explanation. |
| `figures/water_detection_overlay_labeled.png` | 3604×2450 | Supporting water-safety-method visual. |
| `figures/confidence_map_labeled.png` | 3605×2402 | Model-confidence diagnostic. |
| `figures/uncertainty_map_labeled.png` | 3605×2402 | Prediction-uncertainty diagnostic. |
| `figures/margin_map_labeled.png` | 3605×2402 | Top-1/top-2 probability-separation diagnostic. |
| `figures/footprint_valid_centers_labeled.png` | 3604×2332 | Explains where the requested footprint can fit. |

Dimensions were read from existing PNG metadata with the system `file` utility; no image package was installed.

## Copied reports

| Packet file | Purpose |
|---|---|
| `reports/ranked_safe_zones.csv` | Authoritative valid-only ranked-zone table. |
| `reports/ranked_safe_zones.json` | Structured list of all valid zones and their image coordinates. |
| `reports/landing_target.json` | Authoritative Rank-1 target record. |
| `reports/run_metadata.json` | Input, run settings, output settings, water counts, and zone counts. |
| `reports/class_coverage.csv` | Argmax coverage and probability statistics for all 24 classes. |
| `reports/rejected_regions.csv` | Rejected regions and rule-based rejection reasons. |

## Missing preferred assets

None. All 12 preferred figures and all 6 preferred reports were present in `Sample-28` and copied.

## Best poster figures

Use the six-stage visual story:

1. `input_image.png`
2. `semantic_mask_labeled.png`
3. `risk_map_labeled.png`
4. `all_safe_zones_labeled.png`
5. `top_safe_zones_labeled.png`
6. `best_landing_zone_labeled.png`

Use `water_detection_overlay_labeled.png` as a small methods inset if space permits. `overlay_labeled.png` is the preferred substitute if the semantic transition needs more context.

## Best slide figures

- Overview/method: `input_image.png`, `overlay_labeled.png`, `semantic_mask_labeled.png`.
- Risk/hazards: `risk_map_labeled.png`, `water_detection_overlay_labeled.png`.
- Footprint reasoning: `footprint_valid_centers_labeled.png`.
- Results: `all_safe_zones_labeled.png`, `top_safe_zones_labeled.png`, `best_landing_zone_labeled.png`.
- Diagnostics: `confidence_map_labeled.png`, `uncertainty_map_labeled.png`, `margin_map_labeled.png`.

## Best paper figures

- Input and semantic prediction pair: `input_image.png` plus `semantic_mask_labeled.png` or `overlay_labeled.png`.
- Risk and hazard pair: `risk_map_labeled.png` plus `water_detection_overlay_labeled.png`.
- Geometry: `footprint_valid_centers_labeled.png`.
- Final result: `all_safe_zones_labeled.png` plus `best_landing_zone_labeled.png`.
- Diagnostics, if discussed: confidence, uncertainty, and margin maps as a grouped figure.

## Evidence rules

- Preserve the analytical content, legends, contours, centers, and footprint circles in copied figures.
- Do not fabricate accuracy charts, comparison baselines, citations, institutional branding, or operational-safety claims.
- Label Sample-28 values as one image-specific demonstration.
- Keep the pixel-coordinate and research-demo limitations beside any landing-target result.
