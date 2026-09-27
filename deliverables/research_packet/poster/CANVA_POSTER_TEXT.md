# Canva Poster Text

## Header

**Safe Landing Zone Detection for Drone Landing using Semantic Segmentation**

Shafayetul Islam  
Department of Computer Science and Engineering

*Research Demo • UAV Safe Landing Zone Selection • Version 0.3.4*

**Summary:** A semantic-segmentation-based UAV landing-site assessment system that converts one aerial RGB image into semantic masks, risk maps, and ranked safe landing zones.

## Problem Statement

Autonomous UAVs must identify plausible landing areas while avoiding water, vehicles, people, vegetation, structures, obstacles, narrow surfaces, and uncertain terrain. A single RGB image cannot directly measure depth, physical slope, or roughness, so this project combines semantic scene understanding with explainable risk proxies and footprint-aware geometry.

## Research Motivation

- Emergency or unplanned landings benefit from fast, interpretable terrain assessment.
- A semantic mask alone does not guarantee adequate area, clearance, confidence, or footprint fit.
- Ranked alternatives expose candidate quality and preserve fallback choices.
- Labeled figures and CSV/JSON reports make the decision traceable.

## Objectives

1. Segment one aerial RGB image into 24 semantic classes.
2. Convert semantic predictions into a landing-risk map.
3. Detect and conservatively exclude hazards.
4. Verify that a circular drone footprint fits.
5. Rank all valid landing regions.
6. Export interpretable visual and structured results.

## System Overview

**Input:** One aerial RGB image  
**Model:** Locally trained SegFormer-B0, 24 classes  
**Runtime:** Python, PyTorch, Hugging Face Transformers, Streamlit  
**Outputs:** Semantic mask, overlay, risk map, hazard diagnostics, all/top ranked zones, Rank-1 target, CSV/JSON reports

## Methodology

```text
Aerial RGB Image → Preprocessing → SegFormer-B0 Segmentation
→ Semantic Mask and Class Probabilities → Probability-Aware Hazards
→ Temporary Water Safety Override → Landing Risk Map
→ Footprint-Valid Candidate Extraction → Deterministic Ranking
→ Final Zone-01 Landing Target
```

## Risk Formulation

```text
Final Risk =
    0.45  × Semantic Risk
  + 0.25  × Obstacle Proximity Risk
  + 0.15  × Landing Area Size Risk
  + 0.075 × Terrain Slope Proxy Risk
  + 0.075 × Surface Roughness Proxy Risk

Landing Suitability = 1 − Final Risk
```

Probability-aware hazards, confidence-aware risk, water safety evidence, hazard dilation, and a hard hazard floor make the final decision more conservative.

## Footprint-Aware Ranked Selection

- Safe candidates: `paved-area`, `grass`, `dirt`, `gravel`.
- Candidate pixels must meet the risk threshold and remain outside the dilated hazard mask.
- Regions must meet area and confidence requirements.
- A Euclidean distance transform verifies that the requested circular footprint fits.
- Valid zones are sorted by score descending, mean risk ascending, maximum safe radius descending, and area descending.
- `Zone-01` is the authoritative best landing target.

## Sample-28 Demonstration Result

**1 valid `Very Safe` `paved-area` zone**

- Zone: `Zone-01`
- Score: `0.788`
- Mean risk: `0.131`
- Center: `(639, 502)` px
- Footprint radius: `300.0` px
- Maximum safe radius: `374.8` px
- Confidence: `0.904`

*Image-specific demonstration only—not a general accuracy or safety claim.*

## Key Features

- Exact 24-class model vocabulary and trained palette.
- Full-image or overlapping tiled inference.
- Probability-aware hazard handling and dilation.
- Temporary water safety override without changing the raw semantic mask.
- Confidence and uncertainty analysis.
- Footprint-aware candidate validation.
- Stable zone IDs and deterministic valid-only ranking.
- Labeled visual outputs and ranked CSV/JSON reports.

## Limitations

- RGB only; no direct depth, elevation, wind, or vehicle dynamics.
- Slope and roughness are semantic proxies, not physical measurements.
- Targets are image pixels, not GPS or UAV-planner coordinates.
- Water handling is a temporary heuristic, not a trained detector.
- Thresholds require validation and calibration.
- Research demo; not certified for autonomous landing.

## Future Work

- Add depth/elevation and calibrated ground scale.
- Estimate physical slope and roughness.
- Retrain with broader water, vehicle, obstacle, shadow, and reflection data.
- Add quantitative benchmarks and threshold calibration.
- Integrate with ROS2/Gazebo as a separate workspace.
- Convert validated pixel targets into calibrated planner coordinates.

## Conclusion

SegFormer-based scene understanding, explainable risk fusion, conservative hazard handling, footprint-aware geometry, and deterministic ranking transform one aerial RGB image into inspectable safe landing alternatives, with `Zone-01` linked consistently to the final landing target.

**Legend:** green contour = valid zone • white circle = drone footprint • cyan point = selected center • red overlay = hazard/excluded area • green→yellow→red = low→medium→high risk
