
## FEATURE (Agent Mission & Priorities):

Thoroughly research and implement a comprehensive API system for pocketbase in this python program. Use pocketbase's REST API, create wrapper API for its commands. Use the `existing packages/pocketbase_backend`. Go beyond what I have detailed here, as thorough as possible.

Keep in mind the composable, highly modular workflow of uv workspaces: #fetch https://docs.astral.sh/uv/concepts/projects/workspaces

## DOCUMENTATION (Critical Context):

#fetch https://pocketbase.io/docs/
#githubRepo pocketbase/pocketbase

## VALIDATION & SELF-CHECKS (Validation Gates):

- Every new function, class, or route MUST have Pytest unit tests (expected use, edge, and failure cases).
- Run all tests, linting (`ruff`), and type checks (`mypy`) after every change. Never consider a task complete until all validation gates pass.
- If a validation gate fails, debug, fix, and re-run until it passes. Document root causes and solutions.

## OTHER CONSIDERATIONS (Agent Behavior Rules):

- Never assume missing context—if uncertain, halt and request clarification.
- Never hallucinate libraries, functions, or APIs—only use known, verified packages.
- Always confirm file paths and module names exist before referencing them.
- Use `python_dotenv` and `load_env()` for environment variables.
- Include a `.env.example` and a README with setup instructions if needed.
- Document all non-obvious decisions in code comments or docstrings for future agent runs.
