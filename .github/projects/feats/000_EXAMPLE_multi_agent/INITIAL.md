
## FEATURE (Agent Mission & Priorities):

- Build a robust, production-grade Pydantic AI agent that can autonomously use another Pydantic AI agent as a tool.
- The primary agent (Research Agent) must be able to delegate tasks to a subagent (Email Draft Agent) and coordinate workflows end-to-end.
- Provide a CLI for user interaction, ensuring clear streaming output and tool invocation visibility.
- Integrate with Gmail (for email drafts) and Brave API (for research), handling all authentication and error cases autonomously.

## EXAMPLES (Context Awareness):

- Study all files in the `examples/` folder to extract patterns for agent composition, CLI structure, and provider/tool integration.
- Use `examples/cli.py` as a reference for CLI streaming and user experience.
- Use `examples/agent/` for best practices in agent modularity, dependency management, and tool registration.
- Do NOT copy code directly—extract patterns and adapt for this project’s requirements.

## DOCUMENTATION (Critical Context):

- Pydantic AI documentation: https://ai.pydantic.dev/
- Reference all relevant API docs for Gmail and Brave.

## VALIDATION & SELF-CHECKS (Validation Gates):

- Every new function, class, or route MUST have Pytest unit tests (expected use, edge, and failure cases).
- Run all tests, linting (`ruff`), and type checks (`mypy`) after every change. Never consider a task complete until all validation gates pass.
- If a validation gate fails, debug, fix, and re-run until it passes. Document root causes and solutions.

## OTHER CONSIDERATIONS (Agent Behavior Rules):

- Never assume missing context—if uncertain, halt and request clarification.
- Never hallucinate libraries, functions, or APIs—only use known, verified packages.
- Always confirm file paths and module names exist before referencing them.
- Use `python_dotenv` and `load_env()` for environment variables.
- Include a `.env.example` and a README with setup instructions, including Gmail and Brave configuration.
- Document all non-obvious decisions in code comments or docstrings for future agent runs.
