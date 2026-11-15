"""Guide users through Axis commands with menus and suggestions from the CLI definitions."""

from __future__ import annotations

import json
from pathlib import Path
import shlex
from typing import TYPE_CHECKING

import click
from click.shell_completion import ZshComplete, split_arg_string
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.history import DummyHistory

from axis.application import operations
from axis.application.errors import StorageError

if TYPE_CHECKING:
    from collections.abc import Iterable

    from prompt_toolkit.completion import CompleteEvent
    from prompt_toolkit.document import Document

    from axis.application.records import DeviceRecord
    from axis.cli.commands import Runtime


def display_text(value: str) -> str:
    """Escape control characters in device-provided text before showing it in a terminal."""
    return value if value.isprintable() else json.dumps(value, ensure_ascii=True)


def token_start(text: str) -> int:
    """Find the current shell token while respecting quotes and escaped spaces."""
    start = 0
    quote = ""
    escaped = False
    for index, character in enumerate(text):
        if escaped:
            escaped = False
        elif character == "\\" and quote != "'":
            escaped = True
        elif quote:
            if character == quote:
                quote = ""
        elif character in ("'", '"'):
            quote = character
        elif character.isspace():
            start = index + 1
    return start


class CommandCompleter(Completer):
    """Suggest commands, options, and saved devices without making device requests."""

    def __init__(self, command: click.Group, runtime: Runtime) -> None:
        """Use the CLI's command definitions and the chosen device configuration file."""
        self.command = command
        self.runtime = runtime

    def get_completions(
        self, document: Document, complete_event: CompleteEvent
    ) -> Iterable[Completion]:
        """Suggest matching command words and values without running a command."""
        text = document.text_before_cursor
        start = token_start(text)
        args = split_arg_string(text[:start])
        if args and args[0] == "axis":
            args = args[1:]
        incomplete_tokens = split_arg_string(text[start:])
        incomplete = incomplete_tokens[0] if incomplete_tokens else ""
        completion = ZshComplete(self.command, {}, "axis", "_AXIS_COMPLETE")
        items = completion.get_completions(
            ["--config", str(self.runtime.config_path), *args], incomplete
        )
        for item in items:
            if item.type in ("file", "dir"):
                path = Path(incomplete).expanduser()
                parent = path if incomplete.endswith("/") else path.parent
                prefix = "" if incomplete.endswith("/") else path.name
                try:
                    paths = sorted(parent.iterdir())
                except OSError:
                    click.echo(
                        "Path completion unavailable: directory is unreadable.",
                        err=True,
                    )
                    continue
                for candidate in paths:
                    if candidate.name.startswith(prefix):
                        value = str(candidate)
                        if candidate.is_dir():
                            value += "/"
                        yield Completion(
                            shlex.quote(value), start_position=start - len(text)
                        )
                continue
            replacement = shlex.quote(item.value)
            end = document.find_next_word_ending(
                include_current_position=True, WORD=True
            )
            suffix = (
                document.text_after_cursor[:end]
                if document.text_after_cursor
                and not document.text_after_cursor[0].isspace()
                else ""
            )
            if suffix:
                if not replacement.endswith(suffix):
                    continue
                replacement = replacement[: -len(suffix)]
            yield Completion(
                replacement,
                start_position=start - len(text),
                display=item.value,
                display_meta=item.help or "",
            )


def execute(runtime: Runtime, command: click.Group, args: list[str]) -> bool:
    """Run a CLI command and show errors without closing the interactive session."""
    try:
        result = command.main(
            args=["--config", str(runtime.config_path), *args],
            prog_name="axis",
            obj=runtime,
            standalone_mode=False,
        )
        return not isinstance(result, int) or result == 0
    except click.ClickException as exc:
        exc.show()
    except (StorageError, operations.OperationError) as exc:
        click.echo(f"Error: {exc}", err=True)
    except KeyboardInterrupt, click.Abort:
        click.echo("Cancelled; returning to navigation.", err=True)
    return False


def select_device(runtime: Runtime) -> bool:
    """Choose a saved device offline, returning false when selection is cancelled."""
    records = list(runtime.registry.load().values())
    if not records:
        click.echo("No registered devices. Choose Manage saved devices to add one.")
        return False
    for index, record in enumerate(records, 1):
        name = (
            record.alias
            or (record.discovery.name if record.discovery else "")
            or "Axis device"
        )
        click.echo(
            f"  {index}. {display_text(name)} ({record.serial}, {record.config.host})"
        )
    answer = (
        click.prompt("Device number (Enter or b returns; Ctrl-C cancels)", default="b")
        .strip()
        .lower()
    )
    if answer == "b":
        return False
    if not answer.isdigit() or not 1 <= int(answer) <= len(records):
        msg = "Choose a device number from the list."
        raise click.UsageError(msg)
    runtime.selected = records[int(answer) - 1].serial
    return True


def guided_arguments(runtime: Runtime, command: click.Command) -> list[str]:
    """Ask for arguments using the CLI command's definitions, so menu validation stays consistent."""
    args: list[str] = []
    click.echo("Ctrl-C cancels this command and returns to the menu.")
    with command.make_context(
        command.name or "axis", [], resilient_parsing=True
    ) as context:
        defaults = context.params
    for parameter in command.params:
        if isinstance(parameter, click.Argument):
            value = click.prompt(parameter.name or "Value", type=parameter.type)
            args.append(str(value))
            continue
        if not isinstance(parameter, click.Option):
            continue
        if parameter.name in ("as_json", "yes", "password_file"):
            continue
        if parameter.name == "device":
            if runtime.selected is None:
                select_device(runtime)
            if runtime.selected is None:
                msg = "Select a device before running this operation."
                raise click.UsageError(msg)
            continue
        if parameter.is_flag:
            if click.confirm(
                parameter.help or parameter.opts[0],
                default=bool(defaults.get(parameter.name or "")),
            ):
                args.append(parameter.opts[0])
            elif parameter.secondary_opts:
                args.append(parameter.secondary_opts[0])
            continue
        default = defaults.get(parameter.name or "")
        if not parameter.required and default is None:
            value = click.prompt(
                parameter.help or parameter.name or "Value", default=""
            )
            if value == "":
                continue
        else:
            value = click.prompt(
                parameter.help or parameter.name or "Value",
                default=default,
                type=parameter.type,
                show_default=True,
            )
        if value != "":
            args.extend([parameter.opts[0], str(value)])
    return args


def command_prompt(runtime: Runtime, command: click.Group) -> None:
    """Suggest commands as users type and let them correct mistakes without saving history."""
    session: PromptSession[str] = PromptSession(
        completer=CommandCompleter(command, runtime),
        complete_while_typing=True,
        history=DummyHistory(),
    )
    click.echo(
        "Enter commands with or without 'axis'. /back, Ctrl-C, or Ctrl-D returns."
    )
    click.echo("Tab shows suggestions. Command history is disabled for secret safety.")
    retry = ""
    while True:
        try:
            text = session.prompt(
                f"axis[{runtime.selected or 'no device'}]> ", default=retry
            )
        except EOFError, KeyboardInterrupt:
            return
        if text.strip() == "/back":
            return
        if not text.strip():
            continue
        try:
            args = shlex.split(text)
        except ValueError:
            click.echo(
                "Incomplete quoting. Correct the command; nothing was executed.",
                err=True,
            )
            retry = text
            continue
        retry = ""
        if args and args[0] == "axis":
            args = args[1:]
        execute(runtime, command, args or ["--help"])


def browse_api(runtime: Runtime, record: DeviceRecord, command: click.Group) -> None:
    """Let the user select a library handler and read it through the CLI command parser."""
    interfaces = runtime.run(operations.list_interfaces(record))
    if not interfaces:
        click.echo("No interfaces available.")
        return
    click.echo("Enter returns from the interface list; Ctrl-C cancels browsing.")
    while True:
        for index, interface in enumerate(interfaces, 1):
            click.echo(f"  {index}. {interface['name']}")
        answer = click.prompt("Interface number (b returns)", default="b")
        if answer == "b":
            return
        if not answer.isdigit() or not 1 <= int(answer) <= len(interfaces):
            click.echo("Choose an interface number from the list.", err=True)
            continue
        name = str(interfaces[int(answer) - 1]["name"])
        path = click.prompt("Dot path (empty shows all data)", default="")
        args = ["api", "read", name, "--device", record.serial]
        if path:
            args.extend(["--path", path])
        execute(runtime, command, args)


def _command_paths(
    command: click.Command, path: list[str]
) -> dict[click.Command, list[str]]:
    """Find canonical command paths even when menus display commands in other groups."""
    paths = {command: path}
    if isinstance(command, click.Group):
        for name, entry in command.commands.items():
            paths.update(_command_paths(entry, [*path, name]))
    return paths


def launch(runtime: Runtime, command: click.Group) -> None:
    """Separate saved-device management from operations on a chosen device."""
    paths = _command_paths(command, [])
    device_menu = click.Group(
        help="Choose a saved device, then read data, listen to events, or manage accounts."
    )
    tools_menu = click.Group(
        help="Check the local installation or set up shell completion."
    )
    home = click.Group(commands={"Use a device": device_menu})
    for name, entry in command.commands.items():
        if name == "devices":
            home.commands["Manage saved devices"] = entry
        elif name in {"doctor", "completion"}:
            tools_menu.commands[name] = entry
        elif name == "device" and isinstance(entry, click.Group):
            device_menu.commands.update(entry.commands)
        else:
            device_menu.commands[name] = entry
    home.commands["Setup & diagnostics"] = tools_menu
    labels = {
        "health": "Health",
        "api": "APIs",
        "params": "Parameters",
        "events": "Events",
        "accounts": "Accounts",
    }
    stack: list[tuple[click.Group, list[str]]] = [(home, [])]
    while True:
        group, path = stack[-1]
        click.echo(f"\nAxis / {' / '.join(path) or 'home'}")
        click.echo(f"Device: {runtime.selected or 'none selected'}")
        entries = list(group.commands.items())
        names = [labels.get(name, name) for name, _ in entries]
        width = max((len(name) for name in names), default=0)
        for index, (name, entry) in enumerate(entries, 1):
            click.echo(
                f"  {index}. {labels.get(name, name):<{width}} "
                f"{entry.get_short_help_str(limit=1000)}"
            )
        using_device = len(stack) > 1 and stack[1][0] is device_menu
        if using_device:
            click.echo("  s. Change device")
        click.echo(
            "  c. Command prompt   b. Back   e. Exit"
            if len(stack) > 1
            else "  c. Command prompt   e. Exit   Enter stays here"
        )
        choosing_menu = True
        try:
            answer = (
                click.prompt(
                    "Select",
                    default="b" if len(stack) > 1 else "",
                    show_default=len(stack) > 1,
                )
                .strip()
                .lower()
            )
            choosing_menu = False
            if answer == "e":
                return
            if answer == "b" or not answer:
                if len(stack) > 1:
                    stack.pop()
                continue
            if answer == "s" and using_device:
                select_device(runtime)
                continue
            if answer == "c":
                command_prompt(runtime, command)
                continue
            if not answer.isdigit() or not 1 <= int(answer) <= len(entries):
                click.echo("Choose a listed number or shortcut.", err=True)
                continue
            name, entry = entries[int(answer) - 1]
            if isinstance(entry, click.Group):
                if entry is device_menu and not select_device(runtime):
                    continue
                stack.append((entry, [*path, labels.get(name, name)]))
                continue
            args = guided_arguments(runtime, entry)
            execute(runtime, command, [*paths[entry], *args])
        except (StorageError, operations.OperationError) as exc:
            click.echo(f"Error: {exc}", err=True)
        except click.ClickException as exc:
            exc.show()
        except KeyboardInterrupt, click.Abort, EOFError:
            if len(stack) == 1 and choosing_menu:
                return
            click.echo("Cancelled; returning to the menu.", err=True)
            if choosing_menu:
                stack.pop()
