"""Coverage-focused tests for CLI core runtime and pack helpers."""

from __future__ import annotations

import asyncio
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
from axis.cli.packs import api as api_pack, events as events_pack
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
async def test_devices_add_command_persists_when_registry_changes() -> None:
    """devices.add command persists updated devices when registration mutates store."""
    registry = CommandRegistry()
    router = CliRouter()
    compose_builtin_packs(registry, router)

    devices: dict[str, object] = {}

    def _mutate_registry(store: dict[str, object]) -> None:
        store["SN1"] = {
            "config": {"host": "10.0.0.1", "username": "admin", "password": "pwd"}
        }

    with (
        patch("axis.cli.packs.devices.load_devices", return_value=devices),
        patch(
            "axis.cli.packs.devices.register_or_update_device",
            side_effect=_mutate_registry,
        ),
        patch("axis.cli.packs.devices.save_devices") as mock_save,
    ):
        ctx = CliContext(config_path=Path("."), device_gateway=MagicMock())
        io = MagicMock()
        command = registry.get_command("devices.add")
        result = await command.run(ctx, io)

    assert result.status == "ok"
    assert result.message == "Device registry updated."
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

    events_pack._live_listen_flow({"config": "bad"}, topic_filter=None)

    def raise_request_error(coro: object) -> None:
        if asyncio.iscoroutine(coro):
            coro.close()
        msg = "denied"
        raise RequestError(msg)

    with (
        patch(
            "axis.cli.packs.events.get_device_credentials",
            return_value={"host": "h", "username": "u", "password": "p"},
        ),
        patch("axis.cli.packs.events.asyncio.run", side_effect=raise_request_error),
    ):
        events_pack._live_listen_flow({"config": {}}, topic_filter="topic")

    out = capsys.readouterr().out
    assert "incomplete" in out.lower()
    assert "request failed" in out.lower()


def test_api_and_events_register_noop() -> None:
    """Register placeholders are intentionally no-op."""
    assert api_pack.register(object(), object()) is None
    assert events_pack.register(object(), object()) is None


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
