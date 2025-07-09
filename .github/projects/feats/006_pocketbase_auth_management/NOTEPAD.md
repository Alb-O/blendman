# NOTEPAD for PocketBase Auth Management PRD v1

## Task: Plan and design the new modular authentication system

### Date: 2025-07-09

### Summary of Current State
- `db_interface.py` uses `PocketBaseAPI` and performs login with admin credentials from env vars.
- `auth.py` provides `AuthClient` with basic password login, logout, and token retrieval.
- No support for OTP, OAuth2, MFA, impersonation, or advanced token management.
- Error handling is present but basic.

### Design Plan

#### 1. Modular Structure
- `auth.py`: Main `AuthClient` for all auth flows (password, OTP, OAuth2, MFA, impersonation)
- `tokens.py`: Token management utilities (in-memory only, no disk persistence)
- `mfa.py`: MFA and OAuth2 logic (stub if not enabled)

#### 2. AuthClient Responsibilities
- Load all secrets and endpoints from environment variables using `python_dotenv` and `load_env()`
- Support:
  - Password login
  - OTP login (if enabled)
  - OAuth2 login (if enabled)
  - MFA (if enabled)
  - Impersonation (superuser)
- Store tokens securely in memory
- Provide clear error messages and explicit error handling
- Log all errors and important events
- Expose methods for login, logout, token refresh, and impersonation

#### 3. Token Management
- All tokens are stored in memory only
- Provide utilities for token refresh and validation
- Never persist tokens to disk

#### 4. MFA/OAuth2
- Implement as stubs if not enabled in PocketBase
- If enabled, provide flows for OTP, OAuth2, and MFA

#### 5. Integration
- Refactor `db_interface.py` to use the new `AuthClient`
- Ensure all DB operations are authenticated and handle token refresh as needed

#### 6. Testing
- Add/extend Pytest unit tests for all new logic (expected, edge, failure cases)
- Mirror test structure in `/tests` folder

#### 7. Documentation
- Update `.env.example` for all required secrets
- Update `README.md` with setup, security, and environment notes

---

## TODOs
- [x] Implement modular structure as above
- [x] Ensure all validation gates are met
- [x] Document all non-obvious decisions and security tradeoffs
- [x] Mark completed tasks here as they are finished
