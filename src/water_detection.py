from dataclasses import dataclass

import cv2
import numpy as np


@dataclass(frozen=True)
class WaterOverrideMaps:
    water_probability_map: np.ndarray
    water_heuristic_score_map: np.ndarray
    predicted_water_mask: np.ndarray
    probability_override_mask: np.ndarray
    rgb_override_mask: np.ndarray
    effective_water_mask: np.ndarray


def _remove_small_components(mask: np.ndarray, minimum_area_px: int) -> np.ndarray:
    count, labels, stats, _ = cv2.connectedComponentsWithStats(
        mask.astype(np.uint8), connectivity=8
    )
    filtered = np.zeros(mask.shape, dtype=bool)
    for component_id in range(1, count):
        area = int(stats[component_id, cv2.CC_STAT_AREA])
        if area >= minimum_area_px:
            filtered[labels == component_id] = True
    return filtered


def _rgb_water_heuristic_score(
    image_rgb: np.ndarray,
    water_probability: np.ndarray,
) -> np.ndarray:
    """Return a conservative hybrid water score from RGB appearance and weak model support.

    The score favors smooth, non-green, blue/cyan or dark-neutral surfaces. It is
    not a physical water measurement and should only be used as a temporary safety
    override, never as ground-truth semantic labeling.
    """
    image = np.asarray(image_rgb, dtype=np.uint8)
    original_height, original_width = image.shape[:2]
    if (original_height, original_width) != water_probability.shape:
        raise ValueError("RGB image and water probability map must have equal dimensions")

    # Bound temporary float-map memory on large aerial images. The final score is
    # returned at source resolution, so downstream masks and outputs remain aligned.
    maximum_analysis_dimension = 1600
    scale = min(
        1.0,
        maximum_analysis_dimension / float(max(original_height, original_width)),
    )
    probability_for_analysis = water_probability
    if scale < 1.0:
        analysis_size = (
            max(1, round(original_width * scale)),
            max(1, round(original_height * scale)),
        )
        image = cv2.resize(image, analysis_size, interpolation=cv2.INTER_AREA)
        probability_for_analysis = cv2.resize(
            water_probability,
            analysis_size,
            interpolation=cv2.INTER_AREA,
        )

    hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV).astype(np.float32)
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY).astype(np.float32)
    local_mean = cv2.boxFilter(gray, -1, (15, 15))
    local_square_mean = cv2.boxFilter(gray * gray, -1, (15, 15))
    local_texture = np.sqrt(
        np.maximum(local_square_mean - local_mean * local_mean, 0.0)
    )

    red = image[..., 0].astype(np.float32)
    green = image[..., 1].astype(np.float32)
    blue = image[..., 2].astype(np.float32)
    hue, saturation, value = (hsv[..., index] for index in range(3))

    excess_green = (2.0 * green - red - blue) / 255.0
    non_green = np.clip((0.30 - excess_green) / 0.35, 0.0, 1.0)
    smoothness = np.clip((30.0 - local_texture) / 25.0, 0.0, 1.0)

    visible_pixel = value > 30.0
    blue_dominance = np.clip(
        (blue - np.maximum(red, green) + 5.0) / 30.0, 0.0, 1.0
    ) * visible_pixel
    dark_neutral = (
        np.clip((110.0 - saturation) / 90.0, 0.0, 1.0)
        * np.clip((200.0 - value) / 130.0, 0.0, 1.0)
        * visible_pixel
    )
    cyan_tone = (
        ((hue >= 70.0) & (hue <= 115.0)).astype(np.float32)
        * np.clip((saturation - 25.0) / 100.0, 0.0, 1.0)
    )
    spectral_score = (
        np.maximum.reduce(
            [blue_dominance, 0.65 * dark_neutral, 0.70 * cyan_tone]
        )
        * non_green
        * smoothness
    )

    weak_model_support = np.clip(
        (probability_for_analysis.astype(np.float32) - 0.005) / 0.035,
        0.0,
        1.0,
    )
    score = np.clip(
        0.58 * spectral_score + 0.42 * weak_model_support,
        0.0,
        1.0,
    ).astype(np.float32)
    if scale < 1.0:
        score = cv2.resize(
            score,
            (original_width, original_height),
            interpolation=cv2.INTER_LINEAR,
        ).astype(np.float32)
    return score


def build_water_override_maps(
    image_rgb: np.ndarray | None,
    water_probability: np.ndarray,
    predicted_water_mask: np.ndarray,
    safe_class_mask: np.ndarray,
    *,
    enabled: bool,
    probability_threshold: float,
    use_rgb_heuristic: bool,
    rgb_threshold: float,
    minimum_area_px: int,
) -> WaterOverrideMaps:
    water_probability = np.asarray(water_probability, dtype=np.float32)
    predicted_water = np.asarray(predicted_water_mask, dtype=bool)
    safe_surface = np.asarray(safe_class_mask, dtype=bool)
    zero_score = np.zeros(water_probability.shape, dtype=np.float32)

    if not enabled:
        return WaterOverrideMaps(
            water_probability_map=water_probability,
            water_heuristic_score_map=zero_score,
            predicted_water_mask=predicted_water,
            probability_override_mask=np.zeros_like(predicted_water),
            rgb_override_mask=np.zeros_like(predicted_water),
            effective_water_mask=predicted_water.copy(),
        )

    probability_override = (
        (water_probability >= probability_threshold) & ~predicted_water
    )
    heuristic_score = zero_score
    rgb_override = np.zeros_like(predicted_water)
    if use_rgb_heuristic and image_rgb is not None:
        heuristic_score = _rgb_water_heuristic_score(
            image_rgb,
            water_probability,
        )
        rgb_candidate = (
            (heuristic_score >= rgb_threshold)
            & safe_surface
            & ~predicted_water
            & ~probability_override
        )
        opening_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        rgb_candidate = cv2.morphologyEx(
            rgb_candidate.astype(np.uint8),
            cv2.MORPH_OPEN,
            opening_kernel,
        ).astype(bool)
        rgb_override = _remove_small_components(
            rgb_candidate,
            minimum_area_px,
        )

    effective_water = predicted_water | probability_override | rgb_override
    return WaterOverrideMaps(
        water_probability_map=water_probability,
        water_heuristic_score_map=heuristic_score,
        predicted_water_mask=predicted_water,
        probability_override_mask=probability_override,
        rgb_override_mask=rgb_override,
        effective_water_mask=effective_water,
    )
