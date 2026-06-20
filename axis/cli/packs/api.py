# ruff: noqa: D100,D103,TC001

from __future__ import annotations

import asyncio
from dataclasses import asdict, is_dataclass
from enum import Enum
import os
from pprint import pformat
from typing import TYPE_CHECKING, cast

from axis.cli.packs.devices import (
    DeviceEntry,
    _format_device_operations_label,
    run_on_selected_device,
)
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
        interface_states = await device.vapix.inspect_interfaces(
            refresh_discovery=True,
            probe=True,
        )

        return [
            {
                "name": state.name,
                "api_id": state.api_id,
                "api_version": state.api_version,
                "listed": state.listed,
                "probe_attempted": state.probe_attempted,
                "probe_succeeded": state.probe_succeeded,
                "supported": state.supported,
                "initialized": state.initialized,
                "items": state.items,
            }
            for state in interface_states.values()
        ]

    result = await run_on_selected_device(device_entry, _operation)
    if result is None:
        return []
    return result


def _normalize_payload(value: object) -> object:
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value) and not isinstance(value, type):
        return _normalize_payload(asdict(value))
    if isinstance(value, dict):
        normalized: dict[str, object] = {}
        items = cast("Iterable[tuple[object, object]]", value.items())
        for raw_key, raw_item in items:
            key = str(raw_key)
            normalized[key] = _normalize_payload(raw_item)
        return normalized
    if isinstance(value, (list, tuple, set)):
        payload_iterable = cast("Iterable[object]", value)
        return [_normalize_payload(item) for item in payload_iterable]
    return value


def _traverse_payload(data: object, path: str) -> object:
    current: object = data
    for token in (part for part in path.split(".") if part):
        if isinstance(current, dict):
            current_dict = cast("dict[str, object]", current)
            if token not in current:
                raise KeyError(token)
            next_dict_value: object = current_dict[token]
            current = next_dict_value
            continue

        if isinstance(current, list):
            current_list = cast("list[object]", current)
            index = int(token)
            next_list_value: object = current_list[index]
            current = next_list_value
            continue

        raise TypeError(token)

    return current


def _render_api_discovery_table(payload: object) -> bool:
    if not isinstance(payload, dict) or not payload:
        return False

    rows: list[dict[str, str]] = []
    for key, value in payload.items():
        if not isinstance(value, dict):
            return False
        if not {"id", "name", "version", "status"}.issubset(value):
            return False

        row_id = str(value.get("id", key) or key)
        row_name = str(value.get("name", "") or "<unnamed>")
        row_version = str(value.get("version", "") or "-")
        row_status = str(value.get("status", "") or "unknown")
        rows.append(
            {
                "id": row_id,
                "name": row_name,
                "version": row_version,
                "status": row_status,
            }
        )

    id_width = max(len("id"), *(len(row["id"]) for row in rows))
    name_width = max(len("name"), *(len(row["name"]) for row in rows))
    version_width = max(len("version"), *(len(row["version"]) for row in rows))
    status_width = max(len("status"), *(len(row["status"]) for row in rows))

    print(  # noqa: T201
        f"  {'#':>2}  {'id':<{id_width}}  {'name':<{name_width}}"
        f"  {'version':<{version_width}}  {'status':<{status_width}}"
    )
    print(f"  {'-' * (18 + id_width + name_width + version_width + status_width)}")  # noqa: T201
    for idx, row in enumerate(rows, 1):
        print(  # noqa: T201
            f"  {idx:>2}. {row['id']:<{id_width}}"
            f"  {row['name']:<{name_width}}"
            f"  v{row['version']:<{max(version_width - 1, 1)}}"
            f"  {row['status']:<{status_width}}"
        )
    return True


def list_supported_apis_flow(serial: str, device_entry: DeviceEntry) -> None:
    apis = asyncio.run(fetch_supported_apis(device_entry))
    _debug_dump("supported APIs", apis)
    if not apis:
        print("No APIs discovered for this device.")  # noqa: T201
        return

    device_label = _format_device_operations_label(serial, device_entry)
    print(f"\nSupported APIs for {device_label}:")  # noqa: T201
    id_width = max(len("id"), *(len(str(api["id"])) for api in apis))
    name_width = max(len("name"), *(len(str(api["name"])) for api in apis))
    version_width = max(len("version"), *(len(str(api["version"])) for api in apis))
    status_width = max(len("status"), *(len(str(api["status"])) for api in apis))

    print(  # noqa: T201
        f"  {'#':>2}  {'id':<{id_width}}  {'name':<{name_width}}"
        f"  {'version':<{version_width}}  {'status':<{status_width}}"
    )
    print(f"  {'-' * (18 + id_width + name_width + version_width + status_width)}")  # noqa: T201
    for idx, api in enumerate(apis, 1):
        print(  # noqa: T201
            f"  {idx:>2}. {api['id']:<{id_width}}"
            f"  {api['name']:<{name_width}}"
            f"  v{api['version']:<{max(version_width - 1, 1)}}"
            f"  {api['status']:<{status_width}}"
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
        if not _render_api_discovery_table(payload):
            print(pformat(payload))  # noqa: T201

    await run_on_selected_device(device_entry, _operation)


def api_drill_down_flow(device_entry: DeviceEntry) -> None:
    interfaces = asyncio.run(fetch_vapix_interfaces(device_entry))
    if not interfaces:
        print("No interfaces discovered for this device.")  # noqa: T201
        return

    name_width = max(
        len("name"), *(len(str(interface["name"])) for interface in interfaces)
    )
    api_width = max(
        len("api"),
        *(len(str(interface["api_id"] or "internal")) for interface in interfaces),
    )

    while True:
        print("\nInterface drill-down:")  # noqa: T201
        print(  # noqa: T201
            f"  {'#':>2}  {'name':<{name_width}}  {'api':<{api_width}}"
            f"  {'adv':>5}  {'probe':>5}  {'usable':>6}  {'init':>5}  {'items':>5}"
        )
        print(f"  {'-' * (55 + name_width + api_width)}")  # noqa: T201
        for idx, interface in enumerate(interfaces, 1):
            api_label = str(interface["api_id"] or "internal")
            listed = "yes" if bool(interface.get("listed", False)) else "no"
            probe_succeeded = (
                "yes" if bool(interface.get("probe_succeeded", False)) else "no"
            )
            supported = "yes" if bool(interface["supported"]) else "no"
            initialized = "yes" if bool(interface["initialized"]) else "no"
            print(  # noqa: T201
                f"  {idx:>2}. {interface['name']!s:<{name_width}}"
                f"  {api_label:<{api_width}}"
                f"  {listed:>5}"
                f"  {probe_succeeded:>5}"
                f"  {supported:>6}"
                f"  {initialized:>5}"
                f"  {int(interface['items']):>5}"
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
        print(f"  Listed: {selected_interface.get('listed', False)}")  # noqa: T201
        print(  # noqa: T201
            f"  Probe Attempted: {selected_interface.get('probe_attempted', False)}"
        )
        print(  # noqa: T201
            f"  Probe Succeeded: {selected_interface.get('probe_succeeded', False)}"
        )
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
