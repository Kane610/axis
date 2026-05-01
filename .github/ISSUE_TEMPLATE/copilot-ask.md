---
name: Copilot Ask
about: Request a feature, fix, or refactor using Copilot
title: "[COPILOT] "
labels: copilot
---

## What should Copilot do?

[Clear description: implement, fix, refactor, review, etc.]

## Constraints

- [ ] Preserve backward compatibility
- [ ] No changes to public API
- [ ] Keep to one file/module
- [ ] Minimal change (preserve existing behavior)
- [ ] Reuse existing fixtures and patterns

## Acceptance Criteria

- [ ] All checks pass (`ruff check`, `ruff format`, `mypy`, `pytest`)
- [ ] Coverage maintained ≥95% (or specify affected files)
- [ ] Tests added/updated for changed code
- [ ] Follows conventions: enum `_missing_`, input normalization, XML parsing guards

## Context

[Paste relevant code, architecture notes, error traces, or API documentation]

## Verification Command

```bash
# Run these after Copilot work:
uv run ruff check .
uv run ruff format --check .
uv run mypy axis
uv run pytest tests/test_<area>.py -v --cov=axis.<area> --cov-report=term-missing
```

## Related Issues

Relates to #[issue number] (if applicable)
