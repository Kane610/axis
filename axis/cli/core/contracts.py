# ruff: noqa: D100,D101,D102

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal, Protocol

if TYPE_CHECKING:
    from axis.cli.core.context import CliContext
    from axis.cli.core.io import CliIO


@dataclass(frozen=True)
class CommandCapabilities:
    requires_device: bool = False
    destructive: bool = False
    read_only_safe: bool = True


@dataclass
class CommandResult:
    status: Literal["ok", "error", "cancelled"] = "ok"
    message: str | None = None
    payload: object | None = None


class Command(Protocol):
    id: str
    title: str
    capabilities: CommandCapabilities

    async def run(self, ctx: CliContext, io: CliIO) -> CommandResult: ...
