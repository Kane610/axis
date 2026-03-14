When performing git operations in this repository:

- Never create commits on the `master` branch.
- Never push commits directly to the `master` branch.
- Before any commit or push, check the current branch and confirm it is not `master`.
- If work is currently on `master`, create or switch to a feature branch before committing.
- If asked to commit or push from `master`, explain that the change must go through a feature branch and pull request.

When working in this repository:

- Prefer minimal, targeted changes that preserve existing behavior unless the task explicitly requires a behavior change.
- Do not modify unrelated code, formatting, or tests.
- Never revert user changes unless explicitly asked.
- Before changing patterns or APIs, inspect nearby code and follow the existing style and conventions.
- For configuration and model inputs, normalize values at construction boundaries when appropriate.
- When changing behavior, add or update focused tests in the nearest relevant test module.
- After code changes, run targeted tests for touched files; run broader validation only when the change affects shared behavior.
- If tests, typing, or linting fail for unrelated pre-existing reasons, report that clearly instead of trying to fix unrelated issues.
- Prefer root-cause fixes over workarounds.
- If a request involves git operations, verify branch state first and summarize what will happen before committing or pushing.

When validating changes in this repository:

- Run targeted tests for touched files after code changes.
- Run broader tests only when shared behavior is affected.
- Expect commit hooks to run Ruff, Ruff format, and mypy.
- If hooks modify files, re-stage them and retry the commit.
- If validation fails for unrelated pre-existing reasons, report that clearly and do not fix unrelated code unless asked.
- Prefer using the project's configured environment when running tests or mypy.