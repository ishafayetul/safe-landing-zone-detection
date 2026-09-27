# Technical Decisions

These decisions describe the current project contract. Change them only when the user explicitly requests a corresponding design change.

## Model and semantic contract

- Use semantic segmentation as the primary representation for landing-zone analysis.
- Use the locally trained SegFormer-B0 model and keep runtime loading local/offline.
- Preserve the original model files in `models/` and the default runtime copy in `model/`.
- Use a fixed 24-class semantic vocabulary and the trained-dataset RGB palette.
- Keep class order and names aligned across `id2label.json`, `label2id.json`, and `src/risk_config.py`.
- Align semantic, slope-proxy, roughness-proxy, danger, uncertainty, and safe-class configuration with the exact model vocabulary.

The project uses a fixed 24-class semantic vocabulary and RGB palette. Risk configuration, semantic-mask visualization, hazard interpretation, and landing-zone eligibility depend on this exact class order and class naming. Any future change to the class list must update model label maps, risk configuration, visualization palette, tests, and documentation together.

## Risk and hazard interpretation

- Use full class probabilities in addition to the final argmax so weak car or combined-danger evidence can affect risk.
- Dilate effective hazards and hard-exclude the resulting mask from landing candidates.
- Enforce a high-risk floor on hazards after other risk blending.
- Treat `ar-marker` as semantically risky and not a safe candidate unless explicitly enabled.
- Treat the `0.3.3` water override as a separate, temporary safety heuristic—not as a trained detector and not as a modification of the raw semantic mask.

## Inference and landing decision

- Use overlapping tiled inference for large/high-resolution images; keep full-image inference available.
- Select landing centers by whether a circular drone footprint fits completely within a valid surface.
- Use confidence-aware risk and reject regions below the current minimum mean-confidence threshold.
- Keep plain machine-friendly images and labeled research/presentation variants.
- Use sequential `Sample-XX` directories to preserve prior runs and keep each run’s artifacts together.
- Sort all valid regions deterministically and use `Zone-01` as the single source of truth for the best visualization and `landing_target.json`.
- Keep rejected regions out of valid ranked CSV/JSON reports.
- Keep targets in image-pixel coordinates unless calibrated/georeferenced data and an explicit conversion layer are added.

## Project boundaries

- Keep Streamlit and future ROS2/Gazebo integration separate unless explicitly instructed.
- Treat ROS2/Gazebo as a future simulation/workspace consumer, not as implicit scope for changes to this application.
- Keep this project described as a research demo, not certified autonomous-flight software.
