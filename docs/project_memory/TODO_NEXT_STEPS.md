# TODO and Next Steps

These are planning items, not claims of current capability. Reconcile them with `VERSION.md` whenever priorities change.

## Short-term

- [ ] Keep project memory updated after meaningful changes.
- [ ] Verify documentation still matches source code whenever commands, paths, outputs, or behavior change.
- [ ] Add representative examples/screenshots to the root README if needed.
- [ ] Test the current CLI and Streamlit paths after any code change.
- [ ] Keep `VERSION.md` updated after meaningful feature/version changes.

## Medium-term

- [ ] Improve the validation dataset and automated testing coverage.
- [ ] Calibrate risk, hazard, footprint, confidence, and ranking thresholds against representative data.
- [ ] Improve water detection through retraining, better labeled data, or a separate detector.
- [ ] Add optional depth or elevation input.
- [ ] Add physical slope and surface-roughness estimation.
- [ ] Add camera calibration, scale, georeferencing, or coordinate-frame support.
- [ ] Add ROS2 and Gazebo integration as a separate workspace.

## Research/future

- [ ] Convert validated pixel targets into UAV-planner coordinates.
- [ ] Integrate RGB-D, depth maps, elevation maps, or point clouds.
- [ ] Compare alternative semantic segmentation models.
- [ ] Evaluate safe-zone ranking quantitatively with labeled ground truth and operational metrics.
- [ ] Create technical paper, poster, and experiment documentation.
