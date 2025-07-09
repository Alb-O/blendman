
# Blendman CLI

Blendman is a CLI tool for managing Blender-related workflows and PocketBase integration.

## Quickstart


### 1. Set up a virtual environment and install dependencies

```sh
# Create and activate a virtual environment (fish shell)
uv venv .venv
source .venv/bin/activate.fish

# Install main dependencies
uv pip install -e .

# Install local packages in editable mode
uv pip install -e packages/rename_watcher
uv pip install -e packages/pocketbase_backend
```

### 2. Set up environment variables

Copy `.env.example` to `.env` and set:
- `POCKETBASE_URL`
- `POCKETBASE_ADMIN_EMAIL`
- `POCKETBASE_ADMIN_PASSWORD`
- `BLENDMAN_CONFIG` (optional)
These values are used on first launch to automatically create the PocketBase superuser
if it doesn't already exist.


### 3. Run the CLI



From the project root, activate your virtual environment and set the `PYTHONPATH`:

```sh
# For bash/zsh:
source .venv/bin/activate
export PYTHONPATH=src:packages/rename_watcher/src:packages/pocketbase_backend/src

# For fish shell:
source .venv/bin/activate.fish
set -x PYTHONPATH src:packages/rename_watcher/src:packages/pocketbase_backend/src

# Run the interactive shell (works in any shell after activation and PYTHONPATH set)
python -m blendman
```

> **Note:** Use `export` for bash/zsh, and `set -x` for fish. Adjust activation and environment commands as needed for your shell.

Replace the interactive prompt with any command to run it directly. For example:

- Start the watcher:
  ```sh
  python -m blendman watcher start --config-path blendman_config.toml
  ```
  If `blendman_config.toml` doesn't exist, the CLI will create a default one for you.
  On first run the CLI will also start PocketBase automatically. If PocketBase hasn't
  been initialized yet you'll get instructions to create a superuser account.
- Check watcher status:
  ```sh
  python -m blendman watcher status
  ```
- Query backend logs:
  ```sh
  python -m blendman backend query logs
  ```
- Open PocketBase dashboard UI:
  ```sh
  python -m blendman pocketbase ui
  ```
- Create a PocketBase superuser:
  ```sh
  python -m blendman pocketbase superuser admin@example.com password
  ```


> **Tip:** If you use a different shell or platform, adapt the activation and environment variable commands as needed. For fish shell, use `set -x` instead of `export`.

---

## Validation

To run all tests, lint, and type checks:

```sh
python dev.py
```

---

For advanced configuration and troubleshooting, see the documentation and `.env.example`.
