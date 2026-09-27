# LaTeX / IEEE Asset Notes

## Suggested paper workspace

When a LaTeX manuscript is created later, keep it inside `research_packet/paper/` and reference the copied packet assets rather than the original output folder:

```text
research_packet/
├── figures/
├── reports/
└── paper/
    ├── main.tex              # future
    ├── references.bib        # future, verified sources only
    └── [current planning files]
```

## Document setup

For an IEEE-style draft, use the official template required by the target venue. A typical starting point is:

```latex
\documentclass[conference]{IEEEtran}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{amsmath}
\graphicspath{{../figures/}}
```

Add packages only when the actual LaTeX environment and venue instructions require them. For subfigures, follow the venue’s IEEE template guidance; do not assume an incompatible caption package.

## Figure inclusion

Single-column example:

```latex
\begin{figure}[t]
  \centering
  \includegraphics[width=\columnwidth]{best_landing_zone_labeled.png}
  \caption{Final Rank-1 landing target for the Sample-28 demonstration.}
  \label{fig:best-zone}
\end{figure}
```

Two-column example:

```latex
\begin{figure*}[t]
  \centering
  \includegraphics[width=0.98\textwidth]{all_safe_zones_labeled.png}
  \caption{All valid ranked safe landing zones for the Sample-28 demonstration.}
  \label{fig:all-zones}
\end{figure*}
```

The supplied PNGs are high resolution. Keep aspect ratios intact and inspect the compiled PDF at 100% to ensure local legends and labels remain readable. If a figure is illegible at one-column width, use a two-column figure or split it into focused panels; do not erase analytical context.

## Suggested asset mapping

- `input_image.png`: source scene.
- `semantic_mask_labeled.png`: 24-class prediction.
- `overlay_labeled.png`: semantic-to-scene correspondence.
- `risk_map_labeled.png`: final landing-risk interpretation.
- `water_detection_overlay_labeled.png`: temporary water evidence.
- `footprint_valid_centers_labeled.png`: distance-transform footprint result.
- `all_safe_zones_labeled.png`: all valid ranked contours.
- `best_landing_zone_labeled.png`: final Rank-1 result.
- Confidence, uncertainty, and margin maps: optional diagnostic composite.

## Tables and reports

The copied CSV/JSON files are evidence sources, not publication-ready tables. For the paper:

- Transcribe only the required fields and preserve numeric meaning.
- Round display values consistently while retaining exact source values in the packet.
- State units such as pixels explicitly.
- Do not treat class coverage as accuracy.
- Do not omit the “not GPS” coordinate note.
- If report parsing is automated later, document the script and verify its output against the source files.

## Equations

Typeset the base risk and region score with `amsmath`. Define every symbol and distinguish semantic proxy terms from physical measurements. State the confidence blend and hard hazard-floor ordering in prose or an additional equation if space allows.

## Citations

- Current drafts contain `[REF]` placeholders.
- Replace a placeholder only after reading and verifying a real source.
- Use the official bibliography style required by the venue.
- Do not invent titles, authors, venues, years, DOIs, or URLs.
- Cite primary model, segmentation, UAV landing, risk, and uncertainty literature where claims require support.

## IEEE presentation cautions

- Keep the abstract free of citations unless the venue explicitly permits them.
- Avoid oversized headings or poster-style prose in the manuscript.
- Use numbered sections and venue-compliant figure/table captions.
- Describe Sample-28 as an experimental demonstration, not a validation dataset.
- Do not claim accuracy, robustness, real-time performance, or operational safety without corresponding measurements.
- Preserve the research-demo, RGB-only, heuristic-water, and pixel-coordinate limitations.

## Future production assets

Create a vector pipeline diagram later if needed, using only the confirmed stages in `PAPER_OUTLINE.md`. Do not redraw or recolor the scientific raster outputs. If publication requires grayscale legibility, test a proof and add text/pattern explanations rather than modifying the source figures without review.
