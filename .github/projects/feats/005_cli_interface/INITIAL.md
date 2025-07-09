
## FEATURE (Agent Mission & Priorities):

Create a comprehensive cli interface for the blendman program, that bridges the functionality of the [backend](/packages/pocketbase_backend/), the [watcher](/packages/rename_watcher/), the interface between the two. Controls for initiating recursive directory watching with support for the [toml config](/packages/rename_watcher/src/rename_watcher/config.py), initiating a config file at the root, auto-detecting, etc. Use the most idiomatic and comprehensive strategies for typical cli programs of this nature (multiple sub commands, good readable output (you may use a library for this if needed), etc.)

Remember that you are to create the comprehensive plan and documentation and snippets, not implement the code yet.

## DOCUMENTATION (Critical Context):

[List all documentation, API references, and resources that must be used. Include URLs and file paths.]

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
