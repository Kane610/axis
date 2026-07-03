# ruff: noqa: D100,D103,PLC0415

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from axis.cli.core.contracts import CommandCapabilities, CommandResult
from axis.cli.core.router import MenuItem, MenuNode
from axis.cli.packs.devices import (
    DeviceEntry,
    _format_device_operations_label,
    delete_device,
    edit_device_credentials,
    get_config_path,
    health_check_device,
    load_devices,
    save_devices,
)

if TYPE_CHECKING:
    from axis.cli.core.context import CliContext
    from axis.cli.core.io import CliIO
    from axis.cli.core.registry import CommandRegistry
    from axis.cli.core.router import CliRouter


def list_supported_apis_flow(serial: str, device_entry: DeviceEntry) -> None:
    """Compatibility wrapper to avoid import-time pack coupling."""
    from axis.cli.packs.api import list_supported_apis_flow as _impl

    _impl(serial, device_entry)


def api_drill_down_flow(device_entry: DeviceEntry) -> None:
    """Compatibility wrapper to avoid import-time pack coupling."""
    from axis.cli.packs.api import api_drill_down_flow as _impl

    _impl(device_entry)


def events_flow(serial: str, device_entry: DeviceEntry) -> None:
    """Compatibility wrapper to avoid import-time pack coupling."""
    from axis.cli.packs.events import events_flow as _impl

    _impl(serial, device_entry)


def account_management_flow(serial: str, device_entry: DeviceEntry) -> None:
    """Compatibility wrapper to avoid import-time pack coupling."""
    from axis.cli.packs.accounts import account_management_flow as _impl

    _impl(serial, device_entry)


def _selected_device_from_context(
    ctx: CliContext,
) -> tuple[str, DeviceEntry] | None:
    if ctx.selected_serial is None or ctx.selected_device is None:
        return None
    return (ctx.selected_serial, ctx.selected_device)


def _render_device_operations_node(ctx: CliContext, io: CliIO) -> None:
    _render_selected_device_node(ctx, io, "Device operations")


def _render_selected_device_node(
    ctx: CliContext,
    io: CliIO,
    title: str,
) -> None:
    selected = _selected_device_from_context(ctx)
    if selected is None:
        io.write("\nNo selected device.")
        return

    serial, device_entry = selected
    device_label = _format_device_operations_label(serial, device_entry)
    io.write(f"\n{title} for {device_label}:")


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
            render=_render_device_operations_node,
            items=[
                MenuItem(
                    key="1",
                    label="API",
                    action="navigate",
                    next_node_id="api",
                ),
                MenuItem(
                    key="2",
                    label="Events",
                    action="navigate",
                    next_node_id="events",
                ),
                MenuItem(
                    key="3",
                    label="Accounts",
                    action="navigate",
                    next_node_id="accounts",
                ),
                MenuItem(
                    key="4",
                    label="Device health check",
                    action="command",
                    command_id="navigation.health_check",
                ),
                MenuItem(
                    key="5",
                    label="Edit device credentials",
                    action="command",
                    command_id="navigation.edit_credentials",
                ),
                MenuItem(
                    key="6",
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
