# 002_rename_watcher: Feature Documentation

## Feature Overview

This package implements a robust, intelligent system for recursively monitoring directories for file and directory renames and moves. The watcher system must:
- Detect and distinguish between file/directory renames, moves, creations, and deletions in real time.
- Accurately determine the from/to relationship for renames and moves, even when events are received out of order or with delays.
- Operate recursively on all subdirectories.
- Be implemented as a standalone package (like `pocketbase_backend`), suitable for use in a Python monorepo managed by `uv` workspaces.

## Requirements
- **Cross-platform:** Must work on Linux, macOS, and Windows.
- **Real-time detection:** Must identify renames/moves as they happen, not just after-the-fact.
- **Robustness:** Must handle edge cases such as rapid sequences of events, dotfiles, and files moved across directories.
- **Configurability:** Timeout and polling intervals should be configurable for tuning performance and accuracy.
- **Testability:** All logic must be covered by unit tests (expected, edge, and failure cases).
- **Validation:** Must pass all validation gates (tests, lint, type checks) after every change.

## Out of Scope
- Handling of files outside the monitored root directory.
- Handling of files/folders that start with a dot (e.g., `.git`, `.env`).

- Monitoring of network filesystems with unreliable event delivery.

## Error Handling & Edge Cases

## Test Requirements & Validation Gates

## Environment, Setup & Dependency Notes

- **Environment Variables:** All configuration (timeouts, polling intervals, ignore patterns) must be loaded via `python_dotenv` and `load_env()`. Provide a `.env.example` file.
- **Dependency Management:** Use `uv` for all dependency management and script running. All dependencies must be declared in `pyproject.toml`.
- **Workspace Structure:** The package must be structured as a standalone module under `packages/rename_watcher/` with its own `pyproject.toml`.
- **Setup Instructions:**
  - Document installation and setup in the main `README.md`.
  - Include instructions for running tests, linting, and type checks.
- **Onboarding:** Ensure all setup steps are minimal, clear, and reproducible for new contributors.

---

## References & Research Sources

- [Python Watchdog documentation](https://python-watchdog.readthedocs.io/en/stable/)
- [uv workspace documentation](https://docs.astral.sh/uv/concepts/projects/workspaces/#workspace-sources)
- [mnaoumov/obsidian-external-rename-handler (GitHub)](https://github.com/mnaoumov/obsidian-external-rename-handler)
- [Obsidian Dev Utils](https://github.com/mnaoumov/obsidian-dev-utils)

---

- **Unit Tests:** Every function, class, and public API must have Pytest unit tests.
- **Dotfiles:** Ignore files/folders starting with a dot by default, but allow this to be configurable.
- **Missing Events:** If an expected event (e.g., move/rename) is not received, fall back to periodic polling to reconcile state.

---


---
## Next Steps
- Architecture and design plan
- Error handling and edge case documentation
- Test and validation requirements
- Environment and setup notes
- References
