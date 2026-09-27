# Project Overview

## Problem statement

The project explores how semantic understanding of an aerial image can help identify and rank visually plausible drone landing areas. A landing area should be a configured safe surface, have sufficiently low semantic risk, avoid modeled hazards, contain enough connected area, and fit a circular drone footprint at a confident location.

## Research/demo purpose

**Safe Landing Zone Detection for Drone Landing** (`safe_landing_zone_demo`) is an offline research demonstration. It is designed for repeatable analysis, visualization, debugging, and presentation of semantic landing-zone decisions—not for certifying or directly controlling a real aircraft.

## Input and output

The current input is one aerial RGB image. The system returns semantic masks and overlays, landing-risk maps, confidence and uncertainty maps, hazard diagnostics, landing-zone visualizations, CSV/JSON reports, and a deterministic ranked list of valid safe zones.

Reported landing centers and bounding boxes are image-pixel/image-plane coordinates. Optional meter values are local image-plane conversions when a scale is supplied; they are not GPS coordinates or real UAV-planner targets.

## Main pipeline

1. Load the local SegFormer-B0 processor, model, and strict 24-class label maps.
2. Validate and normalize one aerial image to RGB.
3. Run full-image or overlapping tiled semantic inference and recover source-resolution probabilities.
4. Build the semantic mask, overlay, confidence, uncertainty, and probability-aware hazard evidence.
5. Combine semantic, proximity, area, slope-proxy, and roughness-proxy risks; apply confidence blending and hard hazard enforcement.
6. Form low-risk, non-hazard safe surfaces and test whether the requested circular footprint fits.
7. Reject invalid regions, rank every valid region deterministically, and use `Zone-01` as the best target.
8. Save visual outputs, reports, diagnostics, and run metadata in a new `Sample-XX` directory.

## Current capability

Version `0.3.4` can run through Streamlit or the CLI using a locally trained SegFormer-B0. It supports tiled inference, probability-aware hazards, a temporary water safety override, footprint-aware landing centers, confidence-aware risk, labeled presentation graphics, sequential run folders, complete valid-zone ranking, and CSV/JSON export.

## Safety scope

This is not certified autonomous flight software. RGB segmentation cannot measure physical slope, roughness, elevation, load-bearing capacity, wind, hidden obstacles, vehicle dynamics, or real clearance. Results also inherit model error and probability-calibration limits. The output is appropriate for research demonstrations and visualization, not a flight-safety guarantee.

## Future ROS2/Gazebo relationship

ROS2 and Gazebo integration is planned as a separate workspace and later system layer. A future simulation may consume a validated landing target after camera calibration, georeferencing, coordinate conversion, and planner integration are designed. The current Streamlit project should remain separate from that simulation workspace unless the user explicitly instructs otherwise.
