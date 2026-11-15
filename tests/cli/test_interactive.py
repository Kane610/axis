"""Guided and typed command paths share validation, completion, and safe execution."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock, patch

import click
from prompt_toolkit.completion import CompleteEvent
from prompt_toolkit.document import Document
import pytest

from axis.application import operations
from axis.application.records import DiscoverySnapshot
from axis.cli import interactive
from axis.cli.commands import Runtime, cli
from axis.cli.storage import ConnectionSettings, DeviceRecord, StorageError

if TYPE_CHECKING:
    from collections.abc import Iterator


@pytest.fixture
def runtime(tmp_path: Path) -> Iterator[Runtime]:
    """Own a private local device context and loop."""
    value = Runtime(config_path=tmp_path / "devices.toml", interactive=True)
    value.registry.upsert(
        DeviceRecord(
            "SERIAL", ConnectionSettings("camera", "root", "secret"), "front door"
        )
    )
    with value.runner:
        yield value


@pytest.mark.parametrize(
    ("text", "start"),
    [
        ("", 0),
        ("api li", 4),
        ("api read 'long name", 9),
        ('api read "long name"', 9),
        ("api read long\\ name", 9),
        ("api list ", 9),
        ("'a\\b'", 0),
    ],
)
def test_shell_token_boundaries(text: str, start: int) -> None:
    """Quoted and escaped spaces remain part of the argument being completed."""
    assert interactive.token_start(text) == start


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("", "devices"),
        ("api li", "list"),
        ("events listen --stream-mode e", "event"),
        ("api list --device 'front", "'front door'"),
        ("api list --d", "--device"),
        ("axis api li", "list"),
    ],
)
def test_completer_reuses_click(runtime: Runtime, text: str, expected: str) -> None:
    """Interactive completion uses canonical commands, options, and local identifiers."""
    completer = interactive.CommandCompleter(cli, runtime)
    with patch.object(operations, "list_apis", new=AsyncMock()) as operation:
        values = list(completer.get_completions(Document(text), CompleteEvent()))
    assert expected in [value.text for value in values]
    operation.assert_not_awaited()


def test_path_completion(runtime: Runtime, tmp_path: Path) -> None:
    """Local paths are quoted and completion reports unreadable directories."""
    path = tmp_path / "file with spaces"
    path.touch()
    directory = tmp_path / "folder"
    directory.mkdir()
    completer = interactive.CommandCompleter(cli, runtime)
    text = f"--config {tmp_path}/f"
    values = list(completer.get_completions(Document(text), CompleteEvent()))
    assert any("file with spaces" in value.text for value in values)
    assert any("folder/" in value.text for value in values)
    with patch.object(Path, "iterdir", side_effect=PermissionError):
        assert list(completer.get_completions(Document(text), CompleteEvent())) == []
    values = list(
        completer.get_completions(Document(f"--config {tmp_path}/"), CompleteEvent())
    )
    assert values


def test_execute_equivalent_to_direct(
    runtime: Runtime, capsys: pytest.CaptureFixture[str]
) -> None:
    """Guided dispatch resolves the same explicit target and returns JSON results."""
    with patch.object(
        operations, "list_apis", new=AsyncMock(return_value=[{"id": "api"}])
    ) as operation:
        assert interactive.execute(
            runtime, cli, ["api", "list", "--device", "front door", "--json"]
        )
    operation.assert_awaited_once()
    assert '"id": "api"' in capsys.readouterr().out


@pytest.mark.parametrize(
    "error",
    [
        click.UsageError("bad"),
        StorageError("invalid"),
        operations.OperationError("offline"),
        KeyboardInterrupt(),
        click.Abort(),
    ],
)
def test_execute_errors_keep_session(runtime: Runtime, error: BaseException) -> None:
    """Errors and cancellation return to navigation, rather than dropping the session."""
    with patch.object(cli, "main", side_effect=error):
        assert not interactive.execute(runtime, cli, ["api", "list"])
    with patch.object(cli, "main", return_value=1):
        assert not interactive.execute(runtime, cli, ["doctor"])


def test_select_device(runtime: Runtime, capsys: pytest.CaptureFixture[str]) -> None:
    """Device selection handles explicit choice, cancellation, and invalid input."""
    with patch.object(click, "prompt", return_value="b"):
        interactive.select_device(runtime)
    assert runtime.selected is None
    with (
        patch.object(click, "prompt", return_value="bad"),
        pytest.raises(click.UsageError),
    ):
        interactive.select_device(runtime)
    with patch.object(click, "prompt", return_value="1"):
        interactive.select_device(runtime)
    assert runtime.selected == "SERIAL"
    record = runtime.registry.resolve("SERIAL")
    record.alias = ""
    runtime.registry.upsert(record)
    capsys.readouterr()
    with patch.object(click, "prompt", return_value=" b "):
        assert not interactive.select_device(runtime)
    assert capsys.readouterr().out.count("SERIAL") == 1
    runtime.registry.remove("SERIAL")
    interactive.select_device(runtime)


def test_device_picker_displays_discovered_names_safely(
    runtime: Runtime, capsys: pytest.CaptureFixture[str]
) -> None:
    """Discovered names label unaliased devices without interpreting terminal controls."""
    record = runtime.registry.resolve("SERIAL")
    record.alias = ""
    record.discovery = DiscoverySnapshot(
        last_seen=datetime.now(UTC), host="192.0.2.1", name="Fresh \x1b[31mname"
    )
    runtime.registry.upsert(record)
    with patch.object(click, "prompt", return_value="b"):
        interactive.select_device(runtime)
    output = capsys.readouterr().out
    assert "Fresh" in output
    assert "\\u001b" in output
    assert "\x1b" not in output


def test_guided_arguments_derive_from_parser(runtime: Runtime) -> None:
    """Required values, defaults, device selection, and opt-in flags come from Click."""
    command = click.Command(
        "test",
        params=[
            click.Argument(["name"]),
            click.Option(["--device"]),
            click.Option(["--password-file"]),
            click.Option(["--yes"], is_flag=True),
            click.Option(["--json", "as_json"], is_flag=True, default=False),
            click.Option(["--apply"], is_flag=True, help="Apply"),
            click.Option(["--empty"]),
            click.Option(["--path"]),
            click.Option(["--choice"], default="viewer", type=click.Choice(["viewer"])),
        ],
    )
    with (
        patch.object(click, "prompt", side_effect=["1", "value", "", "path", "viewer"]),
        patch.object(click, "confirm", return_value=True),
    ):
        args = interactive.guided_arguments(runtime, command)
    assert args == ["value", "--apply", "--path", "path", "--choice", "viewer"]
    assert runtime.selected == "SERIAL"
    with (
        patch.object(click, "prompt", side_effect=["value", "", "path", "viewer"]),
        patch.object(click, "confirm", return_value=False),
    ):
        assert "--apply" not in interactive.guided_arguments(runtime, command)
    runtime.selected = None
    runtime.registry.remove("SERIAL")
    with (
        patch.object(click, "prompt", return_value="value"),
        pytest.raises(click.Abort),
    ):
        interactive.guided_arguments(runtime, command)


def test_guided_unknown_parameter_is_ignored(runtime: Runtime) -> None:
    """Non-input Click parameters are not turned into invented prompts."""
    command = click.Command("test", params=[MagicMock(spec=click.Parameter)])
    with patch.object(command, "make_context", return_value=click.Context(command)):
        assert interactive.guided_arguments(runtime, command) == []


def test_guided_dual_flag_honors_both_choices(runtime: Runtime) -> None:
    """Guided TLS settings preserve canonical defaults and explicit disabling."""
    command = click.Command(
        "test", params=[click.Option(["--verify-ssl/--no-verify-ssl"], default=True)]
    )
    with patch.object(click, "confirm", return_value=False) as confirm:
        assert interactive.guided_arguments(runtime, command) == ["--no-verify-ssl"]
    assert confirm.call_args.kwargs["default"] is True
    with patch.object(click, "confirm", return_value=True):
        assert interactive.guided_arguments(runtime, command) == ["--verify-ssl"]


def test_command_prompt_quotes_and_navigation(runtime: Runtime) -> None:
    """Malformed quoting remains editable and never dispatches an empty command."""
    session = MagicMock()
    session.prompt.side_effect = [
        "",
        "api read 'bad",
        "api list --device 'front door'",
        "/back",
    ]
    with (
        patch.object(interactive, "PromptSession", return_value=session) as factory,
        patch.object(interactive, "execute", return_value=True) as execute,
    ):
        interactive.command_prompt(runtime, cli)
    execute.assert_called_once_with(
        runtime, cli, ["api", "list", "--device", "front door"]
    )
    assert session.prompt.call_args_list[2].kwargs["default"] == "api read 'bad"
    assert isinstance(factory.call_args.kwargs["history"], interactive.DummyHistory)
    for error in (EOFError, KeyboardInterrupt):
        session.prompt.side_effect = error
        with patch.object(interactive, "PromptSession", return_value=session):
            interactive.command_prompt(runtime, cli)


def test_command_prompt_accepts_copied_commands(runtime: Runtime) -> None:
    """Pasted shell examples and bare axis work without recursive launchers."""
    session = MagicMock()
    session.prompt.side_effect = ["axis api list --device SERIAL", "axis", "/back"]
    with (
        patch.object(interactive, "PromptSession", return_value=session),
        patch.object(interactive, "execute") as execute,
    ):
        interactive.command_prompt(runtime, cli)
    assert execute.call_args_list[0].args[2] == ["api", "list", "--device", "SERIAL"]
    assert execute.call_args_list[1].args[2] == ["--help"]


def test_completion_at_cursor_preserves_existing_suffix(runtime: Runtime) -> None:
    """Completing in the middle of a token does not duplicate its remaining text."""
    completer = interactive.CommandCompleter(cli, runtime)
    values = list(
        completer.get_completions(
            Document("api list", cursor_position=6), CompleteEvent()
        )
    )
    assert [value.text for value in values] == ["li"]
    values = list(
        completer.get_completions(
            Document("api liwrong", cursor_position=6), CompleteEvent()
        )
    )
    assert values == []


def test_api_browse_dispatches_canonical_read(runtime: Runtime) -> None:
    """Browse reads use the same parser and support optional nested traversal."""
    record = runtime.registry.resolve("SERIAL")
    with (
        patch.object(
            operations,
            "list_interfaces",
            new=AsyncMock(return_value=[{"name": "api10"}, {"name": "api2"}]),
        ),
        patch.object(click, "prompt", side_effect=["bad", "1", "0.name", "1", "", "b"]),
        patch.object(interactive, "execute") as execute,
    ):
        interactive.browse_api(runtime, record, cli)
    assert execute.call_args_list[0].args[2] == [
        "api",
        "read",
        "api2",
        "--device",
        "SERIAL",
        "--path",
        "0.name",
    ]
    assert execute.call_args_list[1].args[2] == [
        "api",
        "read",
        "api2",
        "--device",
        "SERIAL",
    ]
    with patch.object(operations, "list_interfaces", new=AsyncMock(return_value=[])):
        interactive.browse_api(runtime, record, cli)


def test_launcher_navigation_and_shared_execution(runtime: Runtime) -> None:
    """Regrouped menus dispatch every kind of operation through its canonical path."""
    with (
        patch.object(
            click,
            "prompt",
            side_effect=[
                "invalid",
                "b",
                "s",
                "c",
                "1",
                "1",
                "2",
                "1",
                "b",
                "s",
                "b",
                "2",
                "1",
                "b",
                "3",
                "1",
                "2",
                "1",
                "b",
                "b",
                "e",
            ],
        ),
        patch.object(interactive, "select_device", return_value=True) as select,
        patch.object(interactive, "command_prompt") as prompt,
        patch.object(interactive, "guided_arguments", return_value=[]),
        patch.object(interactive, "execute") as execute,
    ):
        interactive.launch(runtime, cli)
    assert select.call_count == 2
    prompt.assert_called_once()
    assert [call.args for call in execute.call_args_list] == [
        (runtime, cli, path)
        for path in (
            ["device", "health"],
            ["api", "list"],
            ["devices", "list"],
            ["doctor"],
            ["completion", "zsh"],
        )
    ]


def test_launcher_selects_before_device_operations(
    runtime: Runtime, capsys: pytest.CaptureFixture[str]
) -> None:
    """Entering device operations lists saved devices before offering commands."""
    with (
        patch.object(click, "prompt", side_effect=["1", "1", "1", "b", "e"]),
        patch.object(interactive, "execute") as execute,
    ):
        interactive.launch(runtime, cli)
    output = capsys.readouterr().out
    assert output.index("front door (SERIAL, camera)") < output.index("Health")
    assert runtime.selected == "SERIAL"
    execute.assert_called_once_with(runtime, cli, ["device", "health"])


def test_management_alias_selects_device_before_name(runtime: Runtime) -> None:
    """Renaming a saved device asks for its target before collecting the new name."""
    runtime.registry.upsert(
        DeviceRecord("SECOND", ConnectionSettings("other", "root", "secret"), "other")
    )
    runtime.selected = "SERIAL"
    with patch.object(
        click, "prompt", side_effect=["2", "4", "2", "renamed", "b", "e"]
    ) as prompt:
        interactive.launch(runtime, cli)
    assert "Device number" in prompt.call_args_list[2].args[0]
    assert prompt.call_args_list[3].args[0] == "name"
    assert runtime.registry.resolve("SECOND").alias == "renamed"
    assert runtime.registry.resolve("SERIAL").alias == "front door"


@pytest.mark.parametrize("action", ["4", "5", "6"])
def test_management_cancelled_picker_never_reuses_previous_device(
    runtime: Runtime, action: str
) -> None:
    """Alias, removal, and credentials require a fresh choice even with a previous selection."""
    runtime.selected = "SERIAL"
    with (
        patch.object(
            click, "prompt", side_effect=["2", action, "b", "b", "e"]
        ) as prompt,
        patch.object(click, "confirm") as confirm,
        patch.object(interactive, "execute") as execute,
    ):
        interactive.launch(runtime, cli)
    assert "Device number" in prompt.call_args_list[2].args[0]
    execute.assert_not_called()
    confirm.assert_not_called()


@pytest.mark.parametrize("empty_registry", [False, True])
def test_launcher_cancelled_selection_does_not_enter_device_menu(
    runtime: Runtime, capsys: pytest.CaptureFixture[str], empty_registry: bool
) -> None:
    """Cancelling a new selection never silently reuses a previously selected device."""
    if empty_registry:
        runtime.registry.remove("SERIAL")
        answers = ["1", "e"]
    else:
        runtime.selected = "SERIAL"
        answers = ["1", "b", "e"]
    with (
        patch.object(click, "prompt", side_effect=answers),
        patch.object(interactive, "execute") as execute,
    ):
        interactive.launch(runtime, cli)
    assert "Axis / Use a device" not in capsys.readouterr().out
    execute.assert_not_called()


def test_launcher_enter_defaults_are_non_exiting(
    runtime: Runtime, capsys: pytest.CaptureFixture[str]
) -> None:
    """Enter stays at home and returns from submenus without executing anything."""
    with (
        patch.object(click, "prompt", side_effect=["", "2", "b", "e"]) as prompt,
        patch.object(interactive, "execute") as execute,
    ):
        interactive.launch(runtime, cli)
    assert [call.kwargs["default"] for call in prompt.call_args_list] == [
        "",
        "",
        "b",
        "",
    ]
    assert capsys.readouterr().out.count("Axis / home") == 3
    execute.assert_not_called()


@pytest.mark.parametrize("error", [KeyboardInterrupt, EOFError, click.Abort])
def test_launcher_cancelled_field_returns_to_its_menu(
    runtime: Runtime, capsys: pytest.CaptureFixture[str], error: type[BaseException]
) -> None:
    """Cancelling registration input leaves management open and never submits the command."""
    with (
        patch.object(
            click, "prompt", side_effect=["2", "3", "b", error(), "1", "b", "e"]
        ),
        patch.object(interactive, "execute") as execute,
    ):
        interactive.launch(runtime, cli)
    captured = capsys.readouterr()
    output = captured.out
    assert "Ctrl-C cancels this command" in output
    assert "Cancelled; returning to the menu." in captured.err
    assert output.count("Axis / Manage saved devices") == 3
    execute.assert_called_once_with(runtime, cli, ["devices", "list"])


@pytest.mark.parametrize("error", [KeyboardInterrupt, EOFError, click.Abort])
def test_launcher_cancelled_picker_returns_home(
    runtime: Runtime, error: type[BaseException]
) -> None:
    """Cancelling the device picker returns home rather than exiting the launcher."""
    with patch.object(click, "prompt", side_effect=["1", error(), "e"]):
        interactive.launch(runtime, cli)


@pytest.mark.parametrize(
    "error",
    [
        StorageError("bad"),
        operations.OperationError("offline"),
        click.UsageError("invalid"),
    ],
)
def test_launcher_recovers_expected_errors(runtime: Runtime, error: Exception) -> None:
    """Expected operation failures leave the guided launcher usable."""
    with (
        patch.object(click, "prompt", side_effect=["1", "e"]),
        patch.object(interactive, "select_device", side_effect=error),
    ):
        interactive.launch(runtime, cli)


@pytest.mark.parametrize("error", [KeyboardInterrupt, EOFError, click.Abort])
def test_launcher_cancellation(runtime: Runtime, error: type[BaseException]) -> None:
    """Cancel at the home prompt exits; cancellation at a submenu prompt goes back."""
    with patch.object(click, "prompt", side_effect=error):
        interactive.launch(runtime, cli)
    with patch.object(click, "prompt", side_effect=["2", error(), "e"]):
        interactive.launch(runtime, cli)
