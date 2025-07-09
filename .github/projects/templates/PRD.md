
name: "Base PRD Template v2 - Agent Autonomy & Validation"

## Purpose
This template is optimized for autonomous coding agents to deliver robust, production-grade features through self-validation, error recovery, and iterative improvement. The agent must use all available context, never make assumptions, and ensure all validation gates pass before considering a task complete.

## Core Principles
1. **Agent Autonomy**: Act without human intervention, self-correct, and iterate until all validation gates pass.
2. **Context Awareness**: Include ALL necessary documentation, examples, and caveats. Never assume missing context.
3. **Validation Loops**: Provide and execute all tests/lints/type checks, and fix issues until passing.
4. **Explicitness**: Prefer clarity and explicit documentation over brevity. Document all non-obvious decisions.
5. **Global rules**: Always follow all rules in CLAUDE.md.

## Goal (Agent Mission & Priorities)
[Describe what needs to be built. Be explicit about the end state, required behaviors, and validation gates.]

## Why
- [Business value and user impact]
- [Integration with existing features]
- [Problems this solves and for whom]


## What (Explicit Agent Behaviors)
[Describe user-visible behavior and technical requirements. Specify how the agent should self-validate and handle errors.]

### Success Criteria (Validation Gates)
- [ ] [Specific measurable outcomes and validation gates. All must be self-checked and iterated until passing.]

## All Needed Context (Critical Context Awareness)

### Documentation & References (list all context needed to implement the feature)
```yaml
# MUST READ - Include these in your context window
- url: [Official API docs URL]
  why: [Specific sections/methods you'll need]
  
- file: [.github/projects/feats/XXX_feat_name/examples/example.py]
  why: [Pattern to follow, gotchas to avoid]
  
- doc: [Library documentation URL] 
  section: [Specific section about common pitfalls]
  critical: [Key insight that prevents common errors]

- docfile: [.github/projects/feats/XXX_feat_name/some-doc.md]
  why: [docs that the user has pasted in to the project]

```

### Current Codebase tree (run `tree` in the root of the project) to get an overview of the codebase
```bash

```

### Desired Codebase tree with files to be added and responsibility of file
```bash

```

### Known Gotchas of our codebase & Library Quirks (Agent Self-Validation)
```python
# CRITICAL: [Library name] requires [specific setup]
# Example: FastAPI requires async functions for endpoints
# Example: This ORM doesn't support batch inserts over 1000 records
# Example: We use pydantic v2 and  
# CRITICAL: If any validation gate fails, debug, fix, and re-run until it passes. Document root causes and solutions.
```

## Implementation Blueprint

  - MIRROR pattern from: src/similar_feature.py

## Validation Loop (Agent Self-Validation & Iteration)

### Level 1: Syntax & Style
```bash
./dev.py
# Expected: No errors or warnings. If errors/warnings, analyze, fix, and re-run until passing.
```

### Level 2: Unit Tests each new feature/file/function use existing test patterns
```python
# CREATE test_new_feature.py with these test cases:
            return await external_api.call(validated)
        
        result = await _inner()
    
    # PATTERN: Standardized response format
    return format_response(result)  # see src/utils/responses.py
```

### Integration Points
```yaml
DATABASE:
  - migration: "Add column 'feature_enabled' to users table"
  - index: "CREATE INDEX idx_feature_lookup ON users(feature_id)"
  
CONFIG:
  - add to: config/settings.py
```

```bash
# Run and iterate until passing:
uv run pytest
# If failing: Analyze, fix, and re-run until all tests pass. Document root causes and solutions.
```

## Final validation Checklist (Agent Self-Validation)
- [ ] All tests pass
- [ ] No linting errors (`ruff check .`)
- [ ] No type errors (`mypy .`)
- [ ] Manual test successful: [specific curl/command]
- [ ] Error cases handled gracefully and are documented
- [ ] Logs are informative but not verbose
- [ ] Documentation updated if needed
- [ ] All validation gates are self-checked and iterated until passing
  - pattern: "FEATURE_TIMEOUT = int(os.getenv('FEATURE_TIMEOUT', '30'))"
  
ROUTES:
  - add to: src/api/routes.py  
  - pattern: "router.include_router(feature_router, prefix='/feature')"
```

## Validation Loop

### Level 1: Syntax & Style
```bash
# Run these FIRST - fix any errors before proceeding
ruff check .
ruff format .
mypy .

# Expected: No errors or warnings. If errors/warnings, fix it immediately.
```

### Level 2: Unit Tests each new feature/file/function use existing test patterns
```python
# CREATE test_new_feature.py with these test cases:
def test_happy_path():
    """Basic functionality works"""
    result = new_feature("valid_input")
    assert result.status == "success"

def test_validation_error():
    """Invalid input raises ValidationError"""
    with pytest.raises(ValidationError):
        new_feature("")

def test_external_api_timeout():
    """Handles timeouts gracefully"""
    with mock.patch('external_api.call', side_effect=TimeoutError):
        result = new_feature("valid")
        assert result.status == "error"
        assert "timeout" in result.message
```

```bash
# Run and iterate until passing:
uv pip install pytest
uv run pytest
# If failing: Read error, understand root cause, fix code, re-run (never mock to pass)
```

## Final validation Checklist
- [ ] All tests pass
- [ ] No linting errors (`ruff check .`)
- [ ] No type errors (`mypy .`)
- [ ] Manual test successful: [specific curl/command]
- [ ] Error cases handled gracefully
- [ ] Logs are informative but not verbose
- [ ] Documentation updated if needed

---

## Anti-Patterns to Avoid
- ❌ Don't create new patterns when existing ones work
- ❌ Don't skip validation because "it should work"  
- ❌ Don't ignore failing tests - fix them
- ❌ Don't use sync functions in async context
- ❌ Don't hardcode values that should be config
- ❌ Don't catch all exceptions - be specific