# Poster Generation Description

## Project Identity

| Field | Details |
|---|---|
| Project title | Safe Landing Zone Detection for Drone Landing using Semantic Segmentation |
| Author | Shafayetul Islam |
| Affiliation | Department of Computer Science and Engineering |
| Project type | Research demo / UAV safe landing zone selection |
| Input | One aerial RGB image |
| Model | Locally trained SegFormer-B0 semantic segmentation model |
| Runtime | Python, PyTorch, Hugging Face Transformers, Streamlit |
| Current version | 0.3.4 — Ranked safe landing zone list |

## One-Line Summary

A semantic-segmentation-based UAV landing-site assessment system that converts aerial RGB imagery into semantic masks, risk maps, and ranked safe landing zones.

## Problem Statement

Autonomous UAVs must identify safe landing areas within complex aerial scenes. Water, vehicles, vegetation, structures, obstacles, narrow surfaces, and uncertain terrain can make a visually open area unsafe. Because one RGB image cannot provide true depth, slope, elevation, or physical roughness, this project combines semantic segmentation with explainable risk proxies, hazard exclusion, confidence analysis, and footprint-aware geometry to assess possible landing sites.

## Research Motivation

- Emergency or unplanned UAV landings require a fast and interpretable assessment of the visible terrain.
- A pixel-wise scene understanding model can distinguish potentially landable surfaces from water, vehicles, people, structures, vegetation, and other hazards.
- A class mask alone is insufficient: a landing surface must also have low risk, adequate clearance, enough area, and space for the drone footprint.
- Ranked alternatives are more useful than a single binary decision because they expose candidate quality and preserve fallback choices.
- Explicit visual outputs and CSV/JSON reports make the decision pipeline easier to inspect in a research demonstration.

## Objectives

1. Predict semantic classes from aerial RGB images.
2. Generate a semantic landing risk map.
3. Detect hazards such as water, vehicles, vegetation, structures, and obstacles.
4. Apply footprint-aware landing zone validation.
5. Rank all possible safe landing zones by risk and suitability.
6. Save interpretable visual outputs for research presentation.

## System Input, Model, and Output

**Input**

- One aerial RGB image in JPEG or PNG format.

**Model**

- A locally trained SegFormer-B0 semantic segmentation model.
- A 24-class pixel-wise semantic prediction vocabulary.
- Offline loading through Hugging Face Transformers with PyTorch inference.

**Outputs**

- Predicted semantic class mask.
- Segmentation overlay on the original image.
- Semantic landing risk map.
- Best footprint-valid landing zone.
- All ranked safe landing zones and a Top-N view.
- Candidate, rejection, class-coverage, and landing-target reports in CSV/JSON form.

## Methodology Workflow

```text
Aerial RGB Image
→ Preprocessing
→ SegFormer-B0 Semantic Segmentation
→ Semantic Class Mask
→ Probability-Aware Hazard Detection
→ Temporary Water Safety Override
→ Semantic Landing Risk Map
→ Footprint-Aware Candidate Extraction
→ Ranked Safe Landing Zone List
→ Final Landing Target
```

1. **Aerial RGB image:** A single overhead RGB image provides the visible scene; no depth or elevation sensor is assumed.
2. **Preprocessing:** The image is orientation-corrected, converted to RGB, and processed either as a full image or as overlapping high-resolution tiles.
3. **SegFormer-B0 segmentation:** The trained model produces per-class logits and probabilities for 24 semantic classes; logits are resized to source-image resolution.
4. **Semantic class mask:** The maximum-probability class becomes the raw pixel-wise semantic prediction and is rendered with the trained dataset palette.
5. **Probability-aware hazards:** Argmax danger labels are combined with weak probability evidence, including class-specific car probability and summed danger probability.
6. **Temporary water override:** Low water-probability evidence and a conservative RGB heuristic can mark additional water-like areas without changing the raw semantic mask.
7. **Landing risk map:** Semantic, proximity, area, slope-proxy, and roughness-proxy risks are combined; hazards receive a hard high-risk floor and uncertainty can increase risk.
8. **Footprint-aware extraction:** Safe, low-risk, non-hazard pixels form connected regions. A Euclidean distance transform tests whether the circular drone footprint fits fully inside each region.
9. **Ranked safe zones:** Valid regions are scored using suitability, footprint fit, obstacle clearance, area, shape, and confidence, then assigned stable IDs such as `Zone-01` and `Zone-02`.
10. **Final target:** Rank 1 becomes the best landing zone and provides the selected image-pixel center, footprint circle, bounding box, class, score, and risk.

## Safe Zone Factors

1. **Terrain semantic category:** Each predicted class has a configured base landing risk; paved areas are generally preferred over grass, dirt, or gravel.
2. **Obstacle proximity:** Euclidean distance to the effective hazard mask is converted into a proximity penalty, so regions closer to hazards receive higher risk.
3. **Landing area size:** Connected safe surfaces are evaluated against minimum and desired pixel-area thresholds.
4. **Terrain slope proxy:** A class-dependent lookup represents likely slope risk but does not measure geometric slope.
5. **Surface roughness proxy:** A class-dependent lookup represents likely surface roughness but does not measure physical texture or vibration.

Because the input is RGB only, slope and roughness are not measured physically. They are semantic proxy risks inferred from the predicted terrain class.

## Risk Formulation

The original five-factor formulation is:

```text
Final Risk =
    0.45  × Semantic Risk
  + 0.25  × Obstacle Proximity Risk
  + 0.15  × Landing Area Size Risk
  + 0.075 × Terrain Slope Proxy Risk
  + 0.075 × Surface Roughness Proxy Risk
```

```text
Landing Suitability = 1 − Final Risk
```

The current system extends this foundation with probability-aware hazard overrides, a hard hazard-risk floor, optional confidence-aware risk, the temporary water safety override, and footprint-aware validation. When confidence-aware risk is enabled, normalized uncertainty contributes 15% of the final blended risk, after which the hard hazard floor is reapplied.

Valid regions are ranked with:

```text
Region Score =
    0.30 × Mean Suitability
  + 0.25 × Footprint Fit Score
  + 0.15 × Obstacle Clearance Score
  + 0.10 × Normalized Area Score
  + 0.10 × Shape Quality Score
  + 0.10 × Confidence Score
```

Sorting uses score descending, mean risk ascending, maximum inscribed radius descending, and area descending.

## Model Classes and Landing Suitability

**Safe candidate classes**

```text
paved-area, grass, dirt, gravel
```

**Hazard / obstacle classes**

```text
water, pool, rocks, vegetation, roof, wall, window, door,
fence, fence-pole, person, dog, car, bicycle, tree,
bald-tree, obstacle, conflicting
```

**Uncertain class**

```text
unlabeled
```

**Special class**

`ar-marker` is not treated as normal safe terrain unless explicitly enabled.

Together, the four safe classes, 18 hazard classes, one uncertain class, and one special class form the model's exact 24-class vocabulary.

## Main Algorithms

### Semantic Segmentation

SegFormer-B0 assigns every source-resolution pixel to one of 24 semantic classes. Overlapping tiled inference can preserve small objects and fine scene structure in high-resolution aerial images by averaging tile logits before probabilities and class labels are calculated.

### Probability-Aware Hazard Detection

Hazard reasoning uses both final class labels and class probabilities. Predicted danger labels, car probability, and summed danger-class probability are combined, then dilated to create a conservative exclusion zone. This allows weak hazard evidence to influence safety before it wins the final argmax class.

### Temporary Water Safety Override

A separate water-safety layer combines model-predicted water, a low water-probability threshold, and a conservative RGB appearance heuristic. Effective water pixels enter the hazard pipeline and are excluded from landing candidates, while the raw SegFormer semantic mask remains unchanged.

### Footprint-Aware Landing Validation

The valid surface mask contains safe semantic classes whose final risk is at or below the configured threshold and which lie outside the dilated hazard mask. A distance transform measures the distance to the nearest invalid pixel or image boundary. A region is valid only when its maximum inscribed radius is at least the requested drone footprint radius.

### Ranked Safe Landing Zones

Connected valid regions are evaluated for area, risk, suitability, dominant class, maximum safe radius, footprint fit, obstacle clearance, compactness, elongation, confidence, uncertainty, and probability margin. Regions that fail area, footprint, confidence, risk, or hazard rules remain in rejection reports. Valid regions are sorted deterministically and assigned `Zone-01`, `Zone-02`, and subsequent IDs; `Zone-01` is the final landing target.

## Version 0.3.4 Features

- All valid safe zones are detected rather than retaining only one region.
- Each zone receives a stable ID such as `Zone-01` or `Zone-02`.
- Zones are sorted by score, risk, footprint-fit radius, and area.
- Rank 1 is the authoritative best landing zone used by the landing visualization and JSON target.
- New visuals show every safe zone and a configurable Top-N subset with contours, center points, footprint circles, labels, and hazard overlays.
- New reports include `ranked_safe_zones.csv` and `ranked_safe_zones.json` while preserving the existing candidate and rejected-region reports.
- Streamlit presents a ranked table, zone count, best-zone summary, all-zone view, Top-N view, and report downloads.

## Important Visual Outputs for Poster

The latest available numeric run is `outputs/Sample-28/`. The most useful poster assets are:

1. `outputs/Sample-28/input_image.png` — unmodified aerial RGB input and the starting point of the visual story.
2. `outputs/Sample-28/semantic_mask_labeled.png` — semantic result with a present-class legend.
3. `outputs/Sample-28/overlay_labeled.png` — useful as a secondary figure to connect the semantic prediction to the original scene.
4. `outputs/Sample-28/risk_map_labeled.png` — green-to-red interpretation of landing risk with a colorbar.
5. `outputs/Sample-28/all_safe_zones_labeled.png` — all valid ranked zones with hazard overlay, contour, center, footprint, legend, and table.
6. `outputs/Sample-28/top_safe_zones_labeled.png` — the Top-N presentation view; this run contains one qualifying zone.
7. `outputs/Sample-28/best_landing_zone_labeled.png` — final Rank-1 landing decision and the strongest closing visual.
8. `outputs/Sample-28/water_detection_overlay_labeled.png` — optional supporting visual for the water-safety method.
9. `outputs/Sample-28/ranked_safe_zones.csv` and `outputs/Sample-28/ranked_safe_zones.json` — authoritative ranked result data.
10. `outputs/Sample-28/landing_target.json` — authoritative Rank-1 target details.

**Recommended six-figure poster sequence:** input image → semantic mask → risk map → all ranked zones → Top-N zones → final best landing zone.

**Latest result callout:** Sample-28 found one `Very Safe` paved-area zone. `Zone-01` has score `0.788`, mean risk `0.131`, center `(639, 502)` px, requested footprint radius `300.0` px, and maximum inscribed safe radius `374.8` px. These values are image-specific research-demo results and should not be presented as general model accuracy.

## Suggested Poster Layout

Use a landscape 16:9 canvas, ideally 1920×1080 or a higher-resolution equivalent, with a strong top header, three information columns, a dominant center workflow, and a compact bottom conclusion strip.

**Top header — approximately 12% of poster height**

- Full project title in large bold type.
- Author: Shafayetul Islam.
- Affiliation: Department of Computer Science and Engineering.
- Small tags for “Semantic Segmentation,” “UAV Landing,” “Risk Mapping,” and “Version 0.3.4.”

**Left column — approximately 24% of poster width**

- Problem Statement.
- Research Motivation and Objectives.
- Compact Input / Model / Output card.
- Use a drone icon above an aerial-image icon to establish context.

**Center — approximately 52% of poster width**

- A horizontal methodology workflow near the top with arrows and compact icons.
- A large six-stage visual pipeline below it: input image → semantic mask → risk map → all ranked zones → Top-N zones → best landing zone.
- Keep all image panels aligned, use matching numbered badges, and connect them with thin teal arrows.
- Give the final landing-zone figure slightly more visual weight and a green accent border.

**Right column — approximately 24% of poster width**

- Five Safe Zone Factors card.
- Risk Formulation card with the weighted equation and suitability relationship.
- Ranked Landing Zone Selection and Version 0.3.4 highlights.
- Limitations and Future Work in two compact stacked panels.

**Bottom strip — approximately 10% of poster height**

- Conclusion and main contribution summary.
- Small limitations note: RGB-only proxies, pixel coordinates, and research-demo status.
- Optional repository or contact placeholder; do not invent a URL, QR code, or email address.

## Poster Text Content

### 1. Problem Statement

Autonomous UAVs must recognize safe landing areas in cluttered aerial scenes. Water, vehicles, vegetation, structures, obstacles, narrow surfaces, and ambiguous terrain create landing risk. With only one RGB image, the system cannot directly measure depth, slope, or physical roughness, so it combines semantic understanding with explainable risk proxies.

### 2. Objectives

- Segment one aerial RGB image into 24 semantic classes.
- Convert semantic predictions into an interpretable landing-risk map.
- Detect and conservatively exclude hazards.
- Validate whether the drone's circular footprint fits inside a candidate region.
- Rank all valid landing zones and report Rank 1 as the final target.

### 3. System Overview

- **Input:** One aerial RGB image.
- **Model:** Locally trained SegFormer-B0 with 24 semantic classes.
- **Processing:** Probability-aware hazards, water override, risk fusion, and footprint-aware geometry.
- **Output:** Semantic mask, risk map, all ranked safe zones, best target, and CSV/JSON reports.

### 4. Methodology

- Preprocess the RGB image and run full-image or tiled SegFormer inference.
- Preserve class probabilities as well as the final semantic mask.
- Combine semantic classes, probability evidence, water cues, and hazard dilation.
- Build a risk map, extract valid connected surfaces, and apply distance-transform footprint checks.
- Score, sort, label, visualize, and export every valid landing region.

### 5. Risk Formulation

Five interpretable components form the base risk: semantic category (45%), obstacle proximity (25%), landing area size (15%), slope proxy (7.5%), and roughness proxy (7.5%). Landing suitability is one minus final risk. Confidence, hazard, and water overrides make the final decision more conservative.

### 6. Safe Zone Factors

- Terrain semantic category.
- Distance from effective hazards.
- Connected landing-area size.
- Semantic terrain-slope proxy.
- Semantic surface-roughness proxy.

Slope and roughness are class-based proxies, not physical measurements.

### 7. Ranked Landing Zone Selection

- Candidate pixels must be safe-class, low-risk, and outside the dilated hazard mask.
- Regions must meet minimum area and confidence requirements.
- A distance transform verifies that the requested footprint fits entirely within each region.
- Valid zones are ranked by suitability score, then risk, fit radius, and area.
- `Zone-01` is the single authoritative best landing target.

### 8. Results

- The pipeline generates source-aligned semantic, risk, hazard, and landing-zone visualizations.
- Sample-28 produced one valid `Very Safe` paved-area region.
- Rank-1 score: `0.788`; mean risk: `0.131`; selected center: `(639, 502)` px.
- A `300.0` px footprint fits within a `374.8` px maximum inscribed safe radius.
- Ranked CSV/JSON reports preserve geometry, confidence, risk, and target coordinates.

### 9. Limitations

- RGB image only; no true depth, elevation, wind, or vehicle dynamics.
- Slope and roughness are semantic proxies rather than physical measurements.
- Landing centers are image pixels, not GPS coordinates.
- The water override is a temporary safety heuristic, not a trained detector.
- The system is a research demo and is not certified for autonomous landing.

### 10. Future Work

- Add depth, elevation, or calibrated ground-scale information.
- Estimate physical terrain slope and roughness.
- Retrain with broader water, vehicle, and obstacle examples.
- Add batch evaluation, threshold calibration, and quantitative validation.
- Integrate with ROS2 and Gazebo.
- Convert image targets into UAV planner coordinates using camera calibration.

### 11. Conclusion

This project turns a single aerial RGB image into an explainable UAV landing assessment. SegFormer-based scene understanding is combined with risk fusion, conservative hazard handling, footprint-aware geometry, and deterministic candidate ranking. The result is an inspectable set of safe-zone alternatives with Rank 1 linked consistently to the final landing target.

## Figure Placement Plan

| Figure | Source | Caption | Purpose | Recommended poster size |
|---|---|---|---|---|
| Figure 1 | `outputs/Sample-28/input_image.png` | **Input aerial RGB image.** One overhead scene is the only sensor input to the pipeline. | Establish the scene and RGB-only constraint. | Medium; about 15% of poster area or 1.3×1 visual unit. |
| Figure 2 | `outputs/Sample-28/semantic_mask_labeled.png` | **Predicted semantic class mask.** SegFormer-B0 assigns each pixel to one of 24 classes. | Demonstrate pixel-wise scene understanding and class separation. | Medium-large; about 18% of poster area or 1.5×1 visual units. |
| Figure 3 | `outputs/Sample-28/risk_map_labeled.png` | **Semantic landing risk map.** Green indicates lower risk; yellow and red indicate increasing risk and hazards. | Show how semantic evidence becomes a safety interpretation. | Medium-large; about 18% of poster area or 1.5×1 visual units. |
| Figure 4 | `outputs/Sample-28/all_safe_zones_labeled.png` | **All ranked safe landing zones.** Valid contours, center points, footprint circles, and excluded hazards are shown together. | Explain all-zone extraction and rank-aware visualization. | Large; about 22% of poster area or 1.8×1.1 visual units. |
| Figure 5 | `outputs/Sample-28/top_safe_zones_labeled.png` | **Top-ranked landing candidates.** The configurable Top-N view emphasizes the strongest valid regions. | Communicate candidate prioritization and fallback-zone support. | Medium; about 15% of poster area or 1.3×1 visual unit. |
| Figure 6 | `outputs/Sample-28/best_landing_zone_labeled.png` | **Final Rank-1 landing target.** The selected region, center, required footprint, available radius, class, score, and risk are displayed. | Close the visual narrative with the final interpretable decision. | Large and prominent; about 24% of poster area or 2×1.2 visual units. |

Use the six figures as a left-to-right process strip in the center of the poster. If space is limited, retain Figures 1, 2, 3, 4, and 6, and place Figure 5 as a smaller inset beside Figure 4. The water-detection overlay may be added as a small methodology inset rather than replacing a core figure.

## Color and Design Style

- Landscape 16:9 academic research poster with a clean technical aesthetic.
- Deep navy or royal blue header, teal section accents, white background, and pale blue-gray panel fills.
- Bright green for safe-zone contours, Rank 1, positive findings, and the conclusion accent.
- Red and orange only for hazards, exclusions, warnings, and high-risk areas.
- Yellow as a restrained intermediate-risk color matching the risk map.
- Rounded rectangular panels with thin borders, subtle shadows, consistent internal padding, and generous whitespace.
- A horizontal arrow workflow using small drone, RGB image, AI chip, segmentation, risk-map, warning, ranked-list, and landing-target icons.
- Readable sans-serif typography such as Inter, Source Sans, Helvetica, or a similar modern family.
- Clear figure numbers, captions, legends, and colorbars; never place text over critical visual evidence.
- Use no more than three main font sizes: large title, medium panel heading, and compact body/caption text.
- Keep text concise and prioritize the visual pipeline; avoid decorative 3D effects, crowded gradients, photorealistic UI mockups, or invented performance charts.

## Limitations

- The system receives one RGB image only.
- It has no direct depth, elevation, LiDAR, wind, or vehicle-dynamics input.
- Terrain slope and surface roughness are semantic class proxies, not physical measurements.
- Pixel areas, distances, and target centers are not automatically real-world measurements or GPS coordinates.
- The water override is a temporary conservative safety heuristic, not a separately trained water detector.
- Model confidence and thresholds require validation and calibration for a target environment.
- The output is intended for research demonstration and visualization, not certified autonomous landing or flight-safety decisions.

## Future Work

- Add depth, stereo, LiDAR, DEM, or elevation information.
- Estimate physical terrain slope and surface roughness.
- Retrain the segmentation model with more water, vehicle, obstacle, shadow, and reflection examples.
- Add batch evaluation, labeled landing-zone benchmarks, calibration, and quantitative metrics.
- Integrate the perception pipeline with ROS2 and Gazebo simulations.
- Convert image-pixel targets into UAV planner coordinates using camera calibration, scale, pose, and external positioning.
- Evaluate temporal consistency across video frames and incorporate vehicle dynamics, wind, and approach-path constraints.

## Latest Sample Output References

Latest numeric output folder: `outputs/Sample-28/`

- `outputs/Sample-28/input_image.png`
- `outputs/Sample-28/semantic_mask_labeled.png`
- `outputs/Sample-28/overlay_labeled.png`
- `outputs/Sample-28/risk_map_labeled.png`
- `outputs/Sample-28/all_safe_zones_labeled.png`
- `outputs/Sample-28/top_safe_zones_labeled.png`
- `outputs/Sample-28/best_landing_zone_labeled.png`
- `outputs/Sample-28/water_detection_overlay_labeled.png`
- `outputs/Sample-28/ranked_safe_zones.csv`
- `outputs/Sample-28/ranked_safe_zones.json`
- `outputs/Sample-28/landing_target.json`

## Complete Poster Image Prompt

Create a polished landscape 16:9 academic research poster, ideally 1920×1080 or higher resolution, titled “Safe Landing Zone Detection for Drone Landing using Semantic Segmentation.” Place “Shafayetul Islam” and “Department of Computer Science and Engineering” directly beneath the title, with a small subtitle reading “Research Demo • UAV Safe Landing Zone Selection • Version 0.3.4.” Use this one-line summary prominently: “A semantic-segmentation-based UAV landing-site assessment system that converts aerial RGB imagery into semantic masks, risk maps, and ranked safe landing zones.” Design the poster with a deep navy-blue header, teal section accents, a white background, pale blue-gray rounded panels, thin borders, subtle shadows, generous whitespace, and modern readable sans-serif typography. Use green only for safe landing zones and positive results; use red/orange for hazards and high risk; preserve the green–yellow–red risk-map language. Do not use decorative 3D effects, cluttered gradients, tiny text, fabricated accuracy charts, invented institutional logos, or invented contact details.

Build a three-column composition under the header. In the left column, create concise panels titled “Problem Statement,” “Objectives,” and “System Overview.” State that autonomous UAVs must avoid water, vehicles, vegetation, structures, obstacles, narrow areas, and uncertain terrain; one RGB image cannot directly measure depth, physical slope, or roughness, so semantic reasoning and risk proxies are used. List the six objectives: semantic prediction, landing-risk mapping, hazard detection, footprint validation, ranking all safe zones, and exporting interpretable results. Show Input = one aerial RGB image; Model = locally trained SegFormer-B0 with 24 semantic classes; Outputs = semantic mask, overlay, risk map, all ranked safe zones, best landing target, and CSV/JSON reports.

Make the center the visual focus. Across its upper edge, draw a clean arrow workflow with compact drone, image, AI-chip, segmentation, warning, map, ranked-list, and landing-target icons: “Aerial RGB Image → Preprocessing → SegFormer-B0 Semantic Segmentation → Semantic Class Mask → Probability-Aware Hazard Detection → Temporary Water Safety Override → Semantic Landing Risk Map → Footprint-Aware Candidate Extraction → Ranked Safe Landing Zone List → Final Landing Target.” Below the workflow, create a six-stage numbered figure strip using clearly framed image placeholders in this order: Figure 1 Input RGB Image, Figure 2 Semantic Class Mask, Figure 3 Landing Risk Map, Figure 4 All Ranked Safe Zones, Figure 5 Top Safe Zones, Figure 6 Best Landing Zone. When reference images are supplied, use these exact project assets without redrawing or altering their analytical content: `outputs/Sample-28/input_image.png`, `outputs/Sample-28/semantic_mask_labeled.png`, `outputs/Sample-28/risk_map_labeled.png`, `outputs/Sample-28/all_safe_zones_labeled.png`, `outputs/Sample-28/top_safe_zones_labeled.png`, and `outputs/Sample-28/best_landing_zone_labeled.png`. Give Figure 6 a slightly larger green-accent border. Keep captions legible and do not cover legends, colorbars, contours, center points, or footprint circles.

In the right column, create panels titled “Safe Zone Factors,” “Risk Formulation,” “Ranked Landing Zone Selection,” “Key Features,” “Limitations,” and “Future Work.” Show the five factors with simple icons: terrain semantic category, obstacle proximity, landing area size, terrain slope proxy, and surface roughness proxy. Explicitly label slope and roughness as semantic proxies, not physical measurements. Typeset the formula clearly: “Final Risk = 0.45 × Semantic Risk + 0.25 × Obstacle Proximity Risk + 0.15 × Landing Area Size Risk + 0.075 × Terrain Slope Proxy Risk + 0.075 × Surface Roughness Proxy Risk” and underneath “Landing Suitability = 1 − Final Risk.” Add a compact note that probability-aware hazards, confidence-aware risk, water safety override, and footprint-aware validation make the final decision more conservative.

For ranked selection, explain that valid pixels must belong to `paved-area`, `grass`, `dirt`, or `gravel`, remain at or below the risk threshold, and stay outside the dilated hazard mask; connected regions must meet minimum area and confidence requirements, and a Euclidean distance transform must prove that the circular drone footprint fits. Show the 24-class grouping compactly: safe candidates = paved-area, grass, dirt, gravel; hazards = water, pool, rocks, vegetation, roof, wall, window, door, fence, fence-pole, person, dog, car, bicycle, tree, bald-tree, obstacle, conflicting; uncertain = unlabeled; special = ar-marker, disabled as normal safe terrain unless explicitly enabled. State that valid zones are sorted by score descending, risk ascending, fit radius descending, and area descending, receive stable IDs such as Zone-01 and Zone-02, and Rank 1 becomes the final best target.

Include a green-highlighted “Latest Demonstration Result” callout based only on Sample-28: “1 valid Very Safe paved-area zone • Zone-01 score 0.788 • mean risk 0.131 • center (639, 502) px • required footprint radius 300.0 px • available safe radius 374.8 px.” Label this as an image-specific demonstration, not a general accuracy claim. In “Key Features,” mention all-zone detection, stable IDs, deterministic ranking, Top-N visualization, labeled outputs, and ranked CSV/JSON reports. In “Limitations,” list RGB-only input, no true depth/elevation/wind/vehicle dynamics, slope and roughness as proxies, pixel coordinates not GPS, water override as a temporary heuristic, and research-demo/not-certified status. In “Future Work,” list depth or elevation input, physical slope and roughness, retraining with more water/vehicle/obstacle samples, batch evaluation and calibration, ROS2/Gazebo integration, and calibrated UAV-planner coordinates.

Finish with a full-width bottom conclusion strip: “SegFormer-based scene understanding, explainable risk fusion, conservative hazard handling, footprint-aware geometry, and deterministic ranking transform one aerial RGB image into inspectable safe landing alternatives, with Zone-01 linked consistently to the final landing target.” Add a small visual legend: green contour = valid safe landing zone, white circle = drone footprint, cyan point = selected center, red overlay = hazard/excluded area, and green→yellow→red = low→medium→high risk. Maintain strong hierarchy, aligned grids, balanced spacing, readable equations, concise panel text, and a professional computer-vision/UAV research aesthetic.
