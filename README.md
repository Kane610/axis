# axis

Python library and CLI for reading information, controlling features, and receiving
events from Axis Communications devices.

## Library and application boundaries

Axis is one repository and installable package, organized into Python subpackages.
Home Assistant and other integrations can continue using `AxisDevice`,
configuration, handlers, models, events, and transport directly. Their public
imports and handler initialization phases are unchanged.

`axis.application` provides functions shared by the CLI and future applications:
find devices, save their connection settings, read device information, and manage
accounts. Applications may use these functions or use the device library directly.
The shared functions do not display menus or manage screen selection, and work
without Click, prompt_toolkit, a terminal, or the `cli` extra.

The CLI supplies terminal commands, prompts, and output around these functions.
A future graphical application can call the same async functions while managing
its own screens and event loop; it should not execute CLI commands or reuse
terminal prompts. The device library does not import application or UI code.
Shared application functions do not import CLI or graphical UI code.

The authoritative [contributor and agent architecture contract](CONTRIBUTING.md#shared-applications-and-separation-of-concerns)
describes placement, public APIs, state ownership, dependencies, compatibility,
and safety. Device protocol models remain separate from application records and
future screen state. This separation does not regroup models/interfaces/VAPIX
or introduce a new device-capability layer.

See [supported Python APIs and import paths](CONTRIBUTING.md#supported-python-apis-and-import-paths)
to choose between direct library access and shared application operations.
Existing core imports remain supported. New applications should import shared
functions from `axis.application`'s defining modules, not CLI helpers or older
compatibility re-exports. The guide separates supported APIs, retained
compatibility paths, and private implementation details.

For an application that uses the local registry:

```python
from axis.application.operations import read_health
from axis.application.records import HealthSnapshot
from axis.application.storage import DeviceRegistry, default_config_path


async def inspect_registered_device(identifier: str) -> HealthSnapshot:
    record = DeviceRegistry(default_config_path()).resolve(identifier)
    return await read_health(record)
```

The caller runs the event loop; the operation opens and closes its HTTP session.
`HealthSnapshot` records which saved device was requested, what identity the device
actually reported, and when the information was read in UTC.
`DeviceRecord.summary()` omits login credentials. Saved device details do not prove
that a device is online. If the reported serial differs from the saved one, show
that mismatch rather than treating the connection as healthy. These functions
do not keep a cache or refresh data automatically.

Use `prepare_account_change` to describe a proposed account change without
contacting a device or storing its password, then display its `preview()`.
Only after explicit authorization should an application
await `apply_account_change(..., authorized=True)`; deletion additionally needs
`confirmed=True`. Supply a password only if the reviewed change includes a password
change. Apply rejects changed device or connection settings and checks the device's
serial over the network before writing. `AccountChangeResult.payload()` returns
the reviewed change with its status set to applied. The older `change_account`
function remains for compatibility but does not enforce these review steps.

`OperationError.kind` identifies the type of failure without exposing login details.
`outcome_unknown` means a write may have reached the device but its response was
lost or unclear. Do not retry that change automatically:
read the account state before deciding what to do next. Cancelling a dispatched
write also cannot undo it and may leave an uncertain outcome. No raw transport causes
or credential-bearing traces are exposed by application boundaries.
Discovery closes its network resources even if starting or stopping the search
fails. Saving device settings uses a local file and blocks until the update is
complete. Writes use POSIX file locks; credentials are stored as plaintext in
owner-only files, not encrypted. GUI-specific and cross-platform storage choices
remain future work.

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
Missing or incompatible CLI dependencies and the required Python version are
reported from installed package metadata generated by `pyproject.toml`, so the
diagnostic also works outside a source checkout.

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

Bare `axis` opens guided navigation on a terminal:

- **Use a device** lists saved devices before showing Health, APIs, Parameters,
  Events, and Accounts. Selection is offline; `s` changes the device inside
  these menus.
- **Manage saved devices** lists, discovers, registers, renames, updates
  credentials, or removes local registrations. Alias, remove, and credentials
  always ask for a device first, before other inputs, even if another device
  was previously selected.
- **Setup & diagnostics** provides Doctor and shell completion.

Choose a menu item by number, or open the suggested command prompt with `c`.
Enter or `b` returns to the parent menu; Enter stays at home rather than exiting.
`e` explicitly exits. The command prompt accepts commands with or without the
`axis` prefix; `/back`, Ctrl-C, or Ctrl-D returns to navigation.
Tab displays suggestions as you type. History is disabled to avoid retaining
accidentally entered secrets. Menu shortcuts do not apply inside text fields.

Both paths use the same Click command definitions, validation, and async
operations. The guided path collects inputs and submits a canonical command;
it does not maintain a second parser or silently execute a selected mutation.
Device-targeted commands resolve their device before collecting any other
input; commands inside **Use a device** reuse that menu's visible selection.
Cancelling device selection never collects further inputs or runs the command.
Ctrl-C cancels prompted commands and operations, closes device resources, and
returns to the current menu. At a menu prompt it goes back; at the home menu
prompt it exits. Bare groups show help. `api browse` is terminal-only; scripts use
`api interfaces` and `api read`.
API and interface lists use case-insensitive alphabetical order, with embedded
numbers sorted numerically. Human-readable reads sort dictionary keys the same
way, including API Discovery results; list order and `--path` indices stay intact.

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

Use `axis` and choose **Manage saved devices**, then **add**, for hidden password
entry. For scripts,
`devices add`, `devices credentials`, and account writes accept
`--password-file PATH`; keep that file private. Password arguments are
intentionally unsupported.

Device discovery is an explicit network action and never automatically
registers devices. It prefers non-link-local IPv4 addresses advertised by each
device and lists devices with only link-local addresses (`169.254.x.x`) last.
Those addresses require a suitable local network interface; discovery does not
prove that an address is reachable. If an interface reports "network is down",
the CLI warns that results may be incomplete; other interfaces continue scanning.

Running `devices discover` also refreshes **existing registrations** matched by
serial or MAC, never by their address or name. It saves the advertised name,
model, firmware, vendor/module information, addresses, and the successful scan's
start time as `last_seen`. Missing fields and devices absent from a scan are
retained; older scans cannot overwrite newer discovery observations.

Fresh non-link-local addresses update the saved connection host. If only a
link-local address is advertised, the saved non-link-local host (including a DNS
name) stays primary and the fresh address is saved as `link_local_host`.
Fallbacks are stored, not automatically retried. User aliases, credentials,
ports, protocols, and security settings remain unchanged. **Address refresh
trusts unauthenticated local discovery announcements**, so use it only on a
trusted network; matching an advertised serial/MAC is not proof of identity.
Discovery does not use saved credentials or log in to validate these updates.

`devices list` includes the saved discovered name and link-local fallback;
unaliased devices use their discovered name in the picker. Its JSON output adds
`name` and `link_local_host`; discovery JSON may also include `link_local_host`
when both address types are advertised. Refresh notices go to stderr.

`devices alias`, `list`, `credentials`, and `remove` are
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
Applied account changes now also verify that the connected serial matches the
registered target before writing. A mismatch fails rather than changing another
device at a reused address.

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
