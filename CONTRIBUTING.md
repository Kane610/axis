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

Dependencies are locked via `uv.lock`. The pre-commit hook automatically runs
`uv lock` when `pyproject.toml` or `uv.lock` is included in a commit, preserving
existing dependency versions where possible. No separate lockfile command is needed.
If the hook updates the lockfile, stage it along with the dependency changes and
retry the commit. The bootstrap script installs the hooks automatically.

CI checks lockfile consistency before installing dependencies and uses `--locked`
for dependency installation and checks. A stale or missing committed lockfile
therefore fails CI even when local hooks are not installed or are bypassed.

## Running checks

Always run the full suite before opening a pull request:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy axis
uv run ty check axis
uv run pytest
```

Mypy remains the required type checker. Ty runs alongside it in a non-blocking
**Typing (ty, advisory)** CI check; review its diagnostics without suppressing
them just to make CI pass. Both tools check `axis`, and ty does not honor mypy's
`type: ignore` comments. Ty also runs as an advisory pre-commit hook.

For faster iteration, target only the files you changed:

```bash
uv run pytest tests/test_<area>.py
uv run ruff check axis/<file>.py
```

Run broader checks only when your change affects shared behavior (for example, base classes, event parsing, or configuration).

CLI development dependencies are included by `uv sync --all-extras`.
For quick CLI iteration use `uv run pytest tests/cli --no-cov`; this is not a
coverage acceptance check. The configured full-suite threshold is 100%.
Zsh must be installed for the real completion tests.

Before publishing CLI packaging or entrypoint changes, also run:

```bash
uv run python scripts/check_cli_install.py
```

This builds the wheel and installs library-only and CLI-extra profiles into
temporary environments outside the checkout, verifies package origin, the
single canonical executable, help for every command path, non-terminal
behavior, and isolated Zsh startup/completion. It downloads runtime
dependencies and needs network access. It does not change personal shell or
device configuration. CI runs the same check independently.

Async fixtures use function-scoped event loops, configured explicitly in
`pyproject.toml`. Keep warnings treated as errors rather than suppressing
pytest-asyncio configuration warnings.

## Branch and scope policy

- Never commit directly on `master`; always use a feature branch and open a pull request.
- Keep migrations that change typing syntax or lint policy behavior-neutral.
- Split large migrations into reviewable commits with one clear objective per commit.
- For syntax-only migrations, require full lint/type/test validation before merge.

Coverage must stay at or above 95% overall. All new code you introduce must have 100% test coverage. `axis/stream_transport.py` is excluded from the threshold. `TYPE_CHECKING` blocks are automatically excluded.

## Pre-commit hooks

The repository ships local hooks that refresh dependency lock data when needed
and run `ruff check --fix`, `ruff format`, `mypy`, and advisory `ty check axis`.
The ty hook always displays diagnostics but does not block commits on type
findings. Setup or execution errors still fail the hook. The bootstrap script
installs the hooks automatically; for manual environment setup, install them with:

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

### Shared applications and separation of concerns

Axis remains one repository and distribution. Scale responsibilities with Python
subpackages, not by making the device library depend on a CLI or graphical app.
Home Assistant and other integrations must retain direct access to the device
library without local registrations, terminal dependencies, or application
confirmation policies.

The dependency direction is:

```text
CLI / future graphical adapter
              |
    axis.application services
              |
       existing device library
```

Applications may also use the local persistence adapter. Core library consumers
can bypass application services and own their existing sessions and event loops.
The core does not import `axis.application` or presentation packages; application
services do not import `axis.cli`, Click, or prompt_toolkit. Architecture tests
enforce these import boundaries, and installed-wheel checks exercise the
application services without optional CLI dependencies.

| Responsibility | Placement |
|----------------|-----------|
| VAPIX request, response, enum, or parser | Existing `axis/models/` feature |
| Endpoint support, device control, transport, or event handling | Existing library interfaces/transport |
| Device and handler lifecycle | Existing device/VAPIX orchestration |
| Reusable application read or mutation workflow | `axis/application/operations.py` |
| Offline account validation and immutable intentions | `axis/application/accounts.py` |
| Stored connection records and credential-free summaries | `axis/application/records.py` |
| TOML registry, locking, and atomic local updates | `axis/application/storage.py` |
| Network discovery without prompts or registration | `axis/application/discovery.py` |
| CLI arguments, completion, secret input, confirmation, rendering | `axis/cli/` |
| Future screen navigation, loading state, pending edits | Graphical presentation adapter |

Do not put every dataclass in `axis/models/`. Device protocol models remain
separate from application registrations, mutation intentions, and presentation
state. Keep API-specific enums and parsing close to their feature. The current
separation does not reorganize models, interfaces, VAPIX, or their public imports.
A future device-capability layer or feature regrouping needs a separate proposal.

### Public contracts and ownership

The existing device-library interfaces remain available to integrations.
Application contracts are the records/registry, `discover_axis_devices`, async
read operations, `read_health`/`HealthSnapshot`, and
`prepare_account_change`/`AccountChange`/`apply_account_change`/
`AccountChangeResult`. `DeviceRecord.summary()` returns an immutable
`DeviceSummary` with no login username/password. `OperationError.kind` uses
`ErrorKind`; `outcome_unknown` indicates a lost/ambiguous write acknowledgement.
`health` preserves the existing four-field dictionary for CLI consumers.
`change_account` is a compatibility executor, not the reviewed apply API.
Underscore-prefixed helpers, legacy menu/router machinery, and presentation
helpers are internal. Re-exporting an implementation for compatibility does not
make all of its internals a new supported API.

Application services are directly awaitable: they do not prompt, print, exit,
start an event loop, or choose a selected device. The CLI owns its runner; other
consumers own their loop. Finite application operations own and close their
HTTP sessions. A listener owns its subscription and stream until cancellation or
failure, and releases them before returning. Cancellation is not a successful
empty result. Cancelling a dispatched write cannot undo it and may leave its
remote outcome uncertain; reconcile account state before retrying. Finite HTTP
requests retain existing session timeout defaults; consumers can set an outer
`asyncio.timeout` budget. Stream startup has a 30-second limit. There is no
implicit persistent connection, polling, or retry.

| State | Owner and contract |
|-------|--------------------|
| Saved registrations | Local registry; reads are snapshots, not live health |
| Credentials | Connection records; never expose them as presentation state |
| Observed health | Timestamped immutable result; retain the initiating identity |
| Connections/subscriptions | Operation/listener that created them |
| Selected device, pending edits, displayed data | Presentation adapter |
| Mutation intention | Immutable reviewed target/action; no secrets |

Resolve aliases before starting work. A later selection change must not retarget
an operation or relabel its result. Do not merge stored connection settings with
runtime configuration: runtime configuration includes a live HTTP session.
Do not create a second mutable cache of handler state without defining refresh,
invalidation, and ownership first.

Registry writes lock and read the latest file before atomic replacement.
Credentials-only and alias-only updates preserve unrelated changes. Full-record
upserts are intentionally last-writer-wins; reads and old records are not
transactions. File locks do not serialize remote changes by another administrator.
Registry mutations currently require POSIX locking. Credentials remain plaintext
at rest, protected by owner-only files rather than encryption.

### Safety, errors, and compatibility

Share validation, mutation intentions, and device execution, not prompts or
screens. Preview must not contact a device, read a password, or write. Application
apply requires explicit authorization, and deletion requires confirmation.
An intention is bound to its reviewed serial, address, and connection policy;
friendly alias/model changes do not invalidate it. Apply also verifies live
device identity before writing, so address reuse cannot silently target another
device. Resolving a changed alias is not authorization to operate on another
device. Password collection and terminal
confirmation belong to the adapter. Lower-level library controls remain available
without imposing interactive policy on integrations.

Application errors expose safe categories and messages, never credential-bearing
transport causes. Consumers can distinguish unsupported features, permissions,
authentication, connection/certificate failure, timeout, invalid input, malformed
responses, and unknown operation failure. A failed mutation may have an uncertain
remote outcome: report it, reconcile with a read, and never automatically retry.
Redaction belongs at application display/export boundaries, not in the underlying
device models. Preserve useful library data for integration consumers.

Before adding or moving functionality:

1. Identify its responsibility, consumers, and state/lifecycle owner.
2. Search for existing behavior and choose the lowest appropriate layer.
3. Verify dependency direction and supported public import paths.
4. Preserve CLI output shapes, exit statuses, and device-library contracts.
5. Add focused tests for the changed behavior and update this guide if needed.

Use existing mocks for faults, target binding, cancellation, cleanup, and
concurrent persistence. Test library/application imports without UI dependencies.
Coverage is not evidence of hardware compatibility, usability, or accessibility;
record real-device and human validation separately and state untested limitations.

`read_health` captures its initiating target before awaiting and returns UTC
`observed_at` with separately observed serial/model/product/firmware. A differing
observed serial is not proof that the registered device is healthy: consumers
must display that identity discrepancy, not relabel the result as another
selection. It does not silently update local registration or maintain a cache.
Reads/streams snapshot connection settings, including the redaction password,
so later edits cannot alter transport or leak previously received credentials.
Stream callbacks run synchronously on the operation's loop: adapters should
enqueue bounded work rather than block them or perform UI updates from arbitrary
threads. Cancelling the listener releases its stream and subscription.

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
4. Add tests in `tests/test_<name>.py` using the async fixtures and HTTP mocking layers from [`tests/conftest.py`](tests/conftest.py).

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

This project uses PEP 695 syntax for new or updated typing code:

- Use class type parameters instead of `Generic[...]` base classes.
- Use `type` statements for aliases instead of assignment-style aliases.
- Do not introduce new module-level `TypeVar(...)` declarations when class or function type parameters are sufficient.

### Request and response contracts

Request classes are part of the public typing boundary and must keep static and runtime decode contracts aligned.

- Use `ApiRequest[ConcreteResponse]` for decoded/read requests.
- Set `response_type = ConcreteResponse` on every decoded/read request class.
- Use `ApiRequest[ApiResponse[bytes]]` for write/raw-byte requests.
- Set `response_type = BytesResponse` on every write/raw-byte request class.
- Do not rely on implicit `response_type` defaults.

If an interface method intentionally preserves a legacy `bytes` return type, unwrap `.data` at the handler boundary rather than changing `Vapix.api_request()` semantics.

## Tests

Tests live in `tests/` and mirror the `axis/` structure. Use the nearest relevant test module for any behavior change.

### Fixtures

Reuse the async device fixtures from [`tests/conftest.py`](tests/conftest.py):

- `axis_device` for single-device tests.
- `axis_companion_device` for companion/multi-device tests.

### HTTP mocking layers

Choose the fixture layer based on test scope and assertion needs:

- Prefer `mock_api_request` for tests backed by an `ApiRequest` model class.
- Prefer `aiohttp_mock_server` for most new direct endpoint tests.
- Prefer `http_route_mock` for single-device route-registration tests.
- Use `http_route_mock_factory` only when you need explicit multi-device binding.

| Fixture | Use when | Avoid when |
|---|---|---|
| `mock_api_request` | Model-backed request/response tests where method/path come from an `ApiRequest` class | Transport-side effects, multi-route flows, or tests not centered on a single request class |
| `aiohttp_mock_server` | Direct endpoint/static payload tests, custom handler tests, payload/body capture tests | Complex route-sequence tests that benefit from fluent route registration |
| `http_route_mock` | Common single-device route-registration tests with call-history assertions | Multi-device tests |
| `http_route_mock_factory` | Multi-device or explicit device-binding route-registration tests | Single-device tests where `http_route_mock` is simpler |

Use `mock_api_request` as the default for model-backed tests:

```python
from axis.models.api_discovery import ListApisRequest
from tests.conftest import MockApiResponseSpec


async def test_api_list(mock_api_request, axis_device):
    mock_api_request(
        ListApisRequest,
        response=MockApiResponseSpec(json={"data": {"apiList": []}}),
    )

    await axis_device.vapix.api_discovery.get_api_list()
```

Use `MockApiResponseSpec` when the response should not be inferred from the
request content type, or when the request model uses an explicit-only content
type such as SOAP:

```python
mock_api_request(
    SomeSoapRequest,
    response=MockApiResponseSpec(content=b"<xml />"),
)
```

Use `MockApiRequestAssertions` to verify request params, headers, or encoded body
without leaving the request-class abstraction:

```python
from tests.conftest import MockApiRequestAssertions, MockApiResponseSpec


mock_api_request(
    SomeRequest,
    response=MockApiResponseSpec(text="ok"),
    assertions=MockApiRequestAssertions(
        params={"camera": "1"},
        headers={"X-Test": "true"},
    ),
)
```

Use `aiohttp_mock_server` for most new direct endpoint tests:

```python
async def test_something(aiohttp_mock_server, axis_device):
    server, requests = await aiohttp_mock_server(
        "/axis-cgi/example.cgi",
        response={"data": []},
        device=axis_device,
    )
    assert server.port == axis_device.config.port
    assert requests is not None
```

Use `http_route_mock` for route-registration tests:

```python
async def test_handler(http_route_mock):
    http_route_mock.post("/axis-cgi/example.cgi").respond(
        json={"apiVersion": "1.0", "data": []}
    )
```

Use `http_route_mock_factory` for multi-device tests:

```python
async def test_multi_device(
    http_route_mock_factory,
    axis_device,
    axis_companion_device,
):
    mock = await http_route_mock_factory(
        axis_device,
        axis_companion_device,
    )
    mock.post("/axis-cgi/example.cgi").respond(json={"data": []})
```

When registering a route with `data=...`, body matching is strict. A request body
that does not match the registered payload will not hit the route (it will return
404 from the mock server). Use `data=` only when you intend to assert request-body
shape; otherwise omit it to match only method/path.

When using `Route.respond()`, map response type to the correct keyword:

| Content-Type | `respond()` kwarg |
|---|---|
| `application/json` | `json=` |
| `text/plain` | `text=` |
| `text/xml` | `text=` |

```python
http_route_mock.post("/axis-cgi/...").respond(json={"data": ...})
```

For advanced options like `capture_payload`, `capture_body`, and route-spec dictionaries, use [`tests/conftest.py`](tests/conftest.py) as the source of truth.

If you override shared fixtures in a test module (for example `http_route_mock`),
document the reason in the fixture docstring so the scope difference is explicit to
future contributors.

### Async tests

`asyncio_mode = "auto"` is configured — write `async def test_*` without any extra decorator.

### Future extraction policy

The current recommended architecture is the hybrid pattern already in this repository:

- Shared route/dispatch behavior in support modules (for example [`tests/http_route_mock.py`](tests/http_route_mock.py)).
- Fixture exposure and loading in [`tests/conftest.py`](tests/conftest.py).

Do not extract test support to a standalone pytest plugin yet. Revisit extraction only when all gates are met:

1. Shared fixtures are adopted in roughly 30-40% of eligible tests.
2. Fixture API remains stable for at least two weeks (no semantic/parameter changes).
3. A clear maintenance owner is identified.
4. There is concrete reuse demand outside this repository, or a proven local scaling issue that cannot be addressed by reorganizing `tests/conftest.py`.

If extraction is justified later, extract locally first while keeping `tests/conftest.py` as the loading surface. Separate packaging/release workflows are out of scope until local extraction proves stable.

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
