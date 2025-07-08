---
mode: "agent"
tools: [
    "changes",
    "codebase",
    "editFiles",
    "extensions",
    "fetch",
    "findTestFiles",
    "githubRepo",
    "new",
    "openSimpleBrowser",
    "problems",
    "runCommands",
    "runNotebooks",
    "runTasks",
    "runTests",
    "search",
    "searchResults",
    "terminalLastCommand",
    "terminalSelection",
    "testFailure",
    "usages",
  ]
description: "Execute a PRD (Product Requirements Document)"
---

# Execute PRD

You have been given the end-to-end task of implementing a feature according to a PRD (Product Requirements Document), which must include:

- Complete context and documentation
- Implementation steps with validation
- Error handling patterns
- Test requirements

Your documents, planning, and tasks for this feature will be in `.github/projects/feats/${input:feat}/`. The main PRD File is `.github/projects/feats/${input:feat}/PRD.md`.

## Execution Process

1. **Read the specified PRD file**

   - Understand all context and requirements
   - Follow all instructions in the PRD and extend the research if needed
   - Ensure you have all needed context to implement the PRD fully
   - Do more web searches and codebase exploration as needed

2. **ULTRATHINK**

   - Think hard before you execute the plan. Create a comprehensive plan addressing all requirements.
   - Break down complex tasks into smaller, manageable steps.
   - Use the `.github/projects/feats/${input:feat}/NOTEPAD.md` file to plan, design, brainstorm, and track tasks.
   - Identify implementation patterns from existing code to follow.

3. **Execute the plan**

   - Execute the PRD
   - Implement all the code

4. **Validate**

   - Run each validation command
   - Fix any failures
   - Re-run until all pass

5. **Complete**

   - Ensure all checklist items done
   - Run final validation suite
   - Report completion status
   - Read the PRD again to ensure you have implemented everything

6. **Reference the PRD**
   - You can always reference the PRD again if needed

Note: If validation fails, use error patterns in PRD to fix and retry.

## Project Awareness & Context

- **Always read relevant `.md` files** at the start of a new conversation to understand the project's architecture, goals, style, and constraints. `INITIAL.md` should be legacy at this stage and can be ignored.
- **Check `NOTEPAD.md`** before starting a new task. If the task isn’t listed there, add it with a brief description and a timestamp. Use the `NOTEPAD.md` for tracking TODOs, brainstorming, designing architecture, etc.
- **Use venv_linux** (the virtual environment) whenever executing Python commands, including for unit tests.

### Task Completion

- **Mark completed tasks in `NOTEPAD.md`** immediately after finishing them.
- Add new sub-tasks or TODOs discovered during development.

### Documentation & Explainability

- **Update the main `README.md`** when new features are added, dependencies change, or setup steps are modified. Keep it brief, minimal, functional.
- **Comment non-obvious code** and ensure everything is understandable to a mid-level developer.
- When writing complex logic, **add an inline `# Reason:` comment** explaining the why, not just the what.

### Version Control

- **Commit changes frequently** with clear, functional messages. Make sure there are no lint errors or test failures before committing.
- **Always commit to the feature branch** e.g. `feat/XXX-feat-name` and not the main branch unless told otherwise. Create this branch if it does not exist.
