# axis

Python project to set up a connection towards Axis Communications devices and to subscribe to specific events on the metadatastream.

## Development setup

`uv` is required for development setup:

```bash
uv python install 3.14
uv sync --python 3.14 --all-extras
```

Or run the bootstrap script, which installs `uv` if needed and provisions Python 3.14 automatically:

```bash
./setup.sh
```

Dependencies are locked via `uv.lock`. The pre-commit hook installed by `./setup.sh`
automatically refreshes it when `pyproject.toml` or `uv.lock` is included in a commit.
If the hook modifies it, include the updated lockfile when retrying the commit.
CI rejects stale or missing lockfiles, even when local hooks are bypassed, and
runs checks with `--locked` to prevent implicit lockfile updates.

Run checks with `uv`:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy axis
uv run ty check axis
uv run pytest
```

Pull requests expose independent **Lint**, **Formatting**, **Typing**, and
**Tests (Python 3.14)** checks in GitHub. A failed check does not prevent the
others from running. Ruff lint findings also appear as file-and-line annotations.
An additional **Typing (ty, advisory)** check runs alongside mypy without blocking
CI on ty failures. Its diagnostics appear as file-and-line annotations, and
failures produce an explicit warning. Mypy remains required.
The test job uploads JUnit XML and XML/HTML coverage reports as the
`test-reports-python-3.14` artifact, including when tests fail.
The workflow run summary shows the test outcome, counts, duration, line coverage,
and configured coverage threshold. Missing reports are flagged explicitly.

Both type checkers are installed and pinned through the development setup above.
Ty checks the same `axis` package as mypy and ignores mypy's `type: ignore`
comments so its diagnostics remain independent. Pre-commit runs ty as an advisory
check with diagnostics always shown, without blocking commits on type findings.
Mypy remains required; ty setup or execution errors still block commits.

## CLI navigation contract

### Canonical CLI migration

The next CLI release consolidates the executables under `axis`. It provides
direct commands, offline Zsh completion, and a guided launcher with a
command prompt. All interaction paths use the same argument validation and
operations. Library consumers do not need the optional `cli` dependencies.

The command inventory is:

```text
axis devices list|add|discover|remove|credentials
axis device health
axis api list|interfaces|read|browse
axis params show
axis events list|listen
axis accounts list|create|update|delete
axis doctor
axis completion zsh
```

Bare `axis` opens the launcher only on a terminal. Bare command groups show
help. Direct commands never prompt for missing arguments. `--device` selects
a registered serial number or unique alias; interactive selection never
implicitly supplies a target to an independent shell invocation.

Remote writes require `--apply`; without it, commands validate and preview
the intended change without contacting the device. Destructive changes also
require confirmation, or `--yes` in scripts. Local registration commands
explicitly change the local registry; removal requires confirmation.

Finite results support `--json`; event streaming uses JSON Lines. Diagnostics
go to stderr. Exit statuses are 0 (success), 1 (operation failure), 2 (usage
error), and 130 (interrupted). Passwords must not appear in arguments,
completion, history, logs, diagnostics, or previews.

Completion reads command metadata and local identifiers only: it never
discovers devices, authenticates, or contacts services. Shell setup is
explicit and does not automatically modify startup files.

The breaking upgrade requires reinstalling the CLI extra and replacing
`axis-cli` and old flat event/parameter invocations with canonical subcommands.
Existing registrations remain readable. Internal Python compatibility helpers
are not executable aliases.

The interactive CLI in `axis/cli/` follows a menu-first model.
Router runtime is the only interactive execution path.

- Canonical route graph: `main -> devices -> device_operations -> {api|events|accounts}`.
- `device_operations` routes to feature submenus using router navigation, not direct feature command execution.
- Feature nodes (`api`, `events`, `accounts`) own their local menu layout and selected-device context rendering.
- `b` always navigates to `parent_id`; `e` always exits.

To keep the CLI reusable boundary clear:

- CLI concerns (menu keys, prompts, render text, router state) stay in `axis/cli/`.
- `axis/interfaces/` and `axis/models/` must remain presentation-agnostic and reusable by non-CLI consumers.
- Domain layers return typed data/errors; CLI adapters map them to user-facing text and flow.

## Initialization architecture

Vapix initialization is phase-based and driven by handler metadata:

- `API_DISCOVERY`: handlers initialized after API discovery.
- `PARAM_CGI_FALLBACK`: handlers that may initialize from parameter support when not listed in discovery.
- `APPLICATION`: handlers initialized after applications are loaded.

Handlers declare phase membership through `handler_groups` and may customize phase eligibility through `should_initialize_in_group`.

## Request and response typing

`Vapix.api_request()` is the single typed request entrypoint.

- Request models declare their decode contract with `ApiRequest[ResponseT]`.
- Every `ApiRequest` subclass must set `response_type` explicitly.
- Decoded/read requests use their concrete response model as `response_type`.
- Write-style requests use `BytesResponse` as `response_type`.

Examples:

```python
@dataclass
class ListApisRequest(ApiRequest[GetAllApisResponse]):
    response_type = GetAllApisResponse


@dataclass
class SetPortsRequest(ApiRequest[ApiResponse[bytes]]):
    response_type = BytesResponse
```

Handler methods may unwrap `.data` when they intentionally preserve a bytes-returning boundary.

Example fallback policy:

- `LightHandler` participates in both `API_DISCOVERY` and `PARAM_CGI_FALLBACK`.
- In `PARAM_CGI_FALLBACK`, it initializes only when not listed in API discovery and listed in parameters.

## Event Instance Model Notes

`EventInstance` keeps `name` as the raw device-provided `NiceName` value.

`EventInstance.source` and `EventInstance.data` are typed containers (`EventInstanceSource` and `EventInstanceData`) built from `SimpleItemInstance` payloads.

For compatibility with integrations that still need the historical raw payload shape, `EventInstance` also exposes:

- `raw_source`: returns `{}` or a dict or a list of dicts.
- `raw_data`: returns `{}` or a dict or a list of dicts.
