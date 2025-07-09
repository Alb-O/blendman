
name: "PocketBase Auth Management PRD v1 - Agent Autonomy & Validation"

## Purpose
This PRD defines a robust, secure, and maintainable authentication system for blendman’s integration with PocketBase, replacing the current approach with best practices for API security, error handling, and extensibility. The agent must self-validate, recover from errors, and iterate until all validation gates pass.

## Core Principles
1. **Agent Autonomy**: Self-correct and iterate until all validation gates pass.
2. **Context Awareness**: Include all necessary documentation, examples, and caveats. Never assume missing context.
3. **Validation Loops**: Provide and execute all tests/lints/type checks, and fix issues until passing.
4. **Explicitness**: Prefer clarity and explicit documentation over brevity. Document all non-obvious decisions.
5. **Global rules**: Always follow all rules in CLAUDE.md and project instructions.

## Goal (Agent Mission & Priorities)
- Critique and replace the current PocketBase authentication logic in blendman.
- Implement a new authentication system using best practices from PocketBase documentation and modern API security.
- Support password, OTP, OAuth2, and MFA where possible.
- Ensure all new logic is fully tested, validated, and documented.

## Why
- **Business value**: Secure, reliable authentication is critical for protecting user data and enabling integrations.
- **Integration**: The new system must work seamlessly with existing DB and event logic.
- **Problems solved**: Addresses security gaps, improves maintainability, and enables future extensibility (e.g., MFA, OAuth2).

## What (Explicit Agent Behaviors)
- Use environment variables for all secrets (with `.env.example` and `load_env()`).
- Support all PocketBase auth methods: password, OTP, OAuth2, MFA, impersonation.
- Store and manage tokens securely; never persist tokens to disk.
- Provide clear error messages and handle all failure cases explicitly.
- Document all non-obvious decisions and security tradeoffs.
- Provide Pytest unit tests for all new logic (expected, edge, and failure cases).

### Success Criteria (Validation Gates)
- [ ] All new functions/classes/routes have Pytest unit tests (expected, edge, failure cases).
- [ ] Run `./dev.sh` or `./dev.ps1` after every major change; all validation gates must pass.
- [ ] If a validation gate fails, debug, fix, and re-run until it passes. Document root causes and solutions.
- [ ] No hardcoded secrets; all config via environment variables.
- [ ] All error cases are handled and logged.
- [ ] All code is type-checked (`mypy`), linted (`ruff`), and formatted.

## All Needed Context (Critical Context Awareness)

### Documentation & References
```yaml
- url: https://pocketbase.io/docs/authentication/
  why: Official authentication overview, best practices, and security notes.
- url: https://pocketbase.io/docs/api-records/#auth-with-password
  why: API reference for password authentication and related endpoints.
- url: https://pocketbase.io/docs/api-records/#auth-refresh
  why: Token refresh and verification best practices.
- url: https://pocketbase.io/docs/api-records#impersonate
  why: Superuser impersonation and API key patterns.
- file: src/blendman/db_interface.py
  why: Current integration point for PocketBase authentication.
- file: packages/pocketbase_backend/src/pocketbase/auth.py
  why: Current authentication logic to be critiqued and replaced.
- file: tests/blendman/test_db_interface.py
  why: Existing test patterns for DB and auth logic.
```

### Current Codebase tree (abridged)
```bash
src/blendman/db_interface.py
packages/pocketbase_backend/src/pocketbase/api.py
packages/pocketbase_backend/src/pocketbase/auth.py
packages/pocketbase_backend/src/pocketbase/collections.py
packages/pocketbase_backend/src/pocketbase/exceptions.py
packages/pocketbase_backend/src/pocketbase/utils.py
tests/blendman/test_db_interface.py
```

### Desired Codebase tree (to be added/modified)
```bash
src/blendman/db_interface.py         # Refactored to use new auth logic
packages/pocketbase_backend/src/pocketbase/auth.py  # New secure AuthClient
packages/pocketbase_backend/src/pocketbase/tokens.py # (NEW) Token management utilities
packages/pocketbase_backend/src/pocketbase/mfa.py    # (NEW) MFA/OAuth2 logic
.env.example                         # Example env vars for secrets
README.md                            # Setup and security notes
```

### Known Gotchas & Library Quirks
```python
# PocketBase tokens are stateless JWTs; logout is client-side only.
# No server-side token revocation; to "logout" just clear the token in memory.
# Superuser tokens grant full access; use only for internal server-to-server.
# MFA and OAuth2 require collection options to be enabled/configured in PocketBase admin UI.
# All secrets must be loaded via python_dotenv and load_env().
# If any validation gate fails, debug, fix, and re-run until it passes. Document root causes and solutions.
```

## Implementation Blueprint
- Mirror the modular structure in `src/blendman/db_interface.py` and `packages/pocketbase_backend/src/pocketbase/auth.py`.
- Add new modules for token management and MFA/OAuth2 support.
- Use environment variables for all secrets and endpoints.
- Provide clear error handling and logging for all auth flows.
- Add/extend tests in `tests/blendman/test_db_interface.py` and new test files as needed.

### Pseudocode
```python
# 1. Load env vars (POCKETBASE_URL, POCKETBASE_ADMIN_EMAIL, POCKETBASE_ADMIN_PASSWORD, etc.)
# 2. Initialize AuthClient with base_url
# 3. For login:
#    - Support password, OTP, OAuth2, MFA as configured
#    - Store token in memory only
#    - On failure, raise explicit error
# 4. For logout:
#    - Clear token and user info in memory
# 5. For token refresh:
#    - Call /auth-refresh endpoint and update token
# 6. For impersonation:
#    - Use superuser token to impersonate as needed
# 7. All errors are logged and surfaced to the caller
```

## Validation Loop (Agent Self-Validation & Iteration)

### Level 1: Syntax & Style
```bash
./dev.sh
# Expected: No errors or warnings. If errors/warnings, analyze, fix, and re-run until passing.
```

### Level 2: Unit Tests
- Add/extend tests for:
  - Password login (success, failure, edge)
  - OTP login (if enabled)
  - OAuth2 login (if enabled)
  - MFA (if enabled)
  - Token refresh
  - Impersonation (superuser)
  - All error cases (network, invalid creds, etc.)

### Integration Points
```yaml
ENV:
  - .env.example: Document all required secrets
  - README.md: Setup and security notes
```

```bash
uv run pytest
# If failing: Analyze, fix, and re-run until all tests pass. Document root causes and solutions.
```

## Final validation Checklist
- [ ] All tests pass
- [ ] No linting errors (`ruff check .`)
- [ ] No type errors (`mypy .`)
- [ ] Manual test successful: login, logout, token refresh, error cases
- [ ] Error cases handled gracefully and are documented
- [ ] Logs are informative but not verbose
- [ ] Documentation updated if needed
- [ ] All validation gates are self-checked and iterated until passing

---

## Anti-Patterns to Avoid
- ❌ Don’t create new patterns when existing ones work
- ❌ Don’t skip validation because “it should work”
- ❌ Don’t ignore failing tests—fix them
- ❌ Don’t use sync functions in async context
- ❌ Don’t hardcode values that should be config
- ❌ Don’t catch all exceptions—be specific

## Confidence Score
**8/10** — This PRD provides comprehensive context, references, and a clear implementation path. Success depends on careful adherence to PocketBase security best practices and thorough testing of all auth flows.
