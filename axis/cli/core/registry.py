# ruff: noqa: D100,D101,D102

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from axis.cli.core.contracts import Command


@dataclass
class CommandRegistry:
    _commands: dict[str, Command] = field(default_factory=dict)

    def register_command(self, command: Command) -> None:
        if command.id in self._commands:
            msg = f"Command '{command.id}' is already registered."
            raise ValueError(msg)
        self._commands[command.id] = command

    def get_command(self, command_id: str) -> Command:
        return self._commands[command_id]

    def list_commands(self) -> list[Command]:
        return list(self._commands.values())
