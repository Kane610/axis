# ruff: noqa: D100,D101,TC003

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from axis.cli.core.gateway import DeviceGateway
    from axis.cli.core.registry import CommandRegistry
    from axis.cli.core.router import CliRouter

DeviceEntry = dict[str, Any]
DeviceStore = dict[str, DeviceEntry]


@dataclass
class CliContext:
    config_path: Path
    device_gateway: DeviceGateway
    command_registry: CommandRegistry | None = None
    router: CliRouter | None = None
    selected_serial: str | None = None
    selected_device: DeviceEntry | None = None
