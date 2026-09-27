from dataclasses import dataclass


CLASS_COLOR_PALETTE = {
    "unlabeled": (0, 0, 0),
    "paved-area": (128, 64, 128),
    "dirt": (130, 76, 0),
    "grass": (0, 102, 0),
    "gravel": (112, 103, 87),
    "water": (28, 42, 168),
    "rocks": (48, 41, 30),
    "pool": (0, 50, 89),
    "vegetation": (107, 142, 35),
    "roof": (70, 70, 70),
    "wall": (102, 102, 156),
    "window": (254, 228, 12),
    "door": (254, 148, 12),
    "fence": (190, 153, 153),
    "fence-pole": (153, 153, 153),
    "person": (255, 22, 96),
    "dog": (102, 51, 0),
    "car": (9, 143, 150),
    "bicycle": (119, 11, 32),
    "tree": (51, 51, 0),
    "bald-tree": (190, 250, 190),
    "ar-marker": (112, 150, 146),
    "obstacle": (2, 135, 115),
    "conflicting": (255, 0, 0),
}

MODEL_CLASS_NAMES = tuple(CLASS_COLOR_PALETTE)

SAFE_CLASSES = ["paved-area", "grass", "dirt", "gravel"]

DANGER_CLASSES = [
    "water",
    "rocks",
    "pool",
    "vegetation",
    "roof",
    "wall",
    "window",
    "door",
    "fence",
    "fence-pole",
    "person",
    "dog",
    "car",
    "bicycle",
    "tree",
    "bald-tree",
    "obstacle",
    "conflicting",
]

UNCERTAIN_CLASSES = ["unlabeled"]
ALLOW_AR_MARKER_AS_SAFE = False

SEMANTIC_RISK = {
    "paved-area": 0.10,
    "grass": 0.20,
    "dirt": 0.25,
    "gravel": 0.35,
    "ar-marker": 0.55,
    "vegetation": 0.75,
    "rocks": 0.85,
    "roof": 0.85,
    "water": 1.00,
    "pool": 1.00,
    "wall": 1.00,
    "window": 1.00,
    "door": 1.00,
    "fence": 1.00,
    "fence-pole": 1.00,
    "person": 1.00,
    "dog": 1.00,
    "car": 1.00,
    "bicycle": 1.00,
    "tree": 1.00,
    "bald-tree": 1.00,
    "obstacle": 1.00,
    "conflicting": 1.00,
    "unlabeled": 0.90,
}

SLOPE_PROXY_RISK = {
    "paved-area": 0.10,
    "grass": 0.25,
    "dirt": 0.30,
    "gravel": 0.45,
    "ar-marker": 0.50,
    "vegetation": 0.70,
    "rocks": 0.85,
    "roof": 0.90,
    "water": 1.00,
    "pool": 1.00,
    "wall": 1.00,
    "window": 1.00,
    "door": 1.00,
    "fence": 1.00,
    "fence-pole": 1.00,
    "person": 1.00,
    "dog": 1.00,
    "car": 1.00,
    "bicycle": 1.00,
    "tree": 1.00,
    "bald-tree": 1.00,
    "obstacle": 1.00,
    "conflicting": 1.00,
    "unlabeled": 0.90,
}

ROUGHNESS_PROXY_RISK = {
    "paved-area": 0.10,
    "grass": 0.25,
    "dirt": 0.35,
    "gravel": 0.55,
    "ar-marker": 0.50,
    "vegetation": 0.80,
    "rocks": 0.90,
    "roof": 0.75,
    "water": 1.00,
    "pool": 1.00,
    "wall": 1.00,
    "window": 1.00,
    "door": 1.00,
    "fence": 1.00,
    "fence-pole": 1.00,
    "person": 1.00,
    "dog": 1.00,
    "car": 1.00,
    "bicycle": 1.00,
    "tree": 1.00,
    "bald-tree": 1.00,
    "obstacle": 1.00,
    "conflicting": 1.00,
    "unlabeled": 0.90,
}

FINAL_RISK_WEIGHTS = {
    "semantic": 0.45,
    "obstacle_proximity": 0.25,
    "area_size": 0.15,
    "slope_proxy": 0.075,
    "roughness_proxy": 0.075,
}

CAR_PROB_THRESHOLD = 0.20
DANGER_PROB_THRESHOLD = 0.35
HAZARD_OVERRIDE_RISK = 0.95
OBSTACLE_DILATION_PX = 15
DRONE_FOOTPRINT_RADIUS_PX = 35.0
USE_CONFIDENCE_RISK = True
MIN_CONFIDENCE_SCORE = 0.50
USE_WATER_OVERRIDE = True
WATER_PROB_THRESHOLD = 0.04
USE_RGB_WATER_HEURISTIC = True
WATER_RGB_THRESHOLD = 0.40
WATER_MIN_AREA_PX = 300
MAX_ZONES_TO_LABEL = 20
MAX_ZONES_TO_DRAW_FOOTPRINT = 10
TOP_N_SAFE_ZONES = 5


@dataclass(frozen=True)
class RiskParameters:
    risk_threshold: float = 0.45
    min_area_px: int = 1500
    desired_area_px: int = 8000
    safe_distance_px: float = 40.0
    car_prob_threshold: float = CAR_PROB_THRESHOLD
    danger_prob_threshold: float = DANGER_PROB_THRESHOLD
    hazard_dilation_px: int = OBSTACLE_DILATION_PX
    hazard_override_risk: float = HAZARD_OVERRIDE_RISK
    allow_ar_marker_as_safe: bool = ALLOW_AR_MARKER_AS_SAFE
    footprint_radius_px: float = DRONE_FOOTPRINT_RADIUS_PX
    meters_per_pixel: float | None = None
    footprint_diameter_m: float | None = None
    use_confidence_risk: bool = USE_CONFIDENCE_RISK
    min_confidence_score: float = MIN_CONFIDENCE_SCORE
    use_water_override: bool = USE_WATER_OVERRIDE
    water_prob_threshold: float = WATER_PROB_THRESHOLD
    use_rgb_water_heuristic: bool = USE_RGB_WATER_HEURISTIC
    water_rgb_threshold: float = WATER_RGB_THRESHOLD
    water_min_area_px: int = WATER_MIN_AREA_PX

    @property
    def resolved_footprint_radius_px(self) -> float:
        if self.meters_per_pixel is not None:
            return (self.footprint_diameter_m / 2.0) / self.meters_per_pixel
        return self.footprint_radius_px

    def validate(self) -> None:
        for name, value in (
            ("risk threshold", self.risk_threshold),
            ("car probability threshold", self.car_prob_threshold),
            ("danger probability threshold", self.danger_prob_threshold),
            ("hazard override risk", self.hazard_override_risk),
            ("minimum confidence score", self.min_confidence_score),
            ("water probability threshold", self.water_prob_threshold),
            ("water RGB threshold", self.water_rgb_threshold),
        ):
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be between 0 and 1")
        if self.min_area_px <= 0:
            raise ValueError("minimum area must be positive")
        if self.desired_area_px <= 0:
            raise ValueError("desired area must be positive")
        if self.desired_area_px < self.min_area_px:
            raise ValueError("desired area must be at least the minimum area")
        if self.safe_distance_px <= 0:
            raise ValueError("obstacle safe distance must be positive")
        if self.hazard_dilation_px < 0:
            raise ValueError("hazard dilation must not be negative")
        if self.footprint_radius_px <= 0:
            raise ValueError("drone footprint radius must be positive")
        if self.water_min_area_px <= 0:
            raise ValueError("minimum RGB water area must be positive")
        scale_values = (self.meters_per_pixel, self.footprint_diameter_m)
        if (scale_values[0] is None) != (scale_values[1] is None):
            raise ValueError(
                "meters per pixel and footprint diameter in meters must be provided together"
            )
        if self.meters_per_pixel is not None:
            if self.meters_per_pixel <= 0:
                raise ValueError("meters per pixel must be positive")
            if self.footprint_diameter_m <= 0:
                raise ValueError("footprint diameter in meters must be positive")
        if self.resolved_footprint_radius_px <= 0:
            raise ValueError("resolved drone footprint radius must be positive")
