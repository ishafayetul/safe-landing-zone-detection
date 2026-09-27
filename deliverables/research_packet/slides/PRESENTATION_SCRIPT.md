# Presentation Script

## Slide 1 — Title

This project investigates safe landing-zone assessment from one aerial RGB image. The system uses a locally trained SegFormer-B0 to understand the scene, then adds explainable risk, hazard exclusion, footprint geometry, and deterministic ranking. The current release is version 0.3.4, a research demonstration rather than certified autonomous-flight software.

## Slide 2 — Problem Statement

A landing site can look open and still be unsafe. Water, vehicles, vegetation, structures, obstacles, and narrow terrain all matter, and a single RGB view cannot directly reveal depth, physical slope, or roughness. The challenge is therefore to turn visible semantic evidence into a transparent, conservative assessment without pretending that RGB provides unavailable physical measurements.

## Slide 3 — Research Motivation

Semantic segmentation is useful because it labels every pixel, but a semantic mask is not enough for landing. We also need risk, clearance, area, confidence, and space for the drone itself. Ranking every valid alternative makes the result easier to inspect than a single unexplained point and gives future planning systems a structured list rather than only a binary answer.

## Slide 4 — System Overview

The input is one aerial RGB image. SegFormer-B0 produces probabilities for a fixed 24-class vocabulary. The pipeline then generates hazard evidence, water-safety evidence, confidence and uncertainty, a final risk map, footprint-valid centers, and ranked connected regions. Results are available through Streamlit and the command line and are saved as labeled images plus CSV and JSON reports.

## Slide 5 — Methodology Pipeline

The pipeline begins with image validation and either full-image or tiled inference. It preserves class probabilities, not only the final argmax mask. Those probabilities support hazard reasoning and uncertainty. After risk fusion, candidate pixels must be safe-class, low-risk, and outside hazards. A distance transform verifies footprint fit, then valid regions are scored, sorted, labeled, and exported. Each intermediate stage is retained for inspection.

## Slide 6 — Model and 24-Class Vocabulary

The local SegFormer-B0 has about 3.72 million parameters, a 384-by-384 processor input, and 24 output classes. Four terrain classes are configured as normal safe candidates. Eighteen classes describe hazards or danger-related content, while unlabeled is uncertain and ar-marker is handled specially. The exact label order and palette are a model contract, so label maps, risk configuration, and visualization must stay synchronized.

## Slide 7 — Risk and Hazard Handling

The base risk combines semantic class, obstacle proximity, connected area size, and semantic slope and roughness proxies. Those last two are explicitly not physical measurements. Probability-aware hazard logic can respond to weak car or combined-danger evidence before it wins argmax. Hazards are dilated and forced to high risk. A separate temporary water layer combines model and RGB evidence while leaving the raw semantic mask unchanged.

## Slide 8 — Footprint-Aware Landing Zone Selection

Area alone is not sufficient because a large but narrow region may not fit the drone. The system computes distance from each valid pixel to the nearest invalid surface or image boundary. A center qualifies only if that distance reaches the requested footprint radius. Regions can still be rejected for insufficient area, excessive risk, hazard overlap, low confidence, or lack of footprint fit. The remaining regions receive a multi-factor score and deterministic order.

## Slide 9 — Ranked Safe Zone Results

For Sample-28, the reports contain one valid zone. Zone-01 is a paved-area region categorized as Very Safe, with a score of about 0.788 and mean risk of about 0.131. Its selected center is pixel 639, 502. The requested 300-pixel radius fits inside an available safe radius of about 374.8 pixels, and the mean confidence score is about 0.904. These values agree across the ranked reports and final target file.

This is one image-specific demonstration. It is not a dataset-level accuracy result and it should not be interpreted as a safety guarantee.

## Slide 10 — Limitations

The most important limitation is sensing: one RGB image cannot provide physical terrain geometry, depth, wind, or vehicle dynamics. Slope and roughness remain class-based proxies. The selected target is an image pixel, not a GPS or planner coordinate. The temporary water heuristic may miss difficult water or flag similar-looking surfaces. The model and thresholds also require validation on representative target environments.

## Slide 11 — Future Work

The next research steps are stronger validation and richer sensing. That includes labeled safe-zone benchmarks, calibrated thresholds, and broader water and obstacle data. Depth, elevation, or point clouds could support real slope and roughness estimates. Camera calibration and external positioning are needed for planner coordinates. ROS2 and Gazebo integration should remain a separate workspace until the perception output and coordinate contract are validated.

## Slide 12 — Conclusion

The contribution is an inspectable chain from semantic scene understanding to risk, conservative hazard handling, footprint-aware geometry, and ranked alternatives. Version 0.3.4 guarantees that Zone-01 in the sorted valid list is also the final visualized and exported target. The system is useful as a research and communication platform, while its RGB-only, pixel-coordinate, and non-certified scope remains explicit.
