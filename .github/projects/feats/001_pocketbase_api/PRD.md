# Product Requirements Document (PRD)

## Feature: 001_pocketbase_api

### Overview
Implement a comprehensive, production-grade Python API system for PocketBase, using its REST API, within the `packages/pocketbase_backend` package. The solution must be modular, composable, and fully validated with tests, linting, and type checks. The implementation should go beyond basic CRUD, covering authentication, file handling, relations, and advanced features, while following best practices for uv workspaces and Python packaging.

---

## 1. Critical Context & Documentation

### Internal Context
- **Feature Spec:** `.github/projects/feats/001_pocketbase_api/INITIAL.md`
- **Current Package:** `packages/pocketbase_backend` (see `src/pocketbase/`)
- **Existing Manager:** `pocketbase_manager.py` (process manager for PocketBase binary)
- **API Stubs:** `api.py`, `auth.py`, `collections.py`, `files.py`, `relations.py`, `exceptions.py`, `utils.py`
- **Testing:** All new code must be covered by Pytest tests (expected, edge, failure cases) in `/tests/pocketbase/`
- **Validation Gates:** Lint (`ruff`), type check (`mypy`), and test (`pytest`) after every change

### External Documentation
- **PocketBase Docs:** [https://pocketbase.io/docs/](https://pocketbase.io/docs/)
  - [REST API Reference](https://pocketbase.io/docs/api-records)
  - [Authentication](https://pocketbase.io/docs/authentication)
  - [Collections](https://pocketbase.io/docs/collections)
  - [Files](https://pocketbase.io/docs/files-handling)
  - [Relations](https://pocketbase.io/docs/working-with-relations)
- **uv Workspaces:** [https://docs.astral.sh/uv/concepts/projects/workspaces](https://docs.astral.sh/uv/concepts/projects/workspaces)
- **Python-dotenv:** [https://pypi.org/project/python-dotenv/](https://pypi.org/project/python-dotenv/)
- **Ruff:** [https://docs.astral.sh/ruff/](https://docs.astral.sh/ruff/)
- **Mypy:** [https://mypy.readthedocs.io/en/stable/)
- **Pytest:** [https://docs.pytest.org/en/stable/](https://docs.pytest.org/en/stable/)

---

## 2. Codebase Analysis & Patterns

- **Modular Structure:** Each responsibility (auth, CRUD, files, relations) is a separate module in `src/pocketbase/`.
- **Imports:** Use relative imports within the package.
- **Environment:** Use `python-dotenv` and `load_env()` for configuration.
- **Testing:** Mirror main code structure in `/tests/pocketbase/` with Pytest. Each function/class/route must have:
  - 1 expected use test
  - 1 edge case test
  - 1 failure case test
- **Validation:** Run `ruff`, `mypy`, and `pytest` after every change. Never consider a task complete until all pass.
- **File Size:** No file may exceed 500 lines; refactor into submodules if needed.
- **Error Handling:** Use custom exceptions (`exceptions.py`). All API errors must be caught and wrapped.

---

## 3. External Research & Best Practices

- **PocketBase REST API:** Use standard HTTP methods. Auth via token. Handle 4xx/5xx errors gracefully.
- **uv Workspaces:** Each package has its own `pyproject.toml`, but shares a lockfile. Use `[tool.uv.workspace]` and `[tool.uv.sources]` as needed.
- **Testing:** Use fixtures for setup/teardown. Mock HTTP requests for unit tests. Use `pytest.raises` for failure cases.
- **Type Hints:** Use `dict[str, Any]` for dynamic data. Add `# type: ignore` for missing stubs (e.g., `dotenv`).
- **Linting:** Use `ruff check` and `ruff format` for code style.
- **CI/CD:** All validation gates must be automatable.

---

## 4. Implementation Blueprint

### Pseudocode/Approach

1. **API Client (`api.py`)**
   - Load env vars (base URL, credentials)
   - Compose subclients: Auth, Collections, Files, Relations
2. **Auth (`auth.py`)**
   - Login, logout, token refresh
   - Store/reuse token
3. **Collections (`collections.py`)**
   - CRUD: create, get, update, delete
   - Query/filter support
4. **Files (`files.py`)**
   - Upload/download files to records
5. **Relations (`relations.py`)**
   - Link/unlink records
6. **Exceptions (`exceptions.py`)**
   - Custom error types for API errors
7. **Utils (`utils.py`)**
   - Env loading, request helpers
8. **Tests**
   - Mirror structure in `/tests/pocketbase/`
   - Use Pytest, mock HTTP, cover all cases

### Error Handling
- Catch all HTTP errors, wrap in `PocketBaseError` or subclass
- Validate all inputs, raise `ValueError` for bad arguments
- Log and re-raise unexpected exceptions

### Validation Gates
```bash
uv pip install -r requirements.txt  # or use pyproject.toml
uv venv
uv run ruff check .
uv run ruff format .
./mypy_recursive.sh
uv run pytest
```

---

## 5. Tasks (in order)

1. Implement `api.py` to compose subclients and load env
2. Implement `auth.py` (login, logout, token management)
3. Implement `collections.py` (CRUD, query)
4. Implement `files.py` (upload/download)
5. Implement `relations.py` (link/unlink)
6. Implement `exceptions.py` (custom errors)
7. Implement `utils.py` (env, helpers)
8. Write Pytest tests for each module (expected, edge, failure)
9. Add `.env.example` and update README with setup/usage
10. Run all validation gates and iterate until clean

---

## 6. Gotchas & Notes
- **PocketBase API:** Some endpoints may change; check docs for version compatibility.
- **python-dotenv:** No type stubs; use `# type: ignore` for mypy.
- **uv:** All dependencies must be in `pyproject.toml` for correct sync.
- **Testing:** Mock all network calls; do not hit real PocketBase in unit tests.
- **File Size:** Refactor aggressively if any file nears 500 lines.

---

## 7. Confidence Score
**9/10** — This PRD provides all context, references, and validation steps needed for a one-pass implementation by an AI agent or developer.
