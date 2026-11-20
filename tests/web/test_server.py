"""Exercise the local web protocol and its security boundaries."""

import asyncio
from contextlib import asynccontextmanager
from datetime import UTC, datetime
import json
from pathlib import Path
import socket
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock

from aiohttp import WSMsgType
import pytest

from axis.application.errors import ErrorKind, OperationError
from axis.application.records import (
    ConnectionSettings,
    DeviceRecord,
    DiscoverySnapshot,
    HealthSnapshot,
)
from axis.application.storage import DeviceRegistry
from axis.interfaces.vapix import InterfaceState
from axis.models.api_discovery import Api, ApiStatus
from axis.web import server

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Callable
    from typing import Any

    from aiohttp import ClientWebSocketResponse
    from aiohttp.test_utils import TestClient

HOST = "127.0.0.1:8765"
HEADERS = {"Host": HOST, "Origin": f"http://{HOST}"}
TOKEN = "test-token"


@pytest.fixture(scope="module")
def wire_results() -> dict[str, object]:
    """Load the response examples shared with the TypeScript client tests."""
    path = Path(__file__).resolve().parents[2] / "web/tests/fixtures/websocket.json"
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture
def registry(tmp_path: Path) -> DeviceRegistry:
    """Supply one registered device with a private login."""
    registry = DeviceRegistry(tmp_path / "devices.toml")
    registry.upsert(
        DeviceRecord(
            "SERIAL",
            ConnectionSettings("camera.local", "root", "private-password"),
            alias="Front",
            discovery=DiscoverySnapshot(
                host="192.0.2.1", last_seen=datetime(2026, 1, 1, tzinfo=UTC)
            ),
        )
    )
    return registry


@pytest.fixture
async def client(
    aiohttp_client: Callable[..., Any], registry: DeviceRegistry
) -> TestClient:
    """Start an app with a known authority and access token."""
    return await aiohttp_client(server.create_app(registry, TOKEN, 8765))


async def connect(client: TestClient) -> ClientWebSocketResponse:
    """Open and authenticate a WebSocket."""
    socket = await client.ws_connect("/api/websocket", headers=HEADERS)
    await socket.send_json({"token": TOKEN})
    assert await socket.receive_json() == {"type": "ready", "version": 1}
    return socket


async def command(socket: ClientWebSocketResponse, **message: object) -> dict[str, Any]:
    """Send one command and return its response."""
    await socket.send_json({"id": 1, **message})
    return await socket.receive_json()


async def test_static_assets_and_host_guard(client: TestClient) -> None:
    """Assets require the expected host and are shipped with security headers."""
    response = await client.get("/", headers={"Host": HOST})
    assert response.status == 200
    assert "<axis-app>" in await response.text()
    assert "frame-ancestors 'none'" in response.headers["Content-Security-Policy"]
    response = await client.get("/app.js", headers={"Host": HOST})
    assert response.status == 200
    assert "axis-app" in await response.text()
    assert (await client.get("/", headers={"Host": "attacker.example"})).status == 403
    assert (await client.get("/unknown", headers={"Host": HOST})).status == 404


@pytest.mark.parametrize("origin", [None, "null", "http://attacker.example"])
async def test_websocket_rejects_bad_origin(
    client: TestClient, origin: str | None
) -> None:
    """Browsers from other origins cannot use the local API."""
    headers = {"Host": HOST}
    if origin is not None:
        headers["Origin"] = origin
    response = await client.get("/api/websocket", headers=headers)
    assert response.status == 403


@pytest.mark.parametrize("token", ["wrong", "🔒", None])
async def test_websocket_requires_token(client: TestClient, token: str | None) -> None:
    """An accepted origin still needs the per-run secret."""
    socket = await client.ws_connect("/api/websocket", headers=HEADERS)
    await socket.send_json({"token": token})
    message = await socket.receive()
    assert message.type == WSMsgType.CLOSE
    assert message.data == 1008


async def test_list_returns_only_safe_json(
    client: TestClient, wire_results: dict[str, object]
) -> None:
    """Device summaries serialize discovery timestamps and omit login credentials."""
    socket = await connect(client)
    response = await command(socket, type="devices/list")
    assert response == {"id": 1, "result": wire_results["devices/list"]}
    assert "private-password" not in str(response)
    assert "root" not in str(response)
    await socket.close()


async def test_discovery_is_explicit_and_does_not_update_registry(
    client: TestClient,
    registry: DeviceRegistry,
    monkeypatch: pytest.MonkeyPatch,
    wire_results: dict[str, object],
) -> None:
    """Return announced devices without changing the saved device configuration."""
    discover = AsyncMock(return_value=wire_results["devices/discover"])
    monkeypatch.setattr(server, "discover_axis_devices", discover)
    before = registry.load()
    socket = await connect(client)
    assert await command(socket, type="devices/list") == {
        "id": 1,
        "result": wire_results["devices/list"],
    }
    discover.assert_not_awaited()
    assert await command(socket, type="devices/discover") == {
        "id": 1,
        "result": wire_results["devices/discover"],
    }
    discover.assert_awaited_once_with()
    assert registry.load() == before
    await socket.close()


@pytest.mark.parametrize(
    ("failure", "code", "message"),
    [
        (
            OperationError("Unusable interface.", kind=ErrorKind.CONNECTION),
            "connection",
            "Device discovery failed. Check this computer's local network access and try again.",
        ),
        (TimeoutError(), "timeout", "Device discovery timed out. Try again."),
    ],
)
async def test_discovery_errors(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    failure: Exception,
    code: str,
    message: str,
) -> None:
    """Report scan failures without suggesting edits to a saved device."""
    monkeypatch.setattr(server, "discover_axis_devices", AsyncMock(side_effect=failure))
    socket = await connect(client)
    assert await command(socket, type="devices/discover") == {
        "id": 1,
        "error": {"code": code, "message": message},
    }
    await socket.close()


async def test_health_and_api_reads(
    client: TestClient,
    registry: DeviceRegistry,
    monkeypatch: pytest.MonkeyPatch,
    wire_results: dict[str, object],
) -> None:
    """Dispatch read commands through the shared application operations."""
    snapshot = HealthSnapshot(
        firmware_version="12",
        model="M1",
        observed_at=datetime(2026, 1, 1, tzinfo=UTC),
        product="Camera",
        serial="OTHER",
        target=registry.resolve("SERIAL").summary(),
    )
    health = AsyncMock(return_value=snapshot)
    device = MagicMock()
    device.config.password = "private-password"
    device.vapix.api_discovery.update = AsyncMock(return_value=True)
    device.vapix.api_discovery.values.return_value = [
        Api(
            id="light-control",
            name="Light control",
            status=ApiStatus.OFFICIAL,
            version="1.0",
        )
    ]
    device.vapix.inspect_interfaces = AsyncMock(
        return_value={
            "light_control": InterfaceState(
                name="light_control",
                api_id="light-control",
                api_version="1.0",
                listed=True,
                probe_attempted=False,
                probe_succeeded=False,
                supported=True,
                initialized=True,
                items=1,
            )
        }
    )

    @asynccontextmanager
    async def open_device(_settings: ConnectionSettings) -> AsyncIterator[MagicMock]:
        yield device

    read = AsyncMock(return_value={"state": "on"})
    monkeypatch.setattr(server.operations, "read_health", health)
    monkeypatch.setattr(server.operations, "_device", open_device)
    monkeypatch.setattr(server.operations, "read_interface", read)
    socket = await connect(client)
    for kind in ("device/health", "device/apis", "device/interfaces", "device/read"):
        args = {"name": "light_control"} if kind == "device/read" else {}
        assert await command(socket, type=kind, device="SERIAL", **args) == {
            "id": 1,
            "result": wire_results[kind],
        }
    health.assert_awaited_once()
    read.assert_awaited_once()
    await socket.close()


@pytest.mark.parametrize(
    "message",
    [
        {"type": "delete", "device": "SERIAL"},
        {"type": "device/health", "device": "camera.local"},
        {"type": "device/read", "device": "SERIAL"},
        {"type": ["device/health"]},
    ],
)
async def test_invalid_commands(client: TestClient, message: dict[str, object]) -> None:
    """Reject writes, arbitrary hosts, and malformed commands."""
    socket = await connect(client)
    result = await command(socket, **message)
    assert result["error"]["code"] in {"invalid_request", "storage"}
    await socket.close()


@pytest.mark.parametrize(
    ("kind", "message"),
    [
        (
            ErrorKind.CONNECTION,
            (
                "Cannot reach the device. Check that it is powered on, that this "
                "computer can reach its network, and that its saved address and port are correct."
            ),
        ),
        (
            ErrorKind.TIMEOUT,
            "The device did not respond in time. Check its connection and try again.",
        ),
        (ErrorKind.AUTHENTICATION, "Device unavailable."),
    ],
)
async def test_safe_operation_error(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    kind: ErrorKind,
    message: str,
) -> None:
    """Network failures give recovery advice while other safe errors are preserved."""
    monkeypatch.setattr(
        server.operations,
        "read_health",
        AsyncMock(side_effect=OperationError("Device unavailable.", kind=kind)),
    )
    socket = await connect(client)
    result = await command(socket, type="device/health", device="SERIAL")
    assert result["error"] == {"code": kind.value, "message": message}
    await socket.close()


async def test_disconnect_cancels_operation(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A disconnected tab does not retain its in-flight device request."""
    started = asyncio.Event()
    cancelled = asyncio.Event()

    async def blocked(*args: object) -> None:
        started.set()
        try:
            await asyncio.Event().wait()
        finally:
            cancelled.set()

    monkeypatch.setattr(server.operations, "read_health", blocked)
    socket = await connect(client)
    await socket.send_json({"id": 1, "type": "device/health", "device": "SERIAL"})
    await asyncio.wait_for(started.wait(), 2)
    await socket.close()
    await asyncio.wait_for(cancelled.wait(), 2)


async def test_unresponsive_device_times_out_and_allows_retry(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A stalled health read releases its resources and leaves the connection usable."""
    cancelled = asyncio.Event()

    async def blocked(*args: object) -> None:
        try:
            await asyncio.Event().wait()
        finally:
            cancelled.set()

    monkeypatch.setattr(server, "COMMAND_TIMEOUT", 0.01)
    monkeypatch.setattr(server.operations, "read_health", blocked)
    socket = await connect(client)
    response = await asyncio.wait_for(
        command(socket, type="device/health", device="SERIAL"), 2
    )
    assert response["error"] == {
        "code": "timeout",
        "message": "The device did not respond in time. Check its connection and try again.",
    }
    assert cancelled.is_set()
    assert (await command(socket, type="devices/list"))["result"][0][
        "serial"
    ] == "SERIAL"
    await socket.close()


async def test_duplicate_request_id_closes_socket(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Overlapping requests cannot share a correlation ID."""
    started = asyncio.Event()

    async def blocked(*args: object) -> None:
        started.set()
        await asyncio.Event().wait()

    monkeypatch.setattr(server.operations, "read_health", blocked)
    socket = await connect(client)
    message = {"id": 7, "type": "device/health", "device": "SERIAL"}
    await socket.send_json(message)
    await asyncio.wait_for(started.wait(), 2)
    await socket.send_json(message)
    assert (await socket.receive()).data == 1008


@pytest.mark.parametrize(
    ("payload", "close_code"),
    [(b"binary", 1003), ("not-json", 1008), ('{"id":true}', 1008)],
)
async def test_invalid_frames(
    client: TestClient, payload: str | bytes, close_code: int
) -> None:
    """Malformed protocol frames close the connection without executing a command."""
    socket = await connect(client)
    if isinstance(payload, bytes):
        await socket.send_bytes(payload)
    else:
        await socket.send_str(payload)
    assert (await socket.receive()).data == close_code


async def test_invalid_auth_frame(client: TestClient) -> None:
    """Malformed authentication data is rejected."""
    socket = await client.ws_connect("/api/websocket", headers=HEADERS)
    await socket.send_str("{")
    assert (await socket.receive()).data == 1008


async def test_busy_connection(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A slow device cannot create unbounded concurrent requests per client."""
    started = asyncio.Event()

    async def blocked(*args: object) -> None:
        started.set()
        await asyncio.Event().wait()

    monkeypatch.setattr(server, "MAX_PENDING", 1)
    monkeypatch.setattr(server.operations, "read_health", blocked)
    socket = await connect(client)
    await socket.send_json({"id": 1, "type": "device/health", "device": "SERIAL"})
    await asyncio.wait_for(started.wait(), 2)
    await socket.send_json({"id": 2, "type": "devices/list"})
    assert (await socket.receive_json())["error"]["code"] == "busy"
    await socket.close()


@pytest.mark.parametrize(
    ("failure", "code"),
    [(TimeoutError(), "timeout"), (RuntimeError("private-password"), "internal")],
)
async def test_unexpected_and_timeout_errors_are_safe(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    failure: Exception,
    code: str,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Timeouts and unexpected exceptions produce safe, actionable responses."""
    monkeypatch.setattr(
        server.operations, "read_health", AsyncMock(side_effect=failure)
    )
    socket = await connect(client)
    response = await command(socket, type="device/health", device="SERIAL")
    assert response["error"]["code"] == code
    assert "private-password" not in str(response)
    assert "private-password" not in caplog.text
    await socket.close()


async def test_response_lost_during_send(registry: DeviceRegistry) -> None:
    """A client disconnect during a response does not leak an unhandled exception."""
    socket = MagicMock(
        closed=False, send_json=AsyncMock(side_effect=ConnectionResetError)
    )
    await server._respond(socket, registry, {"id": 1, "type": "devices/list"})
    socket.send_json.assert_awaited_once()


def test_server_starts_only_on_loopback(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    """Only after listening, print the private link and open it in a browser."""
    browser_thread = MagicMock()
    thread_factory = MagicMock(return_value=browser_thread)
    monkeypatch.setattr(server, "Thread", thread_factory)
    runner = MagicMock(side_effect=lambda *args, **kwargs: kwargs["print"]("listening"))
    monkeypatch.setattr(server.web, "run_app", runner)
    monkeypatch.setattr(server.secrets, "token_urlsafe", lambda _: "temporary-token")
    server.run_server(tmp_path / "test", 8766)
    assert "http://127.0.0.1:8766/#temporary-token" in capsys.readouterr().out
    assert runner.call_args.kwargs["host"] == "127.0.0.1"
    assert runner.call_args.kwargs["port"] == 8766
    thread_factory.assert_called_once_with(
        target=server._open_browser,
        args=("http://127.0.0.1:8766/#temporary-token",),
        daemon=True,
    )
    browser_thread.start.assert_called_once()


@pytest.mark.parametrize(
    "failure", [False, OSError("no browser"), server.webbrowser.Error("no browser")]
)
def test_browser_launch_failure(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    failure: bool | Exception,
) -> None:
    """A failed browser launch leaves the printed link usable without exposing it again."""
    browser = MagicMock()
    if isinstance(failure, Exception):
        browser.side_effect = failure
    else:
        browser.return_value = failure
    monkeypatch.setattr(server.webbrowser, "open", browser)
    server._open_browser("http://127.0.0.1:8766/#private-token")
    browser.assert_called_once_with("http://127.0.0.1:8766/#private-token")
    assert "use the private URL above" in capsys.readouterr().err


def test_browser_launch_success(monkeypatch: pytest.MonkeyPatch) -> None:
    """The browser receives the complete private URL."""
    browser = MagicMock(return_value=True)
    monkeypatch.setattr(server.webbrowser, "open", browser)
    server._open_browser("http://127.0.0.1:8766/#private-token")
    browser.assert_called_once_with("http://127.0.0.1:8766/#private-token")


def test_server_does_not_open_browser_when_port_is_busy(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    """A bind failure must not launch a link to another process on that port."""
    thread_factory = MagicMock()
    monkeypatch.setattr(server, "Thread", thread_factory)
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        listener.listen()
        port = listener.getsockname()[1]
        with pytest.raises(OSError, match=r"(?i)address already in use|only one usage"):
            server.run_server(tmp_path / "test", port)
    thread_factory.assert_not_called()
    assert "private URL" not in capsys.readouterr().out
