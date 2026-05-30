# ruff: noqa: D100,D103,TC001

from __future__ import annotations

import asyncio
from dataclasses import asdict, is_dataclass
from enum import Enum
import os
from pprint import pformat
from typing import TYPE_CHECKING, Any, cast

from axis.cli.packs.devices import DeviceEntry, run_on_selected_device
from axis.device import AxisDevice

if TYPE_CHECKING:
    from collections.abc import Iterable


def _debug_enabled() -> bool:
    value = os.getenv("AXIS_CLI_DEBUG", "").strip().lower()
    return value in {"1", "true", "yes", "on"}


def _debug_dump(label: str, payload: object) -> None:
    if _debug_enabled():
        print(f"[debug] {label}:\n{pformat(payload)}")  # noqa: T201


def register(registry: object, router: object) -> None:
    """Register API-pack commands and menu nodes (explicit composition placeholder)."""


async def fetch_supported_apis(device_entry: DeviceEntry) -> list[dict[str, str]]:
    async def _operation(device: AxisDevice) -> list[dict[str, str]]:
        await device.vapix.api_discovery.update()
        return [
            {
                "id": api.id,
                "name": api.name,
                "version": api.version,
                "status": str(api.status),
            }
            for api in device.vapix.api_discovery.values()
        ]

    result = await run_on_selected_device(device_entry, _operation)
    if result is None:
        return []
    return result


async def fetch_vapix_interfaces(
    device_entry: DeviceEntry,
) -> list[dict[str, str | bool | int]]:
    async def _operation(device: AxisDevice) -> list[dict[str, str | bool | int]]:
        interfaces = device.vapix.interfaces()
        return [
            {
                "name": name,
                "api_id": str(getattr(handler.api_id, "value", "") or ""),
                "api_version": handler.api_version,
                "supported": handler.supported,
                "initialized": handler.initialized,
                "items": len(handler),
            }
            for name, handler in sorted(interfaces.items())
        ]

    result = await run_on_selected_device(device_entry, _operation)
    if result is None:
        return []
    return result


def _normalize_payload(value: object) -> Any:
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value) and not isinstance(value, type):
        return _normalize_payload(asdict(value))
    if isinstance(value, dict):
        normalized: dict[str, Any] = {}
        for key, item in value.items():
            normalized[str(key)] = _normalize_payload(item)
        return normalized
    if isinstance(value, (list, tuple, set)):
        payload_iterable = cast("Iterable[Any]", value)
        return [_normalize_payload(item) for item in payload_iterable]
    return value


def _traverse_payload(data: object, path: str) -> Any:
    current: Any = data
    for token in (part for part in path.split(".") if part):
        if isinstance(current, dict):
            current_dict = cast("dict[str, Any]", current)
            if token not in current:
                raise KeyError(token)
            current = current_dict[token]
            continue

        if isinstance(current, list):
            index = int(token)
            current = current[index]
            continue

        raise TypeError(token)

    return current


def list_supported_apis_flow(serial: str, device_entry: DeviceEntry) -> None:
    apis = asyncio.run(fetch_supported_apis(device_entry))
    _debug_dump("supported APIs", apis)
    if not apis:
        print("No APIs discovered for this device.")  # noqa: T201
        return

    print(f"\nSupported APIs for {serial}:")  # noqa: T201
    for idx, api in enumerate(apis, 1):
        print(  # noqa: T201
            f"  {idx}. {api['id']} | {api['name']} | "
            f"v{api['version']} | {api['status']}"
        )


async def run_api_read_action(
    device_entry: DeviceEntry,
    interface_name: str,
    traversal_path: str | None = None,
) -> None:
    async def _operation(device: AxisDevice) -> None:
        handler = device.vapix.interfaces().get(interface_name)
        if handler is None:
            print(f"No interface named '{interface_name}'.")  # noqa: T201
            return

        if not handler.initialized:
            await handler.update()

        if len(handler) == 0:
            print(f"No data available for interface '{interface_name}'.")  # noqa: T201
            return

        payload: object = {
            obj_id: _normalize_payload(item) for obj_id, item in handler.items()
        }
        if traversal_path:
            try:
                payload = _traverse_payload(payload, traversal_path)
            except ValueError, KeyError, IndexError, TypeError:
                print(f"Traversal path '{traversal_path}' not found.")  # noqa: T201
                return

        _debug_dump(f"{interface_name} read action raw", payload)
        title = (
            f"{interface_name} @ {traversal_path}" if traversal_path else interface_name
        )
        print(f"\nInterface data: {title}")  # noqa: T201
        print(pformat(payload))  # noqa: T201

    await run_on_selected_device(device_entry, _operation)


def api_drill_down_flow(device_entry: DeviceEntry) -> None:
    interfaces = asyncio.run(fetch_vapix_interfaces(device_entry))
    if not interfaces:
        print("No interfaces discovered for this device.")  # noqa: T201
        return

    while True:
        print("\nInterface drill-down:")  # noqa: T201
        for idx, interface in enumerate(interfaces, 1):
            api_id = str(interface["api_id"])
            api_marker = f"[{api_id}]" if api_id else "[internal]"
            print(  # noqa: T201
                f"  {idx}. {interface['name']} {api_marker} | "
                f"supported={interface['supported']} | "
                f"initialized={interface['initialized']} | "
                f"items={interface['items']}"
            )
        print("  b. Back")  # noqa: T201
        print("  e. Exit")  # noqa: T201

        selection = input("Select interface [b/e]: ").strip().lower()
        if selection == "e":
            print("Exiting.")  # noqa: T201
            raise SystemExit(0)
        if selection == "b":
            return

        try:
            index = int(selection)
        except ValueError:
            print("Invalid selection.")  # noqa: T201
            continue

        if index < 1 or index > len(interfaces):
            print("Invalid selection.")  # noqa: T201
            continue

        selected_interface = interfaces[index - 1]
        print("\nSelected interface:")  # noqa: T201
        print(f"  Name: {selected_interface['name']}")  # noqa: T201
        print(f"  API ID: {selected_interface['api_id'] or 'internal'}")  # noqa: T201
        print(f"  API Version: {selected_interface['api_version']}")  # noqa: T201
        print(f"  Supported: {selected_interface['supported']}")  # noqa: T201
        print(f"  Initialized: {selected_interface['initialized']}")  # noqa: T201
        print(f"  Items: {selected_interface['items']}")  # noqa: T201

        print("\nInterface actions:")  # noqa: T201
        print("  1. Show all data")  # noqa: T201
        print("  2. Traverse by path")  # noqa: T201
        print("  b. Back")  # noqa: T201
        print("  e. Exit")  # noqa: T201
        action_choice = input("Select action [1/2/b/e]: ").strip().lower()
        if action_choice == "e":
            print("Exiting.")  # noqa: T201
            raise SystemExit(0)
        if action_choice == "b":
            continue

        if action_choice == "1":
            asyncio.run(
                run_api_read_action(device_entry, str(selected_interface["name"]))
            )
            continue

        if action_choice == "2":
            traversal_path = input(
                "Traversal path (dot notation, e.g. 0.source.items.0.name): "
            ).strip()
            if not traversal_path:
                print("Traversal path cannot be empty.")  # noqa: T201
                continue
            asyncio.run(
                run_api_read_action(
                    device_entry,
                    str(selected_interface["name"]),
                    traversal_path,
                )
            )
            continue

        print("Invalid option. Please enter 1, 2, b, or e.")  # noqa: T201
