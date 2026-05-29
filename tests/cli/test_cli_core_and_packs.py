"""Coverage-focused tests for CLI core runtime and pack helpers."""

from __future__ import annotations

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from axis.cli.core.contracts import CommandCapabilities, CommandResult
from axis.cli.core.gateway import DeviceGateway
from axis.cli.core.io import TerminalIO
from axis.cli.core.router import CliRouter, MenuItem, MenuNode
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
async def test_api_pack_read_action_branches(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """API read actions handle implemented and fallback branches."""
    fake_device = MagicMock()
    fake_device.vapix.basic_device_info.get_all_properties = AsyncMock(
        return_value={"0": None}
    )
    fake_device.vapix.api_discovery.get_supported_versions = AsyncMock(
        return_value=["1.0", "2.0"]
    )
    fake_device.vapix.user_groups.get_user_groups = AsyncMock(return_value={"0": None})

    async def invoke_with_device(device_entry: object, operation: object) -> object:
        return await operation(fake_device)

    with patch(
        "axis.cli.packs.api.run_on_selected_device", side_effect=invoke_with_device
    ):
        await api_pack.run_api_read_action({"config": {}}, "basic-device-info")
        await api_pack.run_api_read_action({"config": {}}, "api-discovery")
        await api_pack.run_api_read_action({"config": {}}, "user-management")
        await api_pack.run_api_read_action({"config": {}}, "unknown-api")

    out = capsys.readouterr().out
    assert "No basic device information found." in out
    assert "supported versions" in out
    assert "Current user group information is unavailable." in out
    assert "No read action implemented yet" in out


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
