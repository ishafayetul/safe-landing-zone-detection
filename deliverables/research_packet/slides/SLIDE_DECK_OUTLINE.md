# Slide Deck Outline

Recommended length: 12 slides, approximately 10–15 minutes.

| Slide | Title | Purpose | Primary evidence |
|---:|---|---|---|
| 1 | Title | Establish project identity and scope. | `input_image.png` or `best_landing_zone_labeled.png` background crop |
| 2 | Problem Statement | Define the safe-landing challenge and RGB-only constraint. | `input_image.png` |
| 3 | Research Motivation | Explain why semantic, risk, and ranked reasoning are useful. | Input/result side-by-side |
| 4 | System Overview | Summarize input, model, processing, and outputs. | `overlay_labeled.png` plus compact block diagram |
| 5 | Methodology Pipeline | Walk through the end-to-end decision flow. | Six-stage figure strip |
| 6 | Model and 24-Class Vocabulary | Describe SegFormer-B0 and class groups. | `semantic_mask_labeled.png` |
| 7 | Risk and Hazard Handling | Explain five-factor risk, probability-aware hazards, and water override. | `risk_map_labeled.png`, water inset |
| 8 | Footprint-Aware Landing Zone Selection | Explain distance transform, fit, rejection, and ranking. | `footprint_valid_centers_labeled.png` |
| 9 | Ranked Safe Zone Results | Present Sample-28 and Rank-1 evidence. | All/top/best zone figures |
| 10 | Limitations | State what the current system cannot claim or measure. | Small muted result figure; limitation icons |
| 11 | Future Work | Show development and research directions. | Roadmap graphic |
| 12 | Conclusion | Reinforce the contribution and research-demo scope. | `best_landing_zone_labeled.png` |

## Deck rules

- Keep Sample-28 numbers labeled as one image-specific demonstration.
- Do not present accuracy, precision, recall, IoU, or safety rates; none are established by this packet.
- Preserve analytical figure legends and colors.
- State that output coordinates are pixels, not GPS.
- Use citation placeholders only if literature claims are later added; do not invent sources.
