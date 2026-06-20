# ruff: noqa: D100,D101,TC003

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from axis.cli.core.gateway import DeviceGateway

DeviceEntry = dict[str, Any]
DeviceStore = dict[str, DeviceEntry]


@dataclass
class CliContext:
    config_path: Path
    device_gateway: DeviceGateway
    selected_serial: str | None = None
    selected_device: DeviceEntry | None = None
