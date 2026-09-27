# Project Memory for Codex

This folder is the first project-memory location for future Codex sessions working on **Safe Landing Zone Detection for Drone Landing**. Its short, structured files describe the current release and route readers to deeper evidence without requiring a complete repository scan.

Read only the files relevant to the current instruction. Do not re-analyze the whole repository before checking these memory documents. Inspect working source only to confirm details that are missing, task-sensitive, or potentially stale.

`VERSION.md` remains the detailed historical source of truth for completed work, release verification, limitations, and future-version plans. Do not copy its full history into these files.

## Future Codex Workflow

Step 1: Read CODEX_START_HERE.md  
Step 2: Read docs/project_memory/README_FOR_CODEX.md  
Step 3: Read only the project memory files relevant to the user’s new instruction  
Step 4: Inspect source files only when needed  
Step 5: Complete the requested task  
Step 6: Update project memory documents  
Step 7: Summarize changed files and next steps  

## Memory file guide

| File | Purpose |
|---|---|
| `PROJECT_OVERVIEW.md` | Stable description of the problem, pipeline, outputs, and research scope. |
| `CURRENT_STATE.md` | Snapshot of version `0.3.4` behavior, implemented capabilities, and limitations. |
| `PROJECT_STRUCTURE.md` | Repository map and responsibility of important files and folders. |
| `VERSION_SUMMARY.md` | Compact release-by-release index pointing back to `VERSION.md`. |
| `FEATURE_HISTORY.md` | Evolution of features grouped by system area. |
| `OUTPUT_ARTIFACTS.md` | Meaning and generation conditions of saved files. |
| `MODEL_AND_DATASET.md` | Model layout, validation contract, class vocabulary, and RGB palette. |
| `SETUP_AND_COMMANDS.md` | Installation, Streamlit/CLI commands, confirmed options, and troubleshooting. |
| `DEVELOPMENT_LOG.md` | Concise chronological record of meaningful work. |
| `DECISIONS.md` | Durable technical decisions and constraints. |
| `TODO_NEXT_STEPS.md` | Prioritized development and research checklists. |
| `CODING_RULES.md` | Rules future Codex sessions must preserve while editing. |
| `CHANGELOG.md` | Changes to the project-memory documentation system. |

## Maintenance rules

- Treat `VERSION.md` as the detailed history; keep these files concise and link back to it.
- After meaningful changes, update `CURRENT_STATE.md`, `DEVELOPMENT_LOG.md`, `TODO_NEXT_STEPS.md`, and `CHANGELOG.md`.
- Update other memory files when their subject changes, especially commands, outputs, structure, model contracts, or technical decisions.
- Update `VERSION.md` only when the work is a meaningful version-level change.
- Preserve verified behavior unless the user explicitly requests a change.
