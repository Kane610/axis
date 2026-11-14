"""Canonical Axis commands shared by shells, guided menus, and the command prompt."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
import importlib.metadata
import json
import logging
from pathlib import Path
import re
import shutil
import sys
from typing import TYPE_CHECKING, Any

import click
from click.shell_completion import CompletionItem, ZshComplete, add_completion_class

from axis.cli import interactive, operations
from axis.cli.packs.devices import discover_axis_devices
from axis.cli.storage import (
    ConnectionSettings,
    DeviceRecord,
    DeviceRegistry,
    StorageError,
    default_config_path,
)

if TYPE_CHECKING:
    from collections.abc import Coroutine


@add_completion_class
class AxisZshComplete(ZshComplete):
    """Preserve argument boundaries when Zsh passes paths or aliases with spaces."""

    source_template = ZshComplete.source_template.replace(
        'COMP_WORDS="${words[*]}"', 'COMP_WORDS="${(j: :)${(@q)words}}"'
    ).replace(
        'completions_with_descriptions+=("$key":"$descr")',
        r'completions_with_descriptions+=("${key//:/\\:}":"$descr")',
    )


@dataclass
class Runtime:
    """Own configuration, selection, and one event loop for a CLI invocation."""

    config_path: Path = field(default_factory=default_config_path)
    interactive: bool = False
    selected: str | None = None
    runner: asyncio.Runner = field(default_factory=asyncio.Runner)

    @property
    def registry(self) -> DeviceRegistry:
        """Access the selected local registry without creating it."""
        return DeviceRegistry(self.config_path)

    def run[T](self, coroutine: Coroutine[Any, Any, T]) -> T:
        """Run a shared async operation in the owned event loop."""
        return self.runner.run(coroutine)

    def device(self, identifier: str | None) -> DeviceRecord:
        """Resolve explicit targets or the interactive selection, never guess."""
        target = identifier or (self.selected if self.interactive else None)
        if target is None:
            msg = (
                "Select a device with --device SERIAL_OR_ALIAS. "
                "Use 'axis devices list' to see registered devices."
            )
            raise click.UsageError(msg)
        return self.registry.resolve(target)


def complete_devices(
    ctx: click.Context, param: click.Parameter, incomplete: str
) -> list[CompletionItem]:
    """Complete local public identifiers without invoking command callbacks."""
    root = ctx.find_root()
    path = root.params.get("config") or default_config_path()
    try:
        records = DeviceRegistry(Path(path)).load()
    except StorageError, OSError:
        click.echo("Device completion unavailable: check 'axis doctor'.", err=True)
        return []
    return [
        CompletionItem(
            value,
            help=f"{' '.join(record.model.split()) or 'Axis device'} ({record.serial})",
        )
        for record in records.values()
        for value in (record.serial, record.alias)
        if value and value.startswith(incomplete)
    ]


device_option = click.option(
    "-d",
    "--device",
    shell_complete=complete_devices,
    help="Registered serial or alias.",
)
json_option = click.option("--json", "as_json", is_flag=True, help="Output JSON.")


def render(payload: object, as_json: bool = False) -> None:
    """Render structured results without mixing diagnostics into stdout."""
    if as_json or not isinstance(payload, list) or not payload:
        click.echo(
            json.dumps(payload, indent=None if as_json else 2, ensure_ascii=True)
        )
        return
    if not all(isinstance(row, dict) for row in payload):
        click.echo(json.dumps(payload, indent=2))
        return
    columns = list(payload[0])
    rows = [
        [
            value if value.isprintable() else json.dumps(value, ensure_ascii=True)
            for key in columns
            for value in [str(row.get(key, ""))]
        ]
        for row in payload
    ]
    widths = [
        max(len(str(key)), *(len(row[index]) for row in rows))
        for index, key in enumerate(columns)
    ]
    click.echo(
        "  ".join(
            str(key).ljust(width) for key, width in zip(columns, widths, strict=True)
        )
    )
    for row in rows:
        click.echo(
            "  ".join(
                value.ljust(width) for value, width in zip(row, widths, strict=True)
            )
        )


def secret(runtime: Runtime, password_file: Path | None) -> str:
    """Read a secret from an explicit file or a hidden interactive prompt."""
    if password_file is not None:
        try:
            password = password_file.read_text().rstrip("\r\n")
        except (OSError, UnicodeError) as exc:
            msg = "Unable to read the password file."
            raise click.ClickException(msg) from exc
    elif runtime.interactive:
        password = click.prompt("Password", hide_input=True, confirmation_prompt=True)
    else:
        msg = "Provide --password-file PATH. Password arguments are not supported."
        raise click.UsageError(msg)
    if not 1 <= len(password) <= 64 or "\n" in password or "\r" in password:
        msg = "Password must be 1-64 characters on one line."
        raise click.BadParameter(msg)
    return password


def confirm(runtime: Runtime, yes: bool, message: str) -> None:
    """Require explicit noninteractive intent or an interactive confirmation."""
    if yes:
        return
    if not runtime.interactive:
        msg = f"{message} Requires --yes in scripts."
        raise click.UsageError(msg)
    if not click.confirm(message, default=False):
        msg = "Operation cancelled; nothing was changed."
        raise click.ClickException(msg)


@click.group(invoke_without_command=True, no_args_is_help=False)
@click.option(
    "--config",
    type=click.Path(path_type=Path, dir_okay=False),
    help="Device registry path (default: ~/.axis/config.toml).",
)
@click.option("--debug", is_flag=True, help="Enable safe CLI lifecycle diagnostics.")
@click.version_option(package_name="axis")
@click.pass_context
def cli(ctx: click.Context, config: Path | None, debug: bool) -> None:
    """Explore and manage Axis devices.

    Run without arguments for guided navigation. Direct commands never prompt.
    Examples: axis devices list; axis events listen --device front-door.
    """
    runtime = ctx.ensure_object(Runtime)
    if config is not None:
        runtime.config_path = config
    logging.getLogger("axis.cli").setLevel(logging.DEBUG if debug else logging.WARNING)
    logging.getLogger("axis.cli").debug("Canonical CLI argument validation completed.")
    if ctx.invoked_subcommand is None:
        if not sys.stdin.isatty() or not sys.stdout.isatty():
            msg = (
                "Interactive navigation requires a terminal. "
                "Use 'axis --help' or a direct command."
            )
            raise click.UsageError(msg)
        runtime.interactive = True
        interactive.launch(runtime, cli)


@cli.group()
def devices() -> None:
    """Manage locally registered devices; discovery is an explicit network action."""


@devices.command("list")
@json_option
@click.pass_obj
def devices_list(runtime: Runtime, as_json: bool) -> None:
    """List registered identifiers without contacting devices."""
    render(
        [
            {
                "serial": record.serial,
                "alias": record.alias,
                "model": record.model,
                "host": record.config.host,
            }
            for record in runtime.registry.load().values()
        ],
        as_json,
    )


@devices.command()
@click.option(
    "--seconds", type=click.FloatRange(0.1, 60), default=5.0, show_default=True
)
@json_option
@click.pass_obj
def discover(runtime: Runtime, seconds: float, as_json: bool) -> None:
    """Discover devices on the local network without registering or authenticating."""
    render(runtime.run(discover_axis_devices(scan_seconds=seconds)), as_json)


@devices.command()
@click.option("--host", required=True, help="Hostname or IP, without scheme or path.")
@click.option("--username", required=True, help="Device login name.")
@click.option("--password-file", type=click.Path(path_type=Path, dir_okay=False))
@click.option("--alias", default=None, help="Unique local friendly name.")
@click.option("--port", type=click.IntRange(0, 65535), default=0, show_default=True)
@click.option("--proto", type=click.Choice(["http", "https"]), default="http")
@click.option(
    "--verify-ssl/--no-verify-ssl",
    default=True,
    show_default=True,
    help="Verify HTTPS certificates; disable explicitly for trusted self-signed devices.",
)
@click.option("--auth", type=click.Choice(["auto", "basic", "digest"]), default="auto")
@click.option("--companion", is_flag=True, help="Register a companion device.")
@json_option
@click.pass_obj
def add(
    runtime: Runtime,
    host: str,
    username: str,
    password_file: Path | None,
    alias: str | None,
    port: int,
    proto: str,
    verify_ssl: bool,
    auth: str,
    companion: bool,
    as_json: bool,
) -> None:
    """Authenticate, identify, and register a device locally.

    Example: axis devices add --host 192.0.2.10 --username root
    --password-file /private/path --alias front-door
    """
    settings = ConnectionSettings(
        host=host,
        username=username,
        password=secret(runtime, password_file),
        port=port,
        web_proto=proto,
        verify_ssl=verify_ssl,
        auth_scheme=auth,
        is_companion=companion,
    )
    record = runtime.run(operations.identify(settings))
    record.alias = alias if alias is not None else ""
    runtime.registry.upsert(record, preserve_alias=alias is None)
    render(
        {"status": "registered", "serial": record.serial, "alias": record.alias},
        as_json,
    )


@devices.command()
@click.argument("name")
@device_option
@json_option
@click.pass_obj
def alias(runtime: Runtime, name: str, device: str | None, as_json: bool) -> None:
    """Set a unique friendly name offline. An empty name clears the alias."""
    record = runtime.device(device)
    updated = runtime.registry.update_alias(record.serial, name)
    render(
        {"status": "alias-updated", "serial": record.serial, "alias": updated.alias},
        as_json,
    )


@devices.command()
@device_option
@click.option("--yes", is_flag=True, help="Confirm removal from the local registry.")
@json_option
@click.pass_obj
def remove(runtime: Runtime, device: str | None, yes: bool, as_json: bool) -> None:
    """Remove a local registration, not the remote device or its accounts."""
    record = runtime.device(device)
    confirm(runtime, yes, f"Remove registration {record.serial}?")
    runtime.registry.remove(record.serial)
    if runtime.selected == record.serial:
        runtime.selected = None
    render({"status": "removed", "serial": record.serial}, as_json)


@devices.command()
@device_option
@click.option("--username", required=True, help="Replacement device login name.")
@click.option("--password-file", type=click.Path(path_type=Path, dir_okay=False))
@json_option
@click.pass_obj
def credentials(
    runtime: Runtime,
    device: str | None,
    username: str,
    password_file: Path | None,
    as_json: bool,
) -> None:
    """Replace stored login credentials without changing the remote account."""
    record = runtime.device(device)
    runtime.registry.update_credentials(
        record.serial, username, secret(runtime, password_file)
    )
    render({"status": "credentials-updated", "serial": record.serial}, as_json)


@cli.group("device")
def device_group() -> None:
    """Inspect a registered device."""


@device_group.command()
@device_option
@json_option
@click.pass_obj
def health(runtime: Runtime, device: str | None, as_json: bool) -> None:
    """Check device connectivity and identity over the configured transport."""
    render(runtime.run(operations.health(runtime.device(device))), as_json)


@cli.group()
def api() -> None:
    """Discover VAPIX support and read interface data."""


@api.command("list")
@device_option
@json_option
@click.pass_obj
def api_list(runtime: Runtime, device: str | None, as_json: bool) -> None:
    """List supported APIs. Example: axis api list --device front-door --json."""
    render(runtime.run(operations.list_apis(runtime.device(device))), as_json)


@api.command()
@device_option
@json_option
@click.pass_obj
def interfaces(runtime: Runtime, device: str | None, as_json: bool) -> None:
    """Inspect advertised and probed interfaces using the normal initialization model."""
    render(runtime.run(operations.list_interfaces(runtime.device(device))), as_json)


@api.command()
@click.argument("interface")
@click.option("--path", help="Optional dot-separated dictionary/list traversal.")
@device_option
@json_option
@click.pass_obj
def read(
    runtime: Runtime,
    interface: str,
    path: str | None,
    device: str | None,
    as_json: bool,
) -> None:
    """Read an interface, optionally selecting a nested value with --path."""
    render(
        runtime.run(operations.read_interface(runtime.device(device), interface, path)),
        as_json,
    )


@api.command()
@device_option
@click.pass_obj
def browse(runtime: Runtime, device: str | None) -> None:
    """Browse interfaces interactively; requires a terminal. Scripts use interfaces/read."""
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        msg = "API browsing requires a terminal; use api interfaces/read."
        raise click.UsageError(msg)
    interactive.browse_api(runtime, runtime.device(device), cli)


@cli.group()
def params() -> None:
    """Inspect VAPIX parameters."""


@params.command()
@device_option
@json_option
@click.pass_obj
def show(runtime: Runtime, device: str | None, as_json: bool) -> None:
    """Read device parameters with sensitive values redacted."""
    render(runtime.run(operations.parameters(runtime.device(device))), as_json)


@cli.group()
def events() -> None:
    """List event instances and subscribe to live events."""


@events.command("list")
@device_option
@json_option
@click.pass_obj
def events_list(runtime: Runtime, device: str | None, as_json: bool) -> None:
    """List available event instances."""
    render(runtime.run(operations.list_events(runtime.device(device))), as_json)


@events.command()
@device_option
@click.option("--topic", help="Subscribe only to this event topic.")
@click.option(
    "--stream-mode", type=click.Choice(["auto", "rtsp", "event"]), default="auto"
)
@json_option
@click.pass_obj
def listen(
    runtime: Runtime,
    device: str | None,
    topic: str | None,
    stream_mode: str,
    as_json: bool,
) -> None:
    """Listen until Ctrl-C. --json emits one event per line, without status chatter."""
    record = runtime.device(device)
    click.echo(f"Listening on {record.serial}; Ctrl-C stops the stream.", err=True)
    runtime.run(
        operations.listen(
            record, lambda event: render(event, as_json), topic, stream_mode
        )
    )


@cli.group()
def accounts() -> None:
    """Manage remote accounts. Writes require --apply; previews never contact devices."""


@accounts.command("list")
@device_option
@json_option
@click.pass_obj
def accounts_list(runtime: Runtime, device: str | None, as_json: bool) -> None:
    """List account names and privileges, without credentials."""
    render(runtime.run(operations.list_accounts(runtime.device(device))), as_json)


def account_change(
    runtime: Runtime,
    action: str,
    username: str,
    device: str | None,
    password_file: Path | None,
    privilege: str,
    apply: bool,
    yes: bool,
    as_json: bool,
) -> None:
    """Validate and preview account changes before allowing explicit remote writes."""
    if re.fullmatch(r"[a-zA-Z0-9]{1,14}", username) is None:
        msg = "Username must be 1-14 alphanumeric characters."
        raise click.BadParameter(msg)
    record = runtime.device(device)
    payload: dict[str, object] = {
        "status": "applied" if apply else "preview",
        "action": action,
        "device": record.serial,
        "username": username,
    }
    if action != "delete":
        payload["privilege"] = privilege
        payload["password_change"] = action == "create" or password_file is not None
    if not apply:
        render(payload, as_json)
        return
    if action == "delete":
        confirm(runtime, yes, f"Delete account {username} on {record.serial}?")
    change_password = action == "create" or (
        action == "update"
        and (
            password_file is not None
            or (
                runtime.interactive
                and click.confirm("Change the password too?", default=False)
            )
        )
    )
    password = secret(runtime, password_file) if change_password else None
    if action != "delete":
        payload["password_change"] = change_password
    runtime.run(
        operations.change_account(record, action, username, password, privilege)
    )
    render(payload, as_json)


def register_account_write(action: str) -> None:
    """Register account verbs with one consistent parser and execution contract."""

    @accounts.command(
        action,
        help=f"{action.capitalize()} a remote account. Without --apply, only preview.",
    )
    @click.argument("username")
    @device_option
    @click.option("--apply", is_flag=True, help="Perform the remote write.")
    @json_option
    @click.pass_obj
    def command(
        runtime: Runtime,
        username: str,
        device: str | None,
        apply: bool,
        as_json: bool,
        yes: bool = False,
        password_file: Path | None = None,
        privilege: str = "viewer",
    ) -> None:
        account_change(
            runtime,
            action,
            username,
            device,
            password_file,
            privilege,
            apply,
            yes,
            as_json,
        )

    if action == "delete":
        command.params.append(
            click.Option(
                ["--yes"], is_flag=True, help="Confirm destructive writes in scripts."
            )
        )
    else:
        privilege_option = click.Option(
            ["--privilege"],
            type=click.Choice(
                [
                    "viewer",
                    "viewer_ptz",
                    "operator",
                    "operator_ptz",
                    "admin",
                    "admin_ptz",
                ]
            ),
            required=action == "update",
            show_default=True,
            help="Account privilege; updates require an explicit choice.",
        )
        if action == "create":
            privilege_option.default = "viewer"
        command.params.extend(
            [
                click.Option(
                    ["--password-file"],
                    type=click.Path(path_type=Path, dir_okay=False),
                    help="Read the new password from a private file.",
                ),
                privilege_option,
            ]
        )


for _action in ("create", "update", "delete"):
    register_account_write(_action)


@cli.command()
@click.option(
    "--check",
    "selected_check",
    type=click.Choice(["all", "installation", "path", "config", "completion"]),
    default="all",
    show_default=True,
    help="Select one offline diagnostic.",
)
@json_option
@click.pass_obj
def doctor(runtime: Runtime, selected_check: str, as_json: bool) -> None:
    """Check installation and local configuration offline; never modify shell files."""
    actual = shutil.which("axis")
    expected = Path(sys.executable).parent / (
        "axis.exe" if sys.platform == "win32" else "axis"
    )
    shadowed = actual is not None and Path(actual).resolve() != expected.resolve()
    source = Path.home() / ".axis" / "completion.zsh"
    checks: list[dict[str, object]] = [
        {
            "check": "installation",
            "status": "ok",
            "message": f"axis {importlib.metadata.version('axis')}; Python {sys.version.split()[0]}",
        },
        {
            "check": "path",
            "status": "warning" if shadowed or actual is None else "ok",
            "message": (
                f"PATH resolves to {actual}; this environment expects {expected}."
                if shadowed
                else actual or "axis is not on PATH"
            ),
        },
        {
            "check": "completion",
            "status": "info",
            "message": (
                f"Completion script {'exists' if source.is_file() else 'not found'} at {source}. "
                "Source it after compinit; current-shell activation cannot be checked from a child process."
            ),
        },
    ]
    try:
        count = len(runtime.registry.load())
        checks.append(
            {
                "check": "config",
                "status": "ok",
                "message": f"{count} registered devices in {runtime.config_path}",
            }
        )
        if runtime.config_path.exists() and runtime.config_path.stat().st_mode & 0o077:
            checks.append(
                {
                    "check": "permissions",
                    "status": "warning",
                    "message": "Credential file is accessible to other users; restrict permissions.",
                }
            )
    except StorageError, OSError:
        checks.append(
            {
                "check": "config",
                "status": "error",
                "message": "Invalid or unreadable registry.",
            }
        )
    if selected_check != "all":
        checks = [
            check
            for check in checks
            if check["check"] == selected_check
            or (selected_check == "config" and check["check"] == "permissions")
        ]
    render(checks, as_json)
    if any(check["status"] == "error" for check in checks):
        raise click.exceptions.Exit(1)


@cli.group()
def completion() -> None:
    """Generate offline shell completion; setup never changes your shell files."""


@completion.command()
def zsh() -> None:
    """Print Zsh completion. Source the saved script after running compinit."""
    click.echo(AxisZshComplete(cli, {}, "axis", "_AXIS_COMPLETE").source())


def main() -> None:
    """Execute canonical parsing with explicit failure and resource cleanup."""
    runtime = Runtime()
    logging.basicConfig(level=logging.CRITICAL, format="%(message)s")
    try:
        with runtime.runner:
            result = cli.main(prog_name="axis", obj=runtime, standalone_mode=False)
            if isinstance(result, int) and result:
                raise SystemExit(result)
    except (operations.OperationError, StorageError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1) from exc
    except click.ClickException as exc:
        exc.show()
        raise SystemExit(exc.exit_code) from exc
    except (KeyboardInterrupt, click.Abort) as exc:
        click.echo("Interrupted.", err=True)
        raise SystemExit(130) from exc
    except BrokenPipeError as exc:
        raise SystemExit(0) from exc
