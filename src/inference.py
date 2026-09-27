from dataclasses import dataclass

import numpy as np
import pandas as pd
import torch
import torch.nn.functional as functional
from PIL import Image

from .landing_zone import (
    LandingRegion,
    find_landing_regions,
    ranked_safe_zones_frame,
)
from .model_loader import ModelBundle
from .risk_config import (
    MAX_ZONES_TO_DRAW_FOOTPRINT,
    MAX_ZONES_TO_LABEL,
    TOP_N_SAFE_ZONES,
    RiskParameters,
)
from .risk_map import RiskMaps, build_risk_maps
from .visualization import (
    blend_overlay,
    colorize_mask,
    colorize_risk,
    draw_all_safe_zones,
    draw_best_landing_zone,
    draw_top_safe_zones,
    draw_water_detection_overlay,
)


@dataclass
class AnalysisResult:
    original_image: np.ndarray
    pred_mask: np.ndarray
    class_probabilities: np.ndarray
    semantic_mask: np.ndarray
    overlay: np.ndarray
    risk_visualization: np.ndarray
    best_landing_zone: np.ndarray
    all_safe_zones: np.ndarray
    top_safe_zones: np.ndarray
    water_detection_overlay: np.ndarray
    risks: RiskMaps
    candidates: pd.DataFrame
    ranked_safe_zones: pd.DataFrame
    rejected_regions: pd.DataFrame
    ranked_regions: list[LandingRegion]
    best_region: LandingRegion | None
    class_coverage: pd.DataFrame
    decision_message: str
    footprint_radius_px: float
    meters_per_pixel: float | None
    top_n_zones: int
    max_zones_to_label: int
    max_zones_to_draw_footprint: int

    @property
    def class_legend(self) -> pd.DataFrame:
        """Version 0.1 compatibility alias."""
        return self.class_coverage


def _probabilities_from_logits(logits: np.ndarray) -> np.ndarray:
    logits_tensor = torch.from_numpy(logits)
    return torch.softmax(logits_tensor, dim=0).numpy().astype(np.float32)


def predict_mask_full(image, model, processor, device):
    original_width, original_height = image.size
    inputs = processor(images=image, return_tensors="pt")
    inputs = {name: tensor.to(device) for name, tensor in inputs.items()}
    with torch.no_grad():
        outputs = model(**inputs)
        upsampled_logits = functional.interpolate(
            outputs.logits,
            size=(original_height, original_width),
            mode="bilinear",
            align_corners=False,
        )[0]
    logits = upsampled_logits.cpu().numpy().astype(np.float32)
    probabilities = _probabilities_from_logits(logits)
    pred_mask = logits.argmax(axis=0).astype(np.int32)
    return pred_mask, probabilities


def _tile_starts(length: int, tile_size: int, overlap: int):
    if length <= tile_size:
        return [0]
    step = tile_size - overlap
    starts = list(range(0, length - tile_size + 1, step))
    last_start = length - tile_size
    if starts[-1] != last_start:
        starts.append(last_start)
    return starts


def predict_mask_tiled(
    image,
    model,
    processor,
    device,
    tile_size=512,
    overlap=96,
):
    """Average full-resolution logits from overlapping image tiles."""
    if tile_size <= 0:
        raise ValueError("tile size must be positive")
    if overlap < 0 or overlap >= tile_size:
        raise ValueError("tile overlap must be nonnegative and smaller than tile size")

    width, height = image.size
    x_starts = _tile_starts(width, tile_size, overlap)
    y_starts = _tile_starts(height, tile_size, overlap)
    num_classes = int(model.config.num_labels)
    accumulated_logits = np.zeros((num_classes, height, width), dtype=np.float32)
    accumulated_weights = np.zeros((height, width), dtype=np.float32)

    for y in y_starts:
        for x in x_starts:
            right = min(x + tile_size, width)
            bottom = min(y + tile_size, height)
            tile = image.crop((x, y, right, bottom))
            tile_width, tile_height = tile.size
            inputs = processor(images=tile, return_tensors="pt")
            inputs = {name: tensor.to(device) for name, tensor in inputs.items()}
            with torch.no_grad():
                outputs = model(**inputs)
                tile_logits = functional.interpolate(
                    outputs.logits,
                    size=(tile_height, tile_width),
                    mode="bilinear",
                    align_corners=False,
                )[0]
            accumulated_logits[:, y:bottom, x:right] += (
                tile_logits.cpu().numpy().astype(np.float32)
            )
            accumulated_weights[y:bottom, x:right] += 1.0

    if np.any(accumulated_weights == 0):
        raise RuntimeError("tiled inference left uncovered image pixels")
    averaged_logits = accumulated_logits / accumulated_weights[None, ...]
    probabilities = _probabilities_from_logits(averaged_logits)
    pred_mask = averaged_logits.argmax(axis=0).astype(np.int32)
    return pred_mask, probabilities


def predict_semantic_mask(
    image: Image.Image,
    bundle: ModelBundle,
    use_tiled_inference=True,
    tile_size=512,
    tile_overlap=96,
):
    if use_tiled_inference:
        return predict_mask_tiled(
            image,
            bundle.model,
            bundle.processor,
            bundle.device,
            tile_size=tile_size,
            overlap=tile_overlap,
        )
    return predict_mask_full(
        image, bundle.model, bundle.processor, bundle.device
    )


def _class_coverage(pred_mask, probabilities, id2label):
    total = pred_mask.size
    rows = []
    for class_id in sorted(id2label):
        class_probability = probabilities[class_id]
        count = int((pred_mask == class_id).sum())
        rows.append(
            {
                "class_id": class_id,
                "class_name": id2label[class_id],
                "pixel_count": count,
                "percentage": 100.0 * count / total,
                "max_probability": float(class_probability.max()),
                "mean_probability": float(class_probability.mean()),
            }
        )
    return pd.DataFrame(
        rows,
        columns=[
            "class_id",
            "class_name",
            "pixel_count",
            "percentage",
            "max_probability",
            "mean_probability",
        ],
    )


def analyze_image(
    image: Image.Image,
    bundle: ModelBundle,
    params: RiskParameters,
    overlay_opacity=0.45,
    use_tiled_inference=True,
    tile_size=512,
    tile_overlap=96,
    top_n_zones=TOP_N_SAFE_ZONES,
    max_zones_to_label=MAX_ZONES_TO_LABEL,
    max_zones_to_draw_footprint=MAX_ZONES_TO_DRAW_FOOTPRINT,
) -> AnalysisResult:
    params.validate()
    if not 0.0 <= overlay_opacity <= 1.0:
        raise ValueError("overlay opacity must be between 0 and 1")
    for name, value in (
        ("top N zones", top_n_zones),
        ("maximum zones to label", max_zones_to_label),
        ("maximum zones to draw footprint", max_zones_to_draw_footprint),
    ):
        if int(value) <= 0:
            raise ValueError(f"{name} must be positive")
    rgb_image = image.convert("RGB")
    image_array = np.asarray(rgb_image)
    pred_mask, probabilities = predict_semantic_mask(
        rgb_image,
        bundle,
        use_tiled_inference=use_tiled_inference,
        tile_size=tile_size,
        tile_overlap=tile_overlap,
    )
    risks = build_risk_maps(
        pred_mask,
        probabilities,
        bundle.id2label,
        params,
        image_rgb=image_array,
    )
    ranked_regions, best, candidates, rejected_regions = find_landing_regions(
        pred_mask, bundle.id2label, risks, params
    )
    best = ranked_regions[0] if ranked_regions else None
    ranked_safe_zones = ranked_safe_zones_frame(ranked_regions)
    if best is not None:
        decision_message = "A footprint-valid landing region was found."
    elif not risks.footprint_valid_center_mask.any():
        decision_message = (
            "No landing region can fit the selected drone footprint. "
            "Try reducing footprint radius or choosing another image."
        )
    else:
        decision_message = (
            "Footprint-valid centers exist, but no region passed all area, risk, "
            "hazard, and confidence requirements."
        )
    semantic_mask = colorize_mask(pred_mask, bundle.id2label)
    overlay = blend_overlay(image_array, semantic_mask, overlay_opacity)
    risk_visualization = colorize_risk(risks.final_risk)
    best_visualization = draw_best_landing_zone(
        image_array,
        best,
        risks.dilated_hazard_mask,
        params.resolved_footprint_radius_px,
        decision_message,
    )
    all_safe_zones = draw_all_safe_zones(
        image_array,
        ranked_regions,
        risks.dilated_hazard_mask,
        max_zones_to_label=int(max_zones_to_label),
        max_zones_to_draw_footprint=int(max_zones_to_draw_footprint),
    )
    top_safe_zones = draw_top_safe_zones(
        image_array,
        ranked_regions,
        risks.dilated_hazard_mask,
        top_n=int(top_n_zones),
    )
    water_detection_overlay = draw_water_detection_overlay(
        image_array,
        risks.model_predicted_water_mask,
        risks.water_probability_override_mask,
        risks.water_rgb_override_mask,
    )
    return AnalysisResult(
        original_image=image_array,
        pred_mask=pred_mask,
        class_probabilities=probabilities,
        semantic_mask=semantic_mask,
        overlay=overlay,
        risk_visualization=risk_visualization,
        best_landing_zone=best_visualization,
        all_safe_zones=all_safe_zones,
        top_safe_zones=top_safe_zones,
        water_detection_overlay=water_detection_overlay,
        risks=risks,
        candidates=candidates,
        ranked_safe_zones=ranked_safe_zones,
        rejected_regions=rejected_regions,
        ranked_regions=ranked_regions,
        best_region=best,
        class_coverage=_class_coverage(pred_mask, probabilities, bundle.id2label),
        decision_message=decision_message,
        footprint_radius_px=float(params.resolved_footprint_radius_px),
        meters_per_pixel=params.meters_per_pixel,
        top_n_zones=int(top_n_zones),
        max_zones_to_label=int(max_zones_to_label),
        max_zones_to_draw_footprint=int(max_zones_to_draw_footprint),
    )
