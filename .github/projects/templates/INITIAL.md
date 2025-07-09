
## FEATURE (Agent Mission & Priorities):

[Describe the feature to be built. Be explicit about the end goal, required behaviors, and success criteria.]

## EXAMPLES (Context Awareness):

[List and explain all relevant examples in the `examples/` folder. Specify what patterns or best practices should be extracted and adapted.]

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
