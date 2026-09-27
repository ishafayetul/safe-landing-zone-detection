import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from PIL import Image

from .inference import AnalysisResult
from .risk_config import CLASS_COLOR_PALETTE
from .visualization import (
    colorize_hazard_mask,
    colorize_probability,
    colorize_risk,
    colorize_valid_centers,
    colorize_water_override_sources,
    create_labeled_best_landing_zone,
    create_labeled_binary_mask,
    create_labeled_overlay,
    create_labeled_probability_map,
    create_labeled_ranked_safe_zones,
    create_labeled_risk_map,
    create_labeled_semantic_mask,
    create_labeled_water_detection_overlay,
    create_labeled_water_override_mask,
)


def _save_rgb(array, path):
    Image.fromarray(array, mode="RGB").save(path)


def create_next_sample_output_dir(
    base_output_dir: str | Path = "outputs",
) -> Path:
    """Create and return the next non-overwriting sequential Sample-XX folder."""
    base_dir = Path(base_output_dir)
    base_dir.mkdir(parents=True, exist_ok=True)
    pattern = re.compile(r"Sample-(\d{2,})")
    existing_numbers = []
    for child in base_dir.iterdir():
        match = pattern.fullmatch(child.name)
        if child.is_dir() and match:
            existing_numbers.append(int(match.group(1)))

    next_number = max(existing_numbers, default=0) + 1
    while True:
        sample_dir = base_dir / f"Sample-{next_number:02d}"
        try:
            sample_dir.mkdir(exist_ok=False)
            return sample_dir
        except FileExistsError:
            # Another process may have allocated the same number after the scan.
            next_number += 1


def _metadata_value(value: Any):
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, Mapping):
        return {str(key): _metadata_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_metadata_value(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def landing_target_payload(result: AnalysisResult):
    best = result.best_region
    note = "Pixel coordinates only. No real-world coordinates available without calibration."
    if best is None:
        return {
            "found": False,
            "rank": None,
            "zone_id": None,
            "center_px": None,
            "bbox_px": None,
            "dominant_class": None,
            "score": None,
            "mean_risk": None,
            "footprint_radius_px": result.footprint_radius_px,
            "max_inscribed_radius_px": None,
            "meters_per_pixel": result.meters_per_pixel,
            "center_m": None,
            "confidence_score": None,
            "uncertainty_score": None,
            "reason": result.decision_message,
            "note": note,
        }

    center_px = [best.best_center_x, best.best_center_y]
    center_m = None
    if result.meters_per_pixel is not None:
        center_m = [
            best.best_center_x * result.meters_per_pixel,
            best.best_center_y * result.meters_per_pixel,
        ]
        note = (
            "Local image-plane meter coordinates relative to the image origin; "
            "not GPS or real-world UAV coordinates."
        )
    return {
        "found": True,
        "rank": best.rank,
        "zone_id": best.zone_id,
        "center_px": center_px,
        "bbox_px": list(best.bbox),
        "dominant_class": best.dominant_class,
        "score": best.score,
        "mean_risk": best.mean_risk,
        "footprint_radius_px": best.footprint_radius_px,
        "max_inscribed_radius_px": best.max_inscribed_radius_px,
        "meters_per_pixel": result.meters_per_pixel,
        "center_m": center_m,
        "confidence_score": best.confidence_score,
        "uncertainty_score": best.uncertainty_score,
        "reason": result.decision_message,
        "note": note,
    }


def ranked_safe_zones_payload(result: AnalysisResult):
    if not result.ranked_regions:
        return {
            "found_count": 0,
            "zones": [],
            "note": (
                "No valid landing zone found for the selected thresholds and "
                "footprint size."
            ),
        }

    zones = []
    for region in result.ranked_regions:
        x, y, width, height = region.bbox
        zones.append(
            {
                "rank": int(region.rank),
                "zone_id": region.zone_id,
                "region_id": int(region.region_id),
                "score": float(region.score),
                "mean_risk": float(region.mean_risk),
                "mean_suitability": float(region.mean_suitability),
                "risk_category": region.risk_category,
                "dominant_class": region.dominant_class,
                "best_center_px": [
                    int(region.best_center_x),
                    int(region.best_center_y),
                ],
                "centroid_px": [
                    float(region.centroid_x),
                    float(region.centroid_y),
                ],
                "bbox_px": [int(x), int(y), int(width), int(height)],
                "area_px": int(region.area_px),
                "max_inscribed_radius_px": float(
                    region.max_inscribed_radius_px
                ),
                "footprint_radius_px": float(region.footprint_radius_px),
                "footprint_fit_score": float(region.footprint_fit_score),
                "obstacle_clearance_score": float(
                    region.obstacle_clearance_score
                ),
                "shape_compactness": float(region.shape_compactness),
                "aspect_ratio": float(region.aspect_ratio),
                "elongation_score": float(region.elongation_score),
                "confidence_score": float(region.confidence_score),
                "uncertainty_score": float(region.uncertainty_score),
                "margin_score": float(region.margin_score),
                "hazard_distance_px": float(region.hazard_distance_px),
            }
        )
    return {
        "found_count": len(zones),
        "zones": zones,
        "note": "Coordinates are image-pixel coordinates only, not GPS coordinates.",
    }


def save_analysis_outputs(
    result: AnalysisResult,
    output_dir: Path,
    save_debug: bool = False,
    save_labeled: bool = True,
    run_metadata: Mapping[str, Any] | None = None,
) -> list[str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    target_payload = landing_target_payload(result)
    ranked_payload = ranked_safe_zones_payload(result)
    _save_rgb(result.original_image, output_dir / "input_image.png")
    _save_rgb(result.original_image, output_dir / "original.png")
    _save_rgb(result.semantic_mask, output_dir / "semantic_mask.png")
    _save_rgb(result.overlay, output_dir / "overlay.png")
    _save_rgb(result.risk_visualization, output_dir / "risk_map.png")
    _save_rgb(result.best_landing_zone, output_dir / "best_landing_zone.png")
    _save_rgb(result.all_safe_zones, output_dir / "all_safe_zones.png")
    _save_rgb(result.top_safe_zones, output_dir / "top_safe_zones.png")
    _save_rgb(
        result.water_detection_overlay,
        output_dir / "water_detection_overlay.png",
    )
    result.candidates.to_csv(output_dir / "candidates.csv", index=False)
    result.ranked_safe_zones.to_csv(
        output_dir / "ranked_safe_zones.csv", index=False
    )
    result.rejected_regions.to_csv(output_dir / "rejected_regions.csv", index=False)
    with (output_dir / "landing_target.json").open("w", encoding="utf-8") as handle:
        json.dump(target_payload, handle, indent=2)
        handle.write("\n")
    with (output_dir / "ranked_safe_zones.json").open(
        "w", encoding="utf-8"
    ) as handle:
        json.dump(ranked_payload, handle, indent=2)
        handle.write("\n")

    debug_images = {}
    water_info = {
        "predicted_pixels": int(result.risks.model_predicted_water_mask.sum()),
        "probability_pixels": int(
            result.risks.water_probability_override_mask.sum()
        ),
        "rgb_pixels": int(result.risks.water_rgb_override_mask.sum()),
        "effective_pixels": int(result.risks.effective_water_mask.sum()),
    }
    if save_debug:
        debug_images = {
            "car_probability_map.png": colorize_probability(
                result.risks.car_probability_map
            ),
            "danger_probability_map.png": colorize_probability(
                result.risks.danger_probability_map
            ),
            "hazard_override_mask.png": colorize_hazard_mask(
                result.risks.dilated_hazard_mask
            ),
            "risk_map_before_override.png": colorize_risk(
                result.risks.risk_map_before_override
            ),
            "risk_map_after_override.png": colorize_risk(result.risks.final_risk),
            "confidence_map.png": colorize_probability(
                result.risks.confidence_map
            ),
            "uncertainty_map.png": colorize_probability(
                result.risks.uncertainty_map
            ),
            "margin_map.png": colorize_probability(result.risks.margin_map),
            "footprint_valid_centers.png": colorize_valid_centers(
                result.risks.footprint_valid_center_mask
            ),
            "water_probability_map.png": colorize_probability(
                result.risks.water_probability_map
            ),
            "water_heuristic_score_map.png": colorize_probability(
                result.risks.water_heuristic_score_map
            ),
            "water_override_mask.png": colorize_water_override_sources(
                result.risks.model_predicted_water_mask,
                result.risks.water_probability_override_mask,
                result.risks.water_rgb_override_mask,
            ),
        }
        for filename, image in debug_images.items():
            _save_rgb(image, output_dir / filename)
        result.class_coverage.to_csv(output_dir / "class_coverage.csv", index=False)

    metadata_values = {
        key: _metadata_value(value) for key, value in (run_metadata or {}).items()
    }
    labeled_images = {}
    if save_labeled:
        present_classes = result.class_coverage.loc[
            result.class_coverage["pixel_count"] > 0, "class_name"
        ].tolist()
        risk_threshold = metadata_values.get("risk_threshold")
        overlay_opacity = metadata_values.get("overlay_opacity")
        labeled_images.update(
            {
                "semantic_mask_labeled.png": create_labeled_semantic_mask(
                    result.semantic_mask,
                    present_classes,
                    CLASS_COLOR_PALETTE,
                ),
                "overlay_labeled.png": create_labeled_overlay(
                    result.overlay,
                    present_classes,
                    CLASS_COLOR_PALETTE,
                    overlay_opacity=overlay_opacity,
                ),
                "risk_map_labeled.png": create_labeled_risk_map(
                    result.risk_visualization,
                    risk_threshold=risk_threshold,
                ),
                "best_landing_zone_labeled.png": create_labeled_best_landing_zone(
                    result.best_landing_zone,
                    target_payload,
                    {
                        "risk_threshold": risk_threshold,
                        "decision_message": result.decision_message,
                    },
                ),
                "all_safe_zones_labeled.png": create_labeled_ranked_safe_zones(
                    result.all_safe_zones,
                    result.ranked_regions,
                    title="All Ranked Safe Landing Zones",
                ),
                "top_safe_zones_labeled.png": create_labeled_ranked_safe_zones(
                    result.top_safe_zones,
                    result.ranked_regions[: result.top_n_zones],
                    title=f"Top {result.top_n_zones} Ranked Safe Landing Zones",
                ),
                "water_detection_overlay_labeled.png": create_labeled_water_detection_overlay(
                    result.water_detection_overlay,
                    water_info,
                ),
            }
        )
        if save_debug:
            labeled_images.update(
                {
                    "car_probability_map_labeled.png": create_labeled_probability_map(
                        debug_images["car_probability_map.png"],
                        "Car Probability Map",
                        "Car Probability",
                    ),
                    "danger_probability_map_labeled.png": create_labeled_probability_map(
                        debug_images["danger_probability_map.png"],
                        "Danger Probability Map",
                        "Danger Probability",
                    ),
                    "confidence_map_labeled.png": create_labeled_probability_map(
                        debug_images["confidence_map.png"],
                        "Model Confidence Map",
                        "Confidence",
                    ),
                    "uncertainty_map_labeled.png": create_labeled_probability_map(
                        debug_images["uncertainty_map.png"],
                        "Prediction Uncertainty Map",
                        "Uncertainty",
                    ),
                    "margin_map_labeled.png": create_labeled_probability_map(
                        debug_images["margin_map.png"],
                        "Top-1 / Top-2 Probability Margin Map",
                        "Margin",
                    ),
                    "hazard_override_mask_labeled.png": create_labeled_binary_mask(
                        debug_images["hazard_override_mask.png"],
                        "Hazard Override Mask",
                        "White/Red = Hazard area",
                        "Black/Dark = Non-hazard area",
                        "Areas marked as hazard are excluded from landing candidates.",
                    ),
                    "footprint_valid_centers_labeled.png": create_labeled_binary_mask(
                        debug_images["footprint_valid_centers.png"],
                        "Footprint-Valid Landing Centers",
                        "White/Green = Valid landing center",
                        "Black/Dark = Invalid center",
                        "Valid centers are pixels where the drone footprint can fit inside a safe region.",
                    ),
                    "risk_map_before_override_labeled.png": create_labeled_risk_map(
                        debug_images["risk_map_before_override.png"],
                        risk_threshold=risk_threshold,
                        title="Risk Map Before Hazard Override",
                        subtitle="Weighted semantic risk before the hard hazard floor",
                        explanation="Shows combined semantic, proximity, area, slope-proxy, and roughness-proxy risk.",
                    ),
                    "risk_map_after_override_labeled.png": create_labeled_risk_map(
                        debug_images["risk_map_after_override.png"],
                        risk_threshold=risk_threshold,
                        title="Risk Map After Hazard Override",
                        subtitle="Final confidence-aware risk with hazard enforcement",
                        explanation="Hazard pixels are forced to high risk.",
                    ),
                    "water_probability_map_labeled.png": create_labeled_probability_map(
                        debug_images["water_probability_map.png"],
                        "Water Probability Map",
                        "Water Probability",
                    ),
                    "water_heuristic_score_map_labeled.png": create_labeled_probability_map(
                        debug_images["water_heuristic_score_map.png"],
                        "Water Heuristic Score Map",
                        "Water Heuristic Score",
                    ),
                    "water_override_mask_labeled.png": create_labeled_water_override_mask(
                        debug_images["water_override_mask.png"],
                        water_info,
                    ),
                }
            )
        for filename, image in labeled_images.items():
            _save_rgb(image, output_dir / filename)

    metadata = {
        "sample_folder": output_dir.name,
        "input_filename": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "model_dir": None,
        "tiled_inference": None,
        "risk_threshold": None,
        "footprint_radius_px": result.footprint_radius_px,
        "save_debug": bool(save_debug),
        "save_labeled": bool(save_labeled),
        "labeled_outputs": list(labeled_images),
        "water_override": water_info,
        "num_safe_zones_found": len(result.ranked_regions),
        "top_n_zones": result.top_n_zones,
        "max_zones_to_label": result.max_zones_to_label,
        "max_zones_to_draw_footprint": result.max_zones_to_draw_footprint,
    }
    metadata.update(metadata_values)
    metadata["save_labeled"] = bool(save_labeled)
    metadata["labeled_outputs"] = list(labeled_images)
    metadata["water_override"] = water_info
    safe_zone_outputs = [
        "all_safe_zones.png",
        "top_safe_zones.png",
        "ranked_safe_zones.csv",
        "ranked_safe_zones.json",
    ]
    if save_labeled:
        safe_zone_outputs[1:1] = ["all_safe_zones_labeled.png"]
        safe_zone_outputs[3:3] = ["top_safe_zones_labeled.png"]
    metadata["num_safe_zones_found"] = len(result.ranked_regions)
    metadata["top_n_zones"] = result.top_n_zones
    metadata["max_zones_to_label"] = result.max_zones_to_label
    metadata["max_zones_to_draw_footprint"] = (
        result.max_zones_to_draw_footprint
    )
    metadata["safe_zone_outputs"] = safe_zone_outputs
    with (output_dir / "run_metadata.json").open("w", encoding="utf-8") as handle:
        json.dump(metadata, handle, indent=2)
        handle.write("\n")
    return list(labeled_images)
