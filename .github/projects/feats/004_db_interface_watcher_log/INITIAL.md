
## FEATURE (Agent Mission & Priorities):

Thoroughly research and implement a comprehensive interface between the [Pocketbase backend package](/packages/pocketbase_backend/) and the [Rename watcher](/packages/rename_watcher/). You will implement a logically structured and linked table that represents generic files and dirs, the parent/child relationships between them, and the logs of the renames/movements provided by the rename watcher. The code for this interface will go [here](/src/blendman/), but make sure you use a new highly modular architecture.

Keep in mind the composable, highly modular workflow of uv workspaces: #fetch https://docs.astral.sh/uv/concepts/projects/workspaces

Remember, initially, you will not implement any real code, you have been assigned to document, research, plan, create example snippets, create the PRD.md

## DOCUMENTATION (Critical Context):

#fetch https://pocketbase.io/docs/
#githubRepo pocketbase/pocketbase

## VALIDATION & SELF-CHECKS (Validation Gates):

- Every new function, class, or route MUST have Pytest unit tests (expected use, edge, and failure cases).
- Run all tests (`dev.py`) after every change. Never consider a task complete until all validation gates pass.
- If a validation gate fails, debug, fix, and re-run until it passes. Document root causes and solutions.

## OTHER CONSIDERATIONS (Agent Behavior Rules):

- Never assume missing context—if uncertain, halt and request clarification.
- Never hallucinate libraries, functions, or APIs—only use known, verified packages.
- Always confirm file paths and module names exist before referencing them.
- Use `python_dotenv` and `load_env()` for environment variables.
- Include a `.env.example` and a README with setup instructions if needed.
- Document all non-obvious decisions in code comments or docstrings for future agent runs.
