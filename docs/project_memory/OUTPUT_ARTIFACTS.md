# Output Artifacts

Every successful CLI or explicit Streamlit analysis creates a new sequential directory:

```text
outputs/
├── Sample-01/
├── Sample-02/
└── Sample-XX/
```

Names use two digits through `Sample-99` and continue as `Sample-100` and higher. Existing sample directories are preserved. The CLI `--output_dir` value is the base directory, not the final per-run folder.

## Standard outputs

These files are generated on every successful saved analysis.

| File | Meaning |
|---|---|
| `input_image.png` | Normalized source-resolution RGB image retained for the run. |
| `original.png` | Backward-compatible duplicate of the normalized input. |
| `semantic_mask.png` | Raw model argmax classes rendered with the exact trained 24-class palette; water heuristics do not alter it. |
| `overlay.png` | Semantic colors blended over the input image. |
| `risk_map.png` | Final confidence-aware landing-risk visualization after hazard enforcement. |
| `best_landing_zone.png` | Plain visualization of the single Rank-1 valid zone, or the no-zone result. |
| `water_detection_overlay.png` | Source-colored model/probability/RGB water evidence; generated even when debug saving is off. |
| `candidates.csv` | Backward-compatible table of evaluated connected components, including accepted/rejected status. |
| `rejected_regions.csv` | Invalid regions and reasons such as area, risk, hazard, footprint, or confidence failure. |
| `landing_target.json` | Rank-1 target geometry and metrics, or an explicit no-target payload; coordinates are image-plane, not GPS. |
| `run_metadata.json` | Run time, input/model/settings, output flags, water counts, ranked-zone counts/limits, and generated-file metadata. |

## Version 0.3.4 ranked-zone outputs

These are also standard outputs and are generated even when no zone qualifies; the reports remain schema-valid and visualizations remain available.

| File | Meaning |
|---|---|
| `all_safe_zones.png` | Plain source-resolution visualization of all valid ranked contours, with configured limits on labels and footprint circles. |
| `all_safe_zones_labeled.png` | Presentation variant of the all-zone view; generated when labeled saving is enabled. |
| `top_safe_zones.png` | Plain source-resolution visualization limited to the configured top-N valid zones. |
| `top_safe_zones_labeled.png` | Presentation variant of the top-N view; generated when labeled saving is enabled. |
| `ranked_safe_zones.csv` | Valid zones only, in deterministic rank order, with geometry, fit, confidence, uncertainty, margin, hazard distance, and risk fields. |
| `ranked_safe_zones.json` | Coordinate-friendly valid-zone list with image-pixel centers/bounds and an explicit non-GPS note. |

## Labeled outputs

Labeled saving is enabled by default and can be disabled from the CLI with `--no_labeled`. These expand the canvas for explanation while preserving each plain file.

| File | Meaning and generation condition |
|---|---|
| `semantic_mask_labeled.png` | Semantic mask with title and present-class legend; generated when labeled saving is on. |
| `overlay_labeled.png` | Overlay with title and present-class legend; generated when labeled saving is on. |
| `risk_map_labeled.png` | Risk map with scale, threshold, and suitability explanation; generated when labeled saving is on. |
| `best_landing_zone_labeled.png` | Best/no-zone view with decision, geometry, footprint, and risk explanation; generated when labeled saving is on. |
| `all_safe_zones_labeled.png` | All-zone presentation view with map legend and top-five summary; generated when labeled saving is on. |
| `top_safe_zones_labeled.png` | Top-N presentation view with map legend and summary; generated when labeled saving is on. |
| `water_detection_overlay_labeled.png` | Water-source view with evidence counts and legend; generated when labeled saving is on. |

## Debug outputs

The following plain files are generated only with `--save_debug` or the equivalent Streamlit debug setting.

| File | Meaning |
|---|---|
| `car_probability_map.png` | Per-pixel model probability for `car`. |
| `danger_probability_map.png` | Per-pixel summed probability across configured danger classes. |
| `hazard_override_mask.png` | Final dilated effective-hazard mask used for hard exclusion and risk enforcement. |
| `risk_map_before_override.png` | Combined risk before the hard hazard floor. |
| `risk_map_after_override.png` | Final confidence-aware risk after hazard enforcement. |
| `class_coverage.csv` | All 24 classes with argmax count/percentage and maximum/mean probability. |
| `confidence_map.png` | Maximum class probability per pixel. |
| `uncertainty_map.png` | Normalized predictive entropy per pixel. |
| `margin_map.png` | Top-1 minus top-2 class probability per pixel. |
| `footprint_valid_centers.png` | Pixels where the requested circular footprint fits in the final valid surface. |
| `water_probability_map.png` | Model water probability used by the temporary override. |
| `water_heuristic_score_map.png` | Conservative RGB water-appearance score. |
| `water_override_mask.png` | Source-coded model argmax, probability, and RGB water evidence. |

When both debug and labeled saving are enabled, these labeled debug counterparts are also generated:

| File | Meaning |
|---|---|
| `car_probability_map_labeled.png` | Labeled car-probability map. |
| `danger_probability_map_labeled.png` | Labeled summed-danger probability map. |
| `hazard_override_mask_labeled.png` | Labeled binary hazard mask with exclusion explanation. |
| `risk_map_before_override_labeled.png` | Labeled pre-override risk map. |
| `risk_map_after_override_labeled.png` | Labeled final-risk map. |
| `confidence_map_labeled.png` | Labeled model-confidence map. |
| `uncertainty_map_labeled.png` | Labeled uncertainty map. |
| `margin_map_labeled.png` | Labeled top-1/top-2 margin map. |
| `footprint_valid_centers_labeled.png` | Labeled footprint-valid-center mask. |
| `water_probability_map_labeled.png` | Labeled water-probability map. |
| `water_heuristic_score_map_labeled.png` | Labeled RGB water-heuristic score map. |
| `water_override_mask_labeled.png` | Labeled water-source mask with source counts. |

`run_metadata.json` records whether debug and labeled outputs were requested and lists the labeled files generated for that run.
