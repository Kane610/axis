"""Guided and typed command paths share validation, completion, and safe execution."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock, patch

import click
from prompt_toolkit.completion import CompleteEvent
from prompt_toolkit.document import Document
import pytest

from axis.cli import interactive, operations
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


def test_select_device(runtime: Runtime) -> None:
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
    runtime.registry.remove("SERIAL")
    interactive.select_device(runtime)


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
        patch.object(click, "prompt", side_effect=["value", "1", "", "path", "viewer"]),
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
        pytest.raises(click.UsageError),
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
            operations, "list_interfaces", new=AsyncMock(return_value=[{"name": "api"}])
        ),
        patch.object(click, "prompt", side_effect=["bad", "1", "0.name", "1", "", "b"]),
        patch.object(interactive, "execute") as execute,
    ):
        interactive.browse_api(runtime, record, cli)
    assert execute.call_args_list[0].args[2] == [
        "api",
        "read",
        "api",
        "--device",
        "SERIAL",
        "--path",
        "0.name",
    ]
    assert execute.call_args_list[1].args[2] == [
        "api",
        "read",
        "api",
        "--device",
        "SERIAL",
    ]
    with patch.object(operations, "list_interfaces", new=AsyncMock(return_value=[])):
        interactive.browse_api(runtime, record, cli)


def test_launcher_navigation_and_shared_execution(runtime: Runtime) -> None:
    """Home, subgroup, selection, prompt, back, and operation dispatch are consistent."""
    root = click.Group(
        "axis",
        commands={"api": click.Group("api", commands={"list": click.Command("list")})},
    )
    with (
        patch.object(
            click, "prompt", side_effect=["invalid", "b", "s", "c", "1", "1", "b", "e"]
        ),
        patch.object(interactive, "select_device") as select,
        patch.object(interactive, "command_prompt") as prompt,
        patch.object(interactive, "guided_arguments", return_value=["--json"]),
        patch.object(interactive, "execute") as execute,
    ):
        interactive.launch(runtime, root)
    select.assert_called_once()
    prompt.assert_called_once()
    execute.assert_called_once_with(runtime, root, ["api", "list", "--json"])


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
        patch.object(click, "prompt", side_effect=["s", "e"]),
        patch.object(interactive, "select_device", side_effect=error),
    ):
        interactive.launch(runtime, cli)


@pytest.mark.parametrize("error", [KeyboardInterrupt, EOFError, click.Abort])
def test_launcher_cancellation(runtime: Runtime, error: type[BaseException]) -> None:
    """Cancel at home exits; cancellation in a submenu returns home."""
    with patch.object(click, "prompt", side_effect=error):
        interactive.launch(runtime, cli)
    with patch.object(click, "prompt", side_effect=["1", error(), "e"]):
        interactive.launch(runtime, cli)
