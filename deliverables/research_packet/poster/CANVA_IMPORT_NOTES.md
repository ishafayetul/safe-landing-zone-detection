# Canva Import Notes

## Upload set

Upload the following PNG files from `research_packet/figures/`:

- `input_image.png`
- `semantic_mask_labeled.png`
- `risk_map_labeled.png`
- `all_safe_zones_labeled.png`
- `top_safe_zones_labeled.png`
- `best_landing_zone_labeled.png`
- `water_detection_overlay_labeled.png` if the methods inset is used
- `overlay_labeled.png` as an optional semantic-context substitute

## Import workflow

1. Create the landscape 16:9 canvas.
2. Upload original PNGs; do not resave or preprocess them before import.
3. Place each figure inside a proportional frame with “Fit,” not “Fill,” unless a crop is intentionally limited to empty banner space.
4. Confirm that titles, legends, colorbars, contours, cyan centers, and white footprint circles remain visible.
5. Add figure numbers and captions outside the image boundary.
6. Lock each placed figure before arranging text panels.
7. Export a proof and inspect at 100% for legibility.

## Asset dimensions

- Input: 3375×2250.
- Semantic mask: 3809×2332.
- Risk map: 3605×2402.
- All/top ranked zones: 3604×2426.
- Best zone: 3604×2474.
- Water overlay: 3604×2450.

The labeled assets have slightly different aspect ratios because their local titles, legends, and explanation panels expand the canvas. Avoid forcing every figure into identically cropped frames.

## Evidence integrity

- Do not redraw, recolor, retouch, or remove analytical overlays.
- Do not crop out warnings, captions, axes, colorbars, or result details.
- Do not fabricate accuracy charts or convert Sample-28 values into percentages.
- Do not imply that one valid zone represents dataset-level performance.
- Keep “image-specific demonstration” next to the numeric result.
- Keep “pixel coordinates—not GPS” next to the landing target.

## Text and branding

- Paste content from `CANVA_POSTER_TEXT.md`, shortening only when the meaning and cautions remain intact.
- Use author and affiliation exactly as provided.
- Do not invent a logo, email address, repository URL, QR code, sponsor, citation, or institution name beyond the confirmed affiliation text.
- Use icons only as generic visual cues, not as evidence.

## Export suggestions

- Preserve a Canva-editable master.
- Export a high-resolution PNG for digital review.
- Export PDF Print for printing when required by the venue.
- Check the venue’s exact size, bleed, and color-profile requirements before the final export.
