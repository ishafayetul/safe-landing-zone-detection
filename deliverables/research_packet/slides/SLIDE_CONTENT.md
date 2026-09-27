# Slide Content

## Slide 1 — Title

**Safe Landing Zone Detection for Drone Landing using Semantic Segmentation**

Shafayetul Islam  
Department of Computer Science and Engineering

Research Demo • Version 0.3.4

**Subtitle:** From one aerial RGB image to ranked, footprint-valid landing alternatives.

## Slide 2 — Problem Statement

- UAV landing scenes may contain water, vehicles, people, vegetation, structures, obstacles, and narrow surfaces.
- A visually open region may still be unsuitable because it lacks clearance, area, confidence, or footprint fit.
- One RGB image cannot directly measure depth, elevation, physical slope, or roughness.
- The research question: can semantic evidence and explainable proxies produce an inspectable landing-site ranking?

## Slide 3 — Research Motivation

- Emergency or unplanned landing requires rapid visible-terrain assessment.
- Pixel-wise scene understanding distinguishes candidate surfaces from semantic hazards.
- A risk map translates classes and proximity into an interpretable safety view.
- Footprint validation rejects regions that are too narrow or close to invalid surfaces.
- Ranked alternatives are more informative than a single unexamined decision.
- Labeled figures and structured reports support research inspection.

## Slide 4 — System Overview

**Input:** one aerial RGB image  
**Model:** local SegFormer-B0 semantic segmentation  
**Vocabulary:** 24 fixed semantic classes  
**Runtime:** Python, PyTorch, Hugging Face Transformers, Streamlit

**Processing:**

- Full-image or overlapping tiled inference.
- Semantic and probability analysis.
- Risk fusion, hazard dilation, and temporary water override.
- Confidence-aware and footprint-aware validation.
- Deterministic valid-zone ranking.

**Outputs:** semantic mask, overlay, risk map, diagnostics, all/top zones, Rank-1 target, CSV/JSON reports.

## Slide 5 — Methodology Pipeline

```text
RGB image
→ preprocessing and tiled inference
→ SegFormer-B0 logits and probabilities
→ semantic mask
→ probability-aware hazards and water override
→ confidence-aware landing risk
→ safe connected surfaces
→ distance-transform footprint fit
→ scoring and deterministic ranking
→ Zone-01 landing target
```

Key design principle: preserve intermediate outputs so the final decision remains inspectable.

## Slide 6 — Model and 24-Class Vocabulary

**Model facts**

- SegFormer-B0 semantic segmentation.
- 3,720,312 parameters.
- 384×384 processor input.
- 24-channel output head.
- Local/offline model loading with strict label-map validation.

**Class groups**

- Safe: `paved-area`, `grass`, `dirt`, `gravel`.
- Hazards: water/pool, people/animals/vehicles, vegetation/trees/rocks, structures/fences, obstacles/conflicting.
- Uncertain: `unlabeled`.
- Special: `ar-marker`, excluded from safe terrain by default.

Class order, label maps, palette, risk configuration, and visualization must remain aligned.

## Slide 7 — Risk and Hazard Handling

```text
Base Risk =
    0.45  × Semantic Risk
  + 0.25  × Obstacle Proximity Risk
  + 0.15  × Landing Area Size Risk
  + 0.075 × Slope Proxy Risk
  + 0.075 × Roughness Proxy Risk
```

- Slope and roughness are class-based semantic proxies.
- Car probability and summed danger probability can trigger hazards before argmax.
- Effective hazards are dilated and receive a hard high-risk floor.
- Confidence-aware risk lets uncertainty increase final risk.
- Temporary water handling combines model water evidence with conservative RGB cues while preserving the raw semantic mask.

## Slide 8 — Footprint-Aware Landing Zone Selection

1. Keep safe-class pixels below the risk threshold and outside the dilated hazard mask.
2. Form connected candidate surfaces.
3. Measure distance to the nearest invalid pixel or image boundary.
4. Accept centers only where the circular footprint fits.
5. Reject regions for area, risk, hazard overlap, footprint failure, or low confidence.
6. Score valid regions using suitability, fit, clearance, area, shape, and confidence.

Deterministic order: score ↓, mean risk ↑, maximum safe radius ↓, area ↓.

`Zone-01` is the single source for the final landing target.

## Slide 9 — Ranked Safe Zone Results

**Sample-28 image-specific demonstration**

- Valid zones: **1**
- Rank-1: **`Zone-01`**
- Class/category: **`paved-area` / `Very Safe`**
- Score: **0.788**
- Mean risk: **0.131**
- Center: **(639, 502) px**
- Footprint radius: **300.0 px**
- Maximum safe radius: **374.8 px**
- Confidence: **0.904**

The result is stored consistently in the ranked CSV/JSON, best-zone visualization, and landing-target JSON.

**Caution:** one saved image result is not a general accuracy or safety metric.

## Slide 10 — Limitations

- RGB-only input; no depth, elevation, LiDAR, or calibrated geometry.
- No wind, load-bearing capacity, hidden-obstacle, approach-path, or UAV-dynamics model.
- Slope and roughness are semantic proxies.
- Pixel areas and centers are not GPS or planner coordinates.
- Water override is a temporary heuristic and can miss or falsely flag surfaces.
- Near-zero hazard probability cannot be recovered reliably without new data or another detector.
- Thresholds and confidence need representative calibration.
- Research demo; not certified autonomous-flight software.

## Slide 11 — Future Work

- Add depth, elevation, RGB-D, LiDAR, DEM, or point-cloud inputs.
- Estimate physical slope and roughness.
- Retrain on broader water, vehicle, obstacle, reflection, and shadow examples.
- Build a labeled validation set and quantitative safe-zone benchmark.
- Calibrate risk, confidence, hazard, and footprint thresholds.
- Evaluate alternative segmentation architectures.
- Add camera calibration and georeferenced coordinate conversion.
- Integrate with ROS2/Gazebo in a separate workspace before planner experiments.

## Slide 12 — Conclusion

- SegFormer-B0 provides source-aligned semantic scene understanding.
- Explainable risk fusion converts classes into landing suitability.
- Probability-aware hazards and temporary water evidence make exclusion conservative.
- Distance-transform geometry verifies that the drone footprint fits.
- Deterministic ranking exposes all valid alternatives and keeps `Zone-01` consistent with the final target.

**Takeaway:** the project transforms one aerial RGB image into an inspectable ranked landing assessment while clearly preserving its RGB-only, pixel-coordinate, research-demo limitations.
