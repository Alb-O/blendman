# rename_watcher

A cross-platform, robust file/directory rename and move watcher for Python monorepos.

## Features
- Real-time detection of renames, moves, creates, and deletes
- Robust event correlation and deduplication
- Configurable via environment variables
- Ignores dotfiles/folders by default (configurable)
- Fully unit tested, with platform-specific caveats documented

## Setup

```sh
uv pip install -e .
```

## Usage

See `src/rename_watcher/api.py` for the public API.



## Testing & Coverage

This package uses a bullet-proof, generative and fuzzing-based test suite:
- **Property-based tests** (Hypothesis stateful): Model sequences of file/dir operations and invariants.
- **Fuzz tests**: Randomized, high-frequency file/dir operations, edge-case names, deep nesting, and concurrency.
- **Edge-case tests**: Path length, unicode, symlinks, permissions, and more.
- **Platform-specific tests**: Linux (inotify), Windows (ReadDirectoryChangesW), macOS (FSEvents) event semantics.
- **Coverage**: All tests are run with `pytest-cov` and log minimal failing cases for debugging.

To run all tests and measure coverage:
```sh
uv run pytest --cov=src/rename_watcher --cov-report=term-missing
```

## Platform Compatibility Matrix

| Platform | Event API         | Rename/Move Semantics | Notes |
|----------|-------------------|----------------------|-------|
| Linux    | inotify           | IN_MOVED_FROM/TO     | Not recursive, coalescing, overflow possible |
| Windows  | ReadDirectoryChangesW | Delete+Create for cross-dir | Buffer overflow discards events |
| macOS    | FSEvents          | Coalesced, delayed   | No per-file granularity, event order not guaranteed |

See PRD and tests for details on platform-specific behaviors and limitations.
