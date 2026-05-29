# ruff: noqa: D100,D103,TC001

from __future__ import annotations

import asyncio

from axis.cli.packs.devices import DeviceEntry, run_on_selected_device
from axis.device import AxisDevice


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


def list_supported_apis_flow(serial: str, device_entry: DeviceEntry) -> None:
    apis = asyncio.run(fetch_supported_apis(device_entry))
    if not apis:
        print("No APIs discovered for this device.")  # noqa: T201
        return

    print(f"\nSupported APIs for {serial}:")  # noqa: T201
    for idx, api in enumerate(apis, 1):
        print(  # noqa: T201
            f"  {idx}. {api['id']} | {api['name']} | "
            f"v{api['version']} | {api['status']}"
        )


async def run_api_read_action(device_entry: DeviceEntry, api_id: str) -> None:
    async def _operation(device: AxisDevice) -> None:
        if api_id == "basic-device-info":
            info = await device.vapix.basic_device_info.get_all_properties()
            item = info.get("0")
            if item is None:
                print("No basic device information found.")  # noqa: T201
                return
            serial_number = str(getattr(item, "serial_number", "unknown"))
            product_name = str(getattr(item, "product_full_name", "unknown"))
            firmware = str(getattr(item, "firmware_version", "unknown"))
            print("\nBasic device info:")  # noqa: T201
            print(f"  Serial: {serial_number}")  # noqa: T201
            print(f"  Product: {product_name}")  # noqa: T201
            print(f"  Firmware: {firmware}")  # noqa: T201
            return

        if api_id == "api-discovery":
            versions = await device.vapix.api_discovery.get_supported_versions()
            print("\nAPI Discovery supported versions:")  # noqa: T201
            for version in versions:
                print(f"  - {version}")  # noqa: T201
            return

        if api_id == "user-management":
            groups = await device.vapix.user_groups.get_user_groups()
            user = groups.get("0")
            if user is None:
                print("Current user group information is unavailable.")  # noqa: T201
                return
            print("\nCurrent user rights:")  # noqa: T201
            print(f"  Username: {user.name}")  # noqa: T201
            print(f"  Privileges: {user.privileges.value}")  # noqa: T201
            return

        print(f"No read action implemented yet for API '{api_id}'.")  # noqa: T201

    await run_on_selected_device(device_entry, _operation)


def api_drill_down_flow(device_entry: DeviceEntry) -> None:
    apis = asyncio.run(fetch_supported_apis(device_entry))
    if not apis:
        print("No APIs discovered for this device.")  # noqa: T201
        return

    while True:
        print("\nAPI drill-down:")  # noqa: T201
        for idx, api in enumerate(apis, 1):
            print(  # noqa: T201
                f"  {idx}. {api['id']} | {api['name']} | "
                f"v{api['version']} | {api['status']}"
            )
        print("  b. Back")  # noqa: T201
        print("  e. Exit")  # noqa: T201

        selection = input("Select API [b/e]: ").strip().lower()
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

        if index < 1 or index > len(apis):
            print("Invalid selection.")  # noqa: T201
            continue

        selected_api = apis[index - 1]
        print("\nSelected API:")  # noqa: T201
        print(f"  ID: {selected_api['id']}")  # noqa: T201
        print(f"  Name: {selected_api['name']}")  # noqa: T201
        print(f"  Version: {selected_api['version']}")  # noqa: T201
        print(f"  Status: {selected_api['status']}")  # noqa: T201

        print("\nAPI actions:")  # noqa: T201
        print("  1. Run read action")  # noqa: T201
        print("  b. Back")  # noqa: T201
        print("  e. Exit")  # noqa: T201
        action_choice = input("Select action [1/b/e]: ").strip().lower()
        if action_choice == "e":
            print("Exiting.")  # noqa: T201
            raise SystemExit(0)
        if action_choice == "b":
            continue
        if action_choice != "1":
            print("Invalid option. Please enter 1, b, or e.")  # noqa: T201
            continue

        asyncio.run(run_api_read_action(device_entry, selected_api["id"]))
