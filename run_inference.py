import argparse
import sys
from pathlib import Path

from src.inference import analyze_image
from src.model_loader import load_model_bundle
from src.output import create_next_sample_output_dir, save_analysis_outputs
from src.risk_config import (
    MAX_ZONES_TO_DRAW_FOOTPRINT,
    MAX_ZONES_TO_LABEL,
    TOP_N_SAFE_ZONES,
    RiskParameters,
)
from src.utils import load_image


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run RGB-only semantic safe-landing-zone detection."
    )
    parser.add_argument("--image", required=True, help="Path to one aerial RGB image")
    parser.add_argument(
        "--model_dir", "--model-dir", default="model", help="Local model directory"
    )
    parser.add_argument(
        "--output_dir",
        "--output-dir",
        default="outputs",
        help="Base output directory for sequential Sample-XX folders",
    )
    parser.add_argument("--risk_threshold", type=float, default=0.45)
    parser.add_argument("--min_area_px", type=int, default=1500)
    parser.add_argument("--desired_area_px", type=int, default=8000)
    parser.add_argument("--safe_distance_px", type=float, default=40.0)
    parser.add_argument("--overlay_opacity", type=float, default=0.45)
    parser.add_argument(
        "--tiled",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Use overlapping high-resolution tiles (default: enabled)",
    )
    parser.add_argument("--tile_size", "--tile-size", type=int, default=512)
    parser.add_argument("--tile_overlap", "--tile-overlap", type=int, default=96)
    parser.add_argument(
        "--car_prob_threshold", "--car-prob-threshold", type=float, default=0.20
    )
    parser.add_argument(
        "--danger_prob_threshold",
        "--danger-prob-threshold",
        type=float,
        default=0.35,
    )
    parser.add_argument(
        "--hazard_dilation_px", "--hazard-dilation-px", type=int, default=15
    )
    parser.add_argument(
        "--hazard_override_risk", "--hazard-override-risk", type=float, default=0.95
    )
    parser.add_argument(
        "--use_water_override",
        "--use-water-override",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Use temporary probability/RGB water safety overrides (default: enabled)",
    )
    parser.add_argument(
        "--water_prob_threshold",
        "--water-prob-threshold",
        type=float,
        default=0.04,
    )
    parser.add_argument(
        "--use_rgb_water_heuristic",
        "--use-rgb-water-heuristic",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Use conservative RGB water cues on otherwise safe classes",
    )
    parser.add_argument(
        "--water_rgb_threshold",
        "--water-rgb-threshold",
        type=float,
        default=0.40,
    )
    parser.add_argument(
        "--water_min_area_px",
        "--water-min-area-px",
        type=int,
        default=300,
    )
    parser.add_argument(
        "--allow_ar_marker_as_safe",
        "--allow-ar-marker-as-safe",
        action="store_true",
    )
    parser.add_argument(
        "--footprint_radius_px", "--footprint-radius-px", type=float, default=35.0
    )
    parser.add_argument(
        "--meters_per_pixel", "--meters-per-pixel", type=float, default=None
    )
    parser.add_argument(
        "--footprint_diameter_m", "--footprint-diameter-m", type=float, default=None
    )
    parser.add_argument(
        "--use_confidence_risk",
        "--use-confidence-risk",
        action=argparse.BooleanOptionalAction,
        default=True,
    )
    parser.add_argument("--save_debug", "--save-debug", action="store_true")
    parser.add_argument(
        "--top_n_zones",
        "--top-n-zones",
        type=int,
        default=TOP_N_SAFE_ZONES,
    )
    parser.add_argument(
        "--max_zones_to_label",
        "--max-zones-to-label",
        type=int,
        default=MAX_ZONES_TO_LABEL,
    )
    parser.add_argument(
        "--max_zones_to_draw_footprint",
        "--max-zones-to-draw-footprint",
        type=int,
        default=MAX_ZONES_TO_DRAW_FOOTPRINT,
    )
    labeled_group = parser.add_mutually_exclusive_group()
    labeled_group.add_argument(
        "--save_labeled",
        "--save-labeled",
        dest="save_labeled",
        action="store_true",
        default=True,
        help="Save presentation-friendly labeled images (default: enabled)",
    )
    labeled_group.add_argument(
        "--no_labeled",
        "--no-labeled",
        dest="save_labeled",
        action="store_false",
        help="Disable labeled image outputs",
    )
    parser.add_argument(
        "--device", choices=["auto", "cpu", "cuda"], default="auto"
    )
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        params = RiskParameters(
            risk_threshold=args.risk_threshold,
            min_area_px=args.min_area_px,
            desired_area_px=args.desired_area_px,
            safe_distance_px=args.safe_distance_px,
            car_prob_threshold=args.car_prob_threshold,
            danger_prob_threshold=args.danger_prob_threshold,
            hazard_dilation_px=args.hazard_dilation_px,
            hazard_override_risk=args.hazard_override_risk,
            use_water_override=args.use_water_override,
            water_prob_threshold=args.water_prob_threshold,
            use_rgb_water_heuristic=args.use_rgb_water_heuristic,
            water_rgb_threshold=args.water_rgb_threshold,
            water_min_area_px=args.water_min_area_px,
            allow_ar_marker_as_safe=args.allow_ar_marker_as_safe,
            footprint_radius_px=args.footprint_radius_px,
            meters_per_pixel=args.meters_per_pixel,
            footprint_diameter_m=args.footprint_diameter_m,
            use_confidence_risk=args.use_confidence_risk,
        )
        params.validate()
        if not 0.0 <= args.overlay_opacity <= 1.0:
            raise ValueError("overlay opacity must be between 0 and 1")

        image = load_image(args.image)
        bundle = load_model_bundle(args.model_dir, device=args.device)
        result = analyze_image(
            image,
            bundle,
            params,
            overlay_opacity=args.overlay_opacity,
            use_tiled_inference=args.tiled,
            tile_size=args.tile_size,
            tile_overlap=args.tile_overlap,
            top_n_zones=args.top_n_zones,
            max_zones_to_label=args.max_zones_to_label,
            max_zones_to_draw_footprint=args.max_zones_to_draw_footprint,
        )
        sample_output_dir = create_next_sample_output_dir(args.output_dir)
        save_analysis_outputs(
            result,
            sample_output_dir,
            save_debug=args.save_debug,
            save_labeled=args.save_labeled,
            run_metadata={
                "input_filename": Path(args.image).name,
                "input_path": str(Path(args.image)),
                "model_dir": args.model_dir,
                "device": str(bundle.device),
                "tiled_inference": args.tiled,
                "tile_size": args.tile_size,
                "tile_overlap": args.tile_overlap,
                "risk_threshold": args.risk_threshold,
                "minimum_area_px": args.min_area_px,
                "desired_area_px": args.desired_area_px,
                "safe_distance_px": args.safe_distance_px,
                "overlay_opacity": args.overlay_opacity,
                "footprint_radius_px": params.resolved_footprint_radius_px,
                "meters_per_pixel": args.meters_per_pixel,
                "footprint_diameter_m": args.footprint_diameter_m,
                "confidence_aware_risk": args.use_confidence_risk,
                "use_water_override": args.use_water_override,
                "water_prob_threshold": args.water_prob_threshold,
                "use_rgb_water_heuristic": args.use_rgb_water_heuristic,
                "water_rgb_threshold": args.water_rgb_threshold,
                "water_min_area_px": args.water_min_area_px,
                "save_debug": args.save_debug,
                "save_labeled": args.save_labeled,
                "top_n_zones": args.top_n_zones,
                "max_zones_to_label": args.max_zones_to_label,
                "max_zones_to_draw_footprint": args.max_zones_to_draw_footprint,
            },
        )

        print(f"Inference complete on device: {bundle.device}")
        car_row = result.class_coverage.loc[
            result.class_coverage["class_name"] == "car"
        ].iloc[0]
        print(
            f"Car diagnostics: max_probability={car_row['max_probability']:.3f}, "
            f"argmax_pixels={int(car_row['pixel_count'])}, "
            f"dilated_hazard_pixels={int(result.risks.dilated_hazard_mask.sum())}"
        )
        print(
            "Water safety diagnostics: "
            f"argmax_pixels={int(result.risks.model_predicted_water_mask.sum())}, "
            f"probability_override_pixels={int(result.risks.water_probability_override_mask.sum())}, "
            f"rgb_override_pixels={int(result.risks.water_rgb_override_mask.sum())}, "
            f"effective_water_pixels={int(result.risks.effective_water_mask.sum())}"
        )
        zone_count = len(result.ranked_regions)
        print(f"Found {zone_count} valid safe landing zones.")
        if result.best_region is None:
            print(result.decision_message)
        else:
            best = result.best_region
            print(
                f"Best zone: {best.zone_id} | Score: {best.score:.3f} | "
                f"Risk: {best.mean_risk:.3f} | Class: {best.dominant_class} | "
                f"Center: ({best.best_center_x}, {best.best_center_y})"
            )
        print(f"Results saved to: {sample_output_dir}")
        return 0
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
