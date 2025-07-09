---
name: "007_full_wire_up - PRD (Agent Autonomy & Validation)"
---

## Purpose
Wire up all major modules in the blendman monorepo to enable a full workflow: file/directory watching, event correlation, logging to the database, and robust CLI integration. Ensure all components are connected, tested, and validated with clear documentation and error handling.

## Core Principles
1. **Agent Autonomy**: All integration and validation steps must be automated and self-correcting.
2. **Context Awareness**: Use all provided documentation, code, and diagrams. Never assume missing context.
3. **Validation Loops**: All code must pass lint, type, and test gates. Iterate until green.
4. **Explicitness**: Document all non-obvious design and error handling decisions.
5. **Global rules**: Follow all rules in CLAUDE.md (if present).

## Goal (Agent Mission & Priorities)
- Integrate watcher, event processor, path mapping, and database logging into a seamless workflow.
- CLI commands must start/stop the watcher, bridge events to the DB, and allow querying logs/state.
- All new logic must be unit tested (expected, edge, and failure cases).
- All validation gates must pass (`./dev.sh` or `./dev.ps1`).
- Document the final architecture with mermaid diagrams.

## Why
- Enables end-to-end tracking of file/directory changes for Blender projects.
- Provides a robust, testable, and extensible foundation for future features.
- Ensures all components are validated and maintainable.

## What (Explicit Agent Behaviors)
- The watcher must emit high-level events for file/dir renames, moves, creates, and deletes.
- The watcher bridge must persist these events to the database using the DB interface.
- The CLI must expose commands to start/stop the watcher and query logs/state.
- All error cases (auth, DB, watcher, config) must be logged and surfaced.
- All environment/config must be loaded via `.env` and `blendman_config.toml`.
- All new code must be covered by unit tests (see test patterns).

### Success Criteria (Validation Gates)
- [ ] All watcher events are logged to the DB and queryable via CLI.
- [ ] All new functions/classes/routes have Pytest unit tests (expected, edge, failure cases).
- [ ] `./dev.sh` or `./dev.ps1` passes with no errors.
- [ ] All code is type-checked (`mypy`), linted (`ruff`), and formatted.
- [ ] All error cases are handled and logged.
- [ ] Architecture is documented with mermaid diagrams.

## All Needed Context (Critical Context Awareness)

### Documentation & References
```yaml
- file: mermaid/blendman.md
  why: Full class diagram of all major modules and their relationships.
- file: mermaid/rename_watcher.md
  why: Event processor, watcher, and path mapping internals.
- file: mermaid/pocketbase_backend.md
  why: PocketBase API, auth, and DB client internals.
- url: https://pocketbase.io/docs/
  why: Official PocketBase API docs (collections, auth, relations, error handling).
- url: https://docs.astral.sh/uv/concepts/projects/workspaces/
  why: Workspace/project structure, validation, and best practices.
- file: README.md
  why: Quickstart, CLI usage, validation, and environment setup.
- file: .env.example
  why: Required environment variables for DB/auth.
- file: blendman_config.toml
  why: Example config for watcher patterns.
- file: src/blendman/db_interface.py
  why: DB interface for persisting/querying events.
- file: src/blendman/watcher_bridge.py
  why: Bridge between watcher and DB.
- file: src/blendman/cli.py
  why: Main CLI entry point.
- file: src/blendman/commands/watcher.py
  why: Watcher CLI commands and integration.
- file: src/blendman/commands/backend.py
  why: Backend query CLI commands.
- file: src/blendman/commands/config.py
  why: Config CLI commands.
- file: src/blendman/commands/pocketbase.py
  why: PocketBase CLI commands.
- file: src/blendman/models.py
  why: FileDirModel and RenameLogModel definitions.
- file: packages/rename_watcher/src/rename_watcher/api.py
  why: Public watcher API.
- file: packages/rename_watcher/src/rename_watcher/event_processor.py
  why: Event correlation logic.
- file: packages/rename_watcher/src/rename_watcher/path_map.py
  why: Path/inode mapping logic.
- file: packages/pocketbase_backend/src/pocketbase/api.py
  why: PocketBase API client.
- file: packages/pocketbase_backend/src/pocketbase/auth.py
  why: Auth logic and error handling.
- file: packages/pocketbase_backend/src/pocketbase/collections.py
  why: CRUD/query logic for DB.
- file: packages/pocketbase_backend/src/pocketbase/exceptions.py
  why: Custom error types for DB/auth.
- file: tests/blendman/test_watcher_bridge.py
  why: Unit tests for watcher bridge (expected, edge, failure cases).
- file: tests/blendman/test_db_interface.py
  why: Unit tests for DB interface (expected, edge, failure cases).
- file: tests/blendman/test_models.py
  why: Unit tests for models (expected, edge, failure cases).
- file: packages/rename_watcher/tests/rename_watcher/test_event_processor.py
  why: Unit tests for event processor (expected, edge, failure cases).
```

### Current Codebase tree
```bash
. (see workspace structure above)
```

### Desired Codebase tree
```bash
. (no new files required for wiring, but ensure all integration points are covered by tests and docs)
```

### Known Gotchas & Library Quirks
```python
# PocketBase requires valid admin credentials for all DB operations.
# All secrets must be loaded from .env (never hardcoded).
# Watcher must handle platform-specific event quirks (see rename_watcher/README.md).
# If any validation gate fails, debug, fix, and re-run until it passes. Document root causes and solutions.
# Use python-dotenv and load_env() for all env loading.
# All error cases must be logged and surfaced to the user.
# Do not assume PocketBase is running; start it if needed.
# All config must be loaded from blendman_config.toml or env.
```

## Implementation Blueprint

- MIRROR pattern from: watcher_bridge.py, db_interface.py, watcher.py, event_processor.py, CLI commands.
- Pseudocode:
  1. Load config and env vars.
  2. Start PocketBase if not running.
  3. Start watcher with matcher from config.
  4. On event, bridge to DB (persist_event).
  5. Expose CLI commands for start/stop/status/query.
  6. Ensure all error cases are logged and tested.
  7. Validate with `./dev.sh` or `./dev.ps1`.
  8. Document architecture with mermaid diagrams.

## Validation Loop (Agent Self-Validation & Iteration)

### Level 1: Syntax & Style
```bash
ruff check .
ruff format .
mypy .
```

### Level 2: Unit Tests
```bash
uv run pytest
```

### Level 3: Integration & Manual
```bash
./dev.sh  # or ./dev.ps1 on Windows
```

## Final validation Checklist
- [ ] All watcher events are logged to DB and queryable via CLI
- [ ] All new logic is unit tested (expected, edge, failure cases)
- [ ] All validation gates pass (lint, type, test)
- [ ] All error cases are handled and logged
- [ ] Architecture is documented with mermaid diagrams
- [ ] README and .env.example are up to date

---

## Anti-Patterns to Avoid
- ❌ Don't create new patterns when existing ones work
- ❌ Don't skip validation because "it should work"
- ❌ Don't ignore failing tests - fix them
- ❌ Don't use sync functions in async context
- ❌ Don't hardcode values that should be config
- ❌ Don't catch all exceptions - be specific

---

# PRD Confidence Score: 9/10

This PRD includes all required context, validation gates, references, and implementation steps for a one-pass, agent-driven integration of all major modules in the blendman monorepo. All error handling, test, and documentation requirements are explicit. Only minor clarifications may be needed for edge-case platform behaviors or future extensibility.
