# Coding Rules for Future Codex Work

## Before editing

- Read `CODEX_START_HERE.md` first.
- Read only the relevant files under `docs/project_memory/` before inspecting code.
- Do not re-analyze the whole repository before checking project memory.
- Consult `VERSION.md` when detailed release history, verification, or limitations matter.
- Inspect source files when needed to confirm that memory remains accurate.

## Preserve behavior and assets

- Do not break existing verified features.
- Preserve current CLI and Streamlit behavior unless the user requests a change.
- Preserve the fixed 24-class vocabulary and RGB palette.
- Do not reorder, rename, or recolor classes unless model label maps, risk configuration, visualization palette, tests, and documentation are updated consistently under explicit user instruction.
- Keep model paths configurable and avoid hardcoded absolute paths unless genuinely necessary.
- Do not move model files.
- Do not delete existing outputs or sample images unless explicitly asked.
- Keep CPU fallback working and retain GPU/CUDA compatibility.

## Architecture and simulation

- Use modular Python and keep responsibilities separated across the existing modules.
- Keep the Streamlit project and future ROS2/Gazebo workspace separate.
- Do not reinstall ROS or Gazebo unless explicitly asked.
- For future simulation tasks, use the currently installed ROS/Gazebo versions unless the user instructs otherwise.
- Do not treat pixel/image-plane targets as GPS or UAV-planner coordinates without calibration and an explicit coordinate transform.

## Documentation and handoff

- Update `VERSION.md` only for meaningful version-level changes.
- After every meaningful change, update `CURRENT_STATE.md`, `DEVELOPMENT_LOG.md`, `TODO_NEXT_STEPS.md`, and `CHANGELOG.md` as applicable.
- Update specialized memory files whenever their facts change.
- Keep memory summaries compact and point to `VERSION.md` rather than duplicating its full contents.
- Summarize changed files, verification, assumptions, and next steps after completing a task.
