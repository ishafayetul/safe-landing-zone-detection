# Codex Start Here

Project: **Safe Landing Zone Detection for Drone Landing**  
Identifier: `safe_landing_zone_demo`  
Current version: `0.3.4`

This research demo analyzes one aerial RGB image with a locally trained SegFormer-B0 semantic segmentation model, builds safety and diagnostic maps, ranks valid footprint-aware landing regions, and reports image-pixel landing targets. It is research software, not certified autonomous-flight software.

`VERSION.md` is the detailed source of truth for completed work, verification, release history, outputs, limitations, and planned versions. The files under `docs/project_memory/` are compact working summaries; they should not duplicate the full version history.

## Reading order

1. `CODEX_START_HERE.md`
2. `docs/project_memory/README_FOR_CODEX.md`
3. `docs/project_memory/CURRENT_STATE.md`
4. `docs/project_memory/VERSION_SUMMARY.md`
5. `docs/project_memory/PROJECT_STRUCTURE.md`
6. `docs/project_memory/TODO_NEXT_STEPS.md`
7. `VERSION.md` only when detailed version history is needed

Future Codex sessions should read the memory files before scanning the full repository. Inspect source files only when the requested task requires confirmation that the summaries do not provide.

After every meaningful change, update the relevant project-memory files. Keep `CURRENT_STATE.md`, `DEVELOPMENT_LOG.md`, `TODO_NEXT_STEPS.md`, and `CHANGELOG.md` synchronized, and update `VERSION.md` when the change is version-level.
