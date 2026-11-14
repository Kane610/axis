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

## Command-line interface

### Installation

For isolated everyday use with Python 3.14:

```bash
uv tool install --python 3.14 'axis[cli]'
axis --help
axis doctor
```

To evaluate this checkout rather than a published release:

```bash
uv tool install --python 3.14 --reinstall --from . 'axis[cli]'
```

For editable development, run `./setup.sh`, then `uv run axis`. To use Zsh
completion against the development entrypoint, activate `.venv` in the current
terminal with `source .venv/bin/activate`. This does not modify shell startup.
Library-only installations do not need Click or prompt_toolkit; attempting to
launch the CLI without its extra reports the installation command.

### Discover commands

```text
axis
axis devices list|add|discover|alias|remove|credentials
axis device health
axis api list|interfaces|read|browse
axis params show
axis events list|listen
axis accounts list|create|update|delete
axis doctor
axis completion zsh
```

Bare `axis` opens guided navigation on a terminal. Select a device with `s`,
browse groups by number, or enter the suggested command prompt with `c`.
`b` returns to the parent menu; `e` exits. The command prompt accepts commands
with or without the `axis` prefix; `/back` or Ctrl-D returns to navigation.
Tab displays suggestions as you type. History is disabled to avoid retaining
accidentally entered secrets. Menu shortcuts do not apply inside text fields.

Both paths use the same Click command definitions, validation, and async
operations. The guided path collects inputs and submits a canonical command;
it does not maintain a second parser or silently execute a selected mutation.
Ctrl-C cancels operations and closes device resources; at the home screen it
exits. Bare groups show help. `api browse` is terminal-only; scripts use
`api interfaces` and `api read`.

### Devices and direct commands

Registrations remain in `~/.axis/config.toml`. Set `--config PATH` **before**
the command to use a different registry. Direct commands never prompt or guess
a target: use `--device` (or `-d`) with an exact serial or unique alias.
Only commands inside the launcher can inherit its visible selected device.

```bash
axis devices list
axis devices alias front-door --device B8A44F123456
axis api list --device front-door --json
axis api interfaces --device front-door
axis api read basic_device_info --device front-door --json
axis events listen --device front-door --stream-mode auto --json
axis --config /private/devices.toml devices list
```

Use `axis` and choose `devices add` for hidden password entry. For scripts,
`devices add`, `devices credentials`, and account writes accept
`--password-file PATH`; keep that file private. Password arguments are
intentionally unsupported.

Device discovery is an explicit network action and never automatically
registers devices. `devices alias`, `list`, `credentials`, and `remove` are
local operations; removal does not delete a device or remote account.
Registration authenticates and discovers a real serial number. Re-registering
without `--alias` preserves an existing friendly name.
New HTTPS registrations verify certificates by default; use `--no-verify-ssl`
only for a trusted device with a self-signed certificate. Existing stored
transport and verification settings remain in effect for device operations.

Registry updates preserve unrecognized configuration keys and use locked,
atomic writes with owner-only credential-file permissions. Credentials are
still stored in plaintext at rest: protect the registry, password files, and
their containing storage. The CLI does not display those secrets.

### Safe account changes and output

Remote account writes require `--apply`. Without it, commands validate and
preview the intended change without contacting the device or reading a
password. Updates require an explicit `--privilege` so a password change cannot
silently downgrade an administrator. Account deletion additionally requires
interactive confirmation or `--yes` in scripts.

```bash
axis accounts create viewer --device front-door
axis accounts create viewer --device front-door --apply --password-file /private/password
axis accounts update viewer --device front-door --privilege viewer --apply --password-file /private/password
axis accounts update viewer --device front-door --privilege operator --apply
axis accounts delete viewer --device front-door --apply --yes
```

Password changes are required for creation and optional for updates. Omitting
`--password-file` on a direct update changes privileges only; guided updates
explicitly offer an optional hidden password change.

Finite results support `--json`: device/API/event listings are arrays, health
and mutation results are objects, account listings are keyed by username, and
interface/parameter reads return their structured values. Live events use
JSON Lines, one complete JSON value per line. Human results go to stdout;
diagnostics go to stderr. Failures do not emit empty success results.

Exit statuses are 0 (success), 1 (operation failure), 2 (usage error), and 130
(interrupted). Sensitive values are redacted from reads. `--debug` enables
safe CLI lifecycle diagnostics, not raw credential-bearing HTTP logging.

### Zsh completion and offline diagnostics

Completion reads command metadata and local serials/aliases only. It never
discovers devices, authenticates, or makes service requests. Suggestions
include descriptions, option choices, and paths; quoting preserves spaces.

Generate a script explicitly:

```bash
mkdir -p ~/.axis
axis completion zsh > ~/.axis/completion.zsh
```

For the **current terminal**, run:

```zsh
autoload -Uz compinit
compinit
source ~/.axis/completion.zsh
```

For **fresh terminals**, manually add the source line to your Zsh startup
after your existing `compinit` initialization, then open a new terminal.
The `axis` executable must be on PATH in that terminal. Regenerate the script
after upgrading. The CLI does not automatically edit shell files, activate
the parent shell, or claim that startup is configured merely because a script
exists.

`axis doctor` checks local installation, PATH shadowing, registry readability,
permissions, and completion-script availability without network access.
Use `axis doctor --check config --json` to select a diagnostic. Remote
connectivity is checked separately with `axis device health --device SERIAL`.

### Breaking upgrade and architecture

Reinstall to replace old executable metadata. `axis-cli` is removed; there
are no legacy executable aliases or flag-only compatibility routes.
`python -m axis` uses the same canonical CLI.

| Previous use | Canonical replacement |
| --- | --- |
| `axis-cli` menus | `axis` |
| Flat host/username/password invocation | Register once, then use `--device` |
| `--events` | `axis events listen --device SERIAL` |
| `--params` | `axis params show --device SERIAL` |
| API drill-down | `axis api browse --device SERIAL` or `api interfaces/read` |
| Event transport options | `events listen --stream-mode auto\|rtsp\|event` |

Existing registrations remain readable, with aliases added offline. Update
scripts and service definitions; passwords should no longer be positional
arguments. Internal Python helpers are not executable aliases.

Presentation, prompts, command definitions, and navigation stay in `axis/cli/`.
`axis/interfaces/` and `axis/models/` remain presentation-agnostic. Shared CLI
operations return typed data or explicit errors, and the CLI maps them to
human/JSON output. The old pack router remains an internal import surface;
canonical interactive navigation derives from the Click tree.

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
