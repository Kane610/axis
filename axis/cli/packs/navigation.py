# ruff: noqa: D100,D103,TC003

from __future__ import annotations

import asyncio
import getpass
from pathlib import Path
from typing import TYPE_CHECKING

from axis.cli.core.contracts import CommandCapabilities, CommandResult
from axis.cli.core.router import MenuItem, MenuNode
from axis.cli.packs.accounts import account_management_flow
from axis.cli.packs.api import api_drill_down_flow, list_supported_apis_flow
from axis.cli.packs.devices import (
    DeviceEntry,
    DeviceStore,
    _format_device_operations_label,
    config_to_toml_dict,
    delete_device,
    discover_axis_devices,
    edit_device_credentials,
    filter_discovered_devices,
    find_serial_by_host,
    get_config_path,
    health_check_device,
    load_devices,
    migrate_unknown_entry,
    print_registered_devices,
    prompt_for_device,
    save_devices,
    select_device,
    select_discovered_device,
    validate_and_fetch_device,
)
from axis.cli.packs.events import events_flow

if TYPE_CHECKING:
    from axis.cli.core.context import CliContext
    from axis.cli.core.io import CliIO
    from axis.cli.core.registry import CommandRegistry
    from axis.cli.core.router import CliRouter


def _selected_device_from_context(
    ctx: CliContext,
) -> tuple[str, DeviceEntry] | None:
    if ctx.selected_serial is None or ctx.selected_device is None:
        return None
    return (ctx.selected_serial, ctx.selected_device)


class _HealthCheckCommand:
    id = "navigation.health_check"
    title = "Health check"
    capabilities = CommandCapabilities(requires_device=True)

    async def run(self, ctx: CliContext, io: CliIO) -> CommandResult:
        _ = io
        selected = _selected_device_from_context(ctx)
        if selected is None:
            return CommandResult(
                status="cancelled",
                message="No selected device in context.",
            )

        serial, device_entry = selected
        result = await health_check_device(serial, device_entry)
        if result.success:
            message = f"Health check passed ({result.response_time_ms:.1f}ms)."
            return CommandResult(message=message)

        return CommandResult(
            status="error", message=f"Health check failed: {result.error}"
        )


class _EditCredentialsCommand:
    id = "navigation.edit_credentials"
    title = "Edit credentials"
    capabilities = CommandCapabilities(requires_device=True)

    async def run(self, ctx: CliContext, io: CliIO) -> CommandResult:
        _ = io
        selected = _selected_device_from_context(ctx)
        if selected is None:
            return CommandResult(
                status="cancelled",
                message="No selected device in context.",
            )

        serial, device_entry = selected
        updated = await edit_device_credentials(serial, device_entry)
        if not updated:
            return CommandResult(
                status="cancelled", message="Credential update cancelled."
            )

        devices = load_devices(ctx.config_path)
        devices[serial] = updated
        save_devices(ctx.config_path, devices)
        ctx.selected_device = updated
        return CommandResult(message=f"Device {serial} updated.")


class _DeleteDeviceCommand:
    id = "navigation.delete_device"
    title = "Delete device"
    capabilities = CommandCapabilities(requires_device=True, destructive=True)

    async def run(self, ctx: CliContext, io: CliIO) -> CommandResult:
        _ = io
        selected = _selected_device_from_context(ctx)
        if selected is None:
            return CommandResult(
                status="cancelled",
                message="No selected device in context.",
            )

        serial, _device_entry = selected
        devices = load_devices(ctx.config_path)
        if not delete_device(serial, devices):
            return CommandResult(
                status="cancelled", message="Device deletion cancelled."
            )

        save_devices(ctx.config_path, devices)
        ctx.selected_serial = None
        ctx.selected_device = None
        return CommandResult(message=f"Device {serial} deleted.")


def register(registry: CommandRegistry, router: CliRouter) -> None:
    """Register navigation-pack commands and menu nodes."""
    registry.register_command(_HealthCheckCommand())
    registry.register_command(_EditCredentialsCommand())
    registry.register_command(_DeleteDeviceCommand())

    router.register_node(
        MenuNode(
            id="main",
            title="Axis CLI",
            items=[
                MenuItem(
                    key="1",
                    label="Devices",
                    action="navigate",
                    next_node_id="devices",
                )
            ],
        )
    )

    router.register_node(
        MenuNode(
            id="device_operations",
            title="Device operations",
            parent_id="devices",
            items=[
                MenuItem(
                    key="1",
                    label="List supported APIs",
                    action="command",
                    command_id="api.list_supported",
                ),
                MenuItem(
                    key="2",
                    label="API drill-down",
                    action="command",
                    command_id="api.drill_down",
                ),
                MenuItem(
                    key="3",
                    label="Event instances & live listen",
                    action="command",
                    command_id="events.menu",
                ),
                MenuItem(
                    key="4",
                    label="Account management",
                    action="command",
                    command_id="accounts.menu",
                ),
                MenuItem(
                    key="5",
                    label="Device health check",
                    action="command",
                    command_id="navigation.health_check",
                ),
                MenuItem(
                    key="6",
                    label="Edit device credentials",
                    action="command",
                    command_id="navigation.edit_credentials",
                ),
                MenuItem(
                    key="7",
                    label="Delete device",
                    action="command",
                    command_id="navigation.delete_device",
                ),
            ],
        )
    )


def selected_device_operations(serial: str, device_entry: DeviceEntry) -> None:
    device_label = _format_device_operations_label(serial, device_entry)
    actions = [
        ("1", "List supported APIs"),
        ("2", "API drill-down"),
        ("3", "Event instances & live listen"),
        ("4", "Account management"),
        ("5", "Device health check"),
        ("6", "Edit device credentials"),
        ("7", "Delete device"),
    ]
    while True:
        print(f"\nDevice operations for {device_label}:")  # noqa: T201
        print("   #  action")  # noqa: T201
        print("  --  ----------------------------------")  # noqa: T201
        for key, label in actions:
            print(f"  {key:>2}  {label}")  # noqa: T201
        print("  b. Back")  # noqa: T201
        print("  e. Exit")  # noqa: T201
        choice = input("Select option [1-7/b/e]: ").strip().lower()

        if choice == "1":
            list_supported_apis_flow(serial, device_entry)
            continue

        if choice == "2":
            api_drill_down_flow(device_entry)
            continue

        if choice == "3":
            events_flow(serial, device_entry)
            continue

        if choice == "4":
            account_management_flow(serial, device_entry)
            continue

        if choice == "5":  # Health check
            result = asyncio.run(health_check_device(serial, device_entry))
            if result.success:
                print("\n✓ Device is healthy")  # noqa: T201
                print(f"  Response time: {result.response_time_ms:.1f}ms")  # noqa: T201
                print(f"  Model: {result.model}")  # noqa: T201
                if result.firmware:
                    print(f"  Firmware: {result.firmware}")  # noqa: T201
            else:
                print("\n✗ Device health check failed")  # noqa: T201
                print(f"  Error: {result.error}")  # noqa: T201
            input("\nPress Enter to continue...")
            continue

        if choice == "6":  # Edit credentials
            updated = asyncio.run(edit_device_credentials(serial, device_entry))
            if updated:
                config_path = get_config_path()
                devices = load_devices(config_path)
                devices[serial] = updated
                save_devices(config_path, devices)
                device_entry = updated
                print(f"✓ Device {serial} updated.\n")  # noqa: T201
            continue

        if choice == "7":  # Delete device
            config_path = get_config_path()
            devices = load_devices(config_path)
            if delete_device(serial, devices):
                save_devices(config_path, devices)
                print("\nReturning to main menu.")  # noqa: T201
                return
            continue

        if choice == "b":
            return

        if choice == "e":
            print("Exiting.")  # noqa: T201
            raise SystemExit(0)

        print("Invalid option. Please enter 1-7, b, or e.")  # noqa: T201


def run_main_loop(config_path: Path | None = None) -> None:
    resolved_config_path = config_path if config_path is not None else get_config_path()

    while True:
        devices: DeviceStore = load_devices(resolved_config_path)
        print_registered_devices(devices)

        print("\nOptions:")  # noqa: T201
        print("  1. Add additional device")  # noqa: T201
        print("  2. Discover devices")  # noqa: T201
        print("  3. Device operations")  # noqa: T201
        print("  e. Exit")  # noqa: T201
        choice = input("Select an option [1/2/3/e]: ").strip().lower()

        if choice == "e":
            print("Exiting.")  # noqa: T201
            raise SystemExit(0)

        if choice == "2":
            discovered_devices = asyncio.run(discover_axis_devices(scan_seconds=5.0))
            filtered_discovered = filter_discovered_devices(discovered_devices, devices)
            selected_discovered = select_discovered_device(filtered_discovered)
            if selected_discovered is None:
                continue

            username = input("Enter username: ").strip()
            password = getpass.getpass("Enter password: ")
            device_info = {
                "host": selected_discovered.get("host", "").strip(),
                "username": username,
                "password": password,
            }

            existing_serial_for_host = find_serial_by_host(devices, device_info["host"])
            if existing_serial_for_host is not None:
                update_existing = (
                    input(
                        f"A device with host {device_info['host']} already exists "
                        f"(serial {existing_serial_for_host}). Update it? (y/n): "
                    )
                    .strip()
                    .lower()
                )
                if update_existing != "y":
                    print("Device registration aborted.")  # noqa: T201
                    continue

            config, serial, model, extra = asyncio.run(
                validate_and_fetch_device(device_info)
            )
            if config is None or serial is None or model is None or extra is None:
                continue

            migrate_unknown_entry(devices, serial, device_info["host"])

            if serial in devices:
                update = (
                    input(
                        f"A device with serial {serial} already exists. "
                        "Update its configuration? (y/n): "
                    )
                    .strip()
                    .lower()
                )
                if update != "y":
                    print("Device registration aborted.")  # noqa: T201
                    continue

            devices[serial] = {
                "config": config_to_toml_dict(config),
                "model": model,
                "extra": extra,
            }
            save_devices(resolved_config_path, devices)
            print(f"Device '{serial}' registered/updated.")  # noqa: T201
            continue

        if choice == "3":
            selected = select_device(devices)
            if selected is None:
                continue
            selected_serial, selected_entry = selected
            selected_device_operations(selected_serial, selected_entry)
            continue

        if choice != "1":
            print("Invalid option. Please enter 1, 2, 3, or e.")  # noqa: T201
            continue

        device_info = prompt_for_device()
        existing_serial_for_host = find_serial_by_host(devices, device_info["host"])
        if existing_serial_for_host is not None:
            update_existing = (
                input(
                    f"A device with host {device_info['host']} already exists "
                    f"(serial {existing_serial_for_host}). Update it? (y/n): "
                )
                .strip()
                .lower()
            )
            if update_existing != "y":
                print("Device registration aborted.")  # noqa: T201
                continue

        config, serial, model, extra = asyncio.run(
            validate_and_fetch_device(device_info)
        )
        if config is None or serial is None or model is None or extra is None:
            continue

        migrate_unknown_entry(devices, serial, device_info["host"])

        if serial in devices:
            update = (
                input(
                    f"A device with serial {serial} already exists. "
                    "Update its configuration? (y/n): "
                )
                .strip()
                .lower()
            )
            if update != "y":
                print("Device registration aborted.")  # noqa: T201
                continue

        devices[serial] = {
            "config": config_to_toml_dict(config),
            "model": model,
            "extra": extra,
        }
        save_devices(resolved_config_path, devices)
        print(f"Device '{serial}' registered/updated.")  # noqa: T201
