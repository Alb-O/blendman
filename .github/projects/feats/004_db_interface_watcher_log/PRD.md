# Product Requirements Document (PRD)

## Feature: 004_db_interface_watcher_log

---

## Purpose
Implement a robust, modular interface between the Pocketbase backend package and the Rename watcher. This interface must:
- Represent files and directories as linked database tables (with parent/child relationships)
- Log all rename/move events from the watcher
- Be highly modular, composable, and maintainable
- Live in `src/blendman/` (new architecture)

## Why
- Enables unified tracking of file/dir state and history for downstream features (e.g., audit, sync, analytics)
- Integrates two core packages (Pocketbase backend, Rename watcher) for seamless data flow
- Supports future extensibility (e.g., new event types, richer metadata)

## What (Explicit Agent Behaviors)
- Define DB schema/tables for files, directories, relationships, and rename/move logs
- Implement interface code to receive watcher events and persist them
- Ensure all code is modular (no file >500 lines), with clear separation of concerns
- Use `python-dotenv` and `load_env()` for config/env
- Provide Pytest unit tests for all logic (expected, edge, failure cases)
- Document all non-obvious decisions in code/docstrings
- Validate all changes with `ruff`, `mypy`, and `pytest` via `./dev.sh`

### Success Criteria (Validation Gates)
- [ ] All new code is fully unit tested (expected, edge, failure cases)
- [ ] All validation gates (`ruff`, `mypy`, `pytest`, `./dev.sh`) pass after every change
- [ ] No file exceeds 500 lines
- [ ] All errors are handled and logged; no unhandled exceptions
- [ ] Documentation and .env.example are updated if needed

---

## All Needed Context (Critical Context Awareness)

### Documentation & References
```yaml
- url: https://pocketbase.io/docs/
  why: Collections, relations, file handling, API patterns
- url: https://pocketbase.io/docs/collections
  why: DB schema, parent/child, relations
- url: https://pocketbase.io/docs/working-with-relations
  why: How to model relationships
- url: https://pocketbase.io/docs/files-handling
  why: File metadata, storage
- url: https://docs.astral.sh/uv/concepts/projects/workspaces
  why: Modular Python monorepo, package structure
- file: packages/rename_watcher/README.md
  why: Event types, watcher API, platform caveats
- file: packages/pocketbase_backend/README.md
  why: Backend API, integration points
- file: .github/projects/feats/002_rename_watcher/PRD.md
  why: Patterns for watcher, error handling, validation
- file: .github/projects/feats/001_pocketbase_api/PRD.md
  why: Patterns for modular API, testing, validation
```

### Existing Packages in `packages/` and How to Utilize Them

#### pocketbase_backend
- **Purpose:** Modular Python API client for PocketBase (REST API).
- **Key modules:**
  - `src/pocketbase/api.py`: Main entry point. Use `PocketBaseAPI()` to access all features.
  - `auth.py`: Authentication (login, logout, token management).
  - `collections.py`: CRUD and query for collections (see `CollectionsClient`).
  - `relations.py`: Manage parent/child and other relations.
  - `files.py`: File upload/download.
  - `exceptions.py`: All API errors are wrapped in custom exceptions.
- **Usage Example:**
  ```python
  from pocketbase.api import PocketBaseAPI
  api = PocketBaseAPI()
  api.auth.login(email="admin@example.com", password="changeme")
  record = api.collections.create("files", {"name": "foo.txt"})
  api.relations.link("files", record["id"], "parent", "parent_id")
  api.auth.logout()
  ```
- **Integration:** Use this package to persist file/dir state, manage relationships, and log rename/move events in PocketBase.

#### rename_watcher
- **Purpose:** Cross-platform, robust watcher for file/dir renames, moves, creates, and deletes.
- **Key modules:**
  - `src/rename_watcher/api.py`: Public API. Use `RenameWatcherAPI()` to subscribe to high-level events.
  - `event_processor.py`, `path_map.py`, `watcher.py`: Core event processing and mapping logic.
- **Usage Example:**
  ```python
  from rename_watcher.api import RenameWatcherAPI
  watcher = RenameWatcherAPI()
  def on_event(event):
      print(event)
  watcher.subscribe(on_event)
  # watcher.emit(...) is called internally by the watcher system
  ```
- **Integration:** Subscribe to watcher events and, in your callback, use the PocketBase API to update the DB and log events.

#### How to Utilize These Packages in the Interface
- **Event Flow:** `RenameWatcherAPI` emits events → your interface subscribes and receives events → use `PocketBaseAPI` to update tables and logs.
- **Separation:** Keep watcher event handling and DB logic modular (separate files/classes).
- **Testing:** Both packages are fully unit tested; mock their APIs in your own tests.

### Current Codebase tree
```bash
# See workspace structure in README.md and project root
```

### Desired Codebase tree
```bash
src/blendman/
  db_interface.py         # Main interface logic (modular, <500 lines)
  models.py               # DB models/tables for files, dirs, logs
  watcher_bridge.py       # Receives watcher events, transforms to DB ops
  __init__.py
  ...
tests/blendman/
  test_db_interface.py    # Unit tests (expected, edge, failure)
  test_models.py
  test_watcher_bridge.py
.env.example              # Add any new env vars
README.md                 # Update with setup/integration notes
```

### Known Gotchas & Library Quirks
```python
# PocketBase: Relations must be explicitly defined; see docs for parent/child
# Rename watcher: Platform-specific event quirks (see README, PRD)
# uv workspace: Each package must have its own pyproject.toml
# CRITICAL: If any validation gate fails, debug, fix, and re-run until it passes. Document root causes and solutions.
# No file >500 lines; refactor as needed
# Use python-dotenv and load_env() for all config
```

---

## Implementation Blueprint

### Pseudocode/Approach
1. **Define DB Models**
   - File/Dir table: id, name, path, parent_id, type, created_at, updated_at
   - RenameLog table: id, file_id (FK to File/Dir), old_path, new_path, event_type, timestamp
   - Use explicit foreign keys for parent/child and for linking logs to files/dirs
   - Ensure indexes on file_id and timestamp for efficient queries
   - Support queries:
     - Per-file: fetch all logs for a given file/dir (by file_id)
     - Global: fetch all logs across all files (ordered by timestamp)
2. **Implement Watcher Bridge**
   - Subscribe to watcher events (rename, move, create, delete)
   - On event, update File/Dir table and insert into RenameLog (with file_id FK)
   - Handle edge cases (e.g., missing parent, rapid events)
3. **Interface Logic**
   - Expose API for:
     - Querying logs for a specific file/dir (by file_id)
     - Querying the global event log (all RenameLog entries, ordered)
     - Querying file/dir state and history
   - Ensure all DB ops are atomic and robust
   - Log and handle all errors
4. **Testing**
   - Pytest: expected, edge, failure for all logic
   - Mock watcher events for unit tests
   - Validate DB state and log queries after each event
5. **Validation**
   - Run `./dev.sh` after every change
   - Fix all lint/type/test errors before proceeding

### Error Handling
- All exceptions must be caught and logged
- If DB op fails, rollback and log error
- If watcher event is malformed, skip and log warning
- Document all non-obvious error handling in code

### Validation Loop
```bash
./dev.sh
```

---

## Integration Points
```yaml
DATABASE:
  - Add tables: files, directories, rename_logs
  - Add foreign keys for parent/child
CONFIG:
  - Add any new env vars to .env.example
  - Use load_env() for all config
```

---

## Final Validation Checklist
- [ ] All tests pass
- [ ] No linting errors (`ruff check .`)
- [ ] No type errors (`mypy .`)
- [ ] Manual test: Simulate watcher event, verify DB/log
- [ ] Error cases handled and documented
- [ ] Logs are informative but not verbose
- [ ] Documentation and .env.example updated
- [ ] All validation gates are self-checked and iterated until passing

---

## References & Research Sources
- [PocketBase Docs](https://pocketbase.io/docs/)
- [Collections](https://pocketbase.io/docs/collections)
- [Relations](https://pocketbase.io/docs/working-with-relations)
- [Files](https://pocketbase.io/docs/files-handling)
- [uv Workspace](https://docs.astral.sh/uv/concepts/projects/workspaces)
- [Rename Watcher README](../../../../packages/rename_watcher/README.md)
- [Pocketbase Backend README](../../../../packages/pocketbase_backend/README.md)
- [Watcher PRD](../002_rename_watcher/PRD.md)
- [Pocketbase API PRD](../001_pocketbase_api/PRD.md)

---

## Confidence Score
**9/10** — All context, patterns, and validation gates are included. One-pass implementation is highly likely if agent follows this PRD and referenced patterns.
