### [2025-07-08] Config: TOML + gitignore-style matcher
- [x] Implemented TOML config file support for watcher (include/ignore sections, gitignore globbing)
- [x] Used pathspec for robust gitignore-style matching, including negation (!pattern)
- [x] Added/updated unit tests for config parsing and matcher logic (expected, edge, failure cases)
- [x] All tests, lint, and type checks pass
 - [x] Robust support for simple TOML configs:
   - [x] `*` in ignore patterns (ignores all files)
   - [x] Single extension in include patterns (e.g., `.blend` matches only `.blend` files)
   - [x] Unit tests for these cases (expected, edge, failure)
   - [x] All validation gates pass
# NOTEPAD for 002_rename_watcher

---

## [2025-07-08] Nested Subfolder Detection & Path Propagation

### Problem
- When a subfolder is moved or renamed, all included files and subfolders within it must have their paths updated accordingly.
- The watcher/event processor must detect nested moves/renames and propagate path changes to all tracked descendants.
- This is critical for correct event reporting and for downstream consumers relying on accurate file paths.

### Requirements
- Detect moves/renames of any folder, at any nesting depth.
- For each move/rename, update the path-inode map for all descendants (files and subfolders).
- Ensure that included files (per config/include patterns) are still tracked and their new paths are reported.
- Emit correct high-level events for all affected files/folders.
- Handle edge cases: deeply nested structures, simultaneous moves, and rapid sequences.

### Design/Approach
- On folder move/rename, enumerate all descendants (recursively) in the path-inode map.
- For each descendant, update its path in the map to reflect the new parent path.
- Ensure event processor emits a single high-level event per affected file/folder (avoid duplicate or missing events).
- Use debouncing to handle rapid/batched moves.
- Add/extend unit tests for:
  - Moving a folder with nested files/folders (expected, edge, failure cases)
  - Moving a folder that contains only ignored files (should not emit events)
  - Moving a folder with a mix of included/ignored files
  - Simultaneous moves of multiple nested folders

### TODOs
- [x] Update event_processor to handle recursive path updates on folder move/rename
    - Implemented logic in `EventProcessor` to update all descendant paths and emit events on folder move/rename.
- [x] Update path_map to support efficient descendant enumeration and path updates
    - Implemented `descendants` and `bulk_update_paths` methods in `PathInodeMap` for efficient recursive updates.
- [x] Add/extend unit tests for nested folder moves (expected, edge, failure)
    - Added tests for recursive folder moves and event emission in `test_event_processor.py`.
- [x] Validate watcher emits correct events for all affected files/folders
- [ ] Document logic and edge cases in code and README

### Validation
- [x] All tests (including new nested move tests) pass
- [x] Lint (ruff) and type checks (mypy) pass
- [x] No file >500 lines

---

### Planned File Structure

- `src/rename_watcher/`
  - `__init__.py`: Package init
  - `watcher.py`: Core watcher logic (wraps `watchdog`)
  - `event_processor.py`: Event correlation and rename/move detection
  - `path_map.py`: Path-inode mapping utilities
  - `config.py`: Configuration and environment loading
  - `api.py`: Public API
- `tests/rename_watcher/`
  - `test_watcher.py`
  - `test_event_processor.py`
  - `test_path_map.py`
  - ...

### Key Design Patterns
- **Observer pattern** for event subscription.
- **Debouncing** for event correlation (to handle rapid create/delete pairs as renames).
- **Isolation**: No file should exceed 500 lines; modules grouped by responsibility.
- **Environment loading**: Use `python_dotenv` and `load_env()` for all config.

### Integration
- Designed as a standalone package, installable and testable independently.
- Compatible with `uv` workspace monorepo structure.

### Platform Compatibility
 - **Windows:**
   - File and directory renames within the same directory are detected as true rename events.
   - Moves (cut/paste across directories) are only reported as a delete event at the source and a create event at the destination; the watcher cannot natively correlate these as a move/rename.
   - Implications:
     - The watcher must use heuristics (e.g., timing, file metadata) to attempt to pair delete/create events as moves, but this is not always reliable.
     - Tests must explicitly cover this behavior, and documentation should note the limitation for consumers.
     - Users should be aware that cross-directory moves on Windows may not be reported as atomic renames/moves.

---

## Implementation Plan (2025-07-08)

### Task Completion Checklist
- [x] Scaffolded package structure with src layout and editable install
- [x] Implemented watcher, event processor, path-inode map, config, and API stubs
- [x] Wrote unit tests for all modules (expected, edge, failure cases)
- [x] All tests, lint, and type checks pass
- [x] Updated README and documentation
- [x] PRD requirements reviewed and confirmed complete

### 1. Scaffold Package Structure
  - Create `packages/rename_watcher/` with its own `pyproject.toml`, `.env.example`, and README.md.
  - Add `src/rename_watcher/` and `tests/rename_watcher/` as per planned structure.

### 2. Core Watcher Module (`watcher.py`)
  - Use `watchdog` to recursively monitor directories for all file/directory events.
  - Exclude dotfiles/folders by default (configurable).
  - Use polling observer as fallback if needed.

### 3. Event Processor (`event_processor.py`)
  - Deduplicate and correlate raw events.
  - Implement debouncing to handle rapid event sequences.
  - Pair create/delete events as renames/moves using timing, path, and metadata (esp. for Windows cross-directory moves).
  - Document and test platform-specific limitations.

### 4. Path-Inode Map (`path_map.py`)
  - Maintain two-way mapping between file paths and inodes (or platform equivalent).
  - Use for robust tracking across renames/moves.

### 5. Config Layer (`config.py`)
  - Load all config from environment using `python_dotenv` and `load_env()`.
  - Expose timeouts, polling intervals, and ignore patterns.

### 6. API Layer (`api.py`)
  - Provide observer pattern interface for consumers to subscribe to high-level events (on_rename, on_move, etc.).
  - Ensure clear, documented API surface.

### 7. Testing & Validation
  - Write Pytest unit tests for every function/class/module.
  - Each test file: expected use, edge case, failure case.
  - Explicitly test Windows cross-directory move heuristics and document limitations.
  - Run all tests, lint (`ruff`), and type checks (`mypy`) after every change.

### 8. Documentation
  - Update README.md with setup, usage, and platform caveats.
  - Document all non-obvious logic and platform-specific behaviors.

---

## Error Handling & Edge Cases
- If a move/rename is not detected (e.g., due to missing events), fall back to polling and reconcile state.
- If two events cannot be paired, emit as separate create/delete events and log a warning.
- All exceptions must be caught and logged; never crash the watcher.

## Test Requirements
- 100% coverage for all logic, including edge/failure cases.
- Explicit tests for dotfile exclusion, cross-directory moves, and polling fallback.

## Validation Gates
- All tests must pass.
- Lint (`ruff`) and type checks (`mypy`) must pass.
- No file >500 lines; refactor if needed.