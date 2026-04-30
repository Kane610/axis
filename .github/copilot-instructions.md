# Project Guidelines

## Build And Test

- Use the project environment managed by `uv` (see `README.md`).
- Preferred bootstrap: `./setup.sh`.
- Python requirement is `>=3.14.0` (see `pyproject.toml`).
- Standard full checks:
	- `uv run ruff check .`
	- `uv run ruff format --check .`
	- `uv run mypy axis`
	- `uv run pytest`
- After code changes, run targeted tests for touched files first; run broader validation when shared behavior is affected.

## Architecture

- Keep boundaries clear:
	- `axis/interfaces/` contains API handlers and transport-facing logic.
	- `axis/models/` contains request/response models, enums, and parsing helpers.
	- `axis/device.py` and `axis/interfaces/vapix.py` orchestrate device and handler lifecycle.
- Follow the phase-based handler initialization model documented in `README.md` (`API_DISCOVERY`, `PARAM_CGI_FALLBACK`, `APPLICATION`).
- Prefer boundary normalization for incoming values (for example, enum coercion and defaults in model constructors/post-init).

## Conventions

- Prefer minimal, targeted changes that preserve existing behavior unless the task explicitly requires a behavior change.
- Do not modify unrelated code, formatting, or tests.
- Never revert user changes unless explicitly asked.
- Before changing patterns or APIs, inspect nearby code and follow existing local style.
- Prefer root-cause fixes over workarounds.
- For enums and external inputs, preserve existing defensive normalization patterns (for example `_missing_` fallbacks and constructor normalization).
- For event/XML handling, preserve namespace-aware parsing and root-shape guards instead of assuming a fixed payload shape.

## Testing Conventions

- Add or update focused tests in the nearest relevant `tests/` module when behavior changes.
- Reuse existing async fixtures and HTTP mocking patterns from `tests/conftest.py`.
- If tests, typing, or linting fail for unrelated pre-existing reasons, report that clearly instead of fixing unrelated code.
- Expect commit hooks to run Ruff, Ruff format, and mypy; if hooks modify files, re-stage and re-run checks.

## Git Workflow

- Never create commits on the `master` branch.
- Never push commits directly to the `master` branch.
- Before any commit or push, check the current branch and confirm it is not `master`.
- If work is currently on `master`, create or switch to a feature branch before committing.
- If asked to commit or push from `master`, explain that the change must go through a feature branch and pull request.
- For any requested git operation, verify branch state first and summarize what will happen before committing or pushing.
# Project Guidelines

## Build And Test

- Use the project environment managed by `uv` (see `README.md`).
- Preferred bootstrap: `./setup.sh`.
- Python requirement is `>=3.14.0` (see `pyproject.toml`).
- Standard full checks:
	- `uv run ruff check .`
	- `uv run ruff format --check .`
	- `uv run mypy axis`
	- `uv run pytest`
- After code changes, run targeted tests for touched files first; run broader validation when shared behavior is affected.

## Architecture

- Keep boundaries clear:
	- `axis/interfaces/` contains API handlers and transport-facing logic.
	- `axis/models/` contains request/response models, enums, and parsing helpers.
	- `axis/device.py` and `axis/interfaces/vapix.py` orchestrate device and handler lifecycle.
- Follow the phase-based handler initialization model documented in `README.md` (`API_DISCOVERY`, `PARAM_CGI_FALLBACK`, `APPLICATION`).
- Prefer boundary normalization for incoming values (for example, enum coercion and defaults in model constructors/post-init).

## Conventions

- Prefer minimal, targeted changes that preserve existing behavior unless the task explicitly requires a behavior change.
- Do not modify unrelated code, formatting, or tests.
- Never revert user changes unless explicitly asked.
- Before changing patterns or APIs, inspect nearby code and follow existing local style.
- Prefer root-cause fixes over workarounds.
- For enums and external inputs, preserve existing defensive normalization patterns (for example `_missing_` fallbacks and constructor normalization).
- For event/XML handling, preserve namespace-aware parsing and root-shape guards instead of assuming a fixed payload shape.

## Testing Conventions

- Add or update focused tests in the nearest relevant `tests/` module when behavior changes.
- Reuse existing async fixtures and HTTP mocking patterns from `tests/conftest.py`.
- If tests, typing, or linting fail for unrelated pre-existing reasons, report that clearly instead of fixing unrelated code.
- Expect commit hooks to run Ruff, Ruff format, and mypy; if hooks modify files, re-stage and re-run checks.

## Git Workflow

- Never create commits on the `master` branch.
- Never push commits directly to the `master` branch.
- Before any commit or push, check the current branch and confirm it is not `master`.
- If work is currently on `master`, create or switch to a feature branch before committing.
- If asked to commit or push from `master`, explain that the change must go through a feature branch and pull request.
- For any requested git operation, verify branch state first and summarize what will happen before committing or pushing.