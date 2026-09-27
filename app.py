import hashlib
import os
from io import BytesIO
from pathlib import Path

import streamlit as st

from src.inference import analyze_image
from src.model_loader import load_model_bundle
from src.output import create_next_sample_output_dir, save_analysis_outputs
from src.risk_config import (
    MAX_ZONES_TO_DRAW_FOOTPRINT,
    MAX_ZONES_TO_LABEL,
    TOP_N_SAFE_ZONES,
    RiskParameters,
)
from src.utils import dataframe_to_csv_bytes, load_uploaded_image
from src.visualization import (
    colorize_hazard_mask,
    colorize_probability,
    colorize_risk,
    colorize_valid_centers,
    colorize_water_override_sources,
)


PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_MODEL_DIR = PROJECT_ROOT / "model"
DEFAULT_OUTPUT_BASE_DIR = Path(
    os.environ.get("SAFE_LANDING_OUTPUT_DIR", PROJECT_ROOT / "outputs")
)


st.set_page_config(page_title="Safe Landing Zone Detection", layout="wide")
st.title("Safe Landing Zone Detection for Drone Landing")
st.caption("Version 0.3.4 — ranked safe landing zone list")


@st.cache_resource(show_spinner="Loading local SegFormer model...")
def cached_model(model_dir: str):
    return load_model_bundle(model_dir)


def candidate_display_frame(frame):
    """Add dependency-free status highlighting for Streamlit tables."""
    display = frame.copy()
    statuses = []
    for _, row in display.iterrows():
        if bool(row.get("selected", False)):
            statuses.append("✅ Best selected region")
        elif not bool(row.get("accepted", True)):
            reasons = str(row.get("rejection_reasons", "")).replace(";", ", ")
            statuses.append(f"⚠️ Rejected: {reasons}")
        else:
            statuses.append("✓ Accepted candidate")
    display.insert(0, "status", statuses)
    return display


def rejected_display_frame(frame):
    """Label rejection types without relying on Pandas Styler/Jinja2."""
    display = frame.copy()
    labels = []
    for reasons in display.get("rejection_reasons", []):
        reasons = str(reasons)
        if "hazard_overlap" in reasons:
            labels.append("🛑 Hazard overlap")
        elif "footprint_does_not_fit" in reasons:
            labels.append("⭕ Footprint does not fit")
        elif "too_small" in reasons:
            labels.append("📐 Area too small")
        elif "too_high_risk" in reasons:
            labels.append("🔴 Risk too high")
        elif "low_confidence" in reasons:
            labels.append("❓ Low confidence")
        else:
            labels.append("⚠️ Rejected")
    display.insert(0, "status", labels)
    return display


def preferred_saved_visual(
    output_dir,
    plain_filename,
    labeled_filename,
    prefer_labeled,
    fallback,
):
    """Choose a saved labeled image, with plain-file and array fallbacks."""
    filenames = (
        [labeled_filename, plain_filename]
        if prefer_labeled
        else [plain_filename]
    )
    for filename in filenames:
        candidate = Path(output_dir) / filename
        if candidate.is_file():
            return str(candidate)
    return fallback


with st.sidebar:
    st.header("Landing-risk controls")
    risk_threshold = st.slider("Risk threshold", 0.0, 1.0, 0.45, 0.01)
    min_area_px = st.number_input(
        "Minimum landing area (pixels)", min_value=1, value=1500, step=100
    )
    desired_area_px = st.number_input(
        "Desired landing area (pixels)", min_value=1, value=8000, step=500
    )
    safe_distance_px = st.number_input(
        "Obstacle safe distance (pixels)", min_value=1.0, value=40.0, step=5.0
    )
    overlay_opacity = st.slider("Overlay opacity", 0.0, 1.0, 0.45, 0.05)

    st.divider()
    st.subheader("High-resolution inference")
    use_tiled_inference = st.checkbox("Use tiled inference", value=True)
    tile_size = st.number_input(
        "Tile size", min_value=64, value=512, step=32, disabled=not use_tiled_inference
    )
    tile_overlap = st.number_input(
        "Tile overlap",
        min_value=0,
        value=96,
        step=16,
        disabled=not use_tiled_inference,
    )

    st.divider()
    st.subheader("Probability-aware hazards")
    car_prob_threshold = st.slider(
        "Car probability threshold", 0.0, 1.0, 0.20, 0.01
    )
    danger_prob_threshold = st.slider(
        "Danger probability threshold", 0.0, 1.0, 0.35, 0.01
    )
    hazard_dilation_px = st.number_input(
        "Hazard dilation pixels", min_value=0, value=15, step=1
    )
    hazard_override_risk = st.slider(
        "Hazard override risk", 0.0, 1.0, 0.95, 0.01
    )
    allow_ar_marker_as_safe = st.checkbox(
        "Allow ar-marker as safe surface", value=False
    )
    use_confidence_risk = st.checkbox("Use confidence-aware risk", value=True)

    st.divider()
    st.subheader("Temporary water safety override")
    use_water_override = st.checkbox("Use water safety override", value=True)
    water_prob_threshold = st.slider(
        "Water probability threshold",
        0.0,
        1.0,
        0.04,
        0.01,
        disabled=not use_water_override,
    )
    use_rgb_water_heuristic = st.checkbox(
        "Use RGB water heuristic",
        value=True,
        disabled=not use_water_override,
    )
    water_rgb_threshold = st.slider(
        "RGB water score threshold",
        0.0,
        1.0,
        0.40,
        0.01,
        disabled=not (use_water_override and use_rgb_water_heuristic),
    )
    water_min_area_px = st.number_input(
        "Minimum RGB water area (pixels)",
        min_value=1,
        value=300,
        step=50,
        disabled=not (use_water_override and use_rgb_water_heuristic),
    )

    st.divider()
    st.subheader("Landing footprint settings")
    footprint_radius_px = st.number_input(
        "Drone footprint radius in pixels", min_value=1.0, value=35.0, step=1.0
    )
    use_meter_conversion = st.checkbox(
        "Use meters-per-pixel conversion", value=False
    )
    meters_per_pixel = st.number_input(
        "Meters per pixel",
        min_value=0.0001,
        value=0.05,
        step=0.01,
        format="%.4f",
        disabled=not use_meter_conversion,
    )
    footprint_diameter_m = st.number_input(
        "Drone footprint diameter in meters",
        min_value=0.01,
        value=1.20,
        step=0.10,
        disabled=not use_meter_conversion,
    )

    st.divider()
    st.subheader("Ranked safe-zone display")
    show_all_safe_zones = st.checkbox("Show all safe zones", value=True)
    show_top_safe_zones_only = st.checkbox(
        "Show top safe zones only", value=False
    )
    top_n_zones = st.number_input(
        "Number of top safe zones to display",
        min_value=1,
        value=TOP_N_SAFE_ZONES,
        step=1,
    )
    max_zones_to_label = st.number_input(
        "Maximum zones to label",
        min_value=1,
        value=MAX_ZONES_TO_LABEL,
        step=1,
    )
    show_debug_maps = st.checkbox("Show debug maps", value=True)
    show_labeled_outputs = st.checkbox(
        "Show labeled visual outputs", value=True
    )
    st.caption(f"Local model directory: `{DEFAULT_MODEL_DIR.name}/`")

uploaded_file = st.file_uploader(
    "Upload one aerial RGB image", type=["jpg", "jpeg", "png"]
)

if uploaded_file is None:
    st.info("Upload a JPEG or PNG aerial image to run the analysis.")
    st.stop()

uploaded_bytes = uploaded_file.getvalue()
upload_key = hashlib.sha256(
    uploaded_file.name.encode("utf-8") + b"\0" + uploaded_bytes
).hexdigest()
run_analysis = st.button(
    "Run analysis and save outputs", type="primary", width="stretch"
)

if run_analysis:
    try:
        params = RiskParameters(
            risk_threshold=float(risk_threshold),
            min_area_px=int(min_area_px),
            desired_area_px=int(desired_area_px),
            safe_distance_px=float(safe_distance_px),
            car_prob_threshold=float(car_prob_threshold),
            danger_prob_threshold=float(danger_prob_threshold),
            hazard_dilation_px=int(hazard_dilation_px),
            hazard_override_risk=float(hazard_override_risk),
            use_water_override=bool(use_water_override),
            water_prob_threshold=float(water_prob_threshold),
            use_rgb_water_heuristic=bool(use_rgb_water_heuristic),
            water_rgb_threshold=float(water_rgb_threshold),
            water_min_area_px=int(water_min_area_px),
            allow_ar_marker_as_safe=bool(allow_ar_marker_as_safe),
            footprint_radius_px=float(footprint_radius_px),
            meters_per_pixel=(
                float(meters_per_pixel) if use_meter_conversion else None
            ),
            footprint_diameter_m=(
                float(footprint_diameter_m) if use_meter_conversion else None
            ),
            use_confidence_risk=bool(use_confidence_risk),
        )
        params.validate()
        image = load_uploaded_image(BytesIO(uploaded_bytes))
        bundle = cached_model(str(DEFAULT_MODEL_DIR))
        with st.spinner(f"Running semantic segmentation on {bundle.device}..."):
            result = analyze_image(
                image=image,
                bundle=bundle,
                params=params,
                overlay_opacity=float(overlay_opacity),
                use_tiled_inference=bool(use_tiled_inference),
                tile_size=int(tile_size),
                tile_overlap=int(tile_overlap),
                top_n_zones=int(top_n_zones),
                max_zones_to_label=int(max_zones_to_label),
                max_zones_to_draw_footprint=MAX_ZONES_TO_DRAW_FOOTPRINT,
            )
        sample_output_dir = create_next_sample_output_dir(DEFAULT_OUTPUT_BASE_DIR)
        save_analysis_outputs(
            result,
            sample_output_dir,
            save_debug=bool(show_debug_maps),
            save_labeled=True,
            run_metadata={
                "input_filename": uploaded_file.name,
                "source": "streamlit_upload",
                "model_dir": DEFAULT_MODEL_DIR.name,
                "device": str(bundle.device),
                "tiled_inference": bool(use_tiled_inference),
                "tile_size": int(tile_size),
                "tile_overlap": int(tile_overlap),
                "risk_threshold": float(risk_threshold),
                "minimum_area_px": int(min_area_px),
                "desired_area_px": int(desired_area_px),
                "safe_distance_px": float(safe_distance_px),
                "overlay_opacity": float(overlay_opacity),
                "footprint_radius_px": params.resolved_footprint_radius_px,
                "meters_per_pixel": params.meters_per_pixel,
                "footprint_diameter_m": params.footprint_diameter_m,
                "confidence_aware_risk": bool(use_confidence_risk),
                "use_water_override": bool(use_water_override),
                "water_prob_threshold": float(water_prob_threshold),
                "use_rgb_water_heuristic": bool(use_rgb_water_heuristic),
                "water_rgb_threshold": float(water_rgb_threshold),
                "water_min_area_px": int(water_min_area_px),
                "save_debug": bool(show_debug_maps),
                "save_labeled": True,
                "top_n_zones": int(top_n_zones),
                "max_zones_to_label": int(max_zones_to_label),
                "max_zones_to_draw_footprint": MAX_ZONES_TO_DRAW_FOOTPRINT,
            },
        )
        st.session_state["analysis_result"] = result
        st.session_state["analysis_upload_key"] = upload_key
        st.session_state["analysis_output_dir"] = str(sample_output_dir)
    except Exception as exc:
        st.error(f"Analysis failed: {exc}")
        st.stop()

if st.session_state.get("analysis_upload_key") != upload_key:
    st.info("Click **Run analysis and save outputs** to analyze this uploaded image.")
    st.stop()

result = st.session_state["analysis_result"]
saved_output_dir = Path(st.session_state["analysis_output_dir"])
try:
    displayed_output_dir = saved_output_dir.relative_to(PROJECT_ROOT)
except ValueError:
    displayed_output_dir = saved_output_dir
st.success(f"Results saved to: `{displayed_output_dir}`")
st.caption(
    "Displayed results come from the last completed run. Changing a widget does not "
    "create another sample folder until the run button is clicked again."
)

st.header("Output Gallery")
if show_labeled_outputs:
    st.caption(
        "Showing presentation-friendly labeled images when available, with automatic "
        "fallback to the corresponding plain output."
    )
else:
    st.caption("Showing the original plain image outputs.")

st.subheader("Input and best landing zone")
left, right = st.columns(2)
left.image(result.original_image, caption="Original image", width="stretch")
right.image(
    preferred_saved_visual(
        saved_output_dir,
        "best_landing_zone.png",
        "best_landing_zone_labeled.png",
        show_labeled_outputs,
        result.best_landing_zone,
    ),
    caption="Green = selected landing area; red = effective hazard area",
    width="stretch",
)

if result.best_region is None:
    st.warning(result.decision_message)
else:
    best = result.best_region
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Region score", f"{best.final_region_score:.3f}")
    m2.metric("Mean risk", f"{best.mean_risk:.3f}")
    m3.metric("Area", f"{best.area_px:,} px")
    m4.metric("Dominant class", best.dominant_semantic_class)

st.subheader("Landing decision summary")
if result.best_region is None:
    st.write("**Landing zone found:** No")
    st.write(result.decision_message)
    st.write(f"**Selected footprint radius:** {result.footprint_radius_px:.2f} px")
else:
    best = result.best_region
    summary_left, summary_right = st.columns(2)
    with summary_left:
        st.write("**Landing zone found:** Yes")
        st.write(
            f"**Best center pixel:** ({best.best_center_x}, {best.best_center_y})"
        )
        st.write(f"**Dominant class:** {best.dominant_class}")
        st.write(f"**Final score:** {best.score:.3f}")
        st.write(f"**Mean risk:** {best.mean_risk:.3f}")
    with summary_right:
        st.write(f"**Footprint radius:** {best.footprint_radius_px:.2f} px")
        st.write(
            f"**Max available safe radius:** {best.max_inscribed_radius_px:.2f} px"
        )
        st.write(f"**Confidence score:** {best.confidence_score:.3f}")
        st.write(f"**Uncertainty score:** {best.uncertainty_score:.3f}")
        if result.meters_per_pixel is not None:
            st.write(
                "**Local image-plane center:** "
                f"({best.best_center_x * result.meters_per_pixel:.3f}, "
                f"{best.best_center_y * result.meters_per_pixel:.3f}) m"
                )

st.header("Ranked Safe Landing Zones")
st.metric("Total valid safe zones found", len(result.ranked_regions))
if not result.ranked_regions:
    st.warning(
        "No valid safe landing zones found for the current risk threshold and "
        "footprint settings.\n\nTry increasing the risk threshold, reducing "
        "footprint radius, or using another image."
    )
else:
    best = result.ranked_regions[0]
    st.success(
        f"Best zone: {best.zone_id} | Score: {best.score:.3f} | "
        f"Risk: {best.mean_risk:.3f} ({best.risk_category}) | "
        f"Class: {best.dominant_class} | Center: "
        f"({best.best_center_x}, {best.best_center_y})"
    )

st.dataframe(result.ranked_safe_zones, width="stretch", hide_index=True)
download_left, download_right = st.columns(2)
download_left.download_button(
    "Download ranked safe-zone CSV",
    dataframe_to_csv_bytes(result.ranked_safe_zones),
    file_name="ranked_safe_zones.csv",
    mime="text/csv",
)
ranked_json_path = saved_output_dir / "ranked_safe_zones.json"
download_right.download_button(
    "Download ranked safe-zone JSON",
    ranked_json_path.read_bytes(),
    file_name="ranked_safe_zones.json",
    mime="application/json",
)

if show_all_safe_zones and not show_top_safe_zones_only:
    st.image(
        preferred_saved_visual(
            saved_output_dir,
            "all_safe_zones.png",
            "all_safe_zones_labeled.png",
            show_labeled_outputs,
            result.all_safe_zones,
        ),
        caption="Every valid safe landing zone, ranked and marked",
        width="stretch",
    )
st.image(
    preferred_saved_visual(
        saved_output_dir,
        "top_safe_zones.png",
        "top_safe_zones_labeled.png",
        show_labeled_outputs,
        result.top_safe_zones,
    ),
    caption=f"Top {result.top_n_zones} ranked safe landing zones",
    width="stretch",
)

st.subheader("Semantic segmentation")
left, right = st.columns(2)
left.image(
    preferred_saved_visual(
        saved_output_dir,
        "semantic_mask.png",
        "semantic_mask_labeled.png",
        show_labeled_outputs,
        result.semantic_mask,
    ),
    caption="Predicted semantic mask — exact trained-dataset palette",
    width="stretch",
)
right.image(
    preferred_saved_visual(
        saved_output_dir,
        "overlay.png",
        "overlay_labeled.png",
        show_labeled_outputs,
        result.overlay,
    ),
    caption="Segmentation overlay",
    width="stretch",
)

st.subheader("Temporary water safety override")
st.image(
    preferred_saved_visual(
        saved_output_dir,
        "water_detection_overlay.png",
        "water_detection_overlay_labeled.png",
        show_labeled_outputs,
        result.water_detection_overlay,
    ),
    caption=(
        "Blue shades show model water, weak-probability water, and RGB heuristic "
        "water evidence used by the safety pipeline"
    ),
    width="stretch",
)
water_1, water_2, water_3, water_4 = st.columns(4)
water_1.metric(
    "Model water pixels",
    f"{int(result.risks.model_predicted_water_mask.sum()):,}",
)
water_2.metric(
    "Probability override",
    f"{int(result.risks.water_probability_override_mask.sum()):,}",
)
water_3.metric(
    "RGB override",
    f"{int(result.risks.water_rgb_override_mask.sum()):,}",
)
water_4.metric(
    "Effective water pixels",
    f"{int(result.risks.effective_water_mask.sum()):,}",
)
st.caption(
    "Effective water pixels enter the hazard mask and cannot become landing candidates. "
    "This overlay does not alter the raw predicted semantic mask."
)

st.subheader("Safety landing risk")
st.image(
    preferred_saved_visual(
        saved_output_dir,
        "risk_map.png",
        "risk_map_labeled.png",
        show_labeled_outputs,
        result.risk_visualization,
    ),
    caption="Safety palette: green = lower risk, yellow/orange = medium, red = high",
    width="stretch",
)

st.subheader("Candidate regions")
st.caption(
    "Selected regions are marked in `selected`; rejected valid-surface regions list "
    "their footprint, area, or confidence reason in `rejection_reasons`."
)
st.dataframe(
    candidate_display_frame(result.candidates),
    width="stretch",
    hide_index=True,
)
st.download_button(
    "Download candidate CSV",
    dataframe_to_csv_bytes(result.candidates),
    file_name="candidates.csv",
    mime="text/csv",
)

with st.expander("Predicted class coverage"):
    st.dataframe(result.class_coverage, width="stretch", hide_index=True)

if show_debug_maps:
    with st.expander(
        "Debug: class probability and hazard detection", expanded=True
    ):
        car_row = result.class_coverage.loc[
            result.class_coverage["class_name"] == "car"
        ].iloc[0]
        d1, d2, d3, d4 = st.columns(4)
        d1.metric("Maximum car probability", f"{car_row['max_probability']:.4f}")
        d2.metric("Argmax car pixels", f"{int(car_row['pixel_count']):,}")
        d3.metric(
            "Hazard override pixels",
            f"{int(result.risks.raw_hazard_override_mask.sum()):,}",
        )
        d4.metric(
            "Dilated hazard pixels",
            f"{int(result.risks.dilated_hazard_mask.sum()):,}",
        )
        left, middle, right = st.columns(3)
        left.image(
            preferred_saved_visual(
                saved_output_dir,
                "car_probability_map.png",
                "car_probability_map_labeled.png",
                show_labeled_outputs,
                colorize_probability(result.risks.car_probability_map),
            ),
            caption="Car probability map",
            width="stretch",
        )
        middle.image(
            preferred_saved_visual(
                saved_output_dir,
                "danger_probability_map.png",
                "danger_probability_map_labeled.png",
                show_labeled_outputs,
                colorize_probability(result.risks.danger_probability_map),
            ),
            caption="Summed danger probability map",
            width="stretch",
        )
        right.image(
            preferred_saved_visual(
                saved_output_dir,
                "hazard_override_mask.png",
                "hazard_override_mask_labeled.png",
                show_labeled_outputs,
                colorize_hazard_mask(result.risks.dilated_hazard_mask),
            ),
            caption="Dilated hazard override mask",
            width="stretch",
        )
        c1, c2, c3, c4 = st.columns(4)
        c1.image(
            preferred_saved_visual(
                saved_output_dir,
                "confidence_map.png",
                "confidence_map_labeled.png",
                show_labeled_outputs,
                colorize_probability(result.risks.confidence_map),
            ),
            caption="Confidence map",
            width="stretch",
        )
        c2.image(
            preferred_saved_visual(
                saved_output_dir,
                "uncertainty_map.png",
                "uncertainty_map_labeled.png",
                show_labeled_outputs,
                colorize_probability(result.risks.uncertainty_map),
            ),
            caption="Normalized uncertainty map",
            width="stretch",
        )
        c3.image(
            preferred_saved_visual(
                saved_output_dir,
                "margin_map.png",
                "margin_map_labeled.png",
                show_labeled_outputs,
                colorize_probability(result.risks.margin_map),
            ),
            caption="Top-1 / top-2 probability margin",
            width="stretch",
        )
        c4.image(
            preferred_saved_visual(
                saved_output_dir,
                "footprint_valid_centers.png",
                "footprint_valid_centers_labeled.png",
                show_labeled_outputs,
                colorize_valid_centers(result.risks.footprint_valid_center_mask),
            ),
            caption="Footprint-valid centers",
            width="stretch",
        )
        st.dataframe(result.class_coverage, width="stretch", hide_index=True)

        water_probability_view, water_score_view, water_mask_view = st.columns(3)
        water_probability_view.image(
            preferred_saved_visual(
                saved_output_dir,
                "water_probability_map.png",
                "water_probability_map_labeled.png",
                show_labeled_outputs,
                colorize_probability(result.risks.water_probability_map),
            ),
            caption="Model water probability",
            width="stretch",
        )
        water_score_view.image(
            preferred_saved_visual(
                saved_output_dir,
                "water_heuristic_score_map.png",
                "water_heuristic_score_map_labeled.png",
                show_labeled_outputs,
                colorize_probability(result.risks.water_heuristic_score_map),
            ),
            caption="Hybrid RGB water heuristic score",
            width="stretch",
        )
        water_mask_view.image(
            preferred_saved_visual(
                saved_output_dir,
                "water_override_mask.png",
                "water_override_mask_labeled.png",
                show_labeled_outputs,
                colorize_water_override_sources(
                    result.risks.model_predicted_water_mask,
                    result.risks.water_probability_override_mask,
                    result.risks.water_rgb_override_mask,
                ),
            ),
            caption="Effective water override sources",
            width="stretch",
        )

        before, after = st.columns(2)
        before.image(
            preferred_saved_visual(
                saved_output_dir,
                "risk_map_before_override.png",
                "risk_map_before_override_labeled.png",
                show_labeled_outputs,
                colorize_risk(result.risks.risk_map_before_override),
            ),
            caption="Risk before hazard override",
            width="stretch",
        )
        after.image(
            preferred_saved_visual(
                saved_output_dir,
                "risk_map_after_override.png",
                "risk_map_after_override_labeled.png",
                show_labeled_outputs,
                result.risk_visualization,
            ),
            caption="Risk after hazard override",
            width="stretch",
        )

with st.expander("Debug: rejected landing regions", expanded=False):
    if result.rejected_regions.empty:
        st.success("No evaluated landing-surface regions were rejected.")
    else:
        reason_counts = (
            result.rejected_regions["rejection_reasons"]
            .str.split(";")
            .explode()
            .value_counts()
            .rename_axis("reason")
            .reset_index(name="region_count")
        )
        st.write("Rejection summary")
        st.dataframe(reason_counts, width="stretch", hide_index=True)
        st.dataframe(
            rejected_display_frame(result.rejected_regions),
            width="stretch",
            hide_index=True,
        )
