# Feature History by System Area

This view groups changes by capability. Detailed release evidence remains in `VERSION.md`.

## Model loading and validation

- `0.1.0`: Added local-only SegFormer model/processor loading, automatic CUDA selection, and CPU fallback.
- `0.2.0`: Added strict validation of the exact 24 class names and order against the two label-map files.

## Inference

- `0.1.0`: Added one-image RGB validation, EXIF handling, inference, and source-resolution logit resizing.
- `0.2.0`: Preserved source-resolution softmax probabilities and added overlapping tiled inference with averaged logits.
- `0.3.0`: Added source-resolution confidence, normalized uncertainty, and top-class margin calculations.

## Risk map

- `0.1.0`: Combined semantic, obstacle-proximity, area-size, slope-proxy, and roughness-proxy risks.
- `0.2.0`: Aligned all class risks with the 24-label model and enforced a hard hazard-risk floor.
- `0.3.0`: Added optional confidence-aware risk, enabled by default, while reapplying the hazard floor.

## Hazard detection

- `0.1.0`: Used semantic danger classes for obstacle proximity.
- `0.2.0`: Combined danger argmax labels, car probability, and summed danger probability; added elliptical dilation and hard exclusion from candidates.
- `0.3.3`: Added effective-water evidence to the same hazard, proximity, and exclusion pipeline.

## Water override

- `0.3.3`: Added the temporary water-probability and conservative RGB-heuristic override, connected-component filtering, source counts, diagnostic overlays, and debug maps. It remains a temporary safety heuristic rather than a trained detector.

## Landing-zone selection

- `0.1.0`: Added connected-component candidates, area filtering, scoring, and one best region.
- `0.2.0`: Required candidates to remain outside the dilated probability-aware hazard mask.
- `0.3.0`: Shifted the decision to a valid footprint center and added explicit rejection reasons.
- `0.3.4`: Ranked all valid zones deterministically and made sorted `Zone-01` the sole best-zone source.

## Footprint handling

- `0.3.0`: Added configurable pixel radius, optional scale/diameter conversion, boundary-aware distance transform, footprint-valid center mask, maximum-inscribed-radius center, and fit scoring.
- `0.3.4`: Added footprint and clearance fields for every ranked zone plus display limits for footprint circles.

## Confidence and uncertainty

- `0.3.0`: Added maximum-class confidence, normalized entropy, top-1/top-2 margin, confidence-risk blending, a default `0.50` mean-confidence rejection threshold, and debug maps.
- `0.3.4`: Added confidence, uncertainty, and margin values to every valid ranked-zone report.

## Ranked safe zones

- `0.3.4`: Added stable `Zone-XX` IDs; valid-only four-key sorting; full CSV/JSON reports; all-zone/top-zone graphics; semantic risk categories; Streamlit downloads; and CLI display limits.

## Visualization

- `0.1.0`: Added semantic mask, overlay, risk heatmap, and annotated best-zone image.
- `0.2.0`: Switched semantic rendering to the trained palette and added red hazard rendering plus debug probability/risk images.
- `0.3.0`: Added footprint circle, maximum-clearance center, safe-radius details, and confidence/valid-center maps.
- `0.3.2`: Added presentation-friendly labeled counterparts with titles, legends, colorbars, and explanations.
- `0.3.3`: Added water-source overlay and water debug/labeled views.
- `0.3.4`: Added all-ranked and top-ranked zone graphics, labels, footprint symbols, and summary panels.

## Streamlit interface

- `0.1.0`: Added upload, risk/area/opacity controls, results, and graceful no-zone handling.
- `0.2.0`: Added tiling, hazard thresholds, dilation, AR-marker policy, and debug visibility controls.
- `0.3.0`: Added footprint/scale/confidence controls, decision summary, and rejection debugging; removed reliance on Pandas Styler/Jinja2.
- `0.3.1`: Added explicit run-and-save action and session-state retention so widget reruns do not create outputs.
- `0.3.2`: Added labeled/plain output switching.
- `0.3.3`: Added water-override controls and source diagnostics.
- `0.3.4`: Added ranked-zone count, complete table, gallery, top-N/display controls, and CSV/JSON downloads.

## CLI interface

- `0.1.0`: Added basic one-image inference and risk/area/output controls.
- `0.2.0`: Added tile, hazard, AR-marker, device, and debug options while retaining the original command.
- `0.3.0`: Added footprint radius, optional scale conversion, and confidence-risk controls.
- `0.3.2`: Added default-on labeled saving and `--no_labeled`.
- `0.3.3`: Added temporary water-override options.
- `0.3.4`: Added top-N, maximum-label, and maximum-footprint-circle options plus Rank-1 console reporting.

## Output folders and metadata

- `0.1.0`: Saved six core files to the output directory.
- `0.2.0`: Added optional debug artifacts.
- `0.3.0`: Added rejection and landing-target reports.
- `0.3.1`: Added non-overwriting `Sample-XX` folders, normalized input copy, backward-compatible original copy, and run metadata.
- `0.3.2`: Added metadata for labeled-output settings and generated files.
- `0.3.3`: Added water settings and source-specific counts.
- `0.3.4`: Added ranked-zone files, counts, limits, and safe-zone artifact metadata.

## Testing/verification

- `0.1.0`: Compilation, model-file/label validation, real CPU inference, synthetic risk/selection checks, and Streamlit health/application tests.
- `0.2.0`: Synthetic probability/hazard tests, real tiled CPU inference, palette checks, and interface compatibility tests.
- `0.3.0`: Synthetic footprint/geometry/confidence/scale tests and real tiled CPU output verification.
- `0.3.1`: Sequential numbering, non-overwrite, Streamlit click behavior, metadata, and model-integrity checks.
- `0.3.2`: Synthetic and visual labeled-render checks plus CLI/Streamlit opt-in/out verification.
- `0.3.3`: Synthetic water cases, a real missed-water image, raw semantic checksum preservation, and interface/model-integrity checks.
- `0.3.4`: Synthetic valid-only ranking, real four-tile CPU run, no-zone schema test, output consistency, visual checks, Streamlit AppTest, and pairwise model-hash verification.
