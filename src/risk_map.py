from dataclasses import dataclass

import cv2
import numpy as np
from scipy.ndimage import distance_transform_edt

from .risk_config import (
    DANGER_CLASSES,
    FINAL_RISK_WEIGHTS,
    ROUGHNESS_PROXY_RISK,
    SAFE_CLASSES,
    SEMANTIC_RISK,
    SLOPE_PROXY_RISK,
    RiskParameters,
)
from .water_detection import build_water_override_maps


@dataclass
class RiskMaps:
    semantic_risk: np.ndarray
    obstacle_proximity_risk: np.ndarray
    landing_area_size_risk: np.ndarray
    terrain_slope_proxy_risk: np.ndarray
    surface_roughness_proxy_risk: np.ndarray
    risk_map_before_override: np.ndarray
    final_risk_v2: np.ndarray
    final_risk: np.ndarray
    landing_suitability: np.ndarray
    safe_class_mask: np.ndarray
    predicted_danger_mask: np.ndarray
    raw_hazard_override_mask: np.ndarray
    dilated_hazard_mask: np.ndarray
    car_probability_map: np.ndarray
    danger_probability_map: np.ndarray
    confidence_map: np.ndarray
    uncertainty_map: np.ndarray
    margin_map: np.ndarray
    water_probability_map: np.ndarray
    water_heuristic_score_map: np.ndarray
    model_predicted_water_mask: np.ndarray
    water_probability_override_mask: np.ndarray
    water_rgb_override_mask: np.ndarray
    effective_water_mask: np.ndarray
    valid_surface_mask: np.ndarray
    hazard_distance_map: np.ndarray
    safe_distance_map: np.ndarray
    footprint_valid_center_mask: np.ndarray

    @property
    def obstacle_mask(self) -> np.ndarray:
        """Effective obstacle mask retained for compatibility with version 0.1."""
        return self.dilated_hazard_mask


def _lookup_map(pred_mask, id2label, values):
    result = np.ones(pred_mask.shape, dtype=np.float32)
    for class_id, class_name in id2label.items():
        result[pred_mask == class_id] = values[class_name]
    return result


def _class_mask(pred_mask, id2label, class_names):
    class_ids = [class_id for class_id, name in id2label.items() if name in class_names]
    return np.isin(pred_mask, class_ids)


def _area_size_risk(safe_mask, desired_area_px):
    area_risk = np.ones(safe_mask.shape, dtype=np.float32)
    count, labels, stats, _ = cv2.connectedComponentsWithStats(
        safe_mask.astype(np.uint8), connectivity=8
    )
    for component_id in range(1, count):
        area = int(stats[component_id, cv2.CC_STAT_AREA])
        component_risk = 1.0 - min(area / float(desired_area_px), 1.0)
        area_risk[labels == component_id] = component_risk
    return area_risk


def _dilate_hazards(mask: np.ndarray, dilation_px: int) -> np.ndarray:
    if dilation_px == 0 or not mask.any():
        return mask.copy()
    kernel_size = 2 * dilation_px + 1
    kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE, (kernel_size, kernel_size)
    )
    return cv2.dilate(mask.astype(np.uint8), kernel, iterations=1).astype(bool)


def _confidence_maps(class_probabilities: np.ndarray):
    sorted_top = np.partition(class_probabilities, -2, axis=0)
    top1 = sorted_top[-1].astype(np.float32)
    top2 = sorted_top[-2].astype(np.float32)
    margin = (top1 - top2).astype(np.float32)
    safe_probabilities = np.clip(class_probabilities, 1e-12, 1.0)
    entropy = -np.sum(
        safe_probabilities * np.log(safe_probabilities), axis=0
    ) / np.log(class_probabilities.shape[0])
    return top1, np.clip(entropy, 0.0, 1.0).astype(np.float32), margin


def _distance_inside_image(mask: np.ndarray) -> np.ndarray:
    """Distance to invalid pixels, treating the area outside the image as invalid."""
    padded = np.pad(mask, 1, mode="constant", constant_values=False)
    return distance_transform_edt(padded)[1:-1, 1:-1].astype(np.float32)


def build_risk_maps(
    pred_mask: np.ndarray,
    class_probabilities: np.ndarray,
    id2label,
    params: RiskParameters,
    image_rgb: np.ndarray | None = None,
) -> RiskMaps:
    params.validate()
    expected_shape = (len(id2label), *pred_mask.shape)
    if class_probabilities.shape != expected_shape:
        raise ValueError(
            f"class probabilities have shape {class_probabilities.shape}; "
            f"expected {expected_shape}"
        )

    semantic = _lookup_map(pred_mask, id2label, SEMANTIC_RISK)
    slope = _lookup_map(pred_mask, id2label, SLOPE_PROXY_RISK)
    roughness = _lookup_map(pred_mask, id2label, ROUGHNESS_PROXY_RISK)

    candidate_classes = list(SAFE_CLASSES)
    if params.allow_ar_marker_as_safe:
        candidate_classes.append("ar-marker")
    safe_mask = _class_mask(pred_mask, id2label, candidate_classes)
    predicted_danger = _class_mask(pred_mask, id2label, DANGER_CLASSES)

    label2id = {name: class_id for class_id, name in id2label.items()}
    car_probability = class_probabilities[label2id["car"]].astype(np.float32)
    water_probability = class_probabilities[label2id["water"]].astype(np.float32)
    danger_ids = [label2id[name] for name in DANGER_CLASSES]
    danger_probability = class_probabilities[danger_ids].sum(axis=0).astype(np.float32)
    danger_probability = np.clip(danger_probability, 0.0, 1.0)
    confidence, uncertainty, margin = _confidence_maps(class_probabilities)

    model_predicted_water = pred_mask == label2id["water"]
    water_overrides = build_water_override_maps(
        image_rgb,
        water_probability,
        model_predicted_water,
        safe_mask,
        enabled=params.use_water_override,
        probability_threshold=params.water_prob_threshold,
        use_rgb_heuristic=params.use_rgb_water_heuristic,
        rgb_threshold=params.water_rgb_threshold,
        minimum_area_px=params.water_min_area_px,
    )

    raw_hazard = (
        predicted_danger
        | (car_probability >= params.car_prob_threshold)
        | (danger_probability >= params.danger_prob_threshold)
        | water_overrides.effective_water_mask
    )
    dilated_hazard = _dilate_hazards(raw_hazard, params.hazard_dilation_px)

    if dilated_hazard.any():
        hazard_distance = distance_transform_edt(~dilated_hazard).astype(np.float32)
        obstacle_risk = np.exp(
            -hazard_distance / params.safe_distance_px
        ).astype(np.float32)
    else:
        image_diagonal = float(np.hypot(*pred_mask.shape))
        hazard_distance = np.full(
            pred_mask.shape, image_diagonal, dtype=np.float32
        )
        obstacle_risk = np.zeros(pred_mask.shape, dtype=np.float32)

    area_risk = _area_size_risk(safe_mask, params.desired_area_px)
    risk_before_override = (
        FINAL_RISK_WEIGHTS["semantic"] * semantic
        + FINAL_RISK_WEIGHTS["obstacle_proximity"] * obstacle_risk
        + FINAL_RISK_WEIGHTS["area_size"] * area_risk
        + FINAL_RISK_WEIGHTS["slope_proxy"] * slope
        + FINAL_RISK_WEIGHTS["roughness_proxy"] * roughness
    )
    risk_before_override = np.clip(risk_before_override, 0.0, 1.0).astype(
        np.float32
    )
    final_risk_v2 = np.maximum(
        risk_before_override,
        dilated_hazard.astype(np.float32) * params.hazard_override_risk,
    ).astype(np.float32)
    if params.use_confidence_risk:
        final_risk = np.clip(
            0.85 * final_risk_v2 + 0.15 * uncertainty, 0.0, 1.0
        ).astype(np.float32)
        # Confidence blending must never weaken the version 0.2 hard-hazard rule.
        final_risk = np.maximum(
            final_risk,
            dilated_hazard.astype(np.float32) * params.hazard_override_risk,
        ).astype(np.float32)
    else:
        final_risk = final_risk_v2.copy()
    suitability = (1.0 - final_risk).astype(np.float32)
    valid_surface = (
        safe_mask
        & (final_risk <= params.risk_threshold)
        & ~dilated_hazard
    )
    safe_distance = _distance_inside_image(valid_surface)
    footprint_centers = (
        valid_surface
        & (safe_distance >= params.resolved_footprint_radius_px)
    )

    return RiskMaps(
        semantic_risk=semantic,
        obstacle_proximity_risk=obstacle_risk,
        landing_area_size_risk=area_risk,
        terrain_slope_proxy_risk=slope,
        surface_roughness_proxy_risk=roughness,
        risk_map_before_override=risk_before_override,
        final_risk_v2=final_risk_v2,
        final_risk=final_risk,
        landing_suitability=suitability,
        safe_class_mask=safe_mask,
        predicted_danger_mask=predicted_danger,
        raw_hazard_override_mask=raw_hazard,
        dilated_hazard_mask=dilated_hazard,
        car_probability_map=car_probability,
        danger_probability_map=danger_probability,
        confidence_map=confidence,
        uncertainty_map=uncertainty,
        margin_map=margin,
        water_probability_map=water_overrides.water_probability_map,
        water_heuristic_score_map=water_overrides.water_heuristic_score_map,
        model_predicted_water_mask=water_overrides.predicted_water_mask,
        water_probability_override_mask=water_overrides.probability_override_mask,
        water_rgb_override_mask=water_overrides.rgb_override_mask,
        effective_water_mask=water_overrides.effective_water_mask,
        valid_surface_mask=valid_surface,
        hazard_distance_map=hazard_distance,
        safe_distance_map=safe_distance,
        footprint_valid_center_mask=footprint_centers,
    )
