# Sample-28 Result Summary

## Selected demonstration

| Field | Reported value |
|---|---|
| Selected sample folder | `outputs/Sample-28/` |
| Source input filename | `525.jpg` |
| Analysis timestamp | `2026-06-20T15:39:11.835219+00:00` |
| Inference mode | Tiled, 512 px tiles with 96 px overlap |
| Device recorded | CPU |
| Number of valid zones | 1 |
| Rank-1 zone ID | `Zone-01` |
| Rank-1 class | `paved-area` |
| Risk category | `Very Safe` |
| Score | `0.7878377423406805` (approximately `0.788`) |
| Mean risk | `0.13145259022712708` (approximately `0.131`) |
| Mean suitability | `0.8685476779937744` |
| Center pixel | `(639, 502)` |
| Footprint radius | `300.0 px` |
| Maximum safe/inscribed radius | `374.7972717285156 px` (approximately `374.8 px`) |
| Confidence score | `0.9040105938911438` (approximately `0.904`) |
| Uncertainty score | `0.14331722259521484` |
| Probability margin score | `0.8740330338478088` |
| Hazard distance | `374.8973083496094 px` |

## Interpretation

Sample-28 contains one region that satisfies the configured semantic class, risk, hazard-exclusion, minimum-area, confidence, and circular-footprint requirements. Because valid zones are deterministically sorted, this region is `Zone-01` and is the single source for the final landing visualization and `landing_target.json`.

The requested 300 px radius fits within the region’s approximately 374.8 px maximum inscribed safe radius. The selected target is an image coordinate only. No meters-per-pixel scale was supplied, so no physical or georeferenced target is available.

## Evidence sources

- `reports/ranked_safe_zones.csv`
- `reports/ranked_safe_zones.json`
- `reports/landing_target.json`
- `reports/run_metadata.json`

## Reporting caution

These are image-specific demonstration results from one saved run. They are not general model accuracy, safety, reliability, or operational-performance measurements and must not be presented as such.
