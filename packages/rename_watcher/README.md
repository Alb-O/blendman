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


## Testing

```sh
# Install in editable mode (from package root):
uv pip install -e .[dev]

# Run all tests (from package root):
uv run pytest

# Lint and type checks:
uv run ruff check src tests
uv run mypy src tests
```

If you encounter import errors, ensure you are running tests from the package root and that the package is installed in editable mode. For monorepo setups, you may need to set `PYTHONPATH=src` or run from the correct directory.

## Platform Caveats
- On Windows, cross-directory moves may not be reported as atomic renames/moves. See documentation for details.
