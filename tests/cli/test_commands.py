"""Canonical CLI behavior, offline completion, and explicit mutation contracts."""

from __future__ import annotations

import importlib.metadata
import json
import sys
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock, patch

import click
from click.testing import CliRunner, Result
import pytest

from axis.cli import commands, entrypoint, operations
from axis.cli.commands import Runtime, cli
from axis.cli.storage import (
    ConnectionSettings,
    DeviceRecord,
    DeviceRegistry,
    StorageError,
)

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator
    from pathlib import Path


@pytest.fixture
def runtime(tmp_path: Path) -> Iterator[Runtime]:
    """Provide a private registry and explicitly owned CLI loop."""
    value = Runtime(config_path=tmp_path / "devices.toml")
    value.registry.upsert(
        DeviceRecord(
            "SERIAL",
            ConnectionSettings("camera.local", "root", "top-secret-test-password"),
            "front door",
            "M123",
        )
    )
    with value.runner:
        yield value


def invoke(runtime: Runtime, args: list[str]) -> Result:
    """Invoke canonical parsing against a private runtime."""
    return CliRunner().invoke(cli, args, obj=runtime)


@pytest.mark.parametrize(
    "path",
    [
        [],
        ["devices"],
        ["device"],
        ["api"],
        ["params"],
        ["events"],
        ["accounts"],
        ["completion"],
        ["devices", "list"],
        ["devices", "add"],
        ["devices", "discover"],
        ["devices", "remove"],
        ["devices", "credentials"],
        ["devices", "alias"],
        ["device", "health"],
        ["api", "list"],
        ["api", "interfaces"],
        ["api", "read"],
        ["api", "browse"],
        ["params", "show"],
        ["events", "list"],
        ["events", "listen"],
        ["accounts", "list"],
        ["accounts", "create"],
        ["accounts", "update"],
        ["accounts", "delete"],
        ["doctor"],
        ["completion", "zsh"],
    ],
)
def test_help_contract(runtime: Runtime, path: list[str]) -> None:
    """Every published command path has help without device requests."""
    result = invoke(runtime, [*path, "--help"])
    assert result.exit_code == 0, result.output
    assert "Usage:" in result.output


def test_bare_invocation_and_groups(runtime: Runtime) -> None:
    """Non-TTY launcher refuses to prompt, while bare groups show help."""
    result = invoke(runtime, [])
    assert result.exit_code == 2
    assert "terminal" in result.output
    result = invoke(runtime, ["api"])
    assert "Commands:" in result.output


def test_launcher_and_debug(runtime: Runtime, monkeypatch: pytest.MonkeyPatch) -> None:
    """TTY invocation launches guided navigation instead of legacy routing."""
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
    with (
        patch("axis.cli.commands.sys.stdout") as stdout,
        patch("axis.cli.interactive.launch") as launch,
    ):
        stdout.isatty.return_value = True
        cli.main(args=["--debug"], obj=runtime, standalone_mode=False)
    assert runtime.interactive
    launch.assert_called_once_with(runtime, cli)


def test_local_list_json_and_config_override(runtime: Runtime, tmp_path: Path) -> None:
    """Local listing is redacted and respects explicit root configuration."""
    result = invoke(runtime, ["devices", "list", "--json"])
    assert result.exit_code == 0
    assert json.loads(result.stdout)[0]["alias"] == "front door"
    assert "private" not in result.output
    result = invoke(runtime, ["--config", str(tmp_path / "missing"), "devices", "list"])
    assert result.exit_code == 0
    assert json.loads(result.stdout) == []


@pytest.mark.parametrize(
    ("args", "operation", "payload"),
    [
        (["device", "health"], "health", {"healthy": True}),
        (["api", "list"], "list_apis", [{"id": "api"}]),
        (["api", "interfaces"], "list_interfaces", [{"name": "api"}]),
        (["api", "read", "api", "--path", "0.name"], "read_interface", {"name": "api"}),
        (["params", "show"], "parameters", {"value": "read"}),
        (["events", "list"], "list_events", [{"topic": "topic"}]),
        (["accounts", "list"], "list_accounts", [{"username": "root"}]),
    ],
)
def test_shared_reads(
    runtime: Runtime, args: list[str], operation: str, payload: object
) -> None:
    """Direct reads dispatch structured results to shared operations."""
    with patch.object(
        operations, operation, new=AsyncMock(return_value=payload)
    ) as read:
        result = invoke(runtime, [*args, "--device", "front door", "--json"])
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout) == payload
    assert read.await_args.args[0].serial == "SERIAL"


def test_device_target_never_guessed(runtime: Runtime) -> None:
    """Only interactive mode can inherit selection; explicit identifiers win."""
    runtime.selected = "SERIAL"
    with pytest.raises(click.UsageError):
        runtime.device(None)
    runtime.interactive = True
    assert runtime.device(None).serial == "SERIAL"
    assert runtime.device("front door").serial == "SERIAL"
    with pytest.raises(StorageError):
        runtime.device("missing")


def test_discovery_is_explicit(runtime: Runtime) -> None:
    """Discovery runs only when requested, with validated bounded duration."""
    with patch.object(
        commands,
        "discover_axis_devices",
        new=AsyncMock(return_value=[{"host": "camera"}]),
    ) as discover:
        result = invoke(runtime, ["devices", "discover", "--seconds", "1", "--json"])
    assert result.exit_code == 0
    discover.assert_awaited_once_with(scan_seconds=1.0)
    assert invoke(runtime, ["devices", "discover", "--seconds", "0"]).exit_code == 2


def test_registration_and_credentials(runtime: Runtime, tmp_path: Path) -> None:
    """Registration retains transport settings and credentials never reach output."""
    password = tmp_path / "password"
    password.write_text("new-private\n")
    record = DeviceRecord("NEW", ConnectionSettings("new.local", "root", "new-private"))
    with patch.object(
        operations, "identify", new=AsyncMock(return_value=record)
    ) as identify:
        result = invoke(
            runtime,
            [
                "devices",
                "add",
                "--host",
                "new.local",
                "--username",
                "root",
                "--password-file",
                str(password),
                "--alias",
                "new",
                "--port",
                "443",
                "--proto",
                "https",
                "--verify-ssl",
                "--auth",
                "digest",
                "--companion",
                "--json",
            ],
        )
    assert result.exit_code == 0, result.output
    settings = identify.await_args.args[0]
    assert (
        settings.port,
        settings.web_proto,
        settings.verify_ssl,
        settings.auth_scheme,
        settings.is_companion,
    ) == (443, "https", True, "digest", True)
    assert runtime.registry.resolve("new").serial == "NEW"
    result = invoke(
        runtime,
        [
            "devices",
            "credentials",
            "--device",
            "new",
            "--username",
            "viewer",
            "--password-file",
            str(password),
            "--json",
        ],
    )
    assert result.exit_code == 0, result.output
    assert runtime.registry.resolve("new").config.username == "viewer"
    assert "new-private" not in result.output


def test_secret_input_contract(runtime: Runtime, tmp_path: Path) -> None:
    """Missing, malformed, and unreadable secrets fail explicitly without leaking."""
    with pytest.raises(click.UsageError):
        commands.secret(runtime, None)
    with pytest.raises(click.ClickException):
        commands.secret(runtime, tmp_path / "missing")
    password = tmp_path / "password"
    for value in ("", "x" * 65, "first\nsecond"):
        password.write_text(value)
        with pytest.raises(click.BadParameter):
            commands.secret(runtime, password)
    password.write_bytes(b"\xff")
    with pytest.raises(click.ClickException):
        commands.secret(runtime, password)
    runtime.interactive = True
    with patch.object(click, "prompt", return_value="hidden") as prompt:
        assert commands.secret(runtime, None) == "hidden"
    assert prompt.call_args.kwargs["hide_input"] is True


def test_removal_confirmation_and_selection(runtime: Runtime) -> None:
    """Local removal needs intent and clears deleted interactive selection."""
    assert invoke(runtime, ["devices", "remove", "--device", "SERIAL"]).exit_code == 2
    runtime.interactive = True
    runtime.selected = "SERIAL"
    with patch.object(click, "confirm", return_value=False):
        assert invoke(runtime, ["devices", "remove"]).exit_code == 1
    with patch.object(click, "confirm", return_value=True):
        result = invoke(runtime, ["devices", "remove", "--json"])
    assert result.exit_code == 0
    assert runtime.selected is None
    assert runtime.registry.load() == {}


@pytest.mark.parametrize("action", ["create", "update", "delete"])
def test_account_previews_never_connect(runtime: Runtime, action: str) -> None:
    """Preview does not need a password or invoke any network operation."""
    with patch.object(operations, "change_account", new=AsyncMock()) as change:
        arguments = ["accounts", action, "viewer", "--device", "SERIAL", "--json"]
        if action == "update":
            arguments.extend(["--privilege", "viewer"])
        result = invoke(runtime, arguments)
    assert result.exit_code == 0
    assert json.loads(result.stdout)["status"] == "preview"
    change.assert_not_awaited()


def test_account_apply_and_username_validation(
    runtime: Runtime, tmp_path: Path
) -> None:
    """Applied writes use the same validator and explicit destructive intent."""
    assert (
        invoke(
            runtime, ["accounts", "create", "bad-user", "--device", "SERIAL"]
        ).exit_code
        == 2
    )
    assert (
        invoke(
            runtime, ["accounts", "delete", "viewer", "--device", "SERIAL", "--apply"]
        ).exit_code
        == 2
    )
    password = tmp_path / "password"
    password.write_text("private-password")
    with patch.object(operations, "change_account", new=AsyncMock()) as change:
        result = invoke(
            runtime,
            [
                "accounts",
                "create",
                "viewer",
                "--device",
                "SERIAL",
                "--apply",
                "--password-file",
                str(password),
                "--privilege",
                "operator",
                "--json",
            ],
        )
        assert result.exit_code == 0, result.output
        assert change.await_args.args[1:] == (
            "create",
            "viewer",
            "private-password",
            "operator",
        )
        result = invoke(
            runtime,
            ["accounts", "delete", "viewer", "--device", "SERIAL", "--apply", "--yes"],
        )
        assert result.exit_code == 0
        assert change.await_args.args[3] is None
    assert "private-password" not in result.output


def test_account_options_are_action_specific(runtime: Runtime) -> None:
    """Updates never silently change privilege; irrelevant flags are rejected."""
    assert (
        invoke(runtime, ["accounts", "update", "root", "--device", "SERIAL"]).exit_code
        == 2
    )
    assert (
        invoke(
            runtime, ["accounts", "create", "root", "--device", "SERIAL", "--yes"]
        ).exit_code
        == 2
    )
    assert (
        invoke(
            runtime,
            [
                "accounts",
                "delete",
                "root",
                "--device",
                "SERIAL",
                "--privilege",
                "admin",
            ],
        ).exit_code
        == 2
    )


def test_account_privilege_only_update(runtime: Runtime) -> None:
    """Changing privileges does not demand or overwrite an existing password."""
    with patch.object(operations, "change_account", new=AsyncMock()) as operation:
        result = invoke(
            runtime,
            [
                "accounts",
                "update",
                "root",
                "--device",
                "SERIAL",
                "--apply",
                "--privilege",
                "operator",
                "--json",
            ],
        )
    assert result.exit_code == 0, result.output
    assert operation.await_args.args[3] is None
    assert json.loads(result.stdout)["password_change"] is False
    runtime.interactive = True
    with (
        patch.object(click, "confirm", return_value=False),
        patch.object(commands, "secret") as secret,
        patch.object(operations, "change_account", new=AsyncMock()),
    ):
        result = invoke(
            runtime,
            [
                "accounts",
                "update",
                "root",
                "--device",
                "SERIAL",
                "--apply",
                "--privilege",
                "operator",
            ],
        )
    assert result.exit_code == 0
    secret.assert_not_called()
    with (
        patch.object(click, "confirm", return_value=True),
        patch.object(commands, "secret", return_value="new-hidden") as secret,
        patch.object(operations, "change_account", new=AsyncMock()) as operation,
    ):
        result = invoke(
            runtime,
            [
                "accounts",
                "update",
                "root",
                "--device",
                "SERIAL",
                "--apply",
                "--privilege",
                "operator",
            ],
        )
    assert result.exit_code == 0
    assert operation.await_args.args[3] == "new-hidden"


def test_alias_update_is_offline(runtime: Runtime) -> None:
    """Existing registrations can get nice names without device authentication."""
    result = invoke(
        runtime, ["devices", "alias", "front camera", "--device", "SERIAL", "--json"]
    )
    assert result.exit_code == 0, result.output
    assert runtime.registry.resolve("front camera").serial == "SERIAL"


def test_registration_preserves_existing_alias(
    runtime: Runtime, tmp_path: Path
) -> None:
    """Re-registering without an alias does not erase the friendly identifier."""
    password = tmp_path / "password"
    password.write_text("new-secret")
    with patch.object(
        operations,
        "identify",
        new=AsyncMock(
            return_value=DeviceRecord(
                "SERIAL", ConnectionSettings("camera.local", "root", "new-secret")
            )
        ),
    ):
        result = invoke(
            runtime,
            [
                "devices",
                "add",
                "--host",
                "camera.local",
                "--username",
                "root",
                "--password-file",
                str(password),
            ],
        )
    assert result.exit_code == 0
    assert runtime.registry.resolve("front door").serial == "SERIAL"


def test_registration_preserves_concurrent_alias(
    runtime: Runtime, tmp_path: Path
) -> None:
    """An alias changed during registration is preserved at the write boundary."""
    password = tmp_path / "password"
    password.write_text("new-secret")
    original_upsert = DeviceRegistry.upsert

    def concurrent_alias_change(
        registry: DeviceRegistry, record: DeviceRecord, *, preserve_alias: bool = False
    ) -> None:
        registry.update_alias("SERIAL", "newest-alias")
        original_upsert(registry, record, preserve_alias=preserve_alias)

    with (
        patch.object(
            operations,
            "identify",
            new=AsyncMock(
                return_value=DeviceRecord(
                    "SERIAL", ConnectionSettings("camera.local", "root", "new-secret")
                )
            ),
        ),
        patch.object(DeviceRegistry, "upsert", new=concurrent_alias_change),
    ):
        result = invoke(
            runtime,
            [
                "devices",
                "add",
                "--host",
                "camera.local",
                "--username",
                "root",
                "--password-file",
                str(password),
                "--json",
            ],
        )
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout)["alias"] == "newest-alias"
    assert runtime.registry.resolve("newest-alias").serial == "SERIAL"


def test_new_https_registration_verification(runtime: Runtime, tmp_path: Path) -> None:
    """New HTTPS verifies TLS unless explicitly disabled, preserving old settings."""
    password = tmp_path / "password"
    password.write_text("hidden")

    async def identify(settings: ConnectionSettings) -> DeviceRecord:
        return DeviceRecord("NEW", settings)

    for flags, expected in [([], True), (["--no-verify-ssl"], False)]:
        with patch.object(operations, "identify", side_effect=identify):
            result = invoke(
                runtime,
                [
                    "devices",
                    "add",
                    "--host",
                    "camera.local",
                    "--username",
                    "root",
                    "--proto",
                    "https",
                    "--password-file",
                    str(password),
                    *flags,
                ],
            )
        assert result.exit_code == 0, result.output
        assert runtime.registry.resolve("NEW").config.verify_ssl is expected
    assert runtime.registry.resolve("SERIAL").config.verify_ssl is False


def test_doctor_selected_diagnostic_and_shadowing(runtime: Runtime) -> None:
    """Doctor distinguishes selected checks and wrong executable origin."""
    with patch.object(commands.shutil, "which", return_value="/other/axis"):
        result = invoke(runtime, ["doctor", "--check", "path", "--json"])
    checks = json.loads(result.stdout)
    assert len(checks) == 1
    assert checks[0]["status"] == "warning"
    assert "expects" in checks[0]["message"]


def test_human_tables_escape_terminal_controls(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """External device strings cannot inject control sequences into human tables."""
    commands.render([{"name": "\x1b[31mdevice\n"}])
    output = capsys.readouterr().out
    assert "\x1b" not in output
    assert "\\u001b" in output


def test_live_output_is_json_lines(runtime: Runtime) -> None:
    """Streaming results are independent JSON records and chatter stays on stderr."""

    async def listen(
        record: DeviceRecord,
        emit: Callable[[object], None],
        topic: str | None,
        mode: str,
    ) -> None:
        emit({"topic": topic, "state": "on"})
        emit({"topic": topic, "state": "off"})

    with patch.object(operations, "listen", side_effect=listen):
        result = invoke(
            runtime,
            [
                "events",
                "listen",
                "--device",
                "SERIAL",
                "--topic",
                "topic",
                "--stream-mode",
                "event",
                "--json",
            ],
        )
    assert result.exit_code == 0, result.output
    assert len([json.loads(line) for line in result.stdout.splitlines()]) == 2
    assert "Listening" in result.stderr


def test_browse_tty_contract(runtime: Runtime) -> None:
    """Interactive API browsing fails clearly when invoked from a pipe."""
    assert invoke(runtime, ["api", "browse", "--device", "SERIAL"]).exit_code == 2
    with (
        patch.object(sys.stdin, "isatty", return_value=True),
        patch.object(sys.stdout, "isatty", return_value=True),
        patch("axis.cli.interactive.browse_api") as browse,
    ):
        cli.main(
            args=["api", "browse", "--device", "SERIAL"],
            obj=runtime,
            standalone_mode=False,
        )
    browse.assert_called_once()


def test_completion_reads_only_local_store(runtime: Runtime, tmp_path: Path) -> None:
    """Completion uses explicit configuration, descriptions, and safe failure."""
    context = click.Context(cli)
    context.params["config"] = runtime.config_path
    parameter = click.Option(["--device"])
    items = commands.complete_devices(context, parameter, "front")
    assert [item.value for item in items] == ["front door"]
    assert "SERIAL" in items[0].help
    context.params["config"] = tmp_path / "broken"
    context.params["config"].write_text("[")
    assert commands.complete_devices(context, parameter, "") == []
    context.params.clear()
    with patch.object(
        commands, "default_config_path", return_value=tmp_path / "absent"
    ):
        assert commands.complete_devices(context, parameter, "") == []


def test_completion_source(runtime: Runtime) -> None:
    """Generated Zsh source uses the installed canonical executable."""
    result = invoke(runtime, ["completion", "zsh"])
    assert result.exit_code == 0
    assert "_AXIS_COMPLETE=zsh_complete" in result.output
    assert "compdef" in result.output


def test_doctor_offline_results(runtime: Runtime, tmp_path: Path) -> None:
    """Doctor reports configuration faults and permissions without exposing secrets."""
    result = invoke(runtime, ["doctor", "--json"])
    assert result.exit_code == 0
    assert "top-secret-test-password" not in result.stdout
    runtime.config_path.chmod(0o644)
    with patch.object(commands.shutil, "which", return_value=None):
        result = invoke(runtime, ["doctor", "--json"])
    checks = json.loads(result.stdout)
    assert any(check["check"] == "permissions" for check in checks)
    assert any(
        check["check"] == "path" and check["status"] == "warning" for check in checks
    )
    runtime.config_path = tmp_path / "broken"
    runtime.config_path.write_text("[")
    result = invoke(runtime, ["doctor", "--json"])
    assert result.exit_code == 1
    assert json.loads(result.stdout)[-1]["status"] == "error"


@pytest.mark.parametrize("payload", [[], ["one"], {"value": 1}, [{"a": 1}, {"a": 2}]])
def test_render_shapes(payload: object, capsys: pytest.CaptureFixture[str]) -> None:
    """Human output supports structured scalar, list, and table results."""
    commands.render(payload)
    assert capsys.readouterr().out


@pytest.mark.parametrize(
    ("error", "code"),
    [
        (operations.OperationError("Device operation failed."), 1),
        (StorageError("Registry failed."), 1),
        (click.UsageError("Invalid command."), 2),
        (KeyboardInterrupt(), 130),
        (click.Abort(), 130),
        (BrokenPipeError(), 0),
    ],
)
def test_main_error_contract(error: BaseException, code: int) -> None:
    """Process entrypoint maps expected failures and interruption consistently."""
    with (
        patch.object(cli, "main", side_effect=error),
        pytest.raises(SystemExit) as caught,
    ):
        commands.main()
    assert caught.value.code == code


def test_main_success_and_explicit_failure() -> None:
    """Explicit diagnostic failure remains nonzero outside Click's standalone mode."""
    with patch.object(cli, "main", return_value=None):
        commands.main()
    with patch.object(cli, "main", return_value=1), pytest.raises(SystemExit) as caught:
        commands.main()
    assert caught.value.code == 1


def test_optional_bootstrap(capsys: pytest.CaptureFixture[str]) -> None:
    """Missing extras get actionable errors; installed extras reach canonical parsing."""
    with (
        patch.object(
            importlib.metadata,
            "version",
            side_effect=importlib.metadata.PackageNotFoundError,
        ),
        pytest.raises(SystemExit) as caught,
    ):
        entrypoint.main()
    assert caught.value.code == 1
    message = capsys.readouterr().err
    metadata = importlib.metadata.metadata("axis")
    assert metadata["Requires-Python"] in message
    assert "click" in message
    assert "prompt-toolkit" in message
    with patch.object(commands, "main") as run:
        entrypoint.main()
    run.assert_called_once()


@pytest.mark.parametrize("absent", [True, False])
def test_bootstrap_uses_declared_metadata(
    absent: bool, capsys: pytest.CaptureFixture[str]
) -> None:
    """Declared extras, version ranges, Python requirements, and package names drive diagnostics."""
    distribution = MagicMock(spec=importlib.metadata.Distribution)
    distribution.requires = [
        "base>=1",
        'conditional-base>=1; python_version >= "3"',
        'fake-ui>=2; extra == "cli"',
        'fake-engine>=4; extra == "cli"',
        'test-only>=1; extra == "test"',
        'inactive-ui>=1; extra == "cli" and sys_platform == "unsupported-platform"',
    ]
    distribution.metadata = {"Name": "axis-demo", "Requires-Python": ">=3.16.0"}
    distribution.version = "99"

    def installed_version(name: str) -> str:
        if name == "fake-ui" and absent:
            raise importlib.metadata.PackageNotFoundError(name)
        return {"fake-ui": "1.0", "fake-engine": "4.5"}[name]

    with (
        patch.object(importlib.metadata, "distribution", return_value=distribution),
        patch.object(importlib.metadata, "version", side_effect=installed_version),
        pytest.raises(SystemExit) as caught,
    ):
        entrypoint.main()
    assert caught.value.code == 1
    message = capsys.readouterr().err
    assert "axis-demo 99" in message
    assert "fake-ui>=2" in message
    assert "fake-engine" not in message
    assert "axis-demo[cli]" in message
    assert "Python >=3.16.0" in message
