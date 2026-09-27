# Project Facts Summary

## Identity

| Field | Confirmed fact |
|---|---|
| Title | Safe Landing Zone Detection for Drone Landing using Semantic Segmentation |
| Author | Shafayetul Islam |
| Affiliation | Department of Computer Science and Engineering |
| Project identifier | `safe_landing_zone_demo` |
| Version | `0.3.4` |
| Release stage | Research demo / ranked safe landing zone list |
| Input | One aerial RGB image |
| Model | Locally trained SegFormer-B0 semantic segmentation model |
| Runtime | Python, PyTorch, Hugging Face Transformers, Streamlit |
| Model classes | 24 semantic classes |
| Model parameters | 3,720,312 |
| Processor input | 384×384 |
| Output coordinates | Image pixels/image plane, not GPS or UAV-planner coordinates |

## One-line summary

A semantic-segmentation-based UAV landing-site assessment system that converts one aerial RGB image into semantic masks, risk maps, hazard diagnostics, and a deterministic ranked list of footprint-valid safe landing zones.

## Semantic vocabulary

**Safe candidate classes:** `paved-area`, `grass`, `dirt`, `gravel`.

**Hazard/danger classes:** `water`, `rocks`, `pool`, `vegetation`, `roof`, `wall`, `window`, `door`, `fence`, `fence-pole`, `person`, `dog`, `car`, `bicycle`, `tree`, `bald-tree`, `obstacle`, `conflicting`.

**Uncertain class:** `unlabeled`.

**Special class:** `ar-marker` has semantic risk and is excluded from safe candidates unless explicitly enabled.

The class order, names, and RGB colors must remain aligned across the trained model label maps, `src/risk_config.py`, visualization, tests, and documentation.

## Main pipeline

1. Validate and normalize one aerial RGB image.
2. Load the local SegFormer-B0 model and strict 24-class mappings.
3. Run full-image or overlapping tiled semantic inference.
4. Produce source-resolution class probabilities and the semantic mask.
5. Combine semantic risk, obstacle proximity, landing-area size, slope proxy, and roughness proxy.
6. Add probability-aware hazard evidence, dilation, hard exclusion, confidence-aware risk, and the temporary water safety override.
7. Form safe, low-risk, non-hazard surfaces and apply a Euclidean distance transform.
8. Verify that the circular drone footprint fits inside each candidate region.
9. Score and deterministically rank every valid region; `Zone-01` becomes the final target.
10. Export labeled/plain figures, CSV/JSON reports, and run metadata.

## Key limitations

- RGB-only input provides no direct depth, elevation, terrain geometry, or physical scale.
- Slope and roughness are semantic class proxies, not physical measurements.
- Wind, hidden obstacles, load-bearing capacity, approach path, and UAV dynamics are not modeled.
- Landing targets are image-pixel coordinates, not GPS or calibrated planner coordinates.
- The water override is a temporary probability/RGB safety heuristic, not a trained water detector.
- Hazards receiving almost zero model probability cannot be recovered reliably without better data, retraining, or a separate detector.
- Thresholds and confidence require representative calibration and validation.
- The project is a research demonstration, not certified autonomous-flight or landing-safety software.
