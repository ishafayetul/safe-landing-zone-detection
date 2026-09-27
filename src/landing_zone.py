from dataclasses import dataclass
from math import pi
from typing import List, Optional, Tuple

import cv2
import numpy as np
import pandas as pd

from .risk_config import RiskParameters
from .risk_map import RiskMaps


@dataclass
class LandingRegion:
    region_id: int
    mask: np.ndarray
    score: float
    dominant_class: str
    area_px: int
    bbox: Tuple[int, int, int, int]
    centroid_x: float
    centroid_y: float
    best_center_x: int
    best_center_y: int
    mean_risk: float
    mean_suitability: float
    max_inscribed_radius_px: float
    footprint_radius_px: float
    footprint_fits: bool
    footprint_fit_score: float
    shape_compactness: float
    aspect_ratio: float
    elongation_score: float
    confidence_score: float
    uncertainty_score: float
    margin_score: float
    hazard_distance_px: float
    obstacle_clearance_score: float
    normalized_area_score: float
    accepted: bool
    rejection_reasons: Tuple[str, ...]
    rank: int | None = None
    zone_id: str | None = None

    @property
    def component_id(self) -> int:
        return self.region_id

    @property
    def final_region_score(self) -> float:
        return self.score

    @property
    def dominant_semantic_class(self) -> str:
        return self.dominant_class

    @property
    def risk_category(self) -> str:
        return risk_category(self.mean_risk)

    def record(self, selected: bool):
        x, y, width, height = self.bbox
        return {
            "rank": self.rank,
            "zone_id": self.zone_id,
            "region_id": self.region_id,
            "score": self.score,
            "dominant_class": self.dominant_class,
            "area_px": self.area_px,
            "bbox_x": x,
            "bbox_y": y,
            "bbox_width": width,
            "bbox_height": height,
            "centroid_x": self.centroid_x,
            "centroid_y": self.centroid_y,
            "best_center_x": self.best_center_x,
            "best_center_y": self.best_center_y,
            "mean_risk": self.mean_risk,
            "mean_suitability": self.mean_suitability,
            "max_inscribed_radius_px": self.max_inscribed_radius_px,
            "footprint_radius_px": self.footprint_radius_px,
            "footprint_fits": self.footprint_fits,
            "shape_compactness": self.shape_compactness,
            "aspect_ratio": self.aspect_ratio,
            "elongation_score": self.elongation_score,
            "confidence_score": self.confidence_score,
            "uncertainty_score": self.uncertainty_score,
            "margin_score": self.margin_score,
            "hazard_distance_px": self.hazard_distance_px,
            "risk_category": self.risk_category,
            "obstacle_clearance_score": self.obstacle_clearance_score,
            "footprint_fit_score": self.footprint_fit_score,
            "normalized_area_score": self.normalized_area_score,
            "accepted": self.accepted,
            "selected": selected,
            "rejection_reasons": ";".join(self.rejection_reasons),
        }


CANDIDATE_COLUMNS = [
    "rank",
    "zone_id",
    "region_id",
    "score",
    "dominant_class",
    "area_px",
    "bbox_x",
    "bbox_y",
    "bbox_width",
    "bbox_height",
    "centroid_x",
    "centroid_y",
    "best_center_x",
    "best_center_y",
    "mean_risk",
    "mean_suitability",
    "max_inscribed_radius_px",
    "footprint_radius_px",
    "footprint_fits",
    "shape_compactness",
    "aspect_ratio",
    "elongation_score",
    "confidence_score",
    "uncertainty_score",
    "margin_score",
    "hazard_distance_px",
    "risk_category",
    "obstacle_clearance_score",
    "footprint_fit_score",
    "normalized_area_score",
    "accepted",
    "selected",
    "rejection_reasons",
]

RANKED_SAFE_ZONE_COLUMNS = [
    "rank",
    "zone_id",
    "region_id",
    "score",
    "mean_risk",
    "mean_suitability",
    "dominant_class",
    "area_px",
    "bbox_x",
    "bbox_y",
    "bbox_width",
    "bbox_height",
    "centroid_x",
    "centroid_y",
    "best_center_x",
    "best_center_y",
    "max_inscribed_radius_px",
    "footprint_radius_px",
    "footprint_fit_score",
    "obstacle_clearance_score",
    "shape_compactness",
    "aspect_ratio",
    "elongation_score",
    "confidence_score",
    "uncertainty_score",
    "margin_score",
    "hazard_distance_px",
    "risk_category",
]

REJECTED_COLUMNS = [
    "region_id",
    "rejection_reasons",
    "area_px",
    "bbox_x",
    "bbox_y",
    "bbox_width",
    "bbox_height",
    "mean_risk",
    "confidence_score",
    "max_inscribed_radius_px",
    "details",
]


def risk_category(mean_risk: float) -> str:
    if mean_risk <= 0.25:
        return "Very Safe"
    if mean_risk <= 0.40:
        return "Safe"
    if mean_risk <= 0.55:
        return "Moderate"
    return "Risky"


def ranked_safe_zones_frame(regions: List[LandingRegion]) -> pd.DataFrame:
    rows = []
    for region in regions:
        x, y, width, height = region.bbox
        rows.append(
            {
                "rank": region.rank,
                "zone_id": region.zone_id,
                "region_id": region.region_id,
                "score": region.score,
                "mean_risk": region.mean_risk,
                "mean_suitability": region.mean_suitability,
                "dominant_class": region.dominant_class,
                "area_px": region.area_px,
                "bbox_x": x,
                "bbox_y": y,
                "bbox_width": width,
                "bbox_height": height,
                "centroid_x": region.centroid_x,
                "centroid_y": region.centroid_y,
                "best_center_x": region.best_center_x,
                "best_center_y": region.best_center_y,
                "max_inscribed_radius_px": region.max_inscribed_radius_px,
                "footprint_radius_px": region.footprint_radius_px,
                "footprint_fit_score": region.footprint_fit_score,
                "obstacle_clearance_score": region.obstacle_clearance_score,
                "shape_compactness": region.shape_compactness,
                "aspect_ratio": region.aspect_ratio,
                "elongation_score": region.elongation_score,
                "confidence_score": region.confidence_score,
                "uncertainty_score": region.uncertainty_score,
                "margin_score": region.margin_score,
                "hazard_distance_px": region.hazard_distance_px,
                "risk_category": region.risk_category,
            }
        )
    return pd.DataFrame(rows, columns=RANKED_SAFE_ZONE_COLUMNS)


def _shape_metrics(mask: np.ndarray, width: int, height: int):
    contours, _ = cv2.findContours(
        mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE
    )
    perimeter = sum(cv2.arcLength(contour, True) for contour in contours)
    area = int(mask.sum())
    compactness = 0.0 if perimeter <= 0 else 4.0 * pi * area / (perimeter**2)
    compactness = float(np.clip(compactness, 0.0, 1.0))
    aspect_ratio = max(width, height) / float(max(1, min(width, height)))
    elongation = 1.0 / aspect_ratio
    return compactness, float(aspect_ratio), float(elongation)


def _rejected_fragments(mask, reason, prefix, risks: RiskMaps):
    rows = []
    count, labels, stats, _ = cv2.connectedComponentsWithStats(
        mask.astype(np.uint8), connectivity=8
    )
    for component_id in range(1, count):
        region_mask = labels == component_id
        area = int(stats[component_id, cv2.CC_STAT_AREA])
        x = int(stats[component_id, cv2.CC_STAT_LEFT])
        y = int(stats[component_id, cv2.CC_STAT_TOP])
        width = int(stats[component_id, cv2.CC_STAT_WIDTH])
        height = int(stats[component_id, cv2.CC_STAT_HEIGHT])
        rows.append(
            {
                "region_id": f"{prefix}_{component_id}",
                "rejection_reasons": reason,
                "area_px": area,
                "bbox_x": x,
                "bbox_y": y,
                "bbox_width": width,
                "bbox_height": height,
                "mean_risk": float(risks.final_risk[region_mask].mean()),
                "confidence_score": float(risks.confidence_map[region_mask].mean()),
                "max_inscribed_radius_px": 0.0,
                "details": f"Safe-class pixels rejected because of {reason}",
            }
        )
    return rows


def _region_from_component(
    component_id,
    mask,
    stats,
    centroids,
    pred_mask,
    id2label,
    risks,
    params,
):
    area = int(stats[component_id, cv2.CC_STAT_AREA])
    x = int(stats[component_id, cv2.CC_STAT_LEFT])
    y = int(stats[component_id, cv2.CC_STAT_TOP])
    width = int(stats[component_id, cv2.CC_STAT_WIDTH])
    height = int(stats[component_id, cv2.CC_STAT_HEIGHT])
    class_ids = pred_mask[mask].astype(np.int64)
    dominant_id = int(np.bincount(class_ids).argmax())

    component_distances = np.where(mask, risks.safe_distance_map, -1.0)
    flat_best = int(component_distances.argmax())
    best_y, best_x = np.unravel_index(flat_best, mask.shape)
    max_radius = float(component_distances[best_y, best_x])
    footprint_radius = float(params.resolved_footprint_radius_px)
    footprint_fits = max_radius >= footprint_radius
    desired_clearance = footprint_radius * 1.5
    footprint_fit = min(max_radius / desired_clearance, 1.0)

    compactness, aspect_ratio, elongation = _shape_metrics(mask, width, height)
    confidence = float(risks.confidence_map[mask].mean())
    uncertainty = float(risks.uncertainty_map[mask].mean())
    margin = float(risks.margin_map[mask].mean())
    mean_risk = float(risks.final_risk[mask].mean())
    mean_suitability = float(risks.landing_suitability[mask].mean())
    obstacle_clearance = float(
        (1.0 - risks.obstacle_proximity_risk[mask]).mean()
    )
    hazard_distance = float(risks.hazard_distance_map[best_y, best_x])
    normalized_area = min(area / float(params.desired_area_px), 1.0)
    # Compactness and elongation jointly penalize narrow or irregular regions.
    shape_compactness_score = compactness * elongation
    score = (
        0.30 * mean_suitability
        + 0.25 * footprint_fit
        + 0.15 * obstacle_clearance
        + 0.10 * normalized_area
        + 0.10 * shape_compactness_score
        + 0.10 * confidence
    )

    reasons = []
    if area < params.min_area_px:
        reasons.append("too_small")
    if not footprint_fits:
        reasons.append("footprint_does_not_fit")
    if confidence < params.min_confidence_score:
        reasons.append("low_confidence")

    return LandingRegion(
        region_id=component_id,
        mask=mask,
        score=float(score),
        dominant_class=id2label[dominant_id],
        area_px=area,
        bbox=(x, y, width, height),
        centroid_x=float(centroids[component_id, 0]),
        centroid_y=float(centroids[component_id, 1]),
        best_center_x=int(best_x),
        best_center_y=int(best_y),
        mean_risk=mean_risk,
        mean_suitability=mean_suitability,
        max_inscribed_radius_px=max_radius,
        footprint_radius_px=footprint_radius,
        footprint_fits=footprint_fits,
        footprint_fit_score=float(footprint_fit),
        shape_compactness=compactness,
        aspect_ratio=aspect_ratio,
        elongation_score=elongation,
        confidence_score=confidence,
        uncertainty_score=uncertainty,
        margin_score=margin,
        hazard_distance_px=hazard_distance,
        obstacle_clearance_score=obstacle_clearance,
        normalized_area_score=normalized_area,
        accepted=not reasons,
        rejection_reasons=tuple(reasons),
    )


def find_landing_regions(pred_mask, id2label, risks: RiskMaps, params: RiskParameters):
    params.validate()
    count, labels, stats, centroids = cv2.connectedComponentsWithStats(
        risks.valid_surface_mask.astype(np.uint8), connectivity=8
    )
    regions: List[LandingRegion] = []
    rejected_rows = []

    hazard_overlap = risks.safe_class_mask & risks.dilated_hazard_mask
    high_risk = (
        risks.safe_class_mask
        & ~risks.dilated_hazard_mask
        & (risks.final_risk > params.risk_threshold)
    )
    rejected_rows.extend(
        _rejected_fragments(hazard_overlap, "hazard_overlap", "hazard", risks)
    )
    rejected_rows.extend(
        _rejected_fragments(high_risk, "too_high_risk", "risk", risks)
    )

    for component_id in range(1, count):
        mask = labels == component_id
        region = _region_from_component(
            component_id,
            mask,
            stats,
            centroids,
            pred_mask,
            id2label,
            risks,
            params,
        )
        regions.append(region)
        if region.rejection_reasons:
            x, y, width, height = region.bbox
            rejected_rows.append(
                {
                    "region_id": f"surface_{region.region_id}",
                    "rejection_reasons": ";".join(region.rejection_reasons),
                    "area_px": region.area_px,
                    "bbox_x": x,
                    "bbox_y": y,
                    "bbox_width": width,
                    "bbox_height": height,
                    "mean_risk": region.mean_risk,
                    "confidence_score": region.confidence_score,
                    "max_inscribed_radius_px": region.max_inscribed_radius_px,
                    "details": "Valid-surface component failed landing requirements",
                }
            )

    accepted_regions = [region for region in regions if region.accepted]
    accepted_regions.sort(
        key=lambda region: (
            -region.score,
            region.mean_risk,
            -region.max_inscribed_radius_px,
            -region.area_px,
        )
    )
    for rank, region in enumerate(accepted_regions, start=1):
        region.rank = rank
        region.zone_id = f"Zone-{rank:02d}"
    rejected_regions = [region for region in regions if not region.accepted]
    rejected_regions.sort(key=lambda region: region.score, reverse=True)
    ordered_regions = accepted_regions + rejected_regions
    best: Optional[LandingRegion] = accepted_regions[0] if accepted_regions else None
    table = pd.DataFrame(
        [
            region.record(selected=region is best)
            for region in ordered_regions
        ],
        columns=CANDIDATE_COLUMNS,
    )
    rejected = pd.DataFrame(rejected_rows, columns=REJECTED_COLUMNS)
    return accepted_regions, best, table, rejected
