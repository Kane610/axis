# Contributing

Thank you for considering a contribution. This document covers how to set up the development environment, run checks, write tests, and submit changes.

## Environment setup

Python 3.14 and [`uv`](https://docs.astral.sh/uv/) are required.

The easiest path is the bootstrap script, which installs `uv` if not present and provisions Python 3.14 automatically:

```bash
./setup.sh
```

Or provision manually:

```bash
uv python install 3.14
uv sync --python 3.14 --all-extras
```

Dependencies are locked via `uv.lock`. Regenerate only when dependency inputs in `pyproject.toml` change:

```bash
uv lock
```

## Running checks

Always run the full suite before opening a pull request:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy axis
uv run pytest
```

For faster iteration, target only the files you changed:

```bash
uv run pytest tests/test_<area>.py
uv run ruff check axis/<file>.py
```

Run broader checks only when your change affects shared behavior (for example, base classes, event parsing, or configuration).

Coverage must stay at or above 95% overall. All new code you introduce must have 100% test coverage. `axis/stream_transport.py` is excluded from the threshold. `TYPE_CHECKING` blocks are automatically excluded.

## Pre-commit hooks

The repository ships local hooks that run `ruff check --fix`, `ruff format`, and `mypy` on every commit. Install them after setup:

```bash
uv run pre-commit install
```

If a hook modifies files, stage the changes and re-run the commit:

```bash
git add -u && git commit
```

The hooks require an active `.venv` — run `./setup.sh` or `uv sync --all-extras` first if they report a missing environment.

## Architecture overview

The library is split into three layers. Keep changes inside the appropriate boundary:

| Layer | Path | Responsibility |
|-------|------|----------------|
| Models | `axis/models/` | Request/response dataclasses, enums, XML/event parsing |
| Interfaces | `axis/interfaces/` | API handlers, transport-facing logic, VAPIX calls |
| Orchestration | `axis/device.py`, `axis/interfaces/vapix.py` | Device lifecycle, handler registry, phase-based initialization |

### Handler initialization phases

Handlers declare the phases they participate in via `handler_groups` on the `ApiHandler` subclass. The three phases are:

- `API_DISCOVERY` — initialized after API discovery completes.
- `PARAM_CGI_FALLBACK` — initialized from parameter CGI support when not listed in API discovery.
- `APPLICATION` — initialized after application loading.

Override `should_initialize_in_group()` to customize eligibility within a phase. See [`axis/interfaces/light_control.py`](axis/interfaces/light_control.py) for a concrete fallback example.

## Adding a new API handler

1. Add a model in `axis/models/<name>.py` — dataclass(es), enums with `_missing_` fallbacks, and any parsing helpers.
2. Add a handler in `axis/interfaces/<name>.py` — extend `ApiHandler`, declare `api_id`, `handler_groups`, and implement `_api_request()`.
3. Register the handler on `Vapix` in [`axis/interfaces/vapix.py`](axis/interfaces/vapix.py).
4. Add tests in `tests/test_<name>.py` using the async fixture and `respx` mocking patterns from [`tests/conftest.py`](tests/conftest.py).

## Coding conventions

### Enums

Always provide a `_missing_` fallback that returns a safe sentinel (`.UNKNOWN`) and logs a debug-level warning for unrecognized values. Do not raise:

```python
@classmethod
def _missing_(cls, value: object) -> MyEnum:
    """Set default enum member if an unknown value is provided."""
    LOGGER.debug("Unsupported value %s", value)
    return MyEnum.UNKNOWN
```

### Input normalization

Normalize and coerce enum fields at the constructor boundary, typically in `__post_init__`:

```python
def __post_init__(self) -> None:
    self.web_proto = WebProtocol(self.web_proto)
    self.auth_scheme = AuthScheme(self.auth_scheme)
```

### XML and event parsing

- Use `xmltodict.parse()` with `process_namespaces=True` and the relevant `namespaces` mapping.
- Always normalize the parsed root to a `dict` before traversing — never assume a fixed shape.
- Use the `traverse()` helper in [`axis/models/event.py`](axis/models/event.py) for nested key access.

### Type annotations

All code must pass strict `mypy` (see `[tool.mypy]` in `pyproject.toml`). Key requirements:

- `disallow_untyped_defs = true` — annotate every function/method.
- `disallow_any_generics = true` — avoid bare `list`, `dict`, `tuple`; use parameterized forms.
- Guard imports only needed for type checking with `if TYPE_CHECKING:`.

## Tests

Tests live in `tests/` and mirror the `axis/` structure. Use the nearest relevant test module for any behavior change.

### Fixtures

Reuse the async `axis_device` fixture from [`tests/conftest.py`](tests/conftest.py). It provides an `httpx.AsyncClient` wired to a `respx` mock and handles cleanup:

```python
async def test_something(axis_device):
    ...
```

### Mocking HTTP requests

Use `respx` to mock VAPIX calls. Map `ApiRequest.content_type` to the correct `respond()` kwarg:

| Content-Type | `respond()` kwarg |
|---|---|
| `application/json` | `json=` |
| `text/plain` | `text=` |
| `text/xml` | `text=` |

```python
respx_mock.post("/axis-cgi/...").respond(json={"data": ...})
```

### Async tests

`asyncio_mode = "auto"` is configured — write `async def test_*` without any extra decorator.

## Pull request workflow

- All changes go through a feature branch and pull request. **Never commit directly to `master`.**
- Create a branch from the latest `master`:

  ```bash
  git checkout master && git pull
  git checkout -b feat/<short-description>
  ```

- Keep each PR focused. Don't mix unrelated fixes or refactors.
- If pre-existing tests, typing, or linting fail for reasons unrelated to your change, note that clearly in the PR description rather than fixing unrelated code.
- Ensure all required checks pass (Ruff, mypy, pytest with ≥95% coverage) before requesting review.
