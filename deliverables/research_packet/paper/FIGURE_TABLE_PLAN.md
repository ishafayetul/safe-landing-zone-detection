# Figure and Table Plan

## Planned figures

| Figure | Proposed content | Packet asset(s) | Draft caption |
|---:|---|---|---|
| 1 | End-to-end method diagram | Create later from the confirmed pipeline; no data graphic required | **System pipeline.** One aerial RGB image is segmented, converted into risk and effective hazards, filtered by footprint geometry, and returned as a ranked valid-zone list. |
| 2 | Input and semantic prediction | `input_image.png`, `semantic_mask_labeled.png` | **Input and semantic output for Sample-28.** The RGB image is the only sensor input; the labeled mask shows the source-resolution SegFormer prediction using the fixed model palette. |
| 3 | Overlay and risk interpretation | `overlay_labeled.png`, `risk_map_labeled.png` | **Semantic and risk representations.** The overlay relates classes to the scene, while the final risk map converts semantic and hazard evidence into landing suitability. |
| 4 | Hazard and water evidence | `water_detection_overlay_labeled.png` | **Temporary water safety evidence.** Model, probability, and RGB sources enter the hazard path without changing the raw semantic mask. |
| 5 | Confidence diagnostics | `confidence_map_labeled.png`, `uncertainty_map_labeled.png`, `margin_map_labeled.png` | **Prediction diagnostics.** Maximum probability, normalized entropy, and top-1/top-2 margin provide complementary views of model certainty. |
| 6 | Footprint-valid centers | `footprint_valid_centers_labeled.png` | **Footprint-valid center mask.** Valid centers have sufficient distance from invalid surfaces and image boundaries for the requested circular footprint. |
| 7 | All and top ranked regions | `all_safe_zones_labeled.png`, `top_safe_zones_labeled.png` | **Ranked safe landing zones for Sample-28.** The all-zone and Top-N views retain one valid region in this demonstration. |
| 8 | Final Rank-1 target | `best_landing_zone_labeled.png` | **Final `Zone-01` target.** The selected center, footprint, available radius, class, score, and risk are visualized consistently with the structured reports. |

## Planned tables

| Table | Content | Source |
|---:|---|---|
| I | Model and runtime configuration: SegFormer-B0, parameters, input size, 24 classes, local loading | `PROJECT_FACTS_SUMMARY.md` and project memory |
| II | Semantic class grouping: safe, danger, uncertain, special | `PROJECT_FACTS_SUMMARY.md`; full exact vocabulary from project memory |
| III | Base risk and region-score factors/weights | Confirmed formulas in `PAPER_SECTION_DRAFTS.md` |
| IV | Sample-28 run parameters | `reports/run_metadata.json` |
| V | Sample-28 Rank-1 result | `reports/ranked_safe_zones.csv` and `reports/landing_target.json` |
| VI | Current limitations and planned mitigations | Paper Limitations/Future Work sections |

## Recommended main-paper selection

If page space is limited, prioritize Figures 1, 2, 3, 6, and 8 plus Tables I, III, IV, and V. Move confidence diagnostics, the water overlay, and the all/top comparison to supplemental material or an appendix.

## Data integrity notes

- Sample-28 is a single demonstration, not a benchmark.
- Do not build an accuracy chart from class coverage; class prevalence is not model performance.
- Do not aggregate rejection reasons without a documented data-processing step and verification.
- Do not crop analytical legends or remove the pixel-coordinate warnings.
- Use `[REF]` placeholders in captions or surrounding text until real references are verified.
