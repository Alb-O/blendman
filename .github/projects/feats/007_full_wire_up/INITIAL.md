
## FEATURE (Agent Mission & Priorities):

This project contains a number of modules and features, but they are hardly wired up at all. Examine the existing functionality and stubs, and flesh out a proper integration between all components, e.g. the full workflow of watching for renames/moves, logging it to the database tables, etc. Use `uv run pymermaider -o mermaid .` to generate diagrams that show the connections between the components in the project. I have already ran it on the main `blendman` project and it's packages, see [this output folder](/mermaid/). You can see at the moment almost nothing is wired. Remember, you are to create sophisticated and detailed documentation and the PRD.md first before implementing any real code.

## DOCUMENTATION (Critical Context):

mermaid/blendman.md
#fetch https://pocketbase.io/docs/
#fetch https://docs.astral.sh/uv/concepts/projects/workspaces/

## VALIDATION & SELF-CHECKS (Validation Gates):

- Every new function, class, or route MUST have Pytest unit tests (expected use, edge, and failure cases).
- Run `./dev.sh` or `./dev.ps1` after every major change. Never consider a task complete until all validation gates pass.
- If a validation gate fails, debug, fix, and re-run until it passes. Document root causes and solutions.

## OTHER CONSIDERATIONS (Agent Behavior Rules):

- Never assume missing context—if uncertain, halt and request clarification.
- Never hallucinate libraries, functions, or APIs—only use known, verified packages.
- Always confirm file paths and module names exist before referencing them.
- Use `python_dotenv` and `load_env()` for environment variables.
- Include a `.env.example` and a README with setup instructions if needed.
- Document all non-obvious decisions in code comments or docstrings for future agent runs.
