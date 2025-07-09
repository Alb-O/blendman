# Blendman Workspace (uv)

This project uses [uv workspaces](https://docs.astral.sh/uv/concepts/projects/workspaces/) for robust, idiomatic Python monorepo management.

## Structure

- `pyproject.toml` (root): Declares the workspace and manages shared dependencies and scripts.
- `packages/pocketbase/`: Contains the PocketBase binary manager package.
- `src/blendman/`: Main application code and CLI entry points.

## Workflow


### Install all dependencies (including dev tools)

```sh
uv pip install -e .
```

### Unified development check (lint, type-check, test)

Run all validation steps with one command:

```sh
./dev.sh
```

### Run the PocketBase manager CLI

```sh
uv run --package pocketbase pocketbase-manager start --port 8090
```

### Add a new package

- Create a new directory under `packages/` with its own `pyproject.toml` and `src/`.
- Add it to the `members` list in the root `pyproject.toml` if not using a glob.

## Automation & CI

### Pre-commit hooks

Install and enable pre-commit hooks to automatically lint, type-check, and test before every commit:

```sh
pip install pre-commit
pre-commit install
```

### Continuous Integration (GitHub Actions)

This repo includes `.github/workflows/ci.yml` to run lint, type-check, and tests on every push/PR.

---

### Add a new package

- Create a new directory under `packages/` with its own `pyproject.toml` and `src/`.
- Add it to the `members` list in the root `pyproject.toml` if not using a glob.

## Best Practices

- Use `[tool.uv.sources]` for local package dependencies.
- Keep dev tools (ruff, mypy, pytest, etc.) in the root dependencies for workspace-wide use.
- Use `uv run` and `uv pip` from the workspace root for all operations.

---

See [uv workspace docs](https://docs.astral.sh/uv/concepts/projects/workspaces/) for more details.

See [uv workspace docs](https://docs.astral.sh/uv/concepts/projects/workspaces/) for more details.

---

## DB Interface Watcher Log (Feature 004)

This feature provides a robust, modular interface between the PocketBase backend and the Rename Watcher, enabling unified tracking of file and directory state and history.

### Setup
- Ensure PocketBase is running and configured via `.env` (see `.env.example`).
- All required environment variables:
  - `POCKETBASE_URL`
  - `POCKETBASE_ADMIN_EMAIL`
  - `POCKETBASE_ADMIN_PASSWORD`
- Dependencies: `pydantic`, `python-dotenv` (installed via `uv`).

### Integration
- The watcher bridge subscribes to file/dir events and persists them in PocketBase using the DB interface.
- All code lives in `src/blendman/`:
  - `models.py`: DB models for files, directories, and logs
  - `db_interface.py`: Main interface logic
  - `watcher_bridge.py`: Event subscription and transformation

### Testing & Validation
- Run all validation gates with:
  ```sh
  ./dev.sh
  ```
- Unit tests for all logic are in `tests/blendman/`.
- All errors are logged and handled robustly.

See the PRD for full details and requirements.
