# NOTEPAD for 001_pocketbase_api

## Task Tracking (as of 2025-07-08)

### Main PRD: .github/projects/feats/001_pocketbase_api/PRD.md

- [x] Step 1: Create or update NOTEPAD.md with this task and planning notes
- [x] Step 2: Implement api.py to compose subclients and load env
- [x] Step 3: Implement auth.py (login, logout, token management)
- [x] Step 4: Implement collections.py (CRUD, query)
- [x] Step 5: Write unit tests for collections.py (expected, edge, failure cases)
  - All CRUD/query methods implemented, error handling, docstrings, <500 lines.
  - test_collections.py covers all methods (expected, edge, failure), all tests pass.
  - All validation gates (ruff, mypy, pytest) clean for collections.
  - Next: Implement files.py (upload/download)
- [ ] Step 6: Implement relations.py (link/unlink)
- [ ] Step 7: Implement exceptions.py (custom errors)
- [ ] Step 8: Implement utils.py (env, helpers)
- [ ] Step 10: Add .env.example and update README with setup/usage
- [ ] Step 12: Mark completed tasks in NOTEPAD.md and finalize

### Planning Notes
- All modules must be under 500 lines; refactor if needed.
- Use relative imports within the package.
- Use python-dotenv for env loading; add # type: ignore for mypy.
- All API errors must be wrapped in custom exceptions.
- All tests must mock HTTP requests; do not hit real PocketBase.
- Validation gates: ruff, mypy, pytest after every change.
- Update README and .env.example as needed.

---

## Design: collections.py (CRUD, query)

### Class: CollectionsClient
- Methods:
  - create(collection: str, data: dict[str, Any]) -> dict[str, Any]
  - get(collection: str, record_id: str) -> dict[str, Any]
  - update(collection: str, record_id: str, data: dict[str, Any]) -> dict[str, Any]
  - delete(collection: str, record_id: str) -> None
  - query(collection: str, filters: dict[str, Any] | None = None, page: int = 1, per_page: int = 20) -> dict[str, Any]
- All methods:
  - Use requests to call PocketBase REST API
  - Use token from AuthClient if available
  - Catch and wrap all HTTP errors in PocketBaseError
  - Validate arguments and raise ValueError if invalid

### Tests:
- For each method: expected, edge, and failure case
- All HTTP calls must be mocked

---
## Progress Log
- 2025-07-08: NOTEPAD.md updated, initial plan and todo list added.
- 2025-07-08: Steps 1 and 2 complete, api.py and tests validated, all type/lint/test gates clean.
- 2025-07-08: Steps 3–5 complete, auth.py implemented and validated with tests, all gates clean.