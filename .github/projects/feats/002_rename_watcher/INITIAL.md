
## FEATURE (Agent Mission & Priorities):

Implement a highly intelligent, robust system of recursively monitoring directories for file/dir renames and moves. The watcher system needs to be able to identify files post rename/movement actions and determine the from/to relationship in real time. This implementation will be its own package like the existing pocketbase_backend.

## EXAMPLES (Context Awareness):

use #gitHub tool to study `mnaoumov/obsidian-external-rename-handler`, it is written in ts but the concepts will apply here.

## DOCUMENTATION (Critical Context):

#fetch https://python-watchdog.readthedocs.io/en/stable/

#fetch https://docs.astral.sh/uv/concepts/projects/workspaces/#workspace-sources (for understanding uv workspaces and the project structure)

## VALIDATION & SELF-CHECKS (Validation Gates):

- Every new function, class, or route MUST have Pytest unit tests (expected use, edge, and failure cases).
- Run `./dev.sh` after every major change. Never consider a task complete until all validation gates pass.
- If a validation gate fails, debug, fix, and re-run until it passes. Document root causes and solutions.

## OTHER CONSIDERATIONS (Agent Behavior Rules):

- Never assume missing context—if uncertain, halt and request clarification.
- Never hallucinate libraries, functions, or APIs—only use known, verified packages.
- Always confirm file paths and module names exist before referencing them.
- Use `python_dotenv` and `load_env()` for environment variables.
- Include a `.env.example` and a README with setup instructions if needed.
- Document all non-obvious decisions in code comments or docstrings for future agent runs.
