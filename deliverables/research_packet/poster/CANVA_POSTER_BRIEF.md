# Canva Research Poster Brief

## Deliverable

Create a polished landscape 16:9 academic research poster, ideally 1920×1080 or a higher-resolution equivalent.

**Title:** Safe Landing Zone Detection for Drone Landing using Semantic Segmentation  
**Author:** Shafayetul Islam  
**Affiliation:** Department of Computer Science and Engineering  
**Version:** 0.3.4 — Ranked safe landing zone list

## Communication goal

Explain how one aerial RGB image is converted into semantic understanding, interpretable landing risk, conservative hazard handling, footprint-valid regions, and a deterministic ranked safe-zone list. The poster should read as an inspectable research workflow, not an autonomous-flight certification claim.

## Audience

- Computer vision and machine-learning researchers.
- UAV/robotics students and faculty.
- Project evaluators who need to understand method, outputs, and limitations quickly.

## Core narrative

```text
RGB image → semantic segmentation → hazard and water evidence → risk map
→ footprint-aware valid centers → ranked safe zones → Zone-01 target
```

## Required visual sequence

Use these packet assets without redrawing or changing their analytical content:

1. `../figures/input_image.png`
2. `../figures/semantic_mask_labeled.png`
3. `../figures/risk_map_labeled.png`
4. `../figures/all_safe_zones_labeled.png`
5. `../figures/top_safe_zones_labeled.png`
6. `../figures/best_landing_zone_labeled.png`

Optional method inset: `../figures/water_detection_overlay_labeled.png`.

## Latest demonstration callout

> Sample-28: 1 valid `Very Safe` `paved-area` zone • `Zone-01` score 0.788 • mean risk 0.131 • center (639, 502) px • requested footprint radius 300.0 px • available safe radius 374.8 px • confidence 0.904.

Label this prominently as an image-specific demonstration, not a general accuracy result.

## Content priorities

1. Problem and motivation.
2. One-line system overview.
3. Methodology pipeline.
4. Base risk formulation and conservative extensions.
5. Footprint-aware validation and deterministic ranking.
6. Visual results and numeric Sample-28 callout.
7. Limitations, future work, and research-demo status.

## Visual style

- Deep navy header, teal section accents, white background, pale blue-gray panels.
- Green for valid landing zones and positive results.
- Red/orange for hazards, exclusions, and high risk.
- Preserve the figures’ green→yellow→red risk language.
- Modern sans-serif typography, strong grid, generous whitespace, thin borders, restrained shadows.
- Avoid decorative 3D effects, cluttered gradients, tiny text, invented logos, fabricated charts, QR codes, URLs, or contact information.

## Required caution language

Include a visible note that the system is RGB-only, slope and roughness are semantic proxies, coordinates are pixels rather than GPS, the water override is temporary, and the software is a research demo rather than certified autonomous-flight software.
