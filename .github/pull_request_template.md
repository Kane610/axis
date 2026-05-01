## What does this PR do?

[One-sentence summary, e.g., "Adds new PTZ handler with PARAM_CGI_FALLBACK support"]

## Architecture Layer(s)

- [ ] Models (`axis/models/`)
- [ ] Interfaces (`axis/interfaces/`)
- [ ] Orchestration (`axis/device.py`, `axis/interfaces/vapix.py`)
- [ ] Tests

## Type of Change

- [ ] New feature (handler, interface, model)
- [ ] Bug fix (minimal, targeted)
- [ ] Refactor (no behavior change)
- [ ] Documentation

## Related Issues

Closes #[issue number] (if applicable)

## Verification Checklist

- [ ] `uv run ruff check .` passes
- [ ] `uv run ruff format --check .` passes
- [ ] `uv run mypy axis` passes
- [ ] `uv run pytest` passes (coverage ≥95%)
- [ ] New tests added for new code (100% coverage for new code)
- [ ] Commit hooks modified files? If so, re-staged and re-ran checks
- [ ] No unrelated code/formatting changes
- [ ] Follows conventions: enum `_missing_` fallback, input normalization, XML parsing guards

## Notes for Reviewers

[Context for reviewers: what to focus on, known limitations, decisions made, or why this approach was chosen]
