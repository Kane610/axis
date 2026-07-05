"""Coverage-focused tests for CLI core runtime and pack helpers."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from axis.cli.core.context import CliContext
from axis.cli.core.contracts import CommandCapabilities, CommandResult
from axis.cli.core.gateway import DeviceGateway
from axis.cli.core.io import TerminalIO
from axis.cli.core.registry import CommandRegistry
from axis.cli.core.router import CliRouter, MenuItem, MenuNode
from axis.cli.main import compose_builtin_packs
from axis.cli.packs import (
    api as api_pack,
    events as events_pack,
)
from axis.errors import RequestError


@pytest.mark.asyncio
async def test_router_navigation_invalid_back_and_exit() -> None:
    """Router handles invalid input, navigation, back, and exit paths."""
    io = MagicMock()
    io.prompt = MagicMock(side_effect=["x", "1", "b", "e"])

    router = CliRouter()
    router.register_node(
        MenuNode(
            id="main",
            title="Main",
            items=[
                MenuItem(key="1", label="Go Sub", action="navigate", next_node_id="sub")
            ],
        )
    )
    router.register_node(
        MenuNode(
            id="sub",
            title="Sub",
            items=[MenuItem(key="1", label="Noop", action="noop")],
            parent_id="main",
        )
    )

    with pytest.raises(SystemExit):
        await router.run(ctx=MagicMock(), io=io)

    written = "\n".join(call.args[0] for call in io.write.call_args_list)
    assert "Invalid option." in written
    assert "Exiting." in written


@pytest.mark.asyncio
async def test_router_executes_registered_command_and_writes_message() -> None:
    """Router dispatches command actions through context command registry."""
    io = MagicMock()
    io.prompt = MagicMock(side_effect=["1", "e"])

    command = MagicMock()
    command.id = "say-hello"
    command.run = AsyncMock(return_value=CommandResult(message="hello"))

    registry = CommandRegistry()
    registry.register_command(command)

    router = CliRouter()
    router.register_node(
        MenuNode(
            id="main",
            title="Main",
            items=[
                MenuItem(
                    key="1",
                    label="Say hello",
                    action="command",
                    command_id="say-hello",
                )
            ],
        )
    )

    ctx = MagicMock()
    ctx.command_registry = registry

    with pytest.raises(SystemExit):
        await router.run(ctx=ctx, io=io)

    command.run.assert_awaited_once_with(ctx, io)
    written = "\n".join(call.args[0] for call in io.write.call_args_list)
    assert "hello" in written


@pytest.mark.asyncio
async def test_router_navigates_using_command_result_payload() -> None:
    """Router switches node when command result requests next_node_id."""
    io = MagicMock()
    io.prompt = MagicMock(side_effect=["1", "e"])

    command = MagicMock()
    command.id = "jump"
    command.run = AsyncMock(return_value=CommandResult(payload={"next_node_id": "sub"}))

    registry = CommandRegistry()
    registry.register_command(command)

    router = CliRouter()
    router.register_node(
        MenuNode(
            id="main",
            title="Main",
            items=[
                MenuItem(
                    key="1",
                    label="Jump",
                    action="command",
                    command_id="jump",
                )
            ],
        )
    )
    router.register_node(
        MenuNode(
            id="sub",
            title="Sub",
            parent_id="main",
            items=[],
        )
    )

    ctx = MagicMock()
    ctx.command_registry = registry

    with pytest.raises(SystemExit):
        await router.run(ctx=ctx, io=io)

    written = "\n".join(call.args[0] for call in io.write.call_args_list)
    assert "\nSub:" in written


@pytest.mark.asyncio
async def test_router_writes_message_before_payload_navigation() -> None:
    """Router writes command message even when payload requests node transition."""
    io = MagicMock()
    io.prompt = MagicMock(side_effect=["1", "e"])

    command = MagicMock()
    command.id = "jump-with-message"
    command.run = AsyncMock(
        return_value=CommandResult(
            message="navigating",
            payload={"next_node_id": "sub"},
        )
    )

    registry = CommandRegistry()
    registry.register_command(command)

    router = CliRouter()
    router.register_node(
        MenuNode(
            id="main",
            title="Main",
            items=[
                MenuItem(
                    key="1",
                    label="Jump",
                    action="command",
                    command_id="jump-with-message",
                )
            ],
        )
    )
    router.register_node(
        MenuNode(
            id="sub",
            title="Sub",
            parent_id="main",
            items=[],
        )
    )

    ctx = MagicMock()
    ctx.command_registry = registry

    with pytest.raises(SystemExit):
        await router.run(ctx=ctx, io=io)

    written = "\n".join(call.args[0] for call in io.write.call_args_list)
    assert "navigating" in written
    assert "\nSub:" in written


@pytest.mark.asyncio
async def test_router_writes_default_error_message_when_missing() -> None:
    """Router writes fallback message for error results without explicit text."""
    io = MagicMock()
    io.prompt = MagicMock(side_effect=["1", "e"])

    command = MagicMock()
    command.id = "fail"
    command.run = AsyncMock(return_value=CommandResult(status="error"))

    registry = CommandRegistry()
    registry.register_command(command)

    router = CliRouter()
    router.register_node(
        MenuNode(
            id="main",
            title="Main",
            items=[
                MenuItem(
                    key="1",
                    label="Fail",
                    action="command",
                    command_id="fail",
                )
            ],
        )
    )

    ctx = MagicMock()
    ctx.command_registry = registry

    with pytest.raises(SystemExit):
        await router.run(ctx=ctx, io=io)

    written = "\n".join(call.args[0] for call in io.write.call_args_list)
    assert "Command failed." in written


@pytest.mark.asyncio
async def test_router_writes_default_cancelled_message_when_missing() -> None:
    """Router writes fallback message for cancelled results without explicit text."""
    io = MagicMock()
    io.prompt = MagicMock(side_effect=["1", "e"])

    command = MagicMock()
    command.id = "cancel"
    command.run = AsyncMock(return_value=CommandResult(status="cancelled"))

    registry = CommandRegistry()
    registry.register_command(command)

    router = CliRouter()
    router.register_node(
        MenuNode(
            id="main",
            title="Main",
            items=[
                MenuItem(
                    key="1",
                    label="Cancel",
                    action="command",
                    command_id="cancel",
                )
            ],
        )
    )

    ctx = MagicMock()
    ctx.command_registry = registry

    with pytest.raises(SystemExit):
        await router.run(ctx=ctx, io=io)

    written = "\n".join(call.args[0] for call in io.write.call_args_list)
    assert "Command cancelled." in written


@pytest.mark.asyncio
async def test_router_does_not_navigate_on_cancelled_payload() -> None:
    """Router ignores next_node_id payload when command status is cancelled."""
    io = MagicMock()
    io.prompt = MagicMock(side_effect=["1", "e"])

    command = MagicMock()
    command.id = "cancel-with-payload"
    command.run = AsyncMock(
        return_value=CommandResult(
            status="cancelled",
            payload={"next_node_id": "sub"},
        )
    )

    registry = CommandRegistry()
    registry.register_command(command)

    router = CliRouter()
    router.register_node(
        MenuNode(
            id="main",
            title="Main",
            items=[
                MenuItem(
                    key="1",
                    label="Cancel",
                    action="command",
                    command_id="cancel-with-payload",
                )
            ],
        )
    )
    router.register_node(
        MenuNode(
            id="sub",
            title="Sub",
            parent_id="main",
            items=[],
        )
    )

    ctx = MagicMock()
    ctx.command_registry = registry

    with pytest.raises(SystemExit):
        await router.run(ctx=ctx, io=io)

    written = "\n".join(call.args[0] for call in io.write.call_args_list)
    assert "Command cancelled." in written
    assert "\nSub:" not in written


@pytest.mark.asyncio
async def test_router_calls_node_render_before_menu() -> None:
    """Router invokes node render hook before printing menu options."""
    io = MagicMock()
    io.prompt = MagicMock(side_effect=["e"])
    render = MagicMock()

    router = CliRouter()
    router.register_node(
        MenuNode(
            id="main",
            title="Main",
            items=[],
            render=render,
        )
    )

    with pytest.raises(SystemExit):
        await router.run(ctx=MagicMock(), io=io)

    render.assert_called_once()


@pytest.mark.asyncio
async def test_router_device_operations_node_shows_missing_context_message() -> None:
    """device_operations render hook shows message when no device is selected."""
    registry = CommandRegistry()
    router = CliRouter()
    compose_builtin_packs(registry, router)

    ctx = CliContext(
        config_path=Path("."),
        device_gateway=MagicMock(),
        command_registry=registry,
        router=router,
    )
    io = MagicMock()
    io.prompt = MagicMock(side_effect=["e"])

    with pytest.raises(SystemExit):
        await router.run(ctx=ctx, io=io, start_node_id="device_operations")

    written = "\n".join(call.args[0] for call in io.write.call_args_list)
    assert "No selected device." in written


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("selection", "expected_title", "expected_context"),
    [
        ("1", "\nAPI:", "API for SN1 (10.0.0.1, mac=SN1):"),
        ("2", "\nEvents:", "Events for SN1 (10.0.0.1, mac=SN1):"),
        (
            "3",
            "\nAccounts:",
            "Account management for SN1 (10.0.0.1, mac=SN1):",
        ),
    ],
)
async def test_router_device_operations_navigates_to_selected_device_nodes(
    selection: str,
    expected_title: str,
    expected_context: str,
) -> None:
    """device_operations routes to API/events/accounts and keeps selected context."""
    registry = CommandRegistry()
    router = CliRouter()
    compose_builtin_packs(registry, router)

    ctx = CliContext(
        config_path=Path("."),
        device_gateway=MagicMock(),
        selected_serial="SN1",
        selected_device={
            "config": {"host": "10.0.0.1", "username": "admin", "password": "pwd"}
        },
        command_registry=registry,
        router=router,
    )
    io = MagicMock()
    io.prompt = MagicMock(side_effect=[selection, "e"])

    with pytest.raises(SystemExit):
        await router.run(ctx=ctx, io=io, start_node_id="device_operations")

    written = "\n".join(call.args[0] for call in io.write.call_args_list)
    assert "Device operations for SN1 (10.0.0.1, mac=SN1):" in written
    assert expected_context in written
    assert expected_title in written


@pytest.mark.asyncio
@pytest.mark.parametrize("selection", ["1", "2", "3"])
async def test_router_feature_nodes_back_to_device_operations(
    selection: str,
) -> None:
    """Back from API/events/accounts returns to device_operations."""
    registry = CommandRegistry()
    router = CliRouter()
    compose_builtin_packs(registry, router)

    ctx = CliContext(
        config_path=Path("."),
        device_gateway=MagicMock(),
        selected_serial="SN1",
        selected_device={
            "config": {"host": "10.0.0.1", "username": "admin", "password": "pwd"}
        },
        command_registry=registry,
        router=router,
    )
    io = MagicMock()
    # device_operations -> feature submenu -> back -> exit
    io.prompt = MagicMock(side_effect=[selection, "b", "e"])

    with pytest.raises(SystemExit):
        await router.run(ctx=ctx, io=io, start_node_id="device_operations")

    written = "\n".join(call.args[0] for call in io.write.call_args_list)
    assert written.count("\nDevice operations:") == 2
    assert "Device operations for SN1 (10.0.0.1, mac=SN1):" in written


def test_command_registry_rejects_duplicate_command_ids() -> None:
    """Registering the same command id twice raises ValueError."""
    registry = CommandRegistry()

    command_a = MagicMock()
    command_a.id = "dup"
    command_b = MagicMock()
    command_b.id = "dup"

    registry.register_command(command_a)

    with pytest.raises(ValueError, match="already registered"):
        registry.register_command(command_b)


def test_compose_builtin_packs_registers_commands_and_nodes() -> None:
    """Built-in pack composition registers command and menu metadata."""
    registry = CommandRegistry()
    router = CliRouter()

    compose_builtin_packs(registry, router)

    command_ids = {command.id for command in registry.list_commands()}
    node_ids = set(router.nodes)

    assert {
        "devices.add",
        "devices.discover",
        "devices.operations",
        "api.list_supported",
        "api.drill_down",
        "events.menu",
        "accounts.menu",
        "navigation.health_check",
        "navigation.edit_credentials",
        "navigation.delete_device",
    }.issubset(command_ids)

    assert {
        "main",
        "devices",
        "device_operations",
        "api",
        "events",
        "accounts",
    }.issubset(node_ids)


@pytest.mark.asyncio
async def test_registered_navigation_commands_require_selected_device() -> None:
    """Navigation commands return cancelled status when no device is selected."""
    registry = CommandRegistry()
    router = CliRouter()
    compose_builtin_packs(registry, router)

    ctx = CliContext(config_path=Path("."), device_gateway=MagicMock())
    io = MagicMock()

    for command_id in (
        "navigation.health_check",
        "navigation.edit_credentials",
        "navigation.delete_device",
    ):
        command = registry.get_command(command_id)
        result = await command.run(ctx, io)
        assert result.status == "cancelled"
        assert result.message == "No selected device in context."


@pytest.mark.asyncio
async def test_registered_navigation_health_check_command_results() -> None:
    """Health check command returns ok and error statuses based on probe result."""
    registry = CommandRegistry()
    router = CliRouter()
    compose_builtin_packs(registry, router)

    selected_entry = {
        "config": {"host": "10.0.0.1", "username": "admin", "password": "pwd"}
    }
    ctx = CliContext(
        config_path=Path("."),
        device_gateway=MagicMock(),
        selected_serial="SN1",
        selected_device=selected_entry,
    )
    io = MagicMock()

    command = registry.get_command("navigation.health_check")

    with patch(
        "axis.cli.packs.navigation.health_check_device",
        new=AsyncMock(
            return_value=SimpleNamespace(
                success=True,
                response_time_ms=12.34,
                error=None,
            )
        ),
    ):
        result_ok = await command.run(ctx, io)

    assert result_ok.status == "ok"
    assert result_ok.message == "Health check passed (12.3ms)."

    with patch(
        "axis.cli.packs.navigation.health_check_device",
        new=AsyncMock(
            return_value=SimpleNamespace(
                success=False,
                response_time_ms=0.0,
                error="boom",
            )
        ),
    ):
        result_error = await command.run(ctx, io)

    assert result_error.status == "error"
    assert result_error.message == "Health check failed: boom"


@pytest.mark.asyncio
async def test_registered_navigation_edit_credentials_success_path() -> None:
    """Edit credentials command persists updated device entry and updates context."""
    registry = CommandRegistry()
    router = CliRouter()
    compose_builtin_packs(registry, router)

    selected_entry = {
        "config": {"host": "10.0.0.1", "username": "admin", "password": "pwd"}
    }
    updated_entry = {
        "config": {
            "host": "10.0.0.2",
            "username": "admin2",
            "password": "pwd2",
        }
    }
    ctx = CliContext(
        config_path=Path("."),
        device_gateway=MagicMock(),
        selected_serial="SN1",
        selected_device=selected_entry,
    )
    io = MagicMock()
    command = registry.get_command("navigation.edit_credentials")

    with (
        patch(
            "axis.cli.packs.navigation.edit_device_credentials",
            new=AsyncMock(return_value=updated_entry),
        ),
        patch(
            "axis.cli.packs.navigation.load_devices",
            return_value={"SN1": selected_entry},
        ) as mock_load,
        patch("axis.cli.packs.navigation.save_devices") as mock_save,
    ):
        result = await command.run(ctx, io)

    assert result.status == "ok"
    assert result.message == "Device SN1 updated."
    assert ctx.selected_device == updated_entry
    mock_load.assert_called_once_with(Path("."))
    saved_devices = mock_save.call_args.args[1]
    assert saved_devices["SN1"] == updated_entry


@pytest.mark.asyncio
async def test_registered_navigation_delete_device_success_path() -> None:
    """Delete device command clears selected context after successful deletion."""
    registry = CommandRegistry()
    router = CliRouter()
    compose_builtin_packs(registry, router)

    selected_entry = {
        "config": {"host": "10.0.0.1", "username": "admin", "password": "pwd"}
    }
    ctx = CliContext(
        config_path=Path("."),
        device_gateway=MagicMock(),
        selected_serial="SN1",
        selected_device=selected_entry,
    )
    io = MagicMock()
    command = registry.get_command("navigation.delete_device")

    with (
        patch("axis.cli.packs.navigation.load_devices", return_value={"SN1": {}}),
        patch("axis.cli.packs.navigation.delete_device", return_value=True),
        patch("axis.cli.packs.navigation.save_devices") as mock_save,
    ):
        result = await command.run(ctx, io)

    assert result.status == "ok"
    assert result.message == "Device SN1 deleted."
    assert ctx.selected_serial is None
    assert ctx.selected_device is None
    assert mock_save.call_count == 1


@pytest.mark.asyncio
async def test_registered_pack_menu_commands_require_selected_device() -> None:
    """API/events/accounts menu commands return cancelled when context has no device."""
    registry = CommandRegistry()
    router = CliRouter()
    compose_builtin_packs(registry, router)

    ctx = CliContext(config_path=Path("."), device_gateway=MagicMock())
    io = MagicMock()

    for command_id in (
        "api.list_supported",
        "api.drill_down",
        "events.menu",
        "accounts.menu",
    ):
        command = registry.get_command(command_id)
        result = await command.run(ctx, io)
        assert result.status == "cancelled"
        assert result.message == "No selected device in context."


@pytest.mark.asyncio
async def test_registered_pack_menu_commands_call_flows_with_selected_device() -> None:
    """API/events/accounts menu commands call async handlers when context has device."""
    registry = CommandRegistry()
    router = CliRouter()
    compose_builtin_packs(registry, router)

    selected_entry = {
        "config": {"host": "10.0.0.1", "username": "admin", "password": "pwd"}
    }
    ctx = CliContext(
        config_path=Path("."),
        device_gateway=MagicMock(),
        selected_serial="SN1",
        selected_device=selected_entry,
    )
    io = MagicMock()

    with (
        patch(
            "axis.cli.packs.api.list_supported_apis_async", new=AsyncMock()
        ) as mock_list_supported,
        patch(
            "axis.cli.packs.api.api_drill_down_async", new=AsyncMock()
        ) as mock_api_drill_down,
        patch(
            "axis.cli.packs.events.events_menu_async", new=AsyncMock()
        ) as mock_events_flow,
        patch(
            "axis.cli.packs.accounts.account_management_async", new=AsyncMock()
        ) as mock_accounts_flow,
    ):
        result_api_list = await registry.get_command("api.list_supported").run(ctx, io)
        result_api_drill = await registry.get_command("api.drill_down").run(ctx, io)
        result_events = await registry.get_command("events.menu").run(ctx, io)
        result_accounts = await registry.get_command("accounts.menu").run(ctx, io)

    assert result_api_list.status == "ok"
    assert result_api_drill.status == "ok"
    assert result_events.status == "ok"
    assert result_accounts.status == "ok"

    mock_list_supported.assert_awaited_once_with("SN1", selected_entry)
    mock_api_drill_down.assert_awaited_once_with(selected_entry)
    mock_events_flow.assert_awaited_once_with("SN1", selected_entry)
    mock_accounts_flow.assert_awaited_once_with("SN1", selected_entry)


@pytest.mark.asyncio
async def test_registered_pack_menu_commands_use_to_thread() -> None:
    """API/events/accounts commands are async-native and do not use to_thread."""
    registry = CommandRegistry()
    router = CliRouter()
    compose_builtin_packs(registry, router)

    selected_entry = {
        "config": {"host": "10.0.0.1", "username": "admin", "password": "pwd"}
    }
    ctx = CliContext(
        config_path=Path("."),
        device_gateway=MagicMock(),
        selected_serial="SN1",
        selected_device=selected_entry,
    )
    io = MagicMock()

    with (
        patch("asyncio.to_thread", new=AsyncMock()) as to_thread,
        patch("axis.cli.packs.api.list_supported_apis_async", new=AsyncMock()),
        patch("axis.cli.packs.api.api_drill_down_async", new=AsyncMock()),
        patch("axis.cli.packs.events.events_menu_async", new=AsyncMock()),
        patch("axis.cli.packs.accounts.account_management_async", new=AsyncMock()),
    ):
        await registry.get_command("api.list_supported").run(ctx, io)
        await registry.get_command("api.drill_down").run(ctx, io)
        await registry.get_command("events.menu").run(ctx, io)
        await registry.get_command("accounts.menu").run(ctx, io)

    assert to_thread.await_count == 0


@pytest.mark.asyncio
async def test_devices_operations_command_sets_selected_device_context() -> None:
    """devices.operations command stores selected device and requests navigation."""
    registry = CommandRegistry()
    router = CliRouter()
    compose_builtin_packs(registry, router)

    selected_entry = {
        "config": {"host": "10.0.0.1", "username": "admin", "password": "pwd"}
    }

    with (
        patch(
            "axis.cli.packs.devices.load_devices", return_value={"SN1": selected_entry}
        ),
        patch(
            "axis.cli.packs.devices.select_device",
            return_value=("SN1", selected_entry),
        ),
    ):
        ctx = CliContext(config_path=Path("."), device_gateway=MagicMock())
        io = MagicMock()
        command = registry.get_command("devices.operations")
        result = await command.run(ctx, io)

    assert result.status == "ok"
    assert result.payload == {"next_node_id": "device_operations"}
    assert ctx.selected_serial == "SN1"
    assert ctx.selected_device == selected_entry


@pytest.mark.asyncio
async def test_devices_operations_command_handles_empty_registry() -> None:
    """devices.operations returns explicit cancelled result when no devices exist."""
    registry = CommandRegistry()
    router = CliRouter()
    compose_builtin_packs(registry, router)

    with patch("axis.cli.packs.devices.load_devices", return_value={}):
        ctx = CliContext(config_path=Path("."), device_gateway=MagicMock())
        io = MagicMock()
        command = registry.get_command("devices.operations")
        result = await command.run(ctx, io)

    assert result.status == "cancelled"
    assert result.message == "No devices available."


@pytest.mark.asyncio
async def test_router_device_selection_command_navigates_to_operations() -> None:
    """Selecting devices.operations through router updates context and transitions node."""
    registry = CommandRegistry()
    router = CliRouter()
    compose_builtin_packs(registry, router)

    selected_entry = {
        "config": {"host": "10.0.0.1", "username": "admin", "password": "pwd"}
    }

    ctx = CliContext(
        config_path=Path("."),
        device_gateway=MagicMock(),
        command_registry=registry,
        router=router,
    )

    io = MagicMock()
    # main -> devices -> select operations command -> exit
    io.prompt = MagicMock(side_effect=["1", "3", "e"])

    with (
        patch(
            "axis.cli.packs.devices.load_devices", return_value={"SN1": selected_entry}
        ),
        patch(
            "axis.cli.packs.devices.select_device",
            return_value=("SN1", selected_entry),
        ),
        pytest.raises(SystemExit),
    ):
        await router.run(ctx=ctx, io=io)

    written = "\n".join(call.args[0] for call in io.write.call_args_list)
    assert "Selected device: SN1" in written
    assert "Device operations for" in written
    assert "SN1" in written
    assert "\nDevice operations:" in written
    assert ctx.selected_serial == "SN1"
    assert ctx.selected_device == selected_entry


@pytest.mark.asyncio
async def test_router_main_to_api_submenu_and_back() -> None:
    """Main route reaches API submenu through device_operations and supports back."""
    registry = CommandRegistry()
    router = CliRouter()
    compose_builtin_packs(registry, router)

    selected_entry = {
        "config": {"host": "10.0.0.1", "username": "admin", "password": "pwd"}
    }

    ctx = CliContext(
        config_path=Path("."),
        device_gateway=MagicMock(),
        command_registry=registry,
        router=router,
    )

    io = MagicMock()
    # main -> devices -> select operations -> API submenu -> back -> exit
    io.prompt = MagicMock(side_effect=["1", "3", "1", "b", "e"])

    with (
        patch(
            "axis.cli.packs.devices.load_devices", return_value={"SN1": selected_entry}
        ),
        patch(
            "axis.cli.packs.devices.select_device",
            return_value=("SN1", selected_entry),
        ),
        pytest.raises(SystemExit),
    ):
        await router.run(ctx=ctx, io=io)

    written = "\n".join(call.args[0] for call in io.write.call_args_list)
    assert "\nAPI:" in written
    assert "API for SN1 (10.0.0.1, mac=SN1):" in written
    assert written.count("\nDevice operations:") == 2


@pytest.mark.asyncio
async def test_router_devices_node_renders_registered_devices() -> None:
    """Devices node render hook prints registered devices in router mode."""
    registry = CommandRegistry()
    router = CliRouter()
    compose_builtin_packs(registry, router)

    ctx = CliContext(
        config_path=Path("."),
        device_gateway=MagicMock(),
        command_registry=registry,
        router=router,
    )
    io = MagicMock()
    io.prompt = MagicMock(side_effect=["1", "e"])

    devices = {
        "SN1": {
            "config": {"host": "10.0.0.1"},
            "model": "P3245",
        }
    }

    with (
        patch("axis.cli.packs.devices.load_devices", return_value=devices),
        pytest.raises(SystemExit),
    ):
        await router.run(ctx=ctx, io=io)

    written = "\n".join(call.args[0] for call in io.write.call_args_list)
    assert "Registered devices:" in written
    assert "SN1" in written
    assert "10.0.0.1" in written


@pytest.mark.asyncio
async def test_devices_discover_command_cancelled_without_selection() -> None:
    """devices.discover command returns cancelled when no discovered device is chosen."""
    registry = CommandRegistry()
    router = CliRouter()
    compose_builtin_packs(registry, router)

    with (
        patch("axis.cli.packs.devices.load_devices", return_value={}),
        patch(
            "axis.cli.packs.devices.discover_axis_devices",
            new=AsyncMock(return_value=[]),
        ),
        patch("axis.cli.packs.devices.filter_discovered_devices", return_value=[]),
        patch("axis.cli.packs.devices.select_discovered_device", return_value=None),
    ):
        ctx = CliContext(config_path=Path("."), device_gateway=MagicMock())
        io = MagicMock()
        command = registry.get_command("devices.discover")
        result = await command.run(ctx, io)

    assert result.status == "cancelled"
    assert result.message == "Device discovery aborted."


@pytest.mark.asyncio
async def test_devices_discover_command_writes_abort_via_io() -> None:
    """devices.discover returns explicit abort result when update is declined."""
    registry = CommandRegistry()
    router = CliRouter()
    compose_builtin_packs(registry, router)

    existing_entry = {
        "config": {"host": "10.0.0.1", "username": "admin", "password": "pwd"}
    }
    discovered = {"host": "10.0.0.1"}

    with (
        patch(
            "axis.cli.packs.devices.load_devices", return_value={"SN1": existing_entry}
        ),
        patch(
            "axis.cli.packs.devices.discover_axis_devices",
            new=AsyncMock(return_value=[discovered]),
        ),
        patch(
            "axis.cli.packs.devices.filter_discovered_devices",
            return_value=[discovered],
        ),
        patch(
            "axis.cli.packs.devices.select_discovered_device", return_value=discovered
        ),
        patch("axis.cli.packs.devices.find_serial_by_host", return_value="SN1"),
        patch("axis.cli.packs.devices.validate_and_fetch_device", new=AsyncMock()),
    ):
        ctx = CliContext(config_path=Path("."), device_gateway=MagicMock())
        io = MagicMock()
        io.prompt.side_effect = ["admin", "n"]
        io.prompt_password.return_value = "pwd"

        command = registry.get_command("devices.discover")
        result = await command.run(ctx, io)

    assert result.status == "cancelled"
    assert result.message == "Device registration aborted."


@pytest.mark.asyncio
async def test_devices_add_command_persists_when_registry_changes() -> None:
    """devices.add command persists updated devices when registration mutates store."""
    registry = CommandRegistry()
    router = CliRouter()
    compose_builtin_packs(registry, router)

    devices: dict[str, object] = {}

    async def _mutate_registry(store: dict[str, object], io: object) -> CommandResult:
        _ = io
        store["SN1"] = {
            "config": {"host": "10.0.0.1", "username": "admin", "password": "pwd"}
        }
        return CommandResult(message="Device 'SN1' registered/updated.")

    with (
        patch("axis.cli.packs.devices.load_devices", return_value=devices),
        patch(
            "axis.cli.packs.devices.register_or_update_device_async",
            side_effect=_mutate_registry,
        ),
        patch("axis.cli.packs.devices.save_devices") as mock_save,
    ):
        ctx = CliContext(config_path=Path("."), device_gateway=MagicMock())
        io = MagicMock()
        command = registry.get_command("devices.add")
        result = await command.run(ctx, io)

    assert result.status == "ok"
    assert result.message == "Device 'SN1' registered/updated."
    mock_save.assert_called_once()


def test_contracts_and_terminal_io_smoke(monkeypatch: pytest.MonkeyPatch) -> None:
    """Core contract dataclasses and terminal IO methods are usable."""
    caps = CommandCapabilities(
        requires_device=True, destructive=True, read_only_safe=False
    )
    result = CommandResult(status="ok", message="done", payload={"k": "v"})
    assert caps.requires_device is True
    assert caps.destructive is True
    assert result.payload == {"k": "v"}

    terminal = TerminalIO()
    monkeypatch.setattr("builtins.input", lambda prompt: "answer")
    monkeypatch.setattr("getpass.getpass", lambda prompt: "secret")

    captured: list[str] = []
    monkeypatch.setattr("builtins.print", lambda text: captured.append(str(text)))

    assert terminal.prompt("Q?") == "answer"
    assert terminal.prompt_password("P?") == "secret"
    terminal.write("hello")
    assert captured == ["hello"]


@pytest.mark.asyncio
async def test_device_gateway_branches(capsys: pytest.CaptureFixture[str]) -> None:
    """Gateway returns None for invalid input and handles request errors."""
    gateway = DeviceGateway()

    # Non-dict config path
    assert await gateway.run({"config": "bad"}, AsyncMock()) is None

    # Missing host/username path
    assert (
        await gateway.run({"config": {"host": "", "username": ""}}, AsyncMock()) is None
    )

    # Request error path
    with (
        patch("axis.cli.core.gateway.ClientSession") as mock_session,
        patch("axis.cli.core.gateway.AxisDevice") as mock_axis_device,
    ):
        mock_session.return_value.__aenter__.return_value = MagicMock()
        mock_axis_device.return_value = MagicMock()
        op = AsyncMock(side_effect=RequestError("boom"))
        assert (
            await gateway.run(
                {"config": {"host": "h", "username": "u", "password": "p"}},
                op,
            )
            is None
        )

    out = capsys.readouterr().out
    assert "incomplete" in out.lower()
    assert "request failed" in out.lower()


@pytest.mark.asyncio
async def test_api_pack_fetch_supported_apis_and_empty() -> None:
    """API pack returns discovered entries and falls back to empty list."""
    fake_api = SimpleNamespace(
        id="basic-device-info", name="Basic", version="1", status="released"
    )
    fake_device = MagicMock()
    fake_device.vapix.api_discovery.update = AsyncMock()
    fake_device.vapix.api_discovery.values.return_value = [fake_api]

    async def invoke_with_device(device_entry: object, operation: object) -> object:
        return await operation(fake_device)

    with patch(
        "axis.cli.packs.api.run_on_selected_device", side_effect=invoke_with_device
    ):
        result = await api_pack.fetch_supported_apis({"config": {}})
    assert result == [
        {
            "id": "basic-device-info",
            "name": "Basic",
            "version": "1",
            "status": "released",
        }
    ]

    with patch(
        "axis.cli.packs.api.run_on_selected_device", new=AsyncMock(return_value=None)
    ):
        assert await api_pack.fetch_supported_apis({"config": {}}) == []


@pytest.mark.asyncio
async def test_api_pack_fetch_vapix_interfaces_and_empty() -> None:
    """Dynamic interface listing returns handler metadata and handles empty result."""
    fake_device = MagicMock()
    fake_device.vapix.inspect_interfaces = AsyncMock(
        return_value={
            "basic_device_info": SimpleNamespace(
                name="basic_device_info",
                api_id="basic-device-info",
                api_version="1.0",
                listed=True,
                probe_attempted=True,
                probe_succeeded=True,
                supported=True,
                initialized=False,
                items=0,
            ),
            "unsupported": SimpleNamespace(
                name="unsupported",
                api_id="unsupported-api",
                api_version="1.0",
                listed=False,
                probe_attempted=True,
                probe_succeeded=False,
                supported=False,
                initialized=False,
                items=0,
            ),
        }
    )

    async def invoke_with_device(device_entry: object, operation: object) -> object:
        return await operation(fake_device)

    with patch(
        "axis.cli.packs.api.run_on_selected_device", side_effect=invoke_with_device
    ):
        result = await api_pack.fetch_vapix_interfaces({"config": {}})

    fake_device.vapix.inspect_interfaces.assert_awaited_once_with(
        refresh_discovery=True,
        probe=True,
    )

    assert result == [
        {
            "name": "basic_device_info",
            "api_id": "basic-device-info",
            "api_version": "1.0",
            "listed": True,
            "probe_attempted": True,
            "probe_succeeded": True,
            "supported": True,
            "initialized": False,
            "items": 0,
        },
        {
            "name": "unsupported",
            "api_id": "unsupported-api",
            "api_version": "1.0",
            "listed": False,
            "probe_attempted": True,
            "probe_succeeded": False,
            "supported": False,
            "initialized": False,
            "items": 0,
        },
    ]

    with patch(
        "axis.cli.packs.api.run_on_selected_device", new=AsyncMock(return_value=None)
    ):
        assert await api_pack.fetch_vapix_interfaces({"config": {}}) == []


@pytest.mark.asyncio
async def test_api_pack_fetch_vapix_interfaces_event_instances_probe() -> None:
    """event_instances truth is provided by library inspect_interfaces output."""
    fake_device = MagicMock()
    fake_device.vapix.inspect_interfaces = AsyncMock(
        return_value={
            "event_instances": SimpleNamespace(
                name="event_instances",
                api_id="",
                api_version="",
                listed=False,
                probe_attempted=True,
                probe_succeeded=True,
                supported=True,
                initialized=True,
                items=3,
            )
        }
    )

    async def invoke_with_device(device_entry: object, operation: object) -> object:
        return await operation(fake_device)

    with patch(
        "axis.cli.packs.api.run_on_selected_device", side_effect=invoke_with_device
    ):
        result = await api_pack.fetch_vapix_interfaces({"config": {}})

    fake_device.vapix.inspect_interfaces.assert_awaited_once_with(
        refresh_discovery=True,
        probe=True,
    )
    assert result == [
        {
            "name": "event_instances",
            "api_id": "",
            "api_version": "",
            "listed": False,
            "probe_attempted": True,
            "probe_succeeded": True,
            "supported": True,
            "initialized": True,
            "items": 3,
        }
    ]


@pytest.mark.asyncio
async def test_api_pack_run_api_read_action_dynamic(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Generic read action supports full dump, traversal, and missing interface."""
    fake_handler = MagicMock()
    fake_handler.initialized = False
    fake_handler.update = AsyncMock(return_value=True)
    fake_handler.__len__.return_value = 1
    fake_handler.items.return_value = [
        ("0", {"source": {"items": [{"name": "camera"}]}})
    ]

    fake_device = MagicMock()
    fake_device.vapix.interfaces.return_value = {"event_instances": fake_handler}

    async def invoke_with_device(device_entry: object, operation: object) -> object:
        return await operation(fake_device)

    with patch(
        "axis.cli.packs.api.run_on_selected_device", side_effect=invoke_with_device
    ):
        await api_pack.run_api_read_action({"config": {}}, "event_instances")
        await api_pack.run_api_read_action(
            {"config": {}}, "event_instances", "0.source.items.0.name"
        )
        await api_pack.run_api_read_action({"config": {}}, "unknown-interface")

    out = capsys.readouterr().out
    assert "Interface data: event_instances" in out
    assert "Interface data: event_instances @ 0.source.items.0.name" in out
    assert "camera" in out
    assert "No interface named 'unknown-interface'." in out


@pytest.mark.asyncio
async def test_api_pack_run_api_read_action_api_discovery_table(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """API-discovery shaped payloads are rendered as normalized table columns."""
    fake_handler = MagicMock()
    fake_handler.initialized = True
    fake_handler.__len__.return_value = 2
    fake_handler.items.return_value = [
        (
            "basic-device-info",
            {
                "id": "basic-device-info",
                "name": "Basic Device Information",
                "version": "1.3",
                "status": "official",
            },
        ),
        (
            "packagemanager",
            {
                "id": "packagemanager",
                "name": "Package Manager",
                "version": "1.4",
                "status": "unknown",
            },
        ),
    ]

    fake_device = MagicMock()
    fake_device.vapix.interfaces.return_value = {"api_discovery": fake_handler}

    async def invoke_with_device(device_entry: object, operation: object) -> object:
        return await operation(fake_device)

    with patch(
        "axis.cli.packs.api.run_on_selected_device", side_effect=invoke_with_device
    ):
        await api_pack.run_api_read_action({"config": {}}, "api_discovery")

    out = capsys.readouterr().out
    assert "Interface data: api_discovery" in out
    assert "#" in out
    assert "id" in out
    assert "name" in out
    assert "version" in out
    assert "status" in out
    assert "basic-device-info" in out
    assert "Package Manager" in out


@pytest.mark.asyncio
async def test_events_pack_fetch_and_live_listen_guards(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Events pack fetches entries and handles live listen guard and request errors."""
    fake_event = SimpleNamespace(
        topic="topic",
        name="name",
        stateful=True,
        stateless=False,
        is_available=True,
    )
    fake_device = MagicMock()
    fake_device.vapix.event_instances.update = AsyncMock()
    fake_device.vapix.event_instances.values.return_value = [fake_event]

    async def invoke_with_device(device_entry: object, operation: object) -> object:
        return await operation(fake_device)

    with patch(
        "axis.cli.packs.events.run_on_selected_device", side_effect=invoke_with_device
    ):
        events = await events_pack.fetch_event_instances({"config": {}})
    assert events[0]["topic"] == "topic"

    with patch(
        "axis.cli.packs.events.run_on_selected_device", new=AsyncMock(return_value=None)
    ):
        assert await events_pack.fetch_event_instances({"config": {}}) == []

    await events_pack._live_listen_async({"config": "bad"}, topic_filter=None)

    class _FailingSession:
        async def __aenter__(self) -> object:
            msg = "denied"
            raise RequestError(msg)

        async def __aexit__(
            self,
            exc_type: object,
            exc: object,
            tb: object,
        ) -> bool:
            return False

    with (
        patch(
            "axis.cli.packs.events.get_device_credentials",
            return_value={"host": "h", "username": "u", "password": "p"},
        ),
        patch("axis.cli.packs.events.ClientSession", return_value=_FailingSession()),
    ):
        await events_pack._live_listen_async({"config": {}}, topic_filter="topic")

    out = capsys.readouterr().out
    assert "incomplete" in out.lower()
    assert "request failed" in out.lower()


def test_api_and_events_register_commands_and_nodes() -> None:
    """Pack registration wires commands and menu nodes into the router."""
    registry = MagicMock()
    router = MagicMock()

    api_pack.register(registry, router)
    events_pack.register(registry, router)

    assert registry.register_command.call_count == 3
    assert router.register_node.call_count == 2


def test_command_registry_register_get_list() -> None:
    """CommandRegistry stores and retrieves commands by id."""
    cmd = MagicMock()
    cmd.id = "test-cmd"
    registry = CommandRegistry()
    registry.register_command(cmd)
    assert registry.get_command("test-cmd") is cmd
    assert registry.list_commands() == [cmd]


@pytest.mark.asyncio
async def test_device_gateway_os_error(capsys: pytest.CaptureFixture[str]) -> None:
    """Gateway returns None and prints message on OSError."""
    gateway = DeviceGateway()
    with (
        patch("axis.cli.core.gateway.ClientSession") as mock_session,
        patch("axis.cli.core.gateway.AxisDevice"),
    ):
        mock_session.return_value.__aenter__.return_value = MagicMock()
        op = AsyncMock(side_effect=OSError("connection refused"))
        result = await gateway.run(
            {"config": {"host": "h", "username": "u", "password": "p"}},
            op,
        )
    assert result is None
    assert "failed to connect" in capsys.readouterr().out.lower()


@pytest.mark.asyncio
async def test_router_back_at_root_and_noop() -> None:
    """Router stays at root on 'b' when no parent; noop action loops without error."""
    io = MagicMock()
    # Sequence: "b" at root (no parent → stay), "1" noop, "e" exit
    io.prompt = MagicMock(side_effect=["b", "1", "e"])

    router = CliRouter()
    router.register_node(
        MenuNode(
            id="main",
            title="Main",
            items=[MenuItem(key="1", label="Do nothing", action="noop")],
        )
    )

    with pytest.raises(SystemExit):
        await router.run(ctx=MagicMock(), io=io)

    written = "\n".join(call.args[0] for call in io.write.call_args_list)
    assert "Exiting." in written


def test_router_rejects_duplicate_node_ids() -> None:
    """Registering duplicate menu node ids raises ValueError."""
    router = CliRouter()
    node = MenuNode(id="main", title="Main", items=[])
    router.register_node(node)

    with pytest.raises(ValueError, match="already registered"):
        router.register_node(node)
