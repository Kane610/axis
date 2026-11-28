# axis

Python library and CLI for reading information, controlling features, and receiving
events from Axis Communications devices.

## Library and application boundaries

Axis is one repository and installable package, organized into Python subpackages.
Home Assistant and other integrations can continue using `AxisDevice`,
configuration, handlers, models, events, and transport directly. Their public
imports and handler initialization phases are unchanged.

`axis.application` provides functions shared by the CLI and web application:
find devices, save their connection settings, read device information, and manage
accounts. Applications may use these functions or use the device library directly.
The shared functions do not display menus or manage screen selection, and work
without Click, prompt_toolkit, a terminal, or the `cli` extra.

The CLI supplies terminal commands, prompts, and output around these functions.
The web application calls the same async functions while managing its own
screens and event loop; it does not execute CLI commands or reuse terminal
prompts. The device library does not import application or UI code.
Shared application functions do not import CLI or graphical UI code.

The authoritative [contributor and agent architecture contract](CONTRIBUTING.md#shared-applications-and-separation-of-concerns)
describes placement, public APIs, state ownership, dependencies, compatibility,
and safety. Device protocol models remain separate from application records and
screen state. This separation does not regroup models/interfaces/VAPIX
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

## Local web interface

The local web interface discovers and saves devices, reads device health, and
browses device APIs and interfaces. Run it with Python 3.14 or newer. After
release, install it with:

```bash
uv tool install --python 3.14 'axis[cli]'
axis web
```

For this checkout, use `uv run axis web` after development setup, or choose
**Open web interface** from the `uv run axis` home menu. Both automatically open
the browser. The CLI's `--config` option selects the device registry:
`uv run axis --config PATH web --port 8766`. Ctrl-C stops the server and
returns to the menu when launched there.

The server prints a private URL and waits briefly for an existing authorized
tab to reconnect before opening your default browser. Stop the server with
Ctrl-C. The link contains an access token; do not share it. The token persists
in an owner-only file next to the selected registry so an existing tab can
reconnect after restart. Removing that file while the server is stopped revokes
the old link; the next start creates a new token. Opening a new private link in
an existing tab reconnects it without requiring a reload. The server binds to IPv4 loopback only; it is
not intended for remote or multi-user access. Use `axis web --port 8766` to choose
another port.
The local registry stores device credentials as plaintext in owner-only files.

The web application uses an authenticated local WebSocket. Device details
shown in the saved list are not a live health check; open a saved device to
contact it. Saved and discovered devices appear in a single vertical list,
with an address and MAC address when available. Discovered rows also show the
advertised model when available. Saved rows use an alias, discovered name, or
model as their label, falling back to the serial number, but never append a
separate model field. A reported serial mismatch is displayed as a warning.

In a saved device's **Interfaces** view, **Restart device** requires explicit
confirmation and administrator credentials. The server verifies the saved
serial and uses firmware management when advertised, otherwise `restart.cgi`.
“Restart requested” does not confirm the reboot completed. If the outcome is
unknown, check the device before trying again.

Select **Applications** in the device navigation (or **applications** in
Interfaces) for an overview of installed apps, their status, version, signature,
and confidently assessed updates. Select an app to see its vendor, license,
bundled status, resources, compatible OS versions, and controls when reported.
When available and the app is running, its
configuration page opens on the device in a separate tab and may require a separate
login. Starting and stopping run directly when selected; restarting or
uninstalling requires confirmation. All actions require administrator credentials. Uninstalling
also removes the app's data. If an action's outcome is unknown, refresh and check
the app before trying again.

Select **Manage licenses**, choose the application, and select or drag and
drop a license file (up to 1 MiB); confirm before uploading. Installed valid or
invalid license keys can also be removed after confirmation. The
upload uses the `fileData` form field observed on AXIS OS 12.11; older firmware
may use a different format. License contents are not sent over the WebSocket.
If a license change has an unknown outcome, check the app before retrying.

To install an application, open **Install application**, choose or drag and drop
an `.eap` package (up to 1024 MB / 1 GiB), or select an applicable package
from the configured server catalog, and confirm. Suggested applications use
compact list rows showing vendor, version, signature information, and any need
for review. Select an application row to see its versions, then select a
version row to open package details and choose it. Installation and updates share
the same package details, with technical metadata available on expansion.
Application lists are alphabetical; each application's versions remain newest
first. Version rows distinguish **Newest**, declared incompatibility,
incomplete verification, and downgrades without recommending a package.
Installation's **Device requirements** section contains architecture, SDK,
unsigned-policy, and RAM guidance; selected-package warnings stay visible.
A separate **Selected application** summary identifies the selected catalog
package or uploaded file and offers **Change selection**. Uploaded files are
not inspected locally for compatibility. Catalog installation lists only apps not already installed, and
rechecks that before upload. The device's reported
hardware architecture and supported SDKs are shown to help select a compatible package; other
application requirements still apply.
The **Allow unsigned applications (AllowUnsigned)** toggle reflects the actual
device policy when supported. Changing the toggle opens a confirmation step;
the policy changes only after confirmation.
Allowing unsigned applications weakens security. If a
policy change has an unknown outcome, refresh the policy before retrying.
A matching package may upgrade or downgrade an existing app; a
failed or interrupted upgrade can remove both versions. Newly installed apps
are not started automatically. After a catalog installation or update, the web
interface checks that the device reports the selected version and shows its
running state. A stopped application has an explicit **Start** action.
For uploaded files, it reports observed device changes without claiming the
uninspected file's identity was verified. Failed readback or a missing/different
version leaves an explicit unverified-outcome message; uploads are not retried.
Installation requires administrator credentials
and temporarily uses local disk space for the package. If the result is unknown,
check the device's applications before retrying. Devices that require digest
`auth-int` without `auth` cannot be used for streamed installation.
Signed-package verification may temporarily require approximately twice the
package size in available device RAM.
Upload error 2 means the package signature is missing or invalid; obtain a
correctly signed package from the application vendor.
Upload error 27 means the package and installed application have different
vendor IDs; obtain an upgrade from the original application vendor. Check the
installed application before retrying. In a catalog upgrade, the versions
dialog checks whether the application is still present. If it is, **Remove
and install** offers an explicitly confirmed replacement; removal deletes the
application's data and settings, and installation can still fail. If the
failed upgrade already removed it, the dialog offers installation instead.
The server checks the reviewed device, application, package snapshot, and
installation warnings before removal, then verifies absence and rechecks
compatibility before upload. If removal or the verification has an uncertain
outcome, installation stops and the application state must be checked.

In **Server settings**, browse for a folder or enter its absolute path on the
computer running the web server to catalog local `.eap` files. Browsing shows
directories accessible to the server, not folders on a remote browser's computer.
Select the folder and save the settings. The server scans the
folder at startup, every five minutes, and on request; it does not scan
subdirectories. The settings view shows available package metadata and scan
errors. Inspection is limited to 1 GiB per file and 256 MiB of expanded archive
data; packages exceeding these limits are reported rather than installed.

The Applications view keeps its last application list visible when revisited
and refreshes it silently in the background while remaining interactive.
Writes recheck the reviewed device state before proceeding;
failed refreshes leave the cached list marked as out of date.
The Applications view checks the catalog for versions of installed apps.
The overview marks updates only when the assessment reports no warnings, and
labels them as candidates when verification is incomplete. This does not verify
signatures or guarantee compatibility. Open an app and use
**View versions** to review all its candidates in a dialog.
Version lists use the same compact rows for installation and updates;
choose a version to see its findings and available action.
For field definitions and schema differences, see the
[Axis manifest schema documentation](https://developer.axis.com/acap/reference/manifest-schemas/general-info/).
Packages with a different application name or known architecture mismatch are
hidden. Versions are ordered newest first using semantic version order, with
unrecognized versions last; warnings do not change version order. The web
interface also sorts received versions before caching and displaying them in
installation and update lists. The first
five are shown initially. Assessments distinguish declared incompatibilities,
unknown information, items for review, and checks not performed. Schema v2
declares compatible AXIS OS ranges and a vendor ID; older or unknown schemas
cannot establish OS compatibility from those fields. AXIS OS 12.10 and later
are expected to reject installations outside declared ranges. You can explicitly
confirm a package despite findings or choose a downgrade, but confirmation
cannot override the device's checks. Version comparisons use semantic versions;
an unrecognized version may be a downgrade.
An observed appended signature is reported as present but **not verified**;
other signature formats may be unknown. A matching vendor name does not verify
vendor identity, and the installed application's vendor ID is not available for
comparison. SDK metadata is displayed but not compared automatically. The device makes the final signature, vendor ID, and
compatibility checks. Updates are never installed automatically:
review and confirm each update. The server rechecks the saved device, installed
version, warnings and package contents before sending a private snapshot. New
catalog installations also recheck that the application is not already installed
and that its warnings remain unchanged. If
the warnings change, refresh and review them again. As with other
upgrades, a failure can remove both versions; check the device before retrying
an unknown outcome.

The line under **Axis devices** indicates the web app's connection to the local
server. It is green when connected, pulses orange while connecting or retrying,
and turns red when the app needs a valid access link. Hover over the heading for
the status text. With reduced motion enabled, the orange line stays steady.

The backend starts looking for Axis devices advertising over mDNS on its IPv4
network as it starts. The web app loads the saved list and uses the initial
scan if it is still running or recently finished; otherwise it starts a new scan.
Use **Server settings** to select the network interfaces used for web discovery,
or leave it on automatic to use all interfaces. Settings are saved alongside the
device registry and apply on the next web scan, including after server restart.
Selected interfaces that are down, missing, or have no IPv4 address are skipped
with a warning; if none can be used, discovery fails instead of silently scanning
other interfaces. Interface names are resolved to their current IPv4 addresses for
each scan. This setting does not affect terminal discovery, the loopback web
server, or how the operating system routes connections to saved devices.
Choose **Discover devices** below
the list in the **Devices** card to scan again.
The button shows the scan progress and result. Its dashed outline stays still
when reduced motion is enabled. Devices appear as their announcements resolve.
During a rescan, previous results stay visible. You can open a discovered
device and enter its credentials during the scan. **Test connection** and
**Save device** stay disabled until the final results confirm the device.
If the backend disconnects, the last discovered results remain visible but
disabled. A new scan reconciles them after reconnection.
New devices appear alongside saved devices with a different outline and a
**Discovered** label. Results that match a saved serial number or MAC address
do not get a second tile. Discovery announcements are unverified. A scan does
not log in, register devices, or update saved records.
An empty scan does not mean there are no devices on the network.

Select a discovered device to open a form with the same **General**,
**Connection**, and **Advanced** sections as saved-device Settings. Enter its
credentials and an optional alias, then click **Save device**. The discovered
address is read-only, but you can change the protocol or port. HTTPS is selected
by default. Both forms show the port number (443 for HTTPS or 80 for HTTP by
default) and remember the last port for each protocol while the form is open.
Use **Test connection** in either form to check the current connection
settings without saving. For a saved device, the test also checks that the
reported serial matches the registration. The button turns green on success
or red on failure without changing its label or moving the form. A successful
test is required to register a device or save changed connection settings.
Editing a connection field clears the result; changing only the alias does not
require a test.
The saved-device modal opens on **Health**. Use **Applications**, **APIs**, or
**Interfaces** below the device name to switch views; individual interface
buttons are inside **Interfaces**. The APIs view links to documentation when
the device provides an HTTP or HTTPS documentation URL; the link displays its
destination host. While the modal is open, switching back to
a view or interface reuses its last successful result. Select the active button
again to refresh it. API and interface inspection results are also kept in
browser memory when the modal is closed, and reused after a fresh health read
confirms the saved serial and unchanged AXIS OS version. Application support
is checked using API Discovery, with legacy device properties as a fallback;
installed apps load only when Applications is opened, and installation
compatibility details load when the installation dialog is opened. Interface inspection
includes a snapshot of probe results and item counts; refresh it to check for
changes made elsewhere. Application and license changes, a device restart,
connection-setting changes, or a server disconnection discard these capability
snapshots. Installed applications and individual interface data are not retained
across modal sessions. A moving dashed outline marks the button while it loads
without moving the existing content. The modal starts at the top of the
**Devices** box and scrolls independently. Use **Close** or click outside the
modal to return to the list. **Esc** returns from Settings to the current view,
or closes the modal otherwise.

Use **Settings** next to **Close** to edit a saved device's local alias,
address, port, credentials, protocol, or certificate verification. Clearing
the alias previews the default name in gray. An empty password field keeps the
current password. Re-enter it when changing the address, port, or protocol,
or turning off certificate verification. Axis verifies that changed
connection settings reach the saved serial number before replacing them.
These settings do not change the device itself.

When saving a device, the server connects using the selected protocol and port,
reads the device's serial number, and adds a local registration without replacing
an existing one. Prefer HTTPS because HTTP is not encrypted.
**Verify HTTPS certificates** is off by default to allow self-signed factory
certificates. Enable it if the device has a trusted certificate. If leaving
it off, check the address and continue only on a trusted network. Use the CLI
to register devices at manual addresses or with other connection settings.

Live reads can take up to 60 seconds. If a device cannot be reached, check its
saved address and port and network access from the computer running the server,
then select **Health** again to retry or refresh the health view.

The frontend follows Home Assistant's TypeScript/Lit web-component approach,
using its Web Awesome fork for Axis controls, semantic CSS tokens, and automatic
light/dark styling based on your system preference. Typed WebSocket/data modules
are separate from presentation components. The app remains independent of Home
Assistant; no Home Assistant instance is needed.

The frontend is prebuilt for installation. Node.js and pnpm are development-only
tools, not requirements for running `axis web`. For frontend development, install
Node.js 24 and the pnpm version pinned in [web/package.json](web/package.json),
then run:

```bash
pnpm --dir web install --frozen-lockfile
pnpm --dir web exec playwright install chromium
pnpm --dir web lint
pnpm --dir web format:check
pnpm --dir web test
pnpm --dir web test:e2e
```

`test` runs Vitest unit tests. `test:e2e` rebuilds and type-checks the frontend,
then tests the packaged application in a headless browser with mocked device
responses; no real device is required. To only rebuild, use `pnpm --dir web build`.
Commit the updated assets and `web/pnpm-lock.yaml` alongside frontend changes.
The **Frontend** CI check installs locked dependencies, runs ESLint and Prettier,
builds and tests the frontend, and rejects stale packaged assets.
The PyPI source archive includes `web/` sources and tooling configuration for
rebuilding; the wheel ships the compiled browser assets, not the frontend
development tree. To run both Python and frontend checks from a checkout, see
[Running checks](CONTRIBUTING.md#running-checks).

## Development setup

`uv` is required for development setup:

```bash
uv python install 3.14
uv sync --python 3.14 --all-extras
```

Or run the bootstrap script, which installs `uv` if needed and provisions Python 3.14 automatically:

```bash
./script/setup.sh
```

Dependencies are locked via `uv.lock`. The pre-commit hook installed by `./script/setup.sh`
automatically refreshes it when `pyproject.toml` or `uv.lock` is included in a commit.
If the hook modifies it, include the updated lockfile when retrying the commit.
CI rejects stale or missing lockfiles, even when local hooks are bypassed, and
runs checks with `--locked` to prevent implicit lockfile updates.

All repository maintenance and validation scripts live in `script/`.

To update Python and frontend dependencies, including major versions, run:

```bash
./script/bump_dependencies.sh
```

This updates runtime, CLI, build, test, and development requirements to stable
releases compatible with the current Python minimum, refreshes both lockfiles,
installs the updated dependencies, and rebuilds the frontend bundle. Exact Python
pins stay exact; minimum bounds advance, and existing major-version caps advance
to the next major. The Python requirement and pinned pnpm version are unchanged.
Node.js and either the pinned pnpm version or npm are required. If pnpm is not
on PATH, npm downloads and runs the pinned version without a global installation.
The shell script runs its Python helper in an isolated uv environment.
Frontend release-age, trust, and build
policies remain enabled; an upgrade may be held back or rejected by those policies.
Failures stop the script and may leave partial changes for review. Without
`--pr`, it does not commit or push. Review the diff and run `sh script/check.sh`
before committing.

To validate and publish dependency updates as a pull request:

```bash
./script/bump_dependencies.sh --pr
```

This requires Git, an authenticated GitHub CLI (`gh`), and a checkout on
the repository's default branch at the same commit as `origin`. It accepts a
clean worktree or pending changes limited to `pyproject.toml`, `uv.lock`,
`web/package.json`, `web/pnpm-lock.yaml`, and `axis/web/static/app.js`, including
staged changes. Review these edits before publishing; unrelated staged,
unstaged, or untracked files stop the script. It creates a
feature branch, upgrades dependencies, and runs `sh script/check.sh`, including
Python, frontend, and installed-package checks. Only dependency manifests,
lockfiles, and the rebuilt frontend bundle are committed and pushed. The PR uses
the repository template and includes passing validation results.
You can run this after an initial local `./script/bump_dependencies.sh` run.
It reruns the updater to refresh the existing changes or complete an interrupted
update before validating and publishing them.
No dependency changes means no commit, push, or PR. A failed upgrade, check, or
commit leaves changes on the feature branch for review; the script does not
stash, reset, retry, or bypass failures. If pushing or PR creation fails, the
validated commit remains available for manual publication.
No-op runs also leave the new local feature branch in place. Full validation
requires the frontend test prerequisites, including Playwright Chromium and Zsh
for terminal tests.

To update dependencies, increment the library's integer release version, and open
a pull request:

```bash
./script/bump_version.sh
```

For example, version `75` becomes `76`. Version bumps still require a clean,
up-to-date default-branch checkout so retrying does not accidentally increment
an already edited release version again. They use the same full validation as
dependency PRs. The script always runs
the Python and frontend dependency updater described above, including major
versions while respecting compatibility and frontend safety policies. It bumps
the library version, refreshes both lockfiles, and rebuilds the frontend, then
commits all these changes together on a `release/bump-<version>` branch and opens
one PR using the repository template. The private frontend package version and
pinned pnpm version remain unchanged.
Failures leave local changes for review rather than publishing an unvalidated PR.
The script does not merge the PR, create a GitHub release, or upload to PyPI;
the existing release-publishing workflow still runs when a release is published.

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

For editable development, run `./script/setup.sh`, then `uv run axis`. To use Zsh
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
axis web
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
- **Open web interface** starts the local web server and opens
  the default browser. Ctrl-C stops it and returns to navigation.

Choose a menu item by number, or open the suggested command prompt with `c`.
Menu names and descriptions are separated by a visible ` | `, without relying
on color. Interface choices use the same separator before their live status.
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
Guided **read** and **browse** share numbered handler choices from the previous
check for the same target in this session, labelled as previously checked.
Use `r` for an explicit live check or refresh, or `m` to enter a known handler
without discovery. Failed or empty checks still allow manual entry and retry.
Switching devices or changing the connection target clears the choices; no
interface checks run automatically before a read.
Choose a number or name, use `/text` to filter without renumbering (`/` clears),
or `m` to enter a handler name manually. Enter or `b` cancels selection.
Other guided inputs show allowed values or explain their purpose with examples;
optional fields explicitly say how to skip them. An empty alias clears it.
Doctor runs all checks, discovery scans for the default five seconds, and event
listening uses automatic transport without asking users to reconfirm those
defaults. The launcher prints the option and command path for customization
through its command prompt. Event listening still offers an optional topic.
Registration collects host, login name, and optional alias, then offers one
default-No advanced-settings step for port, protocol, certificate verification,
authentication, and companion mode. Skipping it preserves the canonical defaults,
including HTTPS certificate verification; disabling verification remains explicit.

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
entry. After **discover** in the same launcher session, **add** offers the
scan's numbered devices and fills in the chosen host; `m` allows manual host
entry, and Enter or `b` cancels before any login prompts. Numbers match the
human-readable discovery table. These are unauthenticated announcements from
the last successful scan, not a new reachability check. A new successful scan
replaces the session choices; closing the launcher discards them. Login details
and transport settings are still requested explicitly. Discovery JSON is unchanged.
For scripts,
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

Direct remote account writes require `--apply`. Without it, commands validate and
preview the intended change without contacting the device or reading a
password. Updates require an explicit `--privilege` so a password change cannot
silently downgrade an administrator. Account deletion additionally requires
interactive confirmation or `--yes` in scripts.
Applied account changes now also verify that the connected serial matches the
registered target before writing. A mismatch fails rather than changing another
device at a reused address.

Guided account changes collect the account, privilege, and password-change intent
before showing a credential-free preview with the device serial and host.
Only a final, default-No confirmation authorizes the write; deletion explicitly
names the account and target. Declining leaves the preview without submitting
anything or reading a password. Hidden password entry, when needed, follows
approval; cancelling it still submits nothing. Direct commands and the command
prompt retain their explicit `--apply` contract.
Interrupting approval or password entry reports that no account write was
submitted. Once execution has been handed to the application, interruption
conservatively reports that the outcome may be unknown and advises reading
accounts before retrying. It does not claim rollback, and never retries a write
automatically. Both interruption cases retain exit status 130 in direct use.

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
The applications handler recognizes the `application` API Discovery entry or,
for older devices, the `Properties.EmbeddedDevelopment.Version` parameter.

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
