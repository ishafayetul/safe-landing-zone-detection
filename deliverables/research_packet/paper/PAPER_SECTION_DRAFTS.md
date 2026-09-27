# Paper Section Drafts

## Abstract

Safe UAV landing-site selection requires more than identifying visually open terrain: candidate regions must avoid semantic hazards, maintain adequate clearance, contain sufficient connected area, and accommodate the vehicle footprint. This paper presents an RGB-only research demonstration that combines a locally trained SegFormer-B0 semantic segmentation model with explainable landing-risk fusion, probability-aware hazard interpretation, a temporary water safety override, confidence analysis, and footprint-aware region validation. The model predicts 24 semantic classes from one aerial RGB image. Full-resolution probabilities and labels are converted into risk and hazard maps, after which a boundary-aware Euclidean distance transform identifies centers where a circular drone footprint fits completely within a valid surface. All qualifying regions are scored and sorted deterministically, with `Zone-01` serving as the single source for the final visual and structured target. In the Sample-28 demonstration, the system identifies one `Very Safe` paved-area zone with score 0.788, mean risk 0.131, center `(639, 502)` pixels, a required radius of 300.0 pixels, and an available safe radius of 374.8 pixels. These values illustrate pipeline behavior for one image and do not constitute general accuracy or operational-safety evidence. The current system is intended for research visualization and requires geometric sensing, calibration, broader validation, and planner integration before any operational use.

## Keywords

UAV landing, semantic segmentation, SegFormer, aerial imagery, risk mapping, hazard detection, footprint-aware landing, uncertainty.

## I. Introduction

Unmanned aerial vehicles may need to identify landing areas in scenes containing water, vehicles, people, vegetation, structures, obstacles, and irregular terrain. Vision-based landing analysis is attractive because cameras are common and provide dense scene information, but a visually open surface is not automatically suitable for landing `[REF]`. A useful landing assessment must distinguish terrain classes, interpret nearby hazards, account for uncertainty, and verify that the vehicle footprint can fit within the available region.

Semantic segmentation provides a pixel-wise representation of the visible scene and has been widely studied for computer vision and aerial imagery `[REF]`. However, direct selection from a class mask omits several landing-related considerations. A connected safe-class component may be too small, too narrow, too close to a danger region, or predicted with insufficient confidence. Furthermore, a single RGB image cannot directly provide physical slope, elevation, roughness, or load-bearing capacity.

This work develops an inspectable RGB-only research pipeline around a locally trained SegFormer-B0. The system retains full class probabilities, constructs an explainable risk map, applies conservative hazard and water handling, evaluates footprint-valid centers with a distance transform, and reports all valid zones in deterministic order. The principal contributions are: (1) an exact 24-class semantic and risk contract; (2) probability-aware danger interpretation and hard hazard exclusion; (3) confidence-aware and footprint-aware landing validation; (4) stable valid-only zone ranking with `Zone-01` linked to the final target; and (5) labeled visual and CSV/JSON outputs that preserve intermediate evidence.

## II. Related Work

Semantic segmentation methods for aerial and remote-sensing imagery provide relevant context for the scene-understanding component `[REF]`. SegFormer and other transformer-based segmentation architectures should be discussed using verified primary sources `[REF]`. Vision-based UAV landing-site detection and autonomous landing methods form a second group of related work `[REF]`. A third group concerns uncertainty estimation, risk-aware perception, and geometric clearance or footprint constraints `[REF]`.

This section is intentionally a placeholder. Before publication, select relevant peer-reviewed or authoritative sources, verify each claim against the source, and replace `[REF]` with real bibliography keys. No citation should be inferred from the current implementation alone.

## III. Methodology

The system receives one aerial RGB image and returns source-aligned semantic, risk, hazard, confidence, uncertainty, footprint, and landing-zone products. The image is orientation-corrected and converted to RGB. Inference may operate on the full image or on overlapping tiles. In the tiled path, tile logits are resized to their source tile dimensions, accumulated on the source-resolution canvas, and averaged in overlap regions before softmax probabilities and final class labels are obtained.

The pipeline preserves both the semantic argmax mask and the full class-probability tensor. The argmax mask provides the raw semantic prediction, while probabilities support hazard thresholds, confidence, normalized entropy, top-1/top-2 margin, and temporary water evidence. Risk and hazard processing remain separate from the raw semantic visualization so safety overrides do not silently alter the model output.

After the final risk and dilated hazard mask are available, candidate pixels must belong to a configured safe class, remain at or below the selected risk threshold, and lie outside the effective hazard region. Connected surfaces are assessed for area, confidence, geometry, obstacle clearance, and footprint fit. Valid surfaces are scored, deterministically sorted, assigned stable zone identifiers, visualized, and exported to CSV and JSON.

## IV. Semantic Segmentation Model

The semantic model is a locally trained SegFormer-B0 loaded offline with PyTorch and Hugging Face Transformers. The verified model has 3,720,312 parameters, a 384×384 image-processor input, and a 24-channel segmentation head. Runtime loading requires `model.safetensors`, `config.json`, `preprocessor_config.json`, `label2id.json`, and `id2label.json`.

Strict validation requires contiguous IDs from 0 through 23, exact inverse label maps, and equality between the ordered model labels and the configured class vocabulary. The four ordinary safe candidate classes are `paved-area`, `grass`, `dirt`, and `gravel`. Eighteen classes represent water, objects, vegetation, structures, and other danger-related content. `unlabeled` is treated as uncertain. `ar-marker` has semantic risk and is excluded from normal safe candidates unless explicitly enabled.

The class order and RGB palette form a system contract. Risk configuration, semantic visualization, hazard interpretation, and landing eligibility all depend on the same names and IDs. A future class change must therefore update the model label maps, configuration, visualization, tests, and documentation together.

## V. Risk Map Generation

The base landing risk combines five interpretable factors:

```text
R_base = 0.45 R_semantic
       + 0.25 R_proximity
       + 0.15 R_area
       + 0.075 R_slope_proxy
       + 0.075 R_roughness_proxy.
```

Landing suitability is defined as `1 − R`. Semantic risk is a fixed class lookup. Obstacle-proximity risk is derived from distance to the effective hazard mask. Area risk penalizes connected safe regions below the desired size. Slope and roughness risks are also fixed semantic lookups; they are not measurements of physical geometry or surface texture.

For each source-resolution pixel, maximum class probability provides a confidence map, normalized entropy provides an uncertainty map, and the top-1/top-2 probability difference provides a margin map. When confidence-aware risk is enabled, the current system blends 85% of the preexisting final risk with 15% normalized uncertainty and clips the result to `[0,1]`. The hard hazard floor is reapplied afterward so uncertainty blending cannot weaken an effective hazard.

## VI. Hazard and Water Safety Handling

Hazard reasoning uses both semantic labels and probabilities. Pixels predicted as configured danger classes contribute directly to the hazard mask. In addition, car probability and summed danger-class probability can trigger hazard evidence even when those classes do not win the final argmax. The effective hazard is dilated with an elliptical kernel, used in obstacle-proximity risk, excluded from landing candidates, and forced to at least the configured high-risk floor.

Version 0.3.3 introduced a temporary water safety override for cases in which the segmentation model provides weak water evidence. The layer combines predicted water labels, a low water-probability threshold, and conservative RGB cues for smooth non-green blue/cyan or dark-neutral surfaces. RGB-only evidence is limited to otherwise landable semantic classes and small connected components are filtered. Effective water enters the existing hazard path, while the raw semantic mask and class-coverage report remain unchanged.

This override is not a trained water detector. Reflective, muddy, shadowed, or vegetation-covered water may be missed, while blue roofs, shadows, smooth dark surfaces, and reflections may be false positives. Representative retraining or a separately validated detector is the appropriate long-term solution.

## VII. Footprint-Aware Landing Zone Selection

The valid surface mask contains safe semantic classes whose final risk is below the configured threshold and which remain outside the dilated hazard mask. A Euclidean distance transform measures each valid pixel’s distance to the nearest invalid pixel or image boundary. A pixel is a footprint-valid center only when this distance is at least the resolved circular footprint radius.

Connected regions are rejected when they fail minimum area, risk, hazard, footprint, or confidence requirements. For every valid region, the location with maximum distance-transform value becomes the best center and the corresponding value is the maximum inscribed safe radius. Additional descriptors include bounding box, centroid, compactness, aspect ratio, elongation, confidence, uncertainty, probability margin, and hazard distance.

The current region score is:

```text
S = 0.30 mean_suitability
  + 0.25 footprint_fit
  + 0.15 obstacle_clearance
  + 0.10 normalized_area
  + 0.10 shape_quality
  + 0.10 confidence.
```

Valid regions are sorted by score descending, mean risk ascending, maximum inscribed radius descending, and area descending. Stable identifiers `Zone-01`, `Zone-02`, and so on are assigned after sorting. `Zone-01` is the only source for the best-zone visualization and `landing_target.json`; rejected regions remain outside the ranked valid-zone reports.

## VIII. Experimental Demonstration

The included demonstration uses `outputs/Sample-28/`, generated from source file `525.jpg`. The recorded run used CPU tiled inference with 512-pixel tiles and 96-pixel overlap. The risk threshold was 0.45, the circular footprint radius was 300 pixels, confidence-aware risk and the temporary water override were enabled, and labeled/debug outputs were saved.

The packet contains the normalized 3375×2250 RGB input, semantic and overlay figures, the risk map, water diagnostics, confidence/uncertainty/margin maps, footprint-valid centers, all/top/best landing-zone visualizations, and the authoritative CSV/JSON reports. This case is used to illustrate pipeline operation and output consistency. It is not a held-out benchmark, ablation study, or dataset-level evaluation.

## IX. Results and Discussion

The ranked reports contain one valid zone. `Zone-01` is dominated by `paved-area` and assigned the semantic risk category `Very Safe`. Its score is 0.78784, mean risk is 0.13145, and mean suitability is 0.86855. The selected center is `(639, 502)` pixels. A requested footprint radius of 300.0 pixels fits within a maximum inscribed safe radius of 374.80 pixels. The reported confidence score is 0.90401, uncertainty is 0.14332, and probability margin is 0.87403.

The footprint result shows that the selected center retains additional image-plane clearance beyond the requested radius. The high confidence and margin values indicate strong model preference within the selected region for this run, but they should not be interpreted as calibrated correctness probabilities. Likewise, the `Very Safe` category is a configured semantic-demo label, not an aviation certification.

The same zone ID, center, score, class, risk, and radius values are represented in `ranked_safe_zones.csv`, `ranked_safe_zones.json`, `landing_target.json`, and the best-zone visualization. This consistency is important because version 0.3.4 deliberately removes any separate best-zone calculation. Rejected regions are retained in a separate report and do not enter the valid ranked list.

## X. Limitations

The current input contains RGB pixels only. It does not directly measure depth, elevation, physical slope, physical roughness, wind, load-bearing capacity, hidden obstacles, approach-path clearance, or UAV dynamics. Pixel distances and areas are not physical values unless calibration and scale are supplied. The selected center is not a GPS or UAV-planner coordinate.

Results depend on the segmentation model, its training data, probability calibration, and configured thresholds. Probability-aware logic cannot recover a hazard to which the model assigns almost zero probability. The water override is heuristic and temporary. Finally, this packet presents one image-specific demonstration rather than a quantitative validation study, so no claim is made about general accuracy, robustness, or operational safety.

## XI. Future Work

Future evaluation should use a representative labeled dataset with explicit safe-zone ground truth, environmental diversity, and quantitative measures for segmentation, hazard detection, region ranking, and target suitability. Threshold and confidence calibration should be performed on validation data, and alternative segmentation or auxiliary detection models should be compared using a documented protocol `[REF]`.

Depth, elevation, RGB-D, stereo, LiDAR, DEM, or point-cloud data could support physical slope, roughness, and clearance estimation. Broader water, vehicle, obstacle, shadow, and reflection examples are needed for improved model behavior. Camera calibration, pose, scale, and external positioning are required before converting image pixels into navigation coordinates. ROS2 and Gazebo integration should be implemented as a separate workspace after the perception and coordinate contracts are validated.

## XII. Conclusion

This work presents an inspectable pipeline that combines SegFormer-based semantic segmentation, explainable risk fusion, probability-aware hazard handling, a temporary water safety layer, confidence analysis, footprint-aware geometry, and deterministic valid-zone ranking. The approach converts one aerial RGB image into labeled intermediate products and structured landing alternatives while maintaining `Zone-01` as the consistent final target. Sample-28 demonstrates the complete workflow and report agreement for one image. Broader validation, geometric sensing, calibration, and planner integration remain necessary before operational use.
