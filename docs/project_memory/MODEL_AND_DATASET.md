# Model and Dataset Contract

## Model summary

| Field | Confirmed value |
|---|---|
| Architecture | SegFormer-B0 |
| Task | Semantic segmentation |
| Runtime model path | `model/` by default; configurable with `--model_dir` |
| Preserved original model path | `models/` |
| Classes | 24 |
| Parameters | 3,720,312, as verified in `VERSION.md` |
| Processor input size | 384×384, confirmed by `preprocessor_config.json` and `VERSION.md` |
| Segmentation head | 24 channels |
| Runtime policy | Local/offline Hugging Face loading only |

The repository does not name a specific dataset in `README.md`, `VERSION.md`, or the inspected model configuration. Documentation therefore refers only to the locally trained model and its confirmed trained-dataset vocabulary/palette; do not infer a dataset name without evidence.

## Required model files

Both `model/` and `models/` contain:

- `model.safetensors`
- `config.json`
- `preprocessor_config.json`
- `label2id.json`
- `id2label.json`

`models/` preserves the original files. `model/` is the default runtime copy. `VERSION.md` records the two sets as checksum-identical after verification. Do not move or replace them without explicit instruction.

## Strict validation

`src/model_loader.py` requires all five files, verifies that `id2label.json` and `label2id.json` are exact inverses, requires contiguous IDs `0` through `23`, and compares the complete ordered names with `src/risk_config.py`. It also checks that the model output label count matches the mappings. Missing, reordered, renamed, or unexpected labels cause loading to fail.

## Inference contract

Input is one aerial RGB image. Inference produces a source-resolution semantic mask and class probabilities, then derives risk maps, hazard masks, confidence/uncertainty/margin maps, footprint-aware safe-zone ranking, CSV/JSON reports, and plain/labeled visual outputs.

## Confirmed class vocabulary and RGB palette

| ID | Class name    | RGB               |
| -: | ------------- | ----------------- |
|  0 | `unlabeled`   | `(0, 0, 0)`       |
|  1 | `paved-area`  | `(128, 64, 128)`  |
|  2 | `dirt`        | `(130, 76, 0)`    |
|  3 | `grass`       | `(0, 102, 0)`     |
|  4 | `gravel`      | `(112, 103, 87)`  |
|  5 | `water`       | `(28, 42, 168)`   |
|  6 | `rocks`       | `(48, 41, 30)`    |
|  7 | `pool`        | `(0, 50, 89)`     |
|  8 | `vegetation`  | `(107, 142, 35)`  |
|  9 | `roof`        | `(70, 70, 70)`    |
| 10 | `wall`        | `(102, 102, 156)` |
| 11 | `window`      | `(254, 228, 12)`  |
| 12 | `door`        | `(254, 148, 12)`  |
| 13 | `fence`       | `(190, 153, 153)` |
| 14 | `fence-pole`  | `(153, 153, 153)` |
| 15 | `person`      | `(255, 22, 96)`   |
| 16 | `dog`         | `(102, 51, 0)`    |
| 17 | `car`         | `(9, 143, 150)`   |
| 18 | `bicycle`     | `(119, 11, 32)`   |
| 19 | `tree`        | `(51, 51, 0)`     |
| 20 | `bald-tree`   | `(190, 250, 190)` |
| 21 | `ar-marker`   | `(112, 150, 146)` |
| 22 | `obstacle`    | `(2, 135, 115)`   |
| 23 | `conflicting` | `(255, 0, 0)`     |

Known safe candidate classes are `paved-area`, `grass`, `dirt`, and `gravel`.

Main danger-related classes are `water`, `pool`, `person`, `dog`, `car`, `bicycle`, `tree`, `bald-tree`, `vegetation`, `rocks`, `roof`, `wall`, `window`, `door`, `fence`, `fence-pole`, `obstacle`, and `conflicting`.

`ar-marker` has semantic risk and is excluded from safe candidates unless explicitly enabled.

## Alignment rule

The class palette must remain aligned with the trained model’s `id2label.json`, `label2id.json`, and `src/risk_config.py`. Risk configuration, semantic-mask visualization, hazard interpretation, and landing-zone eligibility all depend on this exact order and naming.

Codex must not reorder, rename, or recolor these classes unless the user explicitly asks and the model files, risk configuration, visualization palette, tests, and documentation are updated consistently.

## Hazard limitations

Hazard interpretation has been probability-aware since `0.2.0`. Water handling also includes the separate temporary water safety override introduced in `0.3.3`; it does not change the model’s raw semantic mask and is not a trained water detector.

If the model gives almost zero probability for a hazard such as `car` or `water`, the system cannot reliably detect it without representative new data, retraining, or a separate detector.
