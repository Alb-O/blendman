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
    "vscodeAPI",
  ]
description: "Create a PRD (Product Requirements Document)"
---

# Create PRD

You have been given the end-to-end task of creating a PRD (Product Requirements Document), which must include:

- Complete context and documentation
- Implementation steps with validation
- Error handling patterns
- Test requirements

## Feature: ${input:feat}

Your workspace for this task is `.github/projects/feats/${input:feat}`, make sure you save all your workings and output in here.

Intelligently interpret the `.github/projects/feats/${input:feat}/INITIAL.md` file.

Generate a complete PRD for general feature implementation with thorough research. Ensure context is passed to the AI agent to enable self-validation and iterative refinement. Read the feature file first to understand what needs to be created, how the examples provided help, and any other considerations.

The AI agent only gets the context you are appending to the PRD and training data. Assume the AI agent has access to the codebase and the same knowledge cutoff as you, so its important that your research findings are included or referenced in the PRD. The Agent has Websearch capabilities, so pass urls to documentation and examples. Be extremely specifc.

## Research Process

1. **Codebase Analysis**

   - Search for similar feats/patterns in the codebase
   - Identify files to reference in PRD
   - Note existing conventions to follow
   - Check test patterns for validation approach

2. **External Research**

   - Search for similar feats/patterns online
   - Library documentation (include specific URLs)
   - Implementation examples (GitHub/StackOverflow/blogs)
   - Best practices and common pitfalls

3. **User Clarification** (if needed)
   - Specific patterns to mirror and where to find them?
   - Integration requirements and where to find them?

## PRD Generation

Using `.github/projects/templates/PRD.md` as template:

### Critical Context to Include and pass to the AI agent as part of the PRD

- **Documentation**: URLs with specific sections
- **Code Examples**: Real snippets from codebase
- **Gotchas**: Library quirks, version issues
- **Patterns**: Existing approaches to follow

### Implementation Blueprint

- Start with pseudocode showing approach
- Reference real files for patterns
- Include error handling strategy
- list tasks to be completed to fullfill the PRD in the order they should be completed

### Validation Gates e.g. for Python:

```bash
uv pip install -r requirements.txt
uv venv
uv run ruff check .
uv run ruff format .
uv run mypy .
uv run pytest
```

**CRITICAL: RESEARCH AND EXPLORE THE CODEBASE BEFORE YOU START WRITING THE PRD**

**ULTRATHINK ABOUT THE PRD AND PLAN YOUR APPROACH THEN START WRITING THE PRD**

## Output

Save as: `.github/projects/feats/${input:feat}/PRD.md`

## Quality Checklist

- [ ] All necessary context included
- [ ] Validation gates are executable by AI
- [ ] References existing patterns
- [ ] Clear implementation path
- [ ] Error handling documented

Score the PRD on a scale of 1-10 (confidence level to succeed in one-pass implementation by passing it to a code assistant)

Remember: The goal is one-pass implementation success through comprehensive context.
