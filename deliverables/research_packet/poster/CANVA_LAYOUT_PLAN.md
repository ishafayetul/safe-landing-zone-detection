# Canva Poster Layout Plan

## Canvas and grid

- Landscape 16:9, ideally 1920×1080 or a higher-resolution equivalent.
- Outer margin: approximately 3% of canvas width.
- Header: 12% of height.
- Main body: 76% of height, arranged as 24% / 52% / 24% columns.
- Conclusion/footer strip: 10–12% of height.
- Use an aligned 12-column grid and consistent panel padding.

## Header

- Deep navy full-width band.
- Left/center: title, author, affiliation, version subtitle.
- Right: compact tags—Semantic Segmentation, UAV Landing, Risk Mapping, Ranked Zones.
- Do not add an institutional logo unless the user supplies one.

## Left column

1. **Problem Statement** — 20% of body height.
2. **Research Motivation** — 22%.
3. **Objectives** — 28%.
4. **System Overview** — 30%, using a compact Input / Model / Outputs card.

Use short bullet text and one restrained drone/aerial-image icon pair.

## Center column

### Workflow band

Place a horizontal or two-row arrow workflow across the top 22%:

```text
RGB → SegFormer → semantic mask → hazards/water → risk map
→ footprint validation → ranking → Zone-01
```

### Six-figure visual story

Use the remaining center area for a 3×2 grid or stepped sequence:

| Figure | Asset | Placement |
|---|---|---|
| 1 | `input_image.png` | Top-left |
| 2 | `semantic_mask_labeled.png` | Top-center |
| 3 | `risk_map_labeled.png` | Top-right |
| 4 | `all_safe_zones_labeled.png` | Bottom-left, slightly wider |
| 5 | `top_safe_zones_labeled.png` | Bottom-center |
| 6 | `best_landing_zone_labeled.png` | Bottom-right, largest with green accent |

Maintain each image’s aspect ratio. Never cover legends, colorbars, contours, centers, or footprint circles. If space becomes tight, reduce Figure 5 and use it as an inset beside Figure 4 rather than shrinking all captions.

## Right column

1. **Safe Zone Factors** — icon list.
2. **Risk Formulation** — readable equation card.
3. **Footprint-Aware Ranking** — four concise decision rules.
4. **Latest Demonstration Result** — green-highlighted Sample-28 callout.
5. **Limitations / Future Work** — two stacked compact panels.

Optional: place `water_detection_overlay_labeled.png` as a small inset beside the hazard/water text.

## Footer strip

- One-sentence conclusion.
- Compact symbol/color legend.
- Small research-demo caution: RGB-only proxies, pixel coordinates, not certified.
- Leave repository/contact space blank unless the user supplies exact details.

## Typography

- Use one modern sans-serif family such as Inter, Source Sans, Helvetica, or Canva equivalent.
- Title: approximately 38–50 pt at 1920×1080.
- Panel headings: 20–26 pt.
- Body/captions: 13–18 pt, never below comfortable presentation readability.
- Use bold sparingly for key values and `Zone-01`.

## Color system

- Header navy: approximately `#0B1F3A`.
- Teal accent: approximately `#0E7490`.
- Pale panel fill: approximately `#F2F7FA`.
- Safe green: approximately `#16A34A`.
- Hazard red: approximately `#DC2626`.
- Warning orange: approximately `#EA580C`.

These interface colors frame the poster; do not recolor the analytical figures or their semantic palette.
