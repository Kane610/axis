# ruff: noqa: D100,D101,D102

from __future__ import annotations

from typing import TYPE_CHECKING

from aiohttp import ClientSession

from axis.device import AxisDevice
from axis.errors import RequestError
from axis.models.configuration import Configuration

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from axis.cli.core.context import DeviceEntry


class DeviceGateway:
    async def run[ReturnT](
        self,
        device_entry: DeviceEntry,
        operation: Callable[[AxisDevice], Awaitable[ReturnT]],
    ) -> ReturnT | None:
        config_data = device_entry.get("config", {})
        if not isinstance(config_data, dict):
            print("Stored device config is incomplete. Please re-add the device.")  # noqa: T201
            return None

        host = str(config_data.get("host", "")).strip()
        username = str(config_data.get("username", "")).strip()
        password = str(config_data.get("password", ""))
        if not host or not username:
            print("Stored device config is incomplete. Please re-add the device.")  # noqa: T201
            return None

        try:
            async with ClientSession() as session:
                config = Configuration(
                    session=session,
                    host=host,
                    username=username,
                    password=password,
                )
                device = AxisDevice(config)
                return await operation(device)
        except RequestError as exc:
            print(f"Device request failed: {exc}")  # noqa: T201
        except (ValueError, KeyError, OSError) as exc:
            print(f"Failed to connect to selected device: {exc}")  # noqa: T201

        return None
