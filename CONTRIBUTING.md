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

Dependabot uses the `uv` ecosystem so dependency update PRs refresh both
`pyproject.toml` and `uv.lock`. The `pip` ecosystem does not maintain `uv.lock`.
For an existing PR that only changes `pyproject.toml`, run `uv lock` on its
branch and include the updated lockfile before rerunning CI.

## Running checks

To run the required Python, frontend, and packaging checks together after
setting up both toolchains and installing Chromium, run:

```bash
sh scripts/check.sh
```

This rebuilds the packaged frontend bundle; include any intended bundle
changes in your PR. CI additionally compares the rebuilt bundle to the
committed version and runs ty as an advisory check.

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

For frontend work, use Node.js 24 and the pnpm version pinned in
`web/package.json`. Run the [frontend checks](README.md#local-web-interface)
before opening a pull request. Commit `web/pnpm-lock.yaml` and the regenerated
`axis/web/static/app.js` when they change. Do not edit the generated bundle
directly. ESLint, Prettier, TypeScript, Vitest, and Playwright run in the
independent **Frontend** CI job.

pnpm waits at least three days after a dependency version is published and
rejects downgrades in package trust evidence. Keep these policies enabled when
updating the lockfile. Only esbuild is allowed to run a dependency install script.

If you change a WebSocket command or response, update the shared
[wire examples](web/tests/fixtures/websocket.json). Python compares them with
actual server replies, and TypeScript checks them against the client result types.

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
CLI / web presentation adapter
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
| Validate and describe account changes without device access or passwords | `axis/application/accounts.py` |
| Saved device settings and displayable details without login credentials | `axis/application/records.py` |
| Save devices in TOML, coordinate writers, and replace completed files | `axis/application/storage.py` |
| Network discovery without prompts or registration | `axis/application/discovery.py` |
| CLI arguments, completion, secret input, confirmation, rendering | `axis/cli/` |
| Local web server, WebSocket API, packaged frontend | `axis/web/` |
| Web screen navigation and loading state | `web/src/app.ts` |
| Typed web commands, responses, and WebSocket lifecycle | `web/src/data/` |
| Reusable Lit presentation and Web Awesome-based Axis controls | `web/src/components/` |
| Semantic theme tokens and shared presentation styles | `web/src/resources/` |

Do not put every dataclass in `axis/models/`. Device protocol models remain
separate from saved device registrations, proposed account changes, and screen
state. Keep API-specific enums and parsing close to their feature. The current
separation does not reorganize models, interfaces, VAPIX, or their public imports.
A future device-capability layer or feature regrouping needs a separate proposal.

### Supported Python APIs and import paths

Choose an API by who manages the device connection, not by which interface the
user sees. A graphical application does not need to import CLI code.

#### Device library: integrations manage their own connections

Home Assistant and other integrations can continue using the existing device
library directly:

```python
from axis import AxisDevice
from axis.models.configuration import Configuration
```

`axis.device.AxisDevice` is also an existing supported import. The device's
`vapix` handlers expose controls and cached device data; `event.subscribe`
registers event callbacks; `stream` manages event streaming. The integration
supplies the HTTP session in `Configuration` and manages its own event loop and
device lifecycle.

Existing documented feature handlers in `axis.interfaces`, request/response
types and enums in `axis.models`, and event/stream APIs remain available at their
current import paths. Device exceptions remain available from `axis.errors` and
the existing `axis` exports. This PR does not remove or move those APIs, or require
integrations to adopt application records, a local registry, or CLI dependencies.

#### Shared application APIs: operations manage their own connections

Use these defining modules for new applications and third-party consumers:

| Purpose | Import from | Supported entry points |
|---------|-------------|------------------------|
| Find devices on the local network | `axis.application.discovery` | `discover_axis_devices` |
| Describe connections and read results | `axis.application.records` | `ConnectionSettings`, `DeviceRecord`, `DeviceSummary`, `DiscoverySnapshot`, `HealthSnapshot` |
| Save and select local registrations | `axis.application.storage` | `DeviceRegistry`, `default_config_path` |
| Identify a device or read its information | `axis.application.operations` | `identify`, `read_health`, `list_apis`, `list_interfaces`, `read_interface`, `parameters`, `list_events`, `list_accounts` |
| Receive live events | `axis.application.operations` | `listen` |
| Validate and review account changes | `axis.application.accounts` | `validate_account_username`, `prepare_account_change`, `AccountChange`, `AccountChangeResult` |
| Execute an approved account change | `axis.application.operations` | `apply_account_change` |
| Convert data for safe display/export | `axis.application.operations` | `normalize_payload` |
| Handle application failures | `axis.application.errors` | `ErrorKind`, `OperationError`, `StorageError` |

`discover_axis_devices` only returns network observations. Applications that
choose to trust local announcements can explicitly pass those results and the
scan's timezone-aware start time to `DeviceRegistry.refresh_discovery`.
It atomically refreshes matching registrations without logging in or creating
new registrations. It preserves aliases, credentials, connection policy,
missing metadata, and newer observations; link-local-only results retain an
existing non-link-local primary and save a fallback without retrying it.
`DeviceRecord.discovery` and `DeviceSummary.discovery` expose the immutable,
credential-free `DiscoverySnapshot`. Discovery-only changes do not invalidate
an account-change review; changing the connection host does.

For example:

```python
from axis.application.operations import read_health
from axis.application.records import DeviceRecord, HealthSnapshot
from axis.application.storage import DeviceRegistry
```

Import application symbols from these modules, not from `axis.cli` or an assumed
package-root facade. `axis.application` currently does not re-export this table's
symbols. A saved registry is optional: callers can construct a `DeviceRecord`
from connection settings instead. These operations open and close their own
connections; they do not borrow an integration's existing `AxisDevice` session.

Public means intended for consumer use, not supported by every device or account.
Handle feature availability and failures. Use exception types for library errors,
and `OperationError.kind`/`outcome_unknown` for application recovery decisions,
rather than matching human-readable error messages.

#### Retained compatibility imports: keep working, but do not build on them

| Existing path | Preferred path for new code |
|---------------|-----------------------------|
| `axis.cli.operations` device-operation re-exports | `axis.application.operations`; exceptions from `axis.application.errors` |
| `axis.cli.storage` record/registry re-exports | `axis.application.records`, `axis.application.storage`, `axis.application.errors` |
| `discover_axis_devices` re-exported by `axis.cli.main` or `axis.cli.packs.devices` | `axis.application.discovery.discover_axis_devices` |

These imports remain in place for existing callers. Their presence, including
names in `__all__`, does not make CLI internals a reusable application API.
No compatibility import is removed or given a new deprecation warning here.

Within application operations, `health` retains the four-field dictionary for
existing callers; prefer `read_health` for a typed result with target and read
time. `change_account` retains the older direct executor; new applications should
use `prepare_account_change` and `apply_account_change` for review, authorization,
and device identity checks. Lower-level device-library account controls remain
available to integrations that manage their own policies.

#### Internal implementation: not a third-party contract

Underscore-prefixed helpers, CLI command callbacks, `Runtime`, completion/menu
machinery, and the earlier `axis.cli.core`/`axis.cli.packs` router implementation
are internal. Implementation constants such as `STARTUP_TIMEOUT` are not
configuration APIs, even if an older module re-exports them. Importability or a
name without an underscore alone does not establish a supported API.

Scripts should use documented `axis` commands and output formats rather than
importing command callbacks. Python applications should use the library or
application APIs above, not launch the CLI to reach device operations.

Changes to supported imports, signatures, result fields/output shapes, connection
ownership, or error meanings require explicit compatibility review and relevant
release/migration documentation. Keep compatibility exports distinct from new
public APIs when adding functionality; do not silently widen the supported
surface by importing a helper into another module.

### Public contracts and ownership

The APIs above follow these state and connection ownership rules.
`DeviceRecord.summary()` returns an immutable
`DeviceSummary` with no login username/password. `OperationError.kind` uses
`ErrorKind`; `outcome_unknown` means a write may have completed without a clear
response from the device.

Application functions can be awaited directly: they do not prompt, print, exit,
start an event loop, or choose a selected device. The CLI owns its runner; other
consumers own their loop. Finite application operations own and close their
HTTP sessions. A listener owns its subscription and stream until cancellation or
failure, and releases them before returning. Cancellation is not a successful
empty result. Cancelling a dispatched write cannot undo it and may leave its
remote outcome uncertain; read the account state before deciding whether to retry. Finite HTTP
requests retain existing session timeout defaults; consumers can set an outer
`asyncio.timeout` budget. Stream startup has a 30-second limit. There is no
implicit persistent connection, polling, or retry.

| State | Owner and contract |
|-------|--------------------|
| Saved registrations | Local registry; reads are snapshots, not live health |
| Credentials | Connection records; never expose them as presentation state |
| Observed health | Read-only result with the requested target, reported identity, and read time |
| Connections/subscriptions | Operation/listener that created them |
| Selected device, pending edits, displayed data | Presentation adapter |
| Proposed account change | Read-only description of the reviewed device and action; no passwords |

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

Share validation, descriptions of proposed changes, and device execution, not prompts or
screens. Preview must not contact a device, read a password, or write. Application
apply requires explicit authorization, and deletion requires confirmation.
Each proposed change records its reviewed serial, address, and connection settings;
friendly alias/model changes do not invalidate it. Apply also verifies live
device identity before writing, so address reuse cannot silently target another
device. Resolving a changed alias is not authorization to operate on another
device. Password collection and terminal
confirmation belong to the adapter. Lower-level library controls remain available
without imposing interactive policy on integrations.

Application errors expose safe categories and messages, never credential-bearing
transport causes. Consumers can distinguish unsupported features, permissions,
authentication, connection/certificate failure, timeout, invalid input, malformed
responses, and unknown operation failure. A failed write may still have changed
the device: report that uncertainty, read the current state, and never automatically retry.
Redaction belongs at application display/export boundaries, not in the underlying
device models. Preserve useful library data for integration consumers.

Before adding or moving functionality:

1. Identify its responsibility, consumers, and state/lifecycle owner.
2. Search for existing behavior and choose the lowest appropriate layer.
3. Verify dependency direction and supported public import paths.
4. Preserve CLI output shapes, exit statuses, and device-library contracts.
5. Add focused tests for the changed behavior and update this guide if needed.

Use existing mocks for failures, device identity checks, cancellation, cleanup, and
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

### Terminal UX guidelines

- Resolve the device before other inputs; keep its identity visible.
- Prefer recognition over recall: show valid, numbered choices for catalogs.
  Sort names naturally and keep choice numbers stable while filtering.
- Explain each input's purpose, format, and example; show finite allowed values,
  defaults, and how to skip optional fields. Never ask for an unexplained internal name.
- Label live network checks separately from offline or previously discovered data.
- Separate names from descriptions visually; do not rely on color alone.
- Make Back and Ctrl-C cancellation explicit. Cancellation must not submit
  unfinished commands or reuse an unconfirmed target.
- Preserve preview defaults and hidden secret input; confirm remote writes
  with the target and consequences. Do not add network reads to offline previews.

### Writing descriptions readers can use

These rules apply to contributors and coding agents across the repository:
module, class, function, test, fixture, CLI help, and documentation descriptions.

- Start with the purpose: what the code lets a caller or user do, and which
  device feature or data it handles. Do not just repeat its filename or class name.
- Use plain language first. Keep precise API and protocol names where needed,
  but explain their practical meaning instead of relying on architecture jargon.
- Describe what the implementation actually does. Distinguish cached data from
  a fresh network read, saved settings from device state, and reviewing a change
  from applying it when that distinction matters.
- Mention important limits or responsibilities when useful: who opens and closes
  connections, whether passwords are included, or whether a call changes a device.
  Do not imply encryption, rollback, automatic recovery, or hardware support that
  the implementation does not provide.
- Test and fixture descriptions should explain the scenario or setup and why it
  matters, not say only "test function" or "mock response."
- Read the implementation before editing its description. Fix copied feature
  names and incorrect return or side-effect claims. Keep already clear wording
  and relevant official VAPIX references; avoid decorative rewrites.
- Keep the first sentence brief. Add detail only where it helps a reader use the
  code correctly. Documentation changes should not change behavior or package
  structure.

For example, describe application operations as:

> Read device information, manage accounts, and receive events for Axis
> applications. Each async operation opens and closes its HTTP connection; these
> functions do not display terminal prompts.

This explains the purpose and connection lifetime instead of relying on
"presentation-free, session-owned operations."

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
