# Slide Visual Plan

Use a 16:9 deck with a navy header/accent, white background, teal dividers, green for valid zones, and red/orange for hazards. Do not recolor analytical figures.

| Slide | Layout | Packet asset(s) | Visual caution |
|---:|---|---|---|
| 1 | Full-bleed image on right 55%, title block left | `best_landing_zone_labeled.png` or `input_image.png` | Avoid cropping the Rank-1 annotation if using the result image. |
| 2 | 60/40 image-text split | `input_image.png` | Use callout labels for visible scene complexity, not unverified object labels. |
| 3 | Before/after comparison | `input_image.png`, `best_landing_zone_labeled.png` | Label as input and demonstration result, not ground truth. |
| 4 | Four-card overview plus central image | `overlay_labeled.png` | Keep the present-class legend visible. |
| 5 | Six-stage horizontal strip | Input, semantic, risk, all zones, top zones, best zone | Use thumbnails with external captions; do not cover local legends. |
| 6 | Semantic image left, class groups right | `semantic_mask_labeled.png` | Preserve the exact trained palette. |
| 7 | Risk image large, water inset, equation card | `risk_map_labeled.png`, `water_detection_overlay_labeled.png` | State that water override is temporary and separate from the raw mask. |
| 8 | Footprint-valid map plus six-step process | `footprint_valid_centers_labeled.png` | White/green valid centers are not the final selected zone by themselves. |
| 9 | Results triptych and numeric callout | `all_safe_zones_labeled.png`, `top_safe_zones_labeled.png`, `best_landing_zone_labeled.png` | This sample has one valid zone; do not imply multiple fallback zones were found. |
| 10 | Limitation icons with muted background | `uncertainty_map_labeled.png` as optional background | Do not imply uncertainty is calibrated accuracy. |
| 11 | Three-horizon roadmap | No analytical image required; optional input thumbnail | Separate near-term validation from future ROS2/Gazebo work. |
| 12 | Large final result with conclusion | `best_landing_zone_labeled.png` | Keep “pixel coordinates, not GPS” visible in the conclusion area. |

## Optional diagnostic backup slides

- Confidence: `confidence_map_labeled.png`.
- Uncertainty: `uncertainty_map_labeled.png`.
- Probability margin: `margin_map_labeled.png`.
- Full class coverage: construct a table from `reports/class_coverage.csv`; do not create a performance chart from coverage percentages.
- Rejections: summarize categories from `reports/rejected_regions.csv` only if carefully aggregated later.

## Visual consistency

- Use the same figure numbers and captions as the poster/paper when practical.
- Apply “Fit” rather than aggressive crop to labeled images.
- Keep at most one key numeric callout per slide.
- Use external arrows to show pipeline order; do not draw over the figures.
- Mark Sample-28 result slides with a small “single-image demonstration” badge.
