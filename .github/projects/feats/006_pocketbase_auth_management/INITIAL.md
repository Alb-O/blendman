
## FEATURE (Agent Mission & Priorities):

Critique the current implementation of blendman's attempt at authenticating with pocketbase. A completely new method of auth needs to be implemented, focusing on best practices and security for connecting to APIs. CRITICAL: You MUST research the documentation below to get the full picture of how to implement. Remember, you are to research, plan, draft, brainstorm and write the PRD only.

## DOCUMENTATION (Critical Context):

#githubRepo pocketbase/pocketbase

#fetch https://pocketbase.io/docs/authentication/

#fetch https://pocketbase.io/docs/api-records/#auth-with-password

## VALIDATION & SELF-CHECKS (Validation Gates):

- Every new function, class, or route MUST have Pytest unit tests (expected use, edge, and failure cases).
- Run `./dev.py` after every major change. Never consider a task complete until all validation gates pass.
- If a validation gate fails, debug, fix, and re-run until it passes. Document root causes and solutions.

## OTHER CONSIDERATIONS (Agent Behavior Rules):

- Never assume missing context—if uncertain, halt and request clarification.
- Never hallucinate libraries, functions, or APIs—only use known, verified packages.
- Always confirm file paths and module names exist before referencing them.
- Use `python_dotenv` and `load_env()` for environment variables.
- Include a `.env.example` and a README with setup instructions if needed.
- Document all non-obvious decisions in code comments or docstrings for future agent runs.
