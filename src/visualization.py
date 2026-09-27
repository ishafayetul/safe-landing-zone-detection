import os
import tempfile
import textwrap
from math import ceil
from pathlib import Path

import cv2
import numpy as np

# Keep Matplotlib's runtime cache in a writable temporary location on locked-down hosts.
os.environ.setdefault(
    "MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "safe_landing_zone_matplotlib")
)
import matplotlib

from .risk_config import CLASS_COLOR_PALETTE


def colorize_mask(pred_mask, id2label):
    """Render class IDs with the trained dataset's exact RGB palette."""
    output = np.zeros((*pred_mask.shape, 3), dtype=np.uint8)
    for class_id, class_name in id2label.items():
        output[pred_mask == class_id] = CLASS_COLOR_PALETTE[class_name]
    return output


def blend_overlay(image_rgb, mask_rgb, opacity=0.45):
    return np.clip(
        (1.0 - opacity) * image_rgb.astype(np.float32)
        + opacity * mask_rgb.astype(np.float32),
        0,
        255,
    ).astype(np.uint8)


def _apply_colormap(values, name):
    normalized = np.clip(values, 0.0, 1.0)
    rgba = matplotlib.colormaps[name](normalized)
    return (rgba[..., :3] * 255).astype(np.uint8)


def colorize_risk(risk_map):
    """Safety palette: low risk green, medium yellow/orange, high risk red."""
    return _apply_colormap(risk_map, "RdYlGn_r")


def colorize_probability(probability_map):
    return _apply_colormap(probability_map, "magma")


def colorize_hazard_mask(hazard_mask):
    output = np.zeros((*hazard_mask.shape, 3), dtype=np.uint8)
    output[hazard_mask] = (255, 0, 0)
    return output


def colorize_valid_centers(center_mask):
    output = np.zeros((*center_mask.shape, 3), dtype=np.uint8)
    output[center_mask] = (0, 255, 0)
    return output


def colorize_water_override_sources(
    predicted_water_mask,
    probability_override_mask,
    rgb_override_mask,
):
    """Render the three water-evidence sources with distinct RGB colors."""
    output = np.zeros((*predicted_water_mask.shape, 3), dtype=np.uint8)
    output[predicted_water_mask] = (28, 42, 168)
    output[probability_override_mask] = (0, 190, 255)
    output[rgb_override_mask] = (0, 110, 255)
    return output


def draw_water_detection_overlay(
    image_rgb,
    predicted_water_mask,
    probability_override_mask,
    rgb_override_mask,
):
    """Blend effective water evidence over the original RGB image."""
    canvas = _as_rgb_uint8(image_rgb)
    sources = colorize_water_override_sources(
        predicted_water_mask,
        probability_override_mask,
        rgb_override_mask,
    )
    active = (
        predicted_water_mask | probability_override_mask | rgb_override_mask
    )
    if active.any():
        canvas[active] = np.clip(
            0.30 * canvas[active].astype(np.float32)
            + 0.70 * sources[active].astype(np.float32),
            0,
            255,
        ).astype(np.uint8)
    return canvas


_FONT = cv2.FONT_HERSHEY_SIMPLEX
_TEXT_COLOR = (25, 30, 38)
_MUTED_TEXT_COLOR = (75, 85, 99)
_PANEL_COLOR = (248, 250, 252)
_BORDER_COLOR = (203, 213, 225)


def _as_rgb_uint8(image):
    array = np.asarray(image)
    if array.ndim != 3 or array.shape[2] != 3:
        raise ValueError("labeled visualization input must be an RGB image")
    return np.clip(array, 0, 255).astype(np.uint8, copy=True)


def _fit_text_scale(text, maximum_width, initial=0.72, thickness=1, minimum=0.34):
    scale = float(initial)
    width = cv2.getTextSize(str(text), _FONT, scale, thickness)[0][0]
    if width > maximum_width and width > 0:
        scale *= maximum_width / float(width)
    return max(minimum, scale)


def _put_text(canvas, text, origin, scale, color=_TEXT_COLOR, thickness=1):
    cv2.putText(
        canvas,
        str(text),
        tuple(map(int, origin)),
        _FONT,
        float(scale),
        color,
        int(thickness),
        cv2.LINE_AA,
    )


def _wrapped_lines(text, characters=52):
    lines = []
    for paragraph in str(text).splitlines() or [""]:
        lines.extend(textwrap.wrap(paragraph, width=max(12, characters)) or [""])
    return lines


def _append_note_panel(image, lines, title=None):
    image = _as_rgb_uint8(image)
    normalized_lines = []
    for line in lines:
        normalized_lines.extend(_wrapped_lines(line, max(28, image.shape[1] // 11)))
    title_height = 28 if title else 0
    panel_height = 18 + title_height + max(1, len(normalized_lines)) * 24
    panel = np.full((panel_height, image.shape[1], 3), _PANEL_COLOR, dtype=np.uint8)
    cv2.line(panel, (0, 0), (panel.shape[1] - 1, 0), _BORDER_COLOR, 1)
    y = 24
    if title:
        _put_text(panel, title, (16, y), 0.56, _TEXT_COLOR, 2)
        y += title_height
    for line in normalized_lines:
        _put_text(panel, line, (16, y), 0.48, _MUTED_TEXT_COLOR, 1)
        y += 24
    return np.vstack([image, panel])


def draw_title_banner(image, title, subtitle=None):
    """Add a consistent light title banner without covering image pixels."""
    image = _as_rgb_uint8(image)
    banner_height = 82 if subtitle else 58
    banner = np.full((banner_height, image.shape[1], 3), _PANEL_COLOR, dtype=np.uint8)
    title_scale = _fit_text_scale(title, image.shape[1] - 32, 0.82, 2)
    _put_text(banner, title, (16, 31), title_scale, _TEXT_COLOR, 2)
    if subtitle:
        subtitle_scale = _fit_text_scale(subtitle, image.shape[1] - 32, 0.50, 1)
        _put_text(
            banner,
            subtitle,
            (16, 61),
            subtitle_scale,
            _MUTED_TEXT_COLOR,
            1,
        )
    cv2.line(
        banner,
        (0, banner_height - 1),
        (image.shape[1] - 1, banner_height - 1),
        _BORDER_COLOR,
        1,
    )
    return np.vstack([banner, image])


def draw_label_with_background(image, text, position, font_scale=0.6):
    """Draw readable text on an opaque light box at an image-relative position."""
    canvas = _as_rgb_uint8(image)
    x, y = map(int, position)
    lines = _wrapped_lines(text, max(16, (canvas.shape[1] - x - 20) // 10))
    sizes = [cv2.getTextSize(line, _FONT, font_scale, 1)[0] for line in lines]
    width = max((size[0] for size in sizes), default=1)
    line_height = max((size[1] for size in sizes), default=12) + 8
    box_x2 = min(canvas.shape[1] - 1, x + width + 18)
    box_y2 = min(canvas.shape[0] - 1, y + line_height * len(lines) + 12)
    overlay = canvas.copy()
    cv2.rectangle(overlay, (max(0, x), max(0, y)), (box_x2, box_y2), _PANEL_COLOR, -1)
    cv2.rectangle(overlay, (max(0, x), max(0, y)), (box_x2, box_y2), _BORDER_COLOR, 1)
    canvas = cv2.addWeighted(overlay, 0.96, canvas, 0.04, 0)
    baseline = y + line_height
    for line in lines:
        _put_text(canvas, line, (x + 9, baseline), font_scale, _TEXT_COLOR, 1)
        baseline += line_height
    return canvas


def draw_legend_box(image, legend_items, title="Legend", position="right"):
    """Add a class/status legend beside or below an image.

    ``legend_items`` accepts ``(label, RGB color)`` pairs or a mapping.
    """
    image = _as_rgb_uint8(image)
    items = list(legend_items.items()) if hasattr(legend_items, "items") else list(legend_items)
    if not items:
        items = [("No legend items present", (220, 220, 220))]

    row_height = 27
    if position == "right":
        rows_per_column = max(1, min(12, (image.shape[0] - 58) // row_height))
        columns = max(1, ceil(len(items) / rows_per_column))
        column_width = 205
        panel = np.full(
            (image.shape[0], columns * column_width + 24, 3),
            _PANEL_COLOR,
            dtype=np.uint8,
        )
        cv2.line(panel, (0, 0), (0, panel.shape[0] - 1), _BORDER_COLOR, 1)
        _put_text(panel, title, (16, 30), 0.60, _TEXT_COLOR, 2)
        for index, (label, color) in enumerate(items):
            column = index // rows_per_column
            row = index % rows_per_column
            x = 16 + column * column_width
            y = 52 + row * row_height
            cv2.rectangle(panel, (x, y), (x + 18, y + 18), tuple(map(int, color)), -1)
            cv2.rectangle(panel, (x, y), (x + 18, y + 18), (60, 60, 60), 1)
            scale = _fit_text_scale(label, column_width - 52, 0.46, 1, 0.31)
            _put_text(panel, label, (x + 28, y + 15), scale, _TEXT_COLOR, 1)
        return np.hstack([image, panel])

    if position != "bottom":
        raise ValueError("legend position must be 'right' or 'bottom'")
    columns = max(1, min(4, len(items)))
    rows = ceil(len(items) / columns)
    panel_height = 48 + rows * row_height
    panel = np.full((panel_height, image.shape[1], 3), _PANEL_COLOR, dtype=np.uint8)
    cv2.line(panel, (0, 0), (panel.shape[1] - 1, 0), _BORDER_COLOR, 1)
    _put_text(panel, title, (16, 28), 0.58, _TEXT_COLOR, 2)
    column_width = max(1, image.shape[1] // columns)
    for index, (label, color) in enumerate(items):
        row, column = divmod(index, columns)
        x = 16 + column * column_width
        y = 42 + row * row_height
        cv2.rectangle(panel, (x, y), (x + 18, y + 18), tuple(map(int, color)), -1)
        cv2.rectangle(panel, (x, y), (x + 18, y + 18), (60, 60, 60), 1)
        scale = _fit_text_scale(label, column_width - 52, 0.46, 1, 0.31)
        _put_text(panel, label, (x + 28, y + 15), scale, _TEXT_COLOR, 1)
    return np.vstack([image, panel])


def draw_colorbar(image, label, min_text, max_text, colormap_name):
    """Add a vertical 0-to-1 colorbar on a dedicated side panel."""
    image = _as_rgb_uint8(image)
    panel_width = 230
    panel = np.full((image.shape[0], panel_width, 3), _PANEL_COLOR, dtype=np.uint8)
    cv2.line(panel, (0, 0), (0, panel.shape[0] - 1), _BORDER_COLOR, 1)
    _put_text(panel, label, (16, 30), _fit_text_scale(label, 198, 0.58, 2), _TEXT_COLOR, 2)

    top = 62
    bottom = max(top + 28, image.shape[0] - 66)
    gradient = np.linspace(1.0, 0.0, bottom - top, dtype=np.float32)[:, None]
    gradient_rgb = _apply_colormap(gradient, colormap_name)
    bar_left, bar_right = 20, 55
    panel[top:bottom, bar_left:bar_right] = np.repeat(
        gradient_rgb, bar_right - bar_left, axis=1
    )
    cv2.rectangle(panel, (bar_left, top), (bar_right, bottom - 1), (55, 65, 81), 1)

    label_x = 68
    max_lines = _wrapped_lines(max_text, 22)
    min_lines = _wrapped_lines(min_text, 22)
    for index, line in enumerate(max_lines[:2]):
        _put_text(panel, line, (label_x, top + 14 + 20 * index), 0.43, _TEXT_COLOR, 1)
    midpoint = "Medium Risk" if "risk" in label.lower() else "0.5 / Medium"
    for index, line in enumerate(_wrapped_lines(midpoint, 22)[:2]):
        _put_text(
            panel,
            line,
            (label_x, (top + bottom) // 2 + 5 + 20 * index),
            0.43,
            _TEXT_COLOR,
            1,
        )
    min_y = max(top + 20, bottom - 8 - 20 * (len(min_lines[:2]) - 1))
    for index, line in enumerate(min_lines[:2]):
        _put_text(panel, line, (label_x, min_y + 20 * index), 0.43, _TEXT_COLOR, 1)
    return np.hstack([image, panel])


def create_labeled_semantic_mask(mask_rgb, class_names_present, class_palette):
    canvas = draw_title_banner(
        mask_rgb,
        "Predicted Semantic Class Mask",
        "Colors show predicted semantic classes",
    )
    legend = [
        (class_name, class_palette[class_name])
        for class_name in class_names_present
        if class_name in class_palette
    ]
    return draw_legend_box(canvas, legend, title="Classes present", position="right")


def create_labeled_overlay(
    overlay_image,
    class_names_present,
    class_palette,
    overlay_opacity=None,
):
    subtitle = "Model prediction blended with original aerial RGB image"
    if overlay_opacity is not None:
        subtitle += f" | Overlay opacity: {float(overlay_opacity):.2f}"
    canvas = draw_title_banner(overlay_image, "Semantic Segmentation Overlay", subtitle)
    legend = [
        (class_name, class_palette[class_name])
        for class_name in class_names_present
        if class_name in class_palette
    ]
    return draw_legend_box(canvas, legend, title="Classes present", position="right")


def create_labeled_risk_map(
    risk_map_rgb,
    risk_threshold=None,
    title="Semantic Landing Risk Map",
    subtitle="Green = low risk, Red = high risk",
    explanation=None,
):
    if risk_threshold is not None:
        subtitle += f" | Candidate threshold: {float(risk_threshold):.2f}"
    canvas = draw_title_banner(risk_map_rgb, title, subtitle)
    notes = [explanation] if explanation else []
    notes.append("Landing Suitability = 1 - Final Risk")
    canvas = _append_note_panel(canvas, notes, title="Interpretation")
    return draw_colorbar(
        canvas,
        "Risk level",
        "0.0 Low Risk / Safer",
        "1.0 High Risk / Avoid",
        "RdYlGn_r",
    )


def create_labeled_best_landing_zone(best_zone_image, landing_target, risk_info):
    landing_target = landing_target or {}
    risk_info = risk_info or {}
    canvas = draw_title_banner(
        best_zone_image,
        "Best Semantically Suitable Landing Area",
        "Semantic, hazard, footprint-fit, geometry, and confidence decision",
    )
    legend = [
        ("Hazard / obstacle zone", (255, 0, 0)),
        ("Selected safe landing region", (0, 255, 0)),
        ("Drone footprint", (255, 255, 255)),
        ("Selected landing center", (0, 255, 255)),
    ]
    canvas = draw_legend_box(canvas, legend, title="Map symbols", position="right")
    if not landing_target.get("found", False):
        reason = landing_target.get("reason") or risk_info.get("decision_message") or "No candidate passed all requirements."
        notes = ["No valid landing zone found", f"Reason: {reason}"]
    else:
        center = landing_target.get("center_px")
        bbox = landing_target.get("bbox_px")
        notes = [
            f"Score: {landing_target.get('score', 0.0):.3f} | Dominant class: {landing_target.get('dominant_class', 'unknown')} | Mean risk: {landing_target.get('mean_risk', 0.0):.3f}",
            f"Selected center: {center} | Bounding box [x, y, width, height]: {bbox}",
            f"Footprint radius: {landing_target.get('footprint_radius_px', 0.0):.1f} px | Available safe radius: {landing_target.get('max_inscribed_radius_px', 0.0):.1f} px",
        ]
    threshold = risk_info.get("risk_threshold")
    if threshold is not None:
        notes.append(f"Landing candidate risk threshold: {float(threshold):.2f}")
    return _append_note_panel(canvas, notes, title="Landing decision")


def create_labeled_water_detection_overlay(water_overlay, water_info):
    water_info = water_info or {}
    canvas = draw_title_banner(
        water_overlay,
        "Temporary Water Safety Override",
        "Model water evidence plus a conservative RGB-only safety heuristic",
    )
    canvas = draw_legend_box(
        canvas,
        [
            ("Model argmax water", (28, 42, 168)),
            ("Water-probability override", (0, 190, 255)),
            ("RGB heuristic override", (0, 110, 255)),
        ],
        title="Water evidence",
        position="right",
    )
    notes = [
        "Override pixels are excluded from landing candidates and forced into the hazard pipeline.",
        "This is a conservative temporary RGB safety cue, not a replacement for retraining or a physical water sensor.",
        (
            f"Argmax water: {int(water_info.get('predicted_pixels', 0)):,} px | "
            f"Probability override: {int(water_info.get('probability_pixels', 0)):,} px | "
            f"RGB override: {int(water_info.get('rgb_pixels', 0)):,} px"
        ),
    ]
    return _append_note_panel(canvas, notes, title="Interpretation")


def create_labeled_water_override_mask(source_mask_rgb, water_info):
    water_info = water_info or {}
    canvas = draw_title_banner(
        source_mask_rgb,
        "Effective Water Override Mask",
        "Every colored pixel is treated as water and excluded from landing",
    )
    canvas = draw_legend_box(
        canvas,
        [
            ("Model argmax water", (28, 42, 168)),
            ("Water-probability override", (0, 190, 255)),
            ("RGB heuristic override", (0, 110, 255)),
            ("No water evidence", (0, 0, 0)),
        ],
        title="Override sources",
        position="right",
    )
    return _append_note_panel(
        canvas,
        [
            f"Effective water pixels: {int(water_info.get('effective_pixels', 0)):,}",
            "This temporary mask is conservative and may include false positives from blue roofs, shadows, or reflective surfaces.",
        ],
        title="Safety behavior",
    )


_PROBABILITY_EXPLANATIONS = {
    "car probability": "Brighter/hotter areas indicate higher model probability for the car class.",
    "danger probability": "Shows summed probability of all danger/obstacle classes.",
    "confidence": "Shows maximum predicted class probability. Higher means the model is more confident.",
    "uncertainty": "Shows normalized entropy of class probabilities. Higher means more uncertainty.",
    "margin": "Shows difference between top-1 and top-2 class probability. Higher means clearer class decision.",
    "water probability": "Brighter/hotter areas indicate higher model probability for the water class.",
    "water heuristic score": "Combines weak water probability with smooth, non-green, water-like RGB appearance.",
}


def create_labeled_probability_map(probability_map_rgb, title, probability_name):
    key = str(probability_name).strip().lower()
    explanation = _PROBABILITY_EXPLANATIONS.get(
        key,
        "Brighter/hotter areas indicate a higher normalized value.",
    )
    canvas = draw_title_banner(probability_map_rgb, title, explanation)
    canvas = _append_note_panel(
        canvas,
        ["Values are normalized from 0.0 (minimum) to 1.0 (maximum)."],
        title="Interpretation",
    )
    return draw_colorbar(
        canvas,
        probability_name,
        "0.0 Minimum",
        "1.0 Maximum",
        "magma",
    )


def create_labeled_binary_mask(
    mask_rgb,
    title,
    positive_label,
    negative_label,
    explanation=None,
):
    canvas = draw_title_banner(
        mask_rgb,
        title,
        explanation or "Binary mask: colored pixels are active; dark pixels are inactive.",
    )
    if "hazard" in title.lower():
        positive_color = (255, 0, 0)
    else:
        positive_color = (0, 255, 0)
    legend = [
        (positive_label, positive_color),
        (negative_label, (0, 0, 0)),
    ]
    return draw_legend_box(canvas, legend, title="Legend", position="right")


def draw_best_landing_zone(
    image_rgb,
    best_region,
    hazard_mask,
    footprint_radius_px,
    decision_message="",
):
    canvas = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

    # Effective danger areas are shown as a translucent red safety overlay.
    if hazard_mask.any():
        red = np.zeros_like(canvas)
        red[..., 2] = 255
        canvas[hazard_mask] = cv2.addWeighted(
            canvas[hazard_mask], 0.55, red[hazard_mask], 0.45, 0
        )

    if best_region is None:
        text = "No valid landing zone for selected footprint"
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = max(0.45, min(0.7, image_rgb.shape[1] / 1000.0))
        (text_width, text_height), _ = cv2.getTextSize(text, font, font_scale, 2)
        cv2.rectangle(
            canvas,
            (8, 8),
            (min(image_rgb.shape[1] - 1, text_width + 24), text_height + 24),
            (0, 0, 0),
            -1,
        )
        cv2.putText(
            canvas,
            text,
            (16, text_height + 16),
            font,
            font_scale,
            (0, 0, 255),
            2,
        )
        return cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB)

    contour_source = best_region.mask.astype(np.uint8)
    contours, _ = cv2.findContours(
        contour_source, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    cv2.drawContours(canvas, contours, -1, (0, 255, 0), 3)
    x, y, width, height = best_region.bbox
    cv2.rectangle(canvas, (x, y), (x + width - 1, y + height - 1), (0, 255, 0), 2)
    center = (best_region.best_center_x, best_region.best_center_y)
    cv2.circle(
        canvas,
        center,
        max(1, round(footprint_radius_px)),
        (255, 255, 255),
        3,
    )
    cv2.circle(canvas, center, 6, (255, 255, 0), -1)

    label_lines = [
        f"Best Landing Zone | Score: {best_region.final_region_score:.2f} | "
        f"Class: {best_region.dominant_semantic_class}",
        f"Fit: {best_region.max_inscribed_radius_px:.0f}px / "
        f"Need: {best_region.footprint_radius_px:.0f}px | "
        f"Center: ({best_region.best_center_x}, {best_region.best_center_y})",
    ]
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = max(0.45, min(0.75, image_rgb.shape[1] / 1100.0))
    initial_sizes = [cv2.getTextSize(line, font, font_scale, 2)[0] for line in label_lines]
    widest = max(width for width, _ in initial_sizes)
    if widest > image_rgb.shape[1] - 20:
        font_scale *= (image_rgb.shape[1] - 20) / float(widest)
    sizes = [cv2.getTextSize(line, font, font_scale, 2)[0] for line in label_lines]
    text_width = max(width for width, _ in sizes)
    text_height = max(height for _, height in sizes)
    line_step = text_height + 7
    block_height = line_step * len(label_lines) + 5
    text_x = max(5, min(x, image_rgb.shape[1] - text_width - 10))
    text_y = y - block_height
    if text_y < 5:
        text_y = min(image_rgb.shape[0] - block_height - 5, y + height + 5)
    cv2.rectangle(
        canvas,
        (text_x - 4, text_y - 4),
        (text_x + text_width + 4, text_y + block_height),
        (0, 0, 0),
        -1,
    )
    for index, line in enumerate(label_lines):
        baseline_y = text_y + text_height + index * line_step
        cv2.putText(
            canvas,
            line,
            (text_x, baseline_y),
            font,
            font_scale,
            (0, 255, 0),
            2,
        )
    return cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB)


def _rank_color_bgr(rank):
    if rank == 1:
        return (0, 255, 0)
    if rank <= 5:
        return (255, 220, 0)
    return (144, 238, 144)


def _overlay_hazards_bgr(canvas, hazard_mask):
    if hazard_mask.any():
        red = np.zeros_like(canvas)
        red[..., 2] = 255
        canvas[hazard_mask] = cv2.addWeighted(
            canvas[hazard_mask], 0.55, red[hazard_mask], 0.45, 0
        )


def _draw_zone_label_bgr(canvas, text, anchor, color):
    font_scale = max(0.34, min(0.58, canvas.shape[1] / 1500.0))
    thickness = 1
    (text_width, text_height), _ = cv2.getTextSize(
        text, _FONT, font_scale, thickness
    )
    x = max(3, min(int(anchor[0]), canvas.shape[1] - text_width - 9))
    y = max(text_height + 7, min(int(anchor[1]), canvas.shape[0] - 5))
    cv2.rectangle(
        canvas,
        (x - 3, y - text_height - 5),
        (x + text_width + 4, y + 4),
        (0, 0, 0),
        -1,
    )
    cv2.putText(
        canvas,
        text,
        (x, y),
        _FONT,
        font_scale,
        color,
        thickness,
        cv2.LINE_AA,
    )


def _draw_ranked_safe_zones(
    image_rgb,
    regions,
    hazard_mask,
    max_zones_to_label,
    max_zones_to_draw_footprint,
    detailed_labels,
):
    canvas = cv2.cvtColor(_as_rgb_uint8(image_rgb), cv2.COLOR_RGB2BGR)
    _overlay_hazards_bgr(canvas, hazard_mask)

    if not regions:
        _draw_zone_label_bgr(
            canvas,
            "No valid safe landing zones",
            (12, 32),
            (0, 0, 255),
        )
        return cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB)

    for region in regions:
        color = _rank_color_bgr(region.rank or 999)
        contours, _ = cv2.findContours(
            region.mask.astype(np.uint8),
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE,
        )
        thickness = 3 if region.rank == 1 else 2
        cv2.drawContours(canvas, contours, -1, color, thickness)
        center = (region.best_center_x, region.best_center_y)
        cv2.circle(canvas, center, 5 if region.rank == 1 else 3, color, -1)

        if (region.rank or 999) <= max_zones_to_draw_footprint:
            cv2.circle(
                canvas,
                center,
                max(1, round(region.footprint_radius_px)),
                (255, 255, 255),
                2,
            )
        if (region.rank or 999) <= max_zones_to_label:
            if detailed_labels:
                label = (
                    f"#{region.rank} | Score: {region.score:.2f} | "
                    f"Risk: {region.mean_risk:.2f} | {region.dominant_class}"
                )
            else:
                label = region.zone_id or f"Zone-{region.rank:02d}"
            x, y, _, _ = region.bbox
            _draw_zone_label_bgr(canvas, label, (x + 3, y + 18), color)

    return cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB)


def draw_all_safe_zones(
    image_rgb,
    regions,
    hazard_mask,
    max_zones_to_label=20,
    max_zones_to_draw_footprint=10,
):
    """Draw every valid region while limiting labels and footprint circles."""
    return _draw_ranked_safe_zones(
        image_rgb,
        regions,
        hazard_mask,
        max_zones_to_label=max_zones_to_label,
        max_zones_to_draw_footprint=max_zones_to_draw_footprint,
        detailed_labels=False,
    )


def draw_top_safe_zones(
    image_rgb,
    regions,
    hazard_mask,
    top_n=5,
):
    """Draw only the highest-ranked valid landing zones."""
    selected = list(regions[:top_n])
    return _draw_ranked_safe_zones(
        image_rgb,
        selected,
        hazard_mask,
        max_zones_to_label=len(selected),
        max_zones_to_draw_footprint=len(selected),
        detailed_labels=True,
    )


def create_labeled_ranked_safe_zones(
    safe_zones_image,
    regions,
    title="All Ranked Safe Landing Zones",
):
    subtitle = "Zones are sorted by landing suitability score and risk"
    canvas = draw_title_banner(safe_zones_image, title, subtitle)
    canvas = draw_legend_box(
        canvas,
        [
            ("Rank 1 / strongest candidate", (0, 255, 0)),
            ("Ranks 2-5", (0, 220, 255)),
            ("Lower-ranked valid zone", (144, 238, 144)),
            ("Number label = zone rank", (248, 250, 252)),
            ("Circle = drone footprint", (255, 255, 255)),
            ("Red overlay = hazard/excluded", (255, 0, 0)),
        ],
        title="Map symbols",
        position="right",
    )
    if regions:
        lines = ["Rank | Class | Score | Mean Risk | Fit Radius"]
        lines.extend(
            f"#{region.rank} | {region.dominant_class} | {region.score:.3f} | "
            f"{region.mean_risk:.3f} | {region.max_inscribed_radius_px:.1f} px"
            for region in regions[:5]
        )
    else:
        lines = ["No valid safe landing zones found."]
    return _append_note_panel(canvas, lines, title="Top 5 ranked zones")
