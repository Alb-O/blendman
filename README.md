# Blendman Workspace (uv)

This project uses [uv workspaces](https://docs.astral.sh/uv/concepts/projects/workspaces/) for robust, idiomatic Python monorepo management.

## Structure

- `pyproject.toml` (root): Declares the workspace and manages shared dependencies and scripts.
- `packages/pocketbase/`: Contains the PocketBase binary manager package.
- `src/blendman/`: Main application code and CLI entry points.

## Quickstart: Blendman CLI

### 1. Install all dependencies (including dev tools)

```sh
uv pip install -e .
```

### 2. Create a default blendman config (optional)

```sh
python -m src.blendman.cli config init --path blendman_config.toml
```

### 3. Run the CLI and see available commands

```sh
python -m src.blendman.cli --help
```

### 4. Example CLI usage

- **Start the watcher:**
  ```sh
  python -m src.blendman.cli watcher start --config-path blendman_config.toml
  ```
- **Check watcher status:**
  ```sh
  python -m src.blendman.cli watcher status
  ```
- **Query backend logs:**
  ```sh
  python -m src.blendman.cli backend query logs
  ```
- **Open PocketBase dashboard UI:**
  ```sh
  python -m src.blendman.cli pocketbase ui
  ```
- **Create a PocketBase superuser:**
  ```sh
  python -m src.blendman.cli pocketbase superuser admin@example.com password
  ```

### 5. Environment variables

Copy `.env.example` to `.env` and set:
- `POCKETBASE_URL`
- `POCKETBASE_ADMIN_EMAIL`
- `POCKETBASE_ADMIN_PASSWORD`
- `BLENDMAN_CONFIG` (optional)

## Unified development check (lint, type-check, test)

Run all validation steps with one command:

```sh
./dev.sh
```

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

## Best Practices

- Use `[tool.uv.sources]` for local package dependencies.
- Keep dev tools (ruff, mypy, pytest, etc.) in the root dependencies for workspace-wide use.
- Use `uv run` and `uv pip` from the workspace root for all operations.

---

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
