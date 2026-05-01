# Using Copilot with Axis

This guide helps you get the most out of Copilot when contributing to the Axis library.

## Quick Links

- **Architecture:** [README.md](README.md) — Phase-based handler initialization
- **Conventions:** [CONTRIBUTING.md](CONTRIBUTING.md) — Coding patterns, tests, fixtures
- **Project rules:** [.github/copilot-instructions.md](.github/copilot-instructions.md) — Build, test, git workflow
- **Request templates:** [.github/copilot-instructions.md](.github/copilot-instructions.md#how-to-ask-copilot-for-high-quality-work) — High-quality ask structure
- **Review agents:** [.github/agents/](.github/agents/) — Code review and validation
- **PR template:** [.github/pull_request_template.md](.github/pull_request_template.md)

## The Axes of Work

### 1. Adding a New Handler (Feature)

**What:** Implement a new Axis device API.

**Steps:**
1. Create a model in `axis/models/<name>.py` with dataclasses and enums (include `_missing_` fallback).
2. Create a handler in `axis/interfaces/<name>.py` extending `ApiHandler`.
3. Register it on `Vapix` in `axis/interfaces/vapix.py`.
4. Add tests in `tests/test_<name>.py` using fixtures from `tests/conftest.py`.

**Copilot request:**
```
I need to add a new handler for [feature].

[CONTEXT]
The VAPIX API is at [endpoint]. The response looks like [example JSON].
This handler should participate in the [API_DISCOVERY / PARAM_CGI_FALLBACK / APPLICATION] phase.

[TASK]
1. Add model in axis/models/[name].py with request/response dataclasses
2. Add handler in axis/interfaces/[name].py extending ApiHandler
3. Register handler on Vapix in axis/interfaces/vapix.py
4. Add tests in tests/test_[name].py using aiohttp_mock_server or http_route_mock

[CONSTRAINTS]
- 100% test coverage for new code
- All enums have _missing_ fallback
- Input normalization in __post_init__
- Preserve existing behavior

[VERIFICATION]
uv run ruff check .
uv run ruff format --check .
uv run mypy axis
uv run pytest tests/test_[name].py -v --cov=axis.[name] --cov-report=term-missing
```

**Then:**
```
@axis-review: Please use Axis Review to check the handler for regressions and test gaps.
```

### 2. Fixing a Bug

**What:** Fix a specific issue in an existing handler or parsing logic.

**Copilot request:**
```
I found a bug in [area]:

[PROBLEM]
[Describe the issue, error trace, or unexpected behavior]

[ROOT CAUSE (if known)]
[What's causing it]

[TASK]
Fix [area] to [desired behavior].

[CONSTRAINTS]
- Minimal, targeted fix (preserve existing behavior)
- Update tests if behavior changes
- No unrelated changes

[VERIFICATION]
uv run pytest tests/test_[area].py -v
```

### 3. Adding Tests

**What:** Improve test coverage for existing code.

**Copilot request:**
```
Add tests for [area] to improve coverage.

[CONTEXT]
Current coverage: [%]. Missing coverage: [specific function/branch].
Tests live in tests/test_[area].py.
Use fixtures: aiohttp_mock_server or http_route_mock (see CONTRIBUTING.md for examples).

[TASK]
Add tests for:
1. [Happy path]
2. [Error case]
3. [Edge case]

[CONSTRAINTS]
- 100% coverage for new/modified code
- Reuse existing fixtures
- Follow existing test patterns

[VERIFICATION]
uv run pytest tests/test_[area].py -v --cov=axis.[area] --cov-report=term-missing
```

### 4. Code Review

**What:** Have Copilot review your code for issues and regressions.

**Copilot request (use Axis Review agent):**
```
@axis-review: Please review my changes in [files]:

[FOCUS AREAS]
- Handler initialization phase behavior
- Enum handling and _missing_ fallback
- XML parsing safety
- Test coverage gaps

[PASS/FAIL CRITERIA]
- PASS: No regressions, behavior matches spec, tests cover changes
- FAIL: Breaks initialization order, missing enum fallback, or untested error paths
```

**Copilot request (use Axis Review Verify agent):**
```
@axis-review-verify: Please validate my PR:

[CHANGED FILES]
[list files]

[RUN]
- uv run pytest tests/test_<area>.py
- uv run ruff check axis/
- uv run mypy axis
```

## Common Pitfalls

| Pitfall | Fix |
|---|---|
| "Coverage is low" | Ensure new code has 100% coverage. Use `--cov=axis.<module> --cov-report=term-missing` to see gaps. |
| "Enum crashes on unknown value" | Add `_missing_` classmethod that returns `.UNKNOWN` and logs a debug warning. |
| "XML parsing assumes fixed structure" | Use `xmltodict.parse(..., process_namespaces=True)` and check root shape before accessing. |
| "Handler doesn't initialize" | Check `handler_groups` and `should_initialize_in_group()` match the initialization phase. |
| "Ruff/mypy/pytest fail" | Run locally before requesting review. Fix issues in your request context. |
| "Pre-commit hook modifies files" | Re-stage and re-commit: `git add -u && git commit`. |

## Useful Commands

```bash
# Setup
./setup.sh

# Full validation
uv run ruff check .
uv run ruff format --check .
uv run mypy axis
uv run pytest

# Targeted validation
uv run pytest tests/test_<area>.py -v
uv run ruff check axis/<file>.py
uv run mypy axis.<module>

# Coverage report
uv run pytest --cov=axis --cov-report=html
# Open htmlcov/index.html

# Pre-commit hooks
uv run pre-commit install
```

## Next Steps

1. Read [CONTRIBUTING.md](CONTRIBUTING.md) for detailed conventions and architecture.
2. Explore [.github/copilot-instructions.md](.github/copilot-instructions.md) for project-wide rules.
3. Check [.github/agents/](.github/agents/) for review agent details.
4. Review the [request template](.github/copilot-instructions.md#request-template) before opening an issue.

## Questions?

If you run into issues, check:
1. [CONTRIBUTING.md](CONTRIBUTING.md) — conventions and patterns
2. [tests/conftest.py](tests/conftest.py) — fixture details
3. Existing test modules in `tests/` — see how similar work is tested
4. [.github/copilot-instructions.md](.github/copilot-instructions.md#troubleshooting) — troubleshooting guide
