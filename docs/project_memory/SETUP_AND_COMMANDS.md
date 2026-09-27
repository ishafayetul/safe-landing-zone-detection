# Setup and Commands

## Install dependencies

```bash
pip install -r requirements.txt
```

Python 3.10 or newer is recommended by the root README. Use a virtual environment when appropriate. Do not install packages merely to inspect or document the repository.

## Run Streamlit

```bash
streamlit run app.py
```

Upload one RGB image, configure the analysis, then use **Run analysis and save outputs**. Uploading or changing presentation controls alone does not create another sample directory.

## Run CLI inference

```bash
python run_inference.py --image sample_images/test.jpg
```

`sample_images/test.jpg` is an example path and was not present during the 2026-06-22 repository inspection. Add that file or use an existing image path.

Full tiled debug run:

```bash
python run_inference.py \
  --image sample_images/test.jpg \
  --model_dir model \
  --output_dir outputs \
  --tiled \
  --save_debug
```

## Confirmed CLI options

The following names are defined in `run_inference.py`. Most underscore-style multiword options also accept hyphenated aliases.

| Option | Current behavior/default |
|---|---|
| `--image` | Required path to one aerial RGB image. |
| `--model_dir` | Local model directory; default `model`. |
| `--output_dir` | Base for sequential folders; default `outputs`. |
| `--risk_threshold` | Final-risk candidate threshold; default `0.45`. |
| `--min_area_px` | Minimum candidate component area; default `1500`. |
| `--desired_area_px` | Desired area used in scoring/risk; default `8000`. |
| `--safe_distance_px` | Obstacle-proximity distance scale; default `40`. |
| `--overlay_opacity` | Semantic overlay opacity; default `0.45`. |
| `--tiled` / `--no-tiled` | Enable/disable overlapping tiled inference; enabled by default. |
| `--tile_size` | Tile side length; default `512`. |
| `--tile_overlap` | Tile overlap; default `96`. |
| `--car_prob_threshold` | Car probability hazard threshold; default `0.20`. |
| `--danger_prob_threshold` | Summed danger probability threshold; default `0.35`. |
| `--hazard_dilation_px` | Elliptical hazard dilation radius; default `15`. |
| `--hazard_override_risk` | Minimum effective-hazard risk; default `0.95`. |
| `--use_water_override` / `--no-use-water-override` | Toggle temporary water safety override; enabled by default. |
| `--water_prob_threshold` | Water probability override threshold; default `0.04`. |
| `--use_rgb_water_heuristic` / `--no-use-rgb-water-heuristic` | Toggle RGB water cues; enabled by default. |
| `--water_rgb_threshold` | RGB heuristic score threshold; default `0.40`. |
| `--water_min_area_px` | Minimum RGB-only water component; default `300`. |
| `--allow_ar_marker_as_safe` | Explicitly allow `ar-marker` as a safe candidate; off by default. |
| `--footprint_radius_px` | Circular drone footprint radius; default `35`. |
| `--meters_per_pixel` | Optional image scale; must be paired with footprint diameter. |
| `--footprint_diameter_m` | Optional physical footprint diameter; must be paired with image scale. |
| `--use_confidence_risk` / `--no-use-confidence-risk` | Toggle uncertainty blending; enabled by default. |
| `--save_debug` | Save probability, hazard, risk-stage, confidence, footprint, water, and coverage diagnostics. |
| `--save_labeled` | Explicitly enable labeled outputs; already enabled by default. |
| `--no_labeled` | Disable labeled image outputs. |
| `--top_n_zones` | Number of ranked zones in the top-zone view; default `5`. |
| `--max_zones_to_label` | Maximum zone labels on all-zone output; default `20`. |
| `--max_zones_to_draw_footprint` | Maximum footprint circles on all-zone output; default `10`. |
| `--device` | `auto`, `cpu`, or `cuda`; default `auto`. |

Examples of ranked display controls:

```bash
python run_inference.py \
  --image sample_images/test.jpg \
  --top_n_zones 5 \
  --max_zones_to_label 20 \
  --max_zones_to_draw_footprint 10
```

Optional scale-based footprint conversion:

```bash
python run_inference.py \
  --image sample_images/test.jpg \
  --meters_per_pixel 0.05 \
  --footprint_diameter_m 1.2
```

## Troubleshooting

- Device `auto` uses CUDA when available and otherwise falls back to CPU.
- If CUDA is requested explicitly but unavailable, select `--device cpu` or `--device auto`.
- Missing-model errors should be resolved by checking all five required files under `model/`; do not move model files casually.
- Large images may use tiled inference, which is enabled by default. Adjust tile settings only with enough memory awareness.
- Every successful save creates the next available `Sample-XX` directory under the configured output base.
- If an image produces no valid zone, the run should still save schema-valid reports and other visual outputs.
- Output landing centers are pixels/image-plane values, not GPS coordinates.
