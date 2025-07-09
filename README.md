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
python dev.py
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


# PocketBase Auth Management - Setup and Security Notes

## Setup

1. Copy `.env.example` to `.env` and fill in all required secrets:
  - `POCKETBASE_URL`
  - `POCKETBASE_ADMIN_EMAIL`
  - `POCKETBASE_ADMIN_PASSWORD`
  - (Optional) `POCKETBASE_OTP_SECRET`, `POCKETBASE_OAUTH2_CLIENT_ID`, etc.
2. Install dependencies:
  - `pip install -r requirements.txt` (or use `uv`/`venv_linux` as per project)
3. Run validation:
  - `python dev.py`

## Security Notes

- All secrets are loaded from environment variables only (never hardcoded).
- Tokens are managed in memory only and never persisted to disk.
- Superuser tokens should be used only for internal server-to-server operations.
- MFA and OAuth2 require configuration in the PocketBase admin UI.
- All error cases are logged and surfaced to the caller.

## Auth Flows Supported
- Password login
- OTP login (if enabled)
- OAuth2 login (if enabled)
- MFA (if enabled)
- Impersonation (superuser)
- Token refresh

## Validation
- All new logic is covered by Pytest unit tests (expected, edge, and failure cases).
- Run `python dev.py` after every major change; all validation gates must pass.
- No hardcoded secrets; all config via environment variables.
- All code is type-checked (`mypy`), linted (`ruff`), and formatted.

## Troubleshooting
- If a validation gate fails, debug, fix, and re-run until it passes. Document root causes and solutions in `NOTEPAD.md`.
- For more details, see `.github/projects/feats/006_pocketbase_auth_management/PRD.md`.
