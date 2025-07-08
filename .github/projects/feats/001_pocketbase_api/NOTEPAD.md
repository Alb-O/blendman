# NOTEPAD for 001_pocketbase_api

## Task Tracking (as of 2025-07-08)

### Main PRD: .github/projects/feats/001_pocketbase_api/PRD.md

- [x] Step 1: Create or update NOTEPAD.md with this task and planning notes
- [x] Step 2: Implement api.py to compose subclients and load env
- [ ] Step 3: Implement auth.py (login, logout, token management)
- [ ] Step 4: Implement collections.py (CRUD, query)
- [ ] Step 5: Implement files.py (upload/download)
- [ ] Step 6: Implement relations.py (link/unlink)
- [ ] Step 7: Implement exceptions.py (custom errors)
- [ ] Step 8: Implement utils.py (env, helpers)
- [ ] Step 9: Write Pytest tests for each module (expected, edge, failure) in /tests/pocketbase/
- [ ] Step 10: Add .env.example and update README with setup/usage
- [ ] Step 11: Run all validation gates and iterate until clean
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

## Progress Log
- 2025-07-08: NOTEPAD.md updated, initial plan and todo list added.
- 2025-07-08: Steps 1 and 2 complete, api.py and tests validated, all type/lint/test gates clean.