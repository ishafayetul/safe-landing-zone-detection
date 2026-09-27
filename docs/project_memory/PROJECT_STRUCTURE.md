# Project Structure

The following tree reflects the repository inspected on 2026-06-22. Generated caches and editor metadata are omitted.

```text
RMTW PR/
├── app.py
├── run_inference.py
├── README.md
├── VERSION.md
├── CODEX_START_HERE.md
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── model_loader.py
│   ├── inference.py
│   ├── risk_config.py
│   ├── risk_map.py
│   ├── water_detection.py
│   ├── landing_zone.py
│   ├── visualization.py
│   ├── output.py
│   └── utils.py
├── model/
│   ├── model.safetensors
│   ├── config.json
│   ├── preprocessor_config.json
│   ├── label2id.json
│   └── id2label.json
├── models/
│   └── [the same five original model files]
├── sample_images/
│   └── [aerial JPEG samples and .gitkeep]
├── outputs/
│   ├── .gitkeep
│   └── Sample-XX/
├── poster_assets/
│   ├── poster_generation_description.md
│   └── poster_image_prompt.txt
└── docs/project_memory/
    └── [compact Codex project-memory documents]
```

## Important paths

| Path | Responsibility |
|---|---|
| `app.py` | Streamlit interface, controls, analysis action, result gallery, diagnostics, tables, and downloads. |
| `run_inference.py` | CLI argument parsing and one-image analysis orchestration. |
| `src/model_loader.py` | Required-file checks, strict label-map validation, offline Hugging Face loading, and CPU/CUDA device selection. |
| `src/inference.py` | Full/tiled model inference and end-to-end analysis-result assembly. |
| `src/risk_config.py` | Canonical 24-class order/palette, class groups, risk tables, defaults, and parameter validation. |
| `src/risk_map.py` | Risk factors, confidence/uncertainty, probability-aware hazards, dilation, and hard risk override. |
| `src/water_detection.py` | Temporary RGB water-heuristic analysis used by the separated safety override. |
| `src/landing_zone.py` | Valid-surface components, footprint fit, rejection reasons, geometry, scoring, deterministic ranking, and best target. |
| `src/visualization.py` | Semantic, risk, landing-zone, ranked-zone, water, debug, and labeled rendering. |
| `src/output.py` | Sequential sample-folder allocation and PNG/CSV/JSON/metadata saving. |
| `src/utils.py` | Image loading/validation and shared utility behavior. |
| `model/` | Default runtime model directory; contains all five required local model files. Do not move these files. |
| `models/` | Preserved original model files; `VERSION.md` reports them checksum-identical to `model/`. |
| `sample_images/` | Local aerial test images. No file named `test.jpg` was present during this inspection, so command examples require adding one or choosing an existing filename. |
| `outputs/` | Generated sequential run directories. Existing samples must not be deleted or overwritten without explicit instruction. |
| `poster_assets/` | Existing poster-generation notes and image prompt. |
| `requirements.txt` | Python dependencies. |
| `README.md` | User-facing overview, setup, behavior, outputs, and limitations. |
| `VERSION.md` | Detailed source of truth for release history, verification, outputs, limitations, and plans. |
| `CODEX_START_HERE.md` | Short entry point for future Codex sessions. |
| `docs/project_memory/` | Lightweight project memory intended to prevent unnecessary full-repository re-analysis. |
