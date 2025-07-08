# NOTEPAD for 002_rename_watcher

- **Core Watcher Module**: Uses `watchdog` to recursively monitor directories for file and directory events (create, delete, move, rename).
- **Event Processor**: Interprets raw events, deduplicates, and correlates them to determine true renames/moves (using inode/path mapping where possible).
- **Path-Inode Map**: Maintains a two-way mapping between file paths and inodes (or platform equivalent) to robustly track files across renames/moves.
- **Config Layer**: Exposes configuration for timeouts, polling intervals, and ignored patterns (e.g., dotfiles).
- **API Layer**: Provides a clean interface for consumers to subscribe to high-level events (on_rename, on_move, etc.).
- **Testing & Validation**: All modules are fully unit tested, with tests for expected, edge, and failure cases.

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