# Version Document

## Safe Landing Zone Detection for Drone Landing

| Field | Value |
|---|---|
| Project identifier | `safe_landing_zone_demo` |
| Current version | `0.3.4` |
| Release date | 2026-06-20 |
| Documentation updated | 2026-06-20 |
| Release stage | Research demo / ranked safe landing zone list |
| Input | One aerial RGB image |
| Model | Locally trained SegFormer-B0 semantic segmentation model |
| Runtime | Python, PyTorch, Hugging Face Transformers, Streamlit |

## Version 0.3.4 - Ranked safe landing zone list

Version 0.3.4 expands the footprint-aware decision from one selected target to a complete, deterministic list of every valid landing region. Existing best-zone behavior remains intact, but `Zone-01` from the sorted valid list is now the sole source for the best visualization and landing target.

### Added

1. Valid-only safe-zone ranking with stable `Zone-01`, `Zone-02`, and subsequent identifiers.
2. Deterministic sorting by score descending, mean risk ascending, maximum inscribed radius descending, and area descending.
3. `ranked_safe_zones.csv` with ranking, geometry, footprint, clearance, shape, confidence, uncertainty, margin, hazard-distance, and risk-category fields.
4. `ranked_safe_zones.json` with all valid targets, image-pixel centers and bounding boxes, and an explicit non-GPS coordinate note.
5. `all_safe_zones.png` and `top_safe_zones.png` with rank-colored contours, best centers, labels, hazard overlays, and footprint circles.
6. Labeled all-zone and top-zone variants with titles, map-symbol legends, and a top-five summary table.
7. Streamlit **Ranked Safe Landing Zones** controls, count, best summary, complete table, labeled gallery, and CSV/JSON downloads.
8. CLI controls for top-N display, label limits, and footprint-circle limits, plus the total safe-zone count and Rank-1 summary.
9. Safe-zone counts, display limits, and the six generated safe-zone artifacts in `run_metadata.json`.
10. `margin_score`, `hazard_distance_px`, and semantic risk categories for every valid zone.

### Valid-zone and Rank-1 behavior

A ranked zone must belong to a configured safe class, meet the final-risk threshold, remain outside the dilated hazard mask, satisfy the minimum area, fit the resolved circular footprint, and meet the minimum mean confidence. Rejected regions stay out of the ranked CSV/JSON and continue to appear in `rejected_regions.csv`.

The existing outputs now use:

```text
best_landing_zone = ranked_safe_zones[0]
```

This guarantees that `best_landing_zone.png`, `best_landing_zone_labeled.png`, and `landing_target.json` agree with `Zone-01`.

### New standard outputs

```text
all_safe_zones.png
all_safe_zones_labeled.png
top_safe_zones.png
top_safe_zones_labeled.png
ranked_safe_zones.csv
ranked_safe_zones.json
```

Default display limits are five top zones, 20 zone labels, and 10 footprint circles. All valid contours are still drawn even when the label limit is reached.

### Version 0.3.4 verification

- Python compilation passed for both entry points and all source modules.
- Synthetic disconnected-region tests confirmed valid-only inclusion, exact four-key sorting, stable ranks and zone IDs, confidence filtering, rejection reporting, and Rank-1 identity.
- A real 1300×956 four-tile CPU run found and ranked four valid zones, generated all standard, debug, labeled, CSV, JSON, and metadata outputs, and retained the water safety override.
- The real CSV column order and sorting were checked, and `landing_target.json` matched the first JSON/CSV zone for center and score.
- A no-zone run with an oversized footprint generated empty-but-schema-valid CSV/JSON reports and all four zone visualizations without failure.
- All plain all-zone, top-zone, and best-zone images remained at source resolution; the labeled images were visually checked for contours, ranks, centers, footprints, legends, and the top-five panel.
- Streamlit AppTest passed and confirmed the all-zone, top-only, top-N, and maximum-label controls without requiring Jinja2/Pandas Styler.
- Runtime and original model-file SHA-256 hashes remained pairwise identical after the implementation and verification runs.

## Version 0.3.3 - Temporary water safety override

Version 0.3.3 mitigates missed water without retraining the local SegFormer model. It preserves the raw predicted semantic mask and adds a clearly separated, conservative safety override based on weak model water probability and RGB appearance.

### Added

1. A dedicated water-probability threshold, defaulting to `0.04`.
2. An optional RGB heuristic that scores smooth, non-green, blue/cyan or dark-neutral surfaces while restricting RGB-only overrides to otherwise landable semantic classes.
3. Connected-component filtering with a default minimum RGB-water area of `300 px`.
4. Effective-water integration with the existing hazard floor, dilation, obstacle-proximity risk, and hard landing-candidate exclusion.
5. A source-colored `water_detection_overlay.png` that distinguishes model argmax water, probability overrides, and RGB overrides.
6. Debug water-probability, heuristic-score, and source-mask images, with labeled counterparts.
7. CLI and Streamlit controls for enabling, thresholding, tuning, or disabling the temporary override.
8. Source-specific water pixel counts in the CLI, Streamlit, and `run_metadata.json`.
9. A 1600-pixel heuristic-analysis cap to control temporary RAM use on large inputs while returning the final mask at source resolution.

### Default controls

```text
use water override        true
water probability         0.04
use RGB heuristic         true
RGB heuristic threshold   0.40
minimum RGB area          300 px
```

### Scientific limitation

The override is not a trained water detector and does not change `semantic_mask.png` or `class_coverage.csv`. It is intentionally safety-biased: reflective, muddy, shadowed, or vegetation-covered water may still be missed, while blue roofs, shadows, smooth dark surfaces, or reflections may be false positives. Retraining on representative water imagery remains the correct long-term fix.

### Version 0.3.3 verification

- Synthetic tests covered probability-only detection, RGB-assisted detection, green-surface rejection, disabled behavior, and hazard exclusion.
- The previously failing river image had zero model argmax water pixels but produced 14,022 probability-override pixels and 51,085 RGB-override pixels.
- The resulting 65,107 effective-water pixels entered the hazard pipeline, while the new and previous raw semantic masks remained checksum-identical.
- Standard, debug, labeled, metadata, CLI, Streamlit, compilation, and local model-integrity checks passed.

## Version 0.3.2 - Labeled visual outputs

Version 0.3.2 keeps every plain visualization and adds a presentation-friendly labeled counterpart. Labels are rendered locally with the existing OpenCV and Matplotlib dependencies; no network access or heavyweight package was added.

### Added

1. Reusable title-banner, background-label, legend, and vertical-colorbar drawing utilities.
2. Present-class-only legends for the semantic mask and segmentation overlay using the exact model palette.
3. Risk-map colorbars with low, medium, and high risk meanings, candidate threshold, and landing-suitability formula.
4. A best-zone explanation containing hazard, selected-region, footprint, center, bounding-box, score, class, mean-risk, and safe-radius details, plus a rejection message when no zone qualifies.
5. Labeled car/danger probability, confidence, uncertainty, and margin maps with 0-to-1 meanings and concise explanations.
6. Labeled hazard and footprint-valid-center binary masks.
7. Labeled risk maps before and after hazard override, including the enforced high-risk hazard note.
8. A default-on Streamlit **Show labeled visual outputs** selector with automatic plain-image fallback.
9. Default-on CLI labeled saving through `--save_labeled`, with `--no_labeled` to disable it.
10. `save_labeled` and the complete generated `labeled_outputs` list in `run_metadata.json`.

### Generated labeled files

Standard runs add:

```text
semantic_mask_labeled.png
overlay_labeled.png
risk_map_labeled.png
best_landing_zone_labeled.png
```

Debug runs also add:

```text
car_probability_map_labeled.png
danger_probability_map_labeled.png
hazard_override_mask_labeled.png
risk_map_before_override_labeled.png
risk_map_after_override_labeled.png
confidence_map_labeled.png
uncertainty_map_labeled.png
margin_map_labeled.png
footprint_valid_centers_labeled.png
```

### Version 0.3.2 verification

- Python compilation passed for the application, CLI, and every source module.
- Synthetic rendering checks covered semantic legends, overlays, risk colorbars, probability colorbars, and binary legends.
- A real offline CPU inference generated all four standard and all nine debug labeled images alongside their plain counterparts.
- Representative semantic, risk, no-zone landing, probability, and binary-mask outputs were visually checked for readable titles, legends, color scales, and explanations.
- Metadata listed all 13 generated labeled files and retained the run parameters.
- A successful landing case rendered the selected contour, bounding box, footprint, center, score, class, mean risk, and available safe radius correctly.
- CLI tests confirmed default-on labeled saving and the `--no_labeled` opt-out; Streamlit testing confirmed labeled/plain switching without creating another sample folder.

## Version 0.3.1 - Sequential sample output folders

Version 0.3.1 organizes every successful CLI and Streamlit analysis in its own numbered directory. The output base now contains `Sample-01`, `Sample-02`, and so on through `Sample-99`, then continues naturally with `Sample-100` and higher. Existing sample directories are never overwritten.

### Changes completed in 0.3.1

- Added a shared, race-safe output-directory allocator that scans existing `Sample-XX` directories and creates the next available number.
- Changed `--output_dir` into the output base directory while preserving the existing CLI syntax. The CLI reports `Results saved to: .../Sample-XX` after a successful run.
- Added an explicit **Run analysis and save outputs** action to Streamlit. Uploads and widget reruns do not create directories by themselves; each clicked analysis creates exactly one new sample directory.
- Stored the current Streamlit result and its output path in session state, so changing presentation controls does not repeat inference or overwrite saved data.
- Added `input_image.png` to every run while retaining the backward-compatible `original.png` output.
- Added `run_metadata.json` to every run. It records the sample folder, input filename, ISO timestamp, model directory, tiled-inference state, risk threshold, resolved footprint radius, debug state, and other available parameters.
- Kept all standard and optional debug artifacts together inside the same sample directory.

### Output layout

```text
outputs/
├── Sample-01/
│   ├── input_image.png
│   ├── original.png
│   ├── semantic_mask.png
│   ├── overlay.png
│   ├── risk_map.png
│   ├── best_landing_zone.png
│   ├── candidates.csv
│   ├── rejected_regions.csv
│   ├── landing_target.json
│   └── run_metadata.json
└── Sample-02/
    └── ...
```

Debug runs add the probability, hazard, confidence, uncertainty, margin, valid-center, and class-coverage artifacts to that same directory.

### Version 0.3.1 verification

- Two consecutive real CLI analyses created `Sample-01` and `Sample-02`, each with all standard, metadata, and requested debug artifacts.
- The saved `input_image.png` and `original.png` were verified as identical source-resolution RGB images.
- Numbering was checked across the two-digit boundary: an existing `Sample-99` produced `Sample-100`, followed by `Sample-101`.
- Streamlit created no folder on upload or ordinary widget reruns, created one folder per explicit analysis click, and retained the displayed result between reruns.
- Python compilation, metadata contents, source-resolution outputs, and local model-file integrity were checked.

## Version 0.3.0 - Footprint-aware and confidence-aware landing zone selection

Version 0.3.0 changes the final decision from area-oriented connected-component selection to landing-point selection based on whether a circular drone footprint fits fully inside a safe, confident, low-risk region.

### Added

1. Configurable drone footprint radius in pixels, defaulting to `35 px`.
2. Optional meters-per-pixel and footprint-diameter conversion.
3. Safe-distance transform with image boundaries treated as unsafe.
4. Footprint-valid center mask and maximum-inscribed-radius landing center.
5. Region compactness, aspect ratio, and elongation metrics.
6. Full-resolution confidence, normalized uncertainty, and top-1/top-2 margin maps.
7. Optional confidence-aware risk, enabled by default.
8. Improved candidate ranking table with geometry, fit, confidence, and selection fields.
9. Rejected-region report with area, risk, hazard, footprint, and confidence reasons.
10. `landing_target.json` with pixel coordinates and optional local image-plane meter conversion.
11. White footprint circle, maximum-radius fit label, and maximum-clearance center in the best-zone visualization.

### Footprint-aware decision flow

- Build a valid surface from safe classes, the final risk threshold, and exclusion from the dilated hazard mask.
- Calculate Euclidean distance to the nearest invalid surface or image boundary.
- Accept landing-center pixels only where distance is at least the resolved footprint radius.
- Find each component's best center at its maximum distance-transform value.
- Reject components that are too small, cannot fit the footprint, or fall below the confidence threshold.
- Score remaining regions using suitability, footprint fit, obstacle clearance, area, shape quality, and confidence.

The initial low-confidence rejection threshold is `0.50`; it should be calibrated against validation data before operational use.

The region score is:

```text
region_score =
    0.30 * mean_suitability
  + 0.25 * footprint_fit_score
  + 0.15 * obstacle_clearance_score
  + 0.10 * normalized_area_score
  + 0.10 * shape_quality_score
  + 0.10 * confidence_score
```

`shape_quality_score` combines contour compactness with inverse bounding-box aspect ratio so narrow and irregular components receive less credit.

### Confidence-aware risk

Version 0.3.0 calculates maximum probability, normalized entropy, and top-class margin for every source-resolution pixel. When enabled:

```text
final_risk_v3 = clip(
    0.85 * final_risk_v2 + 0.15 * uncertainty_risk,
    0,
    1
)
```

The version 0.2 hazard floor is reapplied afterward, ensuring confidence blending never weakens a red danger override.

### New outputs

Standard runs now add:

```text
rejected_regions.csv
landing_target.json
```

Debug runs also add:

```text
confidence_map.png
uncertainty_map.png
margin_map.png
footprint_valid_centers.png
```

### Interface changes

- Streamlit adds a **Landing footprint settings** section, optional scale conversion, confidence-risk control, landing-decision summary, improved candidate table, and rejected-region debugger.
- CLI adds `--footprint_radius_px`, `--meters_per_pixel`, `--footprint_diameter_m`, and `--use_confidence_risk` while preserving the existing command.
- The landing visualization shows the selected component, actual footprint circle, best center, score, class, required radius, and available inscribed radius.

### Fixes

- Removed the Pandas `.style`/Jinja2 dependency from Streamlit result tables. Candidate and rejection highlighting now uses explicit status labels in ordinary DataFrames, preventing `AttributeError: The '.style' accessor requires jinja2` on minimal offline installations.

### Coordinate limitation

Landing centers are image pixel coordinates. Optional meter values are local image-plane offsets from the image origin only. They are not GPS, georeferenced, or real UAV planner coordinates without calibration and external positioning.

### Version 0.3.0 verification

- Synthetic tests covered footprint fit, thin-strip rejection, small-region rejection, low-confidence rejection, hazard exclusion, geometry normalization, image-edge clearance, and optional scale conversion.
- A real 700×620 image completed four-tile CPU inference with a `35 px` footprint and selected a center with `64 px` available safe radius.
- All standard, version 0.2 debug, and version 0.3 debug/report outputs were generated at source resolution.
- Candidate CSV fields, rejection records, landing-target JSON, semantic palette, hard hazard floor, and backward-compatible CLI behavior were checked.

## Version 0.2.0 - Model-class-aligned hazard detection

Version 0.2.0 aligns the application with the exact 24-class model vocabulary and trained-dataset RGB palette. It also makes hazard interpretation probability-aware so small or weakly predicted danger objects can influence risk before they win the final argmax.

### Changes completed in 0.2.0

The latest implementation pass changed the complete inference-to-visualization path:

- Added the model's exact 24 class names and RGB values to `src/risk_config.py`; model loading now rejects missing, reordered, or unexpected labels.
- Replaced generated semantic colors with the original trained-dataset palette while keeping the landing-risk map on a separate green/yellow/orange/red safety palette.
- Preserved full-resolution softmax probabilities instead of retaining only the final argmax mask.
- Added dedicated car probability and summed danger-class probability maps.
- Combined argmax danger labels, car probability, and total danger probability into one hazard override mask.
- Dilated hazards with an elliptical OpenCV kernel and used the result for both obstacle proximity and hard candidate exclusion.
- Forced effective hazard pixels to at least `0.95` risk so cars and other danger regions appear red in safety visualizations.
- Added overlapping tiled inference. Tile logits are resized to their source tile size, accumulated on the full image canvas, and averaged before probabilities and class predictions are calculated.
- Added a red hazard overlay to the best-landing-zone image while retaining the green selected-region contour, bounding box, center point, score, and dominant class.
- Added Streamlit controls and diagnostics for tiling, probability thresholds, hazard dilation, override strength, AR-marker eligibility, and debug visibility.
- Added matching CLI flags and optional probability, hazard, before/after-risk, and class-coverage exports.
- Kept the original Streamlit and CLI commands compatible.

### Files updated for 0.2.0

| File | Change |
|---|---|
| `src/risk_config.py` | Exact palette, class groups, aligned risks, and hazard defaults |
| `src/model_loader.py` | Strict validation of the 24 model classes and their order |
| `src/inference.py` | Full probabilities, tiled inference, and class coverage |
| `src/risk_map.py` | Probability-aware hazards, dilation, overrides, and proximity risk |
| `src/landing_zone.py` | Hazard exclusion from candidate regions |
| `src/visualization.py` | Exact semantic colors and red safety-hazard rendering |
| `src/output.py` | Six optional debug artifacts |
| `run_inference.py` | Tiling, hazard, AR-marker, and debug CLI options |
| `app.py` | New controls, metrics, probability maps, and hazard debug section |
| `README.md` | Version 0.2.0 behavior, commands, outputs, and limitations |

### Added

1. Exact 24-class semantic RGB palette.
2. Class-specific risk configuration aligned with every model label.
3. Full-resolution car probability map.
4. Summed danger-class probability map.
5. Probability-aware hazard override mask.
6. Elliptical hazard dilation with a 15-pixel default radius.
7. Red/high-risk safety rendering for effective car, obstacle, person, animal, structure, vegetation, and water hazards.
8. Explicit hazard-mask exclusion from candidate landing zones.
9. Overlapping tiled inference with averaged full-resolution logits and probabilities.
10. Streamlit controls for tiled inference, probability thresholds, hazard behavior, AR-marker eligibility, and debug display.
11. CLI hazard/tile options and six debug exports.

### Behavioral changes

- The semantic mask now uses the trained dataset's exact colors instead of a generated palette.
- The safety map remains a distinct green-to-yellow/orange-to-red risk visualization.
- `ar-marker` has semantic risk `0.55` and is excluded from safe candidates unless explicitly enabled.
- Danger is triggered by an argmax danger label, car probability of at least `0.20`, or summed danger probability of at least `0.35`.
- The resulting hazard is dilated and forces final risk to at least `0.95`.
- Obstacle proximity is calculated from the effective probability-aware, dilated hazard mask.
- Landing candidates must be a configured safe class, meet the risk threshold, and lie outside the dilated hazard mask.

### Debug outputs

With `--save_debug`, version 0.2.0 saves:

```text
car_probability_map.png
danger_probability_map.png
hazard_override_mask.png
risk_map_before_override.png
risk_map_after_override.png
class_coverage.csv
```

`class_coverage.csv` reports `class_id`, `class_name`, argmax `pixel_count`, image `percentage`, `max_probability`, and `mean_probability` for all 24 classes.

### Version 0.2.0 verification

- `compileall` passed for the complete project.
- Exact class names, palette values, risk tables, thresholds, and defaults were checked against the requested configuration.
- Synthetic probability tests confirmed that weak car evidence and combined danger evidence trigger hazards even without winning argmax.
- Tests confirmed dilation expansion, minimum risk override, AR-marker opt-in behavior, and zero overlap between candidate masks and effective hazards.
- A real 700×620 image completed four-tile CPU inference and produced all standard and debug outputs at source resolution.
- The generated semantic mask contained only trained-dataset palette colors, while effective hazard pixels rendered red in the safety map.
- The standard non-debug CLI path remained operational.
- Streamlit passed its application test, exposed every new control, and returned a healthy server status.

### Detection limitation

If the SegFormer model gives almost zero probability for `car`, the system still cannot detect that car reliably without retraining or adding a separate object detector. Version 0.2.0 improves risk interpretation from the model output; it does not create a new detector.

### Commands

Existing commands remain valid:

```bash
streamlit run app.py
python run_inference.py --image sample_images/test.jpg
```

Full tiled debug run:

```bash
python run_inference.py \
  --image sample_images/test.jpg \
  --model_dir model \
  --output_dir outputs \
  --tiled \
  --save_debug
```

## Version 0.1.0

This is the first complete working version of the demo. It turns the original trained-model-only folder into an offline application with both a browser interface and command-line inference.

### Implemented features

- Local-only SegFormer model and image-processor loading.
- Automatic CUDA use when available, with CPU fallback.
- RGB image validation, EXIF orientation handling, and RGB conversion.
- Original-resolution semantic prediction by bilinearly resizing logits before `argmax`.
- Deterministic color rendering for all 24 semantic classes.
- Semantic mask and segmentation-overlay generation.
- Five-factor semantic landing-risk calculation:
  - terrain semantic category;
  - obstacle proximity;
  - connected landing-area size;
  - semantic terrain-slope proxy;
  - semantic surface-roughness proxy.
- Connected-component candidate detection and region ranking.
- Best landing-zone contour, bounding box, centroid, class, and score visualization.
- Candidate-region CSV generation.
- Streamlit controls for risk threshold, area thresholds, obstacle distance, and overlay opacity.
- Graceful handling of missing files, invalid settings, CPU-only systems, and images with no qualifying landing zone.

### Risk configuration

The initial release uses:

```text
final_risk =
    0.45  * semantic_risk
  + 0.25  * obstacle_proximity_risk
  + 0.15  * landing_area_size_risk
  + 0.075 * terrain_slope_proxy_risk
  + 0.075 * surface_roughness_proxy_risk
```

Default parameters:

| Parameter | Default |
|---|---:|
| Risk threshold | `0.45` |
| Minimum candidate area | `1500 px` |
| Desired candidate area | `8000 px` |
| Obstacle safe distance | `40 px` |
| Overlay opacity | `0.45` |

Safe candidate classes are `paved-area`, `grass`, `dirt`, and `gravel`. Risk values and obstacle classes are defined in `src/risk_config.py`.

### Generated outputs

Every CLI analysis writes:

```text
outputs/original.png
outputs/semantic_mask.png
outputs/overlay.png
outputs/risk_map.png
outputs/best_landing_zone.png
outputs/candidates.csv
```

### Project components

- `app.py`: Streamlit browser application.
- `run_inference.py`: command-line entry point.
- `src/model_loader.py`: model validation, label-map loading, and device selection.
- `src/inference.py`: model inference and pipeline orchestration.
- `src/risk_map.py`: factor maps and combined semantic risk.
- `src/landing_zone.py`: connected regions, metrics, and ranking.
- `src/visualization.py`: class colors, overlays, heatmaps, and landing-zone annotation.
- `src/output.py`: required PNG and CSV export.
- `src/utils.py`: image and CSV utilities.

### Model preservation

The five original files remain unchanged under `models/`. Checksum-identical copies were placed under `model/`, which is the default runtime path:

```text
model.safetensors
config.json
preprocessor_config.json
label2id.json
id2label.json
```

The loaded model has 24 classes, 3,720,312 parameters, a 384×384 processor input, and a 24-channel segmentation head.

### Verification completed

- Python compilation passed for both entry points and every `src/` module.
- All model files and label mappings were validated.
- Original and runtime model files were verified as checksum-identical.
- Real CPU inference completed with the local model.
- All six required CLI outputs were generated at the source-image resolution.
- Normal candidate selection and the no-qualifying-region path both passed.
- Risk formulas, distance behavior, area filtering, parameter validation, and region ranking were exercised with synthetic masks.
- Streamlit passed a server health check and an application test covering its title, uploader, controls, and proxy-risk warning.

## Scientific limitations

This release receives RGB pixels only. It does not measure physical slope, physical roughness, elevation, depth, wind, vehicle dynamics, or real-world clearance. The slope and roughness layers are fixed semantic risk lookups based solely on predicted class labels. Pixel areas and centroids are not physical areas or navigation coordinates.

The result is appropriate for research demonstrations and visualization, not certified autonomous landing or flight-safety decisions.

## Running the current version

```bash
pip install -r requirements.txt
streamlit run app.py
python run_inference.py --image sample_images/test.jpg
```

Place an aerial RGB image at `sample_images/test.jpg` before running the CLI example.

## Planned future versions

- Add depth or elevation inputs for geometry-aware analysis.
- Estimate physical terrain slope and surface roughness.
- Calibrate thresholds against labeled landing-zone validation data.
- Add ROS2 and Gazebo integration.
- Convert validated image targets into UAV-planner coordinates.
