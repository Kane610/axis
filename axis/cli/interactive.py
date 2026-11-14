"""Guided Axis navigation and command suggestions backed by the canonical Click tree."""

from __future__ import annotations

from pathlib import Path
import shlex
from typing import TYPE_CHECKING

import click
from click.shell_completion import ZshComplete, split_arg_string
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.history import DummyHistory

from axis.cli import operations
from axis.cli.storage import StorageError

if TYPE_CHECKING:
    from collections.abc import Iterable

    from prompt_toolkit.completion import CompleteEvent
    from prompt_toolkit.document import Document

    from axis.cli.commands import Runtime
    from axis.cli.storage import DeviceRecord


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
    """Reuse Click's completion protocol, including offline device providers."""

    def __init__(self, command: click.Group, runtime: Runtime) -> None:
        """Bind suggestions to the current parser and registry path."""
        self.command = command
        self.runtime = runtime

    def get_completions(
        self, document: Document, complete_event: CompleteEvent
    ) -> Iterable[Completion]:
        """Suggest canonical commands and values without executing callbacks."""
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
    """Execute through the canonical parser while keeping the interactive session alive."""
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


def select_device(runtime: Runtime) -> None:
    """Select an explicit local identifier without contacting devices."""
    records = list(runtime.registry.load().values())
    if not records:
        click.echo("No registered devices. Use devices add or discover.")
        return
    for index, record in enumerate(records, 1):
        click.echo(
            f"  {index}. {record.alias or record.serial} "
            f"({record.serial}, {record.config.host})"
        )
    answer = click.prompt("Device number (b cancels)", default="b")
    if answer == "b":
        return
    if not answer.isdigit() or not 1 <= int(answer) <= len(records):
        msg = "Choose a device number from the list."
        raise click.UsageError(msg)
    runtime.selected = records[int(answer) - 1].serial


def guided_arguments(runtime: Runtime, command: click.Command) -> list[str]:
    """Build a command from its actual argument definitions, not a second schema."""
    args: list[str] = []
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
    """Offer live suggestions and retry malformed input without retaining secrets."""
    session: PromptSession[str] = PromptSession(
        completer=CommandCompleter(command, runtime),
        complete_while_typing=True,
        history=DummyHistory(),
    )
    click.echo("Enter commands with or without 'axis'. /back returns; Ctrl-D returns.")
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
    """Browse actual interface names, dispatching reads through the same parser."""
    interfaces = runtime.run(operations.list_interfaces(record))
    if not interfaces:
        click.echo("No interfaces available.")
        return
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


def launch(runtime: Runtime, command: click.Group) -> None:
    """Navigate the command tree with visible context and predictable back/exit keys."""
    stack: list[tuple[click.Group, list[str]]] = [(command, [])]
    while True:
        group, path = stack[-1]
        click.echo(f"\nAxis / {' / '.join(path) or 'home'}")
        click.echo(f"Device: {runtime.selected or 'none selected'}")
        entries = list(group.commands.items())
        for index, (name, entry) in enumerate(entries, 1):
            click.echo(f"  {index}. {name:<12} {entry.get_short_help_str()}")
        click.echo("  s. Select device   c. Command prompt   b. Back   e. Exit")
        try:
            answer = click.prompt("Select", default="e").strip().lower()
            if answer == "e":
                return
            if answer == "b":
                if len(stack) > 1:
                    stack.pop()
                continue
            if answer == "s":
                select_device(runtime)
                continue
            if answer == "c":
                command_prompt(runtime, command)
                continue
            if not answer.isdigit() or not 1 <= int(answer) <= len(entries):
                click.echo("Choose a listed number, s, c, b, or e.", err=True)
                continue
            name, entry = entries[int(answer) - 1]
            if isinstance(entry, click.Group):
                stack.append((entry, [*path, name]))
                continue
            args = guided_arguments(runtime, entry)
            execute(runtime, command, [*path, name, *args])
        except (StorageError, operations.OperationError) as exc:
            click.echo(f"Error: {exc}", err=True)
        except click.ClickException as exc:
            exc.show()
        except KeyboardInterrupt, click.Abort, EOFError:
            if len(stack) == 1:
                return
            click.echo("Cancelled; returning home.", err=True)
            stack = [(command, [])]
