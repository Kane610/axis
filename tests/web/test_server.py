"""Exercise the local web protocol and its security boundaries."""

import asyncio
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from io import BytesIO
import json
from pathlib import Path
import socket
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock

from aiohttp import WSMsgType
import pytest

from axis.application.errors import ErrorKind, OperationError, StorageError
from axis.application.records import (
    ConnectionSettings,
    DeviceRecord,
    DiscoverySnapshot,
    HealthSnapshot,
)
from axis.application.storage import DeviceRegistry
from axis.interfaces.vapix import InterfaceState
from axis.models.api_discovery import Api, ApiStatus
from axis.web import network, server
from axis.web.network import NetworkInterface

from tests.application.test_acap_catalog import create_package

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Awaitable, Callable
    from typing import Any

    from aiohttp import ClientWebSocketResponse
    from aiohttp.test_utils import TestClient

HOST = "127.0.0.1:8765"
HEADERS = {"Host": HOST, "Origin": f"http://{HOST}"}
TOKEN = "test-token"


def test_network_interface_inventory(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep down, addressless, and unknown-status interfaces distinct."""
    monkeypatch.setattr(
        network.psutil,
        "net_if_addrs",
        lambda: {
            "lan": [MagicMock(family=socket.AF_INET, address="192.0.2.10")],
            "unknown": [MagicMock(family=socket.AF_INET6, address="::1")],
        },
    )
    monkeypatch.setattr(
        network.psutil,
        "net_if_stats",
        lambda: {"lan": MagicMock(isup=True), "down": MagicMock(isup=False)},
    )
    interfaces = network.network_interfaces()
    assert interfaces == [
        NetworkInterface("down", "down", (), False),
        NetworkInterface("lan", "lan", ("192.0.2.10",), True),
        NetworkInterface("unknown", "unknown", (), None),
    ]
    assert [item.available for item in interfaces] == [False, True, False]


@pytest.mark.parametrize("method", ["net_if_addrs", "net_if_stats"])
def test_network_inventory_failure_is_explicit(
    monkeypatch: pytest.MonkeyPatch, method: str
) -> None:
    """Surface operating-system failures instead of silently selecting all interfaces."""
    monkeypatch.setattr(network.psutil, "net_if_addrs", dict)
    monkeypatch.setattr(network.psutil, "net_if_stats", dict)
    monkeypatch.setattr(
        network.psutil, method, MagicMock(side_effect=OSError("unavailable"))
    )
    with pytest.raises(OperationError, match="Cannot list local network interfaces"):
        network.network_interfaces()


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


async def test_restart_requires_confirmation_and_reports_unknown(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The authenticated command requires confirmation and preserves uncertainty."""
    restart = AsyncMock()
    monkeypatch.setattr(server.operations, "restart_device", restart)
    socket = await connect(client)
    for confirmation in (None, False, 1, "true"):
        result = await command(
            socket, type="device/restart", device="SERIAL", confirmed=confirmation
        )
        assert result["error"]["code"] == "validation"
    restart.assert_not_awaited()
    result = await command(
        socket, type="device/restart", device="SERIAL", confirmed=True
    )
    assert result == {"id": 1, "result": None}
    assert restart.await_args.args[0].serial == "SERIAL"
    assert restart.await_args.kwargs == {"confirmed": True}
    restart.side_effect = OperationError(
        "Restart outcome is unknown. Check the device before trying again.",
        kind=ErrorKind.CONNECTION,
        outcome_unknown=True,
    )
    result = await command(
        socket, type="device/restart", device="SERIAL", confirmed=True
    )
    assert result["error"] == {
        "code": "connection",
        "message": "Restart outcome is unknown. Check the device before trying again.",
        "outcome_unknown": True,
    }


async def test_application_action_requires_confirmation(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Only explicit confirmed application actions reach the device operation."""
    action = AsyncMock()
    monkeypatch.setattr(server.operations, "control_application", action)
    socket = await connect(client)
    request = {
        "type": "device/application-action",
        "device": "SERIAL",
        "action": "remove",
        "package": "example",
        "version": "1.0",
        "status": "Stopped",
    }
    for confirmed in (False, 1, None):
        response = await command(socket, **request, confirmed=confirmed)
        assert response["error"]["code"] == "validation"
    action.assert_not_awaited()
    assert await command(socket, **request, confirmed=True) == {"id": 1, "result": None}
    assert action.await_args.args[1:] == ("remove", "example", "1.0", "Stopped")
    assert action.await_args.kwargs == {"confirmed": True}


async def test_application_support_command(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Return lightweight support results and propagate unavailable discovery."""
    support = AsyncMock(return_value={"apis": [], "supported": True})
    monkeypatch.setattr(server.operations, "application_support", support)
    socket = await connect(client)
    assert await command(
        socket, type="device/application-support", device="SERIAL"
    ) == {"id": 1, "result": {"apis": [], "supported": True}}
    assert support.await_args.args[0].serial == "SERIAL"
    support.side_effect = OperationError(
        "Application support could not be determined.", kind=ErrorKind.UNSUPPORTED
    )
    result = await command(socket, type="device/application-support", device="SERIAL")
    assert result["error"]["code"] == "unsupported"
    assert result["error"]["message"] == "Application support could not be determined."


async def test_application_policy_and_license_commands(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Require confirmation for policy and license writes over the authenticated socket."""
    policy = AsyncMock()
    license_write = AsyncMock()
    monkeypatch.setattr(server.operations, "set_application_policy", policy)
    monkeypatch.setattr(server.operations, "manage_application_license", license_write)
    monkeypatch.setattr(
        server.operations, "application_sdks", AsyncMock(return_value=["acap3"])
    )
    monkeypatch.setattr(
        server.operations, "application_policy", AsyncMock(return_value=False)
    )
    socket = await connect(client)
    assert await command(socket, type="device/application-sdks", device="SERIAL") == {
        "id": 1,
        "result": ["acap3"],
    }
    assert await command(socket, type="device/application-policy", device="SERIAL") == {
        "id": 1,
        "result": False,
    }
    policy_request = {
        "type": "device/application-policy-set",
        "device": "SERIAL",
        "previous": False,
        "value": True,
    }
    license_request = {
        "type": "device/application-license-remove",
        "device": "SERIAL",
        "package": "app",
        "version": "1",
        "status": "Stopped",
        "license_status": "Valid",
    }
    for request in (policy_request, license_request):
        assert (await command(socket, **request, confirmed=False))["error"][
            "code"
        ] == "validation"
        assert await command(socket, **request, confirmed=True) == {
            "id": 1,
            "result": None,
        }
    policy.assert_awaited_once()
    license_write.assert_awaited_once()
    assert (await command(socket, **{**policy_request, "previous": 1}, confirmed=True))[
        "error"
    ]["code"] == "validation"


async def test_license_upload_authentication_validation_and_contents(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Only authenticated, confirmed, bounded license files reach the operation."""
    contents = []

    async def upload(
        record, package, version, status, license_status, file, *, confirmed
    ):
        contents.append(
            (
                record.serial,
                package,
                version,
                status,
                license_status,
                file.read(),
                confirmed,
            )
        )

    monkeypatch.setattr(server.operations, "manage_application_license", upload)
    headers = {
        **HEADERS,
        "X-Axis-Token": TOKEN,
        "X-Axis-Device": "SERIAL",
        "X-Axis-Package": "my%20app",
        "X-Axis-Version": "1",
        "X-Axis-Status": "Stopped",
        "X-Axis-License-Status": "Missing",
        "X-Axis-Confirmed": "true",
    }
    for changes in ({"Origin": "http://attacker"}, {"X-Axis-Token": "bad"}):
        assert (
            await client.post(
                "/api/application-license", headers={**headers, **changes}, data=b"key"
            )
        ).status == 403
    for changes in ({"X-Axis-Confirmed": "false"}, {"X-Axis-Package": ""}):
        assert (
            await client.post(
                "/api/application-license", headers={**headers, **changes}, data=b"key"
            )
        ).status == 400
    assert (
        await client.post("/api/application-license", headers=headers, data=b"")
    ).status == 400
    assert (
        await client.post(
            "/api/application-license",
            headers={**headers, "X-Axis-Device": "unknown"},
            data=b"key",
        )
    ).status == 400
    assert (
        await client.post(
            "/api/application-license",
            headers=headers,
            data=BytesIO(b"x" * (1024 * 1024 + 1)),
        )
    ).status == 400
    assert not contents
    response = await client.post(
        "/api/application-license", headers=headers, data=b"private key"
    )
    assert response.status == 200
    assert contents == [
        ("SERIAL", "my app", "1", "Stopped", "Missing", b"private key", True)
    ]


@pytest.mark.parametrize("body", [b"ab", b"abcd"])
async def test_license_upload_rejects_mismatched_stream_length(
    client, monkeypatch, body
):
    """Interrupted or overflowing license streams never reach the device."""
    write = AsyncMock()
    monkeypatch.setattr(server.operations, "manage_application_license", write)
    request = MagicMock()
    request.headers = {
        **HEADERS,
        "X-Axis-Token": TOKEN,
        "X-Axis-Device": "SERIAL",
        "X-Axis-Package": "app",
        "X-Axis-Confirmed": "true",
    }
    request.content_length = 3

    async def chunks(size):
        yield body

    request.content.iter_chunked = chunks
    route = next(
        route
        for route in client.server.app.router.routes()
        if route.resource.canonical == "/api/application-license"
    )
    assert (await route.handler(request)).status == 400
    write.assert_not_awaited()


async def test_license_upload_busy_and_errors(client, monkeypatch):
    """Reject simultaneous uploads and retain safe errors and unknown outcomes."""
    headers = {
        **HEADERS,
        "X-Axis-Token": TOKEN,
        "X-Axis-Device": "SERIAL",
        "X-Axis-Package": "app",
        "X-Axis-Confirmed": "true",
    }
    started, finish = asyncio.Event(), asyncio.Event()

    async def upload(*args, **kwargs):
        started.set()
        await finish.wait()
        msg = "Check license before retrying."
        raise OperationError(msg, outcome_unknown=True)

    monkeypatch.setattr(server.operations, "manage_application_license", upload)
    first = asyncio.create_task(
        client.post("/api/application-license", headers=headers, data=b"key")
    )
    await started.wait()
    assert (
        await client.post("/api/application-license", headers=headers, data=b"key")
    ).status == 409
    finish.set()
    response = await first
    assert response.status == 400
    assert (await response.json())["error"]["outcome_unknown"] is True
    monkeypatch.setattr(server, "TemporaryFile", MagicMock(side_effect=OSError()))
    response = await client.post(
        "/api/application-license", headers=headers, data=b"key"
    )
    assert response.status == 400
    assert "Could not receive" in (await response.json())["error"]["message"]


async def test_application_upload_authentication_and_validation(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Only authenticated, confirmed, bounded packages reach a saved device."""
    upload = AsyncMock()
    monkeypatch.setattr(server.operations, "install_application", upload)
    headers = {
        **HEADERS,
        "X-Axis-Token": TOKEN,
        "X-Axis-Device": "SERIAL",
        "X-Axis-Filename": "example.eap",
        "X-Axis-Confirmed": "true",
    }
    for changed in (
        {"Origin": "http://attacker.example"},
        {"X-Axis-Token": "wrong"},
        {"Host": "attacker.example"},
    ):
        response = await client.post(
            "/api/application-upload", headers={**headers, **changed}, data=b"abc"
        )
        assert response.status == 403
    for changed in (
        {"X-Axis-Confirmed": "false"},
        {"X-Axis-Filename": "../example.eap"},
        {"X-Axis-Filename": "example.txt"},
        {"X-Axis-Device": ""},
        {"X-Axis-Device": "%FF"},
        {"X-Axis-Device": "missing"},
    ):
        response = await client.post(
            "/api/application-upload", headers={**headers, **changed}, data=b"abc"
        )
        assert response.status == 400
    response = await client.post("/api/application-upload", headers=headers, data=b"")
    assert response.status == 400
    assert server.MAX_APPLICATION_PACKAGE_SIZE == 1024 * 1024 * 1024
    monkeypatch.setattr(server, "MAX_APPLICATION_PACKAGE_SIZE", 3)
    response = await client.post(
        "/api/application-upload", headers=headers, data=b"abcd"
    )
    assert response.status == 400
    upload.assert_not_awaited()

    captured = []

    async def install(record, package, *, confirmed):
        captured.append((record.serial, package.read(), confirmed, package))

    upload.side_effect = install
    response = await client.post(
        "/api/application-upload", headers=headers, data=b"abc"
    )
    assert response.status == 200
    assert await response.json() == {"result": None}
    assert captured[0][:3] == ("SERIAL", b"abc", True)
    assert captured[0][3].closed

    monkeypatch.setattr(server, "MAX_APPLICATION_PACKAGE_SIZE", 20000)
    response = await client.post(
        "/api/application-upload", headers=headers, data=b"x" * 20000
    )
    assert response.status == 200
    assert len(captured[1][1]) == 20000


@pytest.mark.parametrize("body", [b"ab", b"abcd"])
async def test_application_upload_rejects_mismatched_stream_length(
    client: TestClient, monkeypatch: pytest.MonkeyPatch, body: bytes
) -> None:
    """Reject interrupted or overflowing request streams before device dispatch."""
    upload = AsyncMock()
    monkeypatch.setattr(server.operations, "install_application", upload)
    request = MagicMock()
    request.headers = {
        **HEADERS,
        "X-Axis-Token": TOKEN,
        "X-Axis-Device": "SERIAL",
        "X-Axis-Filename": "example.eap",
        "X-Axis-Confirmed": "true",
    }
    request.content_length = 3

    async def chunks(size):
        yield body

    request.content.iter_chunked = chunks
    route = next(
        route
        for route in client.server.app.router.routes()
        if route.resource.canonical == "/api/application-upload"
    )
    response = await route.handler(request)
    assert response.status == 400
    upload.assert_not_awaited()


async def test_application_upload_reports_temporary_storage_failure(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A full or unavailable temporary filesystem does not dispatch a write."""
    upload = AsyncMock()
    monkeypatch.setattr(server.operations, "install_application", upload)
    monkeypatch.setattr(server, "TemporaryFile", MagicMock(side_effect=OSError()))
    headers = {
        **HEADERS,
        "X-Axis-Token": TOKEN,
        "X-Axis-Device": "SERIAL",
        "X-Axis-Filename": "example.eap",
        "X-Axis-Confirmed": "true",
    }
    response = await client.post(
        "/api/application-upload", headers=headers, data=b"abc"
    )
    assert response.status == 400
    assert "Could not receive" in (await response.json())["error"]["message"]
    upload.assert_not_awaited()


async def test_application_upload_busy_and_unknown_outcome(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Reject concurrent uploads and preserve uncertain write results."""
    started = asyncio.Event()
    finish = asyncio.Event()

    async def install(*args, **kwargs):
        started.set()
        await finish.wait()
        msg = "Check applications before trying again."
        raise OperationError(msg, outcome_unknown=True)

    monkeypatch.setattr(server.operations, "install_application", install)
    headers = {
        **HEADERS,
        "X-Axis-Token": TOKEN,
        "X-Axis-Device": "SERIAL",
        "X-Axis-Filename": "example.eap",
        "X-Axis-Confirmed": "true",
    }
    first = asyncio.create_task(
        client.post("/api/application-upload", headers=headers, data=b"abc")
    )
    await started.wait()
    second = await client.post("/api/application-upload", headers=headers, data=b"abc")
    assert second.status == 409
    finish.set()
    response = await first
    assert response.status == 400
    assert (await response.json())["error"]["outcome_unknown"] is True


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


async def test_architecture_command_reads_saved_device(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Expose the reported architecture through the authenticated protocol."""
    read = AsyncMock(return_value="armv7hf")
    monkeypatch.setattr(server.operations, "read_architecture", read)
    socket = await connect(client)
    assert await command(socket, type="device/architecture", device="SERIAL") == {
        "id": 1,
        "result": "armv7hf",
    }
    assert read.await_args.args[0].serial == "SERIAL"


async def test_settings_only_change_the_alias_without_contacting_device(
    client: TestClient, registry: DeviceRegistry, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Keep passwords server-side and save alias changes without a live read."""
    original = registry.resolve("SERIAL")
    identify = AsyncMock()
    monkeypatch.setattr(server.operations, "identify", identify)
    socket = await connect(client)
    invalid = await command(socket, type="device/settings", device="")
    assert invalid["error"]["code"] == "invalid_request"
    response = await command(socket, type="device/settings", device="SERIAL")
    assert response["result"]["username"] == original.config.username
    assert "private-password" not in str(response)
    args = {
        "type": "device/configure",
        "device": "SERIAL",
        "host": original.config.host,
        "port": original.config.port,
        "username": original.config.username,
        "password": "",
        "web_proto": original.config.web_proto,
        "verify_ssl": original.config.verify_ssl,
    }
    assert (await command(socket, **args, alias=None))["error"][
        "code"
    ] == "invalid_request"
    result = (await command(socket, **args, alias="  Lobby  "))["result"]
    assert result["device"]["alias"] == "Lobby"
    assert not result["connection_changed"]
    original.alias = "Lobby"
    assert registry.resolve("SERIAL") == original
    result = (await command(socket, **args, alias="SERIAL"))["result"]
    assert result["device"]["alias"] == ""
    identify.assert_not_awaited()
    await socket.close()


async def test_connection_settings_require_verified_identity(
    client: TestClient, registry: DeviceRegistry, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Never reuse the saved password at a new address or commit an unverified change."""
    original = registry.resolve("SERIAL")
    args = {
        "type": "device/configure",
        "device": "SERIAL",
        "alias": "Lobby",
        "host": "192.0.2.10",
        "port": 8443,
        "username": "operator",
        "password": "replacement",
        "web_proto": "https",
        "verify_ssl": True,
    }
    socket = await connect(client)
    identify = AsyncMock()
    monkeypatch.setattr(server.operations, "identify", identify)
    for overrides in ({"password": ""}, {"host": "user@camera.local"}):
        response = await command(socket, **(args | overrides))
        assert response["error"]["code"] == "validation"
    identify.assert_not_awaited()

    identify.return_value = DeviceRecord("OTHER", original.config)
    assert (await command(socket, **args))["error"]["code"] == "conflict"
    assert registry.resolve("SERIAL") == original

    identify.side_effect = OperationError("Unreachable.", kind=ErrorKind.CONNECTION)
    response = await command(socket, **args)
    assert response["error"]["code"] == "connection"
    assert "protocol" in response["error"]["message"]
    assert registry.resolve("SERIAL") == original

    async def concurrent_update(config: ConnectionSettings) -> DeviceRecord:
        registry.update_alias("SERIAL", "Updated elsewhere")
        return DeviceRecord("SERIAL", config)

    identify.side_effect = concurrent_update
    assert (await command(socket, **args))["error"]["code"] == "storage"
    assert registry.resolve("SERIAL").config == original.config

    identify.side_effect = None
    identify.return_value = original
    response = await command(socket, **args)
    assert response["result"]["connection_changed"]
    assert "replacement" not in str(response)
    assert registry.resolve("SERIAL").config == ConnectionSettings(
        "192.0.2.10",
        "operator",
        "replacement",
        port=8443,
        web_proto="https",
        verify_ssl=True,
    )
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


async def test_streams_discovery_without_authorizing_provisional_devices(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Keep the request open for updates and require a final result before connecting."""
    finish = asyncio.Event()
    entry = {
        "name": "Entrance",
        "host": "192.0.2.2",
        "macaddress": "00:40:8c:01:02:03",
    }

    async def discover(
        *, on_device: Callable[[dict[str, str]], Awaitable[None]]
    ) -> list[dict[str, str]]:
        await on_device(entry)
        await finish.wait()
        return [entry]

    monkeypatch.setattr(server, "discover_axis_devices", discover)
    socket = await connect(client)
    await socket.send_json({"id": 2, "type": "devices/discover", "stream": True})
    assert await socket.receive_json(timeout=2) == {
        "id": 2,
        "type": "discovery/device",
        "device": entry,
    }
    attempt = await command(
        socket,
        type="devices/test-connection",
        host=entry["host"],
        username="root",
        password="test-password",
        verify_ssl=True,
    )
    assert attempt["error"]["code"] == "validation"
    finish.set()
    assert await socket.receive_json(timeout=2) == {"id": 2, "result": [entry]}
    await socket.close()


async def test_web_network_settings_control_discovery(
    client: TestClient, registry: DeviceRegistry, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Persist choices and scan only available selected IPv4 addresses."""
    adapters = [
        NetworkInterface("lan", "Ethernet", ("192.0.2.10", "192.0.2.11"), True),
        NetworkInterface("vpn", "VPN", ("192.0.2.30",), False),
        NetworkInterface("other", "Other", ("192.0.2.20",), True),
    ]
    monkeypatch.setattr(server, "network_interfaces", lambda: adapters)
    discover = AsyncMock(return_value=[])
    monkeypatch.setattr(server, "discover_axis_devices", discover)
    socket = await connect(client)
    assert (await command(socket, type="server/settings"))["result"]["selected"] is None
    for invalid in (
        {},
        {"interfaces": []},
        {"interfaces": ["other", "other"]},
        {"interfaces": ["unknown"]},
        {"interfaces": [None]},
    ):
        response = await command(socket, type="server/configure", **invalid)
        assert response["error"]["code"] == "invalid_request"
    response = await command(socket, type="server/configure", interfaces=["lan", "vpn"])
    assert response["result"]["selected"] == ["lan", "vpn"]
    assert DeviceRegistry(registry.path).web_discovery_interfaces() == ["lan", "vpn"]
    await socket.send_json({"id": 2, "type": "devices/discover", "stream": True})
    warning = await socket.receive_json(timeout=2)
    assert warning["type"] == "discovery/warning"
    assert "vpn" in warning["message"]
    assert await socket.receive_json(timeout=2) == {"id": 2, "result": []}
    assert discover.call_args.kwargs["interfaces"] == ["192.0.2.10", "192.0.2.11"]

    adapters[:] = [adapters[1]]
    settings = (await command(socket, type="server/settings"))["result"]
    assert any(
        item["name"] == "lan" and item["addresses"] == []
        for item in settings["interfaces"]
    )
    await socket.send_json({"id": 3, "type": "devices/discover", "stream": True})
    assert (await socket.receive_json(timeout=2))["type"] == "discovery/warning"
    assert (await socket.receive_json(timeout=2))["error"]["message"] == (
        "No selected network interface is up with an IPv4 address."
    )
    assert discover.await_count == 1
    assert (await command(socket, type="server/configure", interfaces=None))["result"][
        "selected"
    ] is None
    assert registry.web_discovery_interfaces() is None
    await command(socket, type="devices/discover")
    discover.assert_awaited_with()
    await socket.close()


async def test_acap_folder_settings_and_catalog(
    client: TestClient, registry: DeviceRegistry, tmp_path: Path
) -> None:
    """Persist and scan a server-side folder without changing discovery settings."""
    folder = tmp_path / "acaps"
    folder.mkdir()
    create_package(folder / "package.eap", signed=True)
    socket = await connect(client)
    response = await command(
        socket, type="server/configure", interfaces=None, acap_folder=str(folder)
    )
    assert response["result"]["acap_folder"] == str(folder)
    assert DeviceRegistry(registry.path).web_acap_folder() == str(folder)
    response = await command(socket, type="acap/scan")
    assert response["result"]["packages"][0]["signature"] == "present_unverified"
    assert response["result"]["packages"][0]["name"] == "example"
    response = await command(
        socket, type="server/configure", interfaces=None, acap_folder="relative"
    )
    assert response["error"]["code"] == "invalid_request"
    assert registry.web_acap_folder() == str(folder)
    response = await command(
        socket,
        type="server/configure",
        interfaces=None,
        acap_folder=str(tmp_path / "missing"),
    )
    assert response["error"]["message"] == (
        "ACAP folder does not exist or is not a directory."
    )
    assert registry.web_acap_folder() == str(folder)
    response = await command(
        socket, type="server/configure", interfaces=None, acap_folder=None
    )
    assert response["result"]["acap_folder"] is None
    await socket.close()


async def test_catalog_discards_scans_when_folder_changes(
    registry: DeviceRegistry, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Retry a scan if settings changed, and report repeated changes."""
    catalog = server._AcapCatalog(registry)
    folders = MagicMock(side_effect=["old", "new", "new", "new", "new", "new"])
    monkeypatch.setattr(registry, "web_acap_folder", folders)
    scan = MagicMock(return_value={"packages": [], "errors": []})
    monkeypatch.setattr(server, "scan_folder", scan)
    result = await catalog.scan()
    assert result["folder"] == "new"
    assert scan.call_args_list[0].args == ("old",)
    assert scan.call_args_list[1].args == ("new",)

    folders.side_effect = ["one", "two", "three", "four", "five", "six"]
    with pytest.raises(OperationError, match="folder changed during scanning"):
        await catalog.scan()


async def test_catalog_background_reports_settings_failure(
    registry: DeviceRegistry,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Log settings errors without terminating periodic catalog scans."""
    catalog = server._AcapCatalog(registry)
    scan = AsyncMock(side_effect=StorageError("unavailable"))
    monkeypatch.setattr(catalog, "scan", scan)
    monkeypatch.setattr(
        server.asyncio, "sleep", AsyncMock(side_effect=asyncio.CancelledError)
    )
    with pytest.raises(asyncio.CancelledError):
        await catalog.run()
    assert "ACAP catalog could not read server settings" in caplog.text
    scan.assert_awaited_once()


async def test_catalog_cleanup_cancels_pending_scan(
    aiohttp_client: Callable[..., Any],
    registry: DeviceRegistry,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Cancel the shielded scan when the web application shuts down."""
    started = asyncio.Event()
    release = asyncio.Event()

    async def blocked_scan(self: server._AcapCatalog) -> dict[str, Any]:
        started.set()
        await release.wait()
        return {"folder": None, "packages": [], "errors": [], "error": ""}

    monkeypatch.setattr(server._AcapCatalog, "_scan", blocked_scan)
    client = await aiohttp_client(server.create_app(registry, TOKEN, 8765))
    await asyncio.wait_for(started.wait(), 2)
    await client.close()
    assert not release.is_set()


async def test_catalog_commands_validate_context_and_device(
    registry: DeviceRegistry,
) -> None:
    """Reject catalog commands without a catalog or a valid device identifier."""
    with pytest.raises(ValueError, match=r"^$"):
        await server._execute(MagicMock(), registry, {"type": "acap/catalog"}, {})
    catalog = server._AcapCatalog(registry)
    with pytest.raises(ValueError, match=r"^$"):
        await server._execute(
            MagicMock(),
            registry,
            {"type": "device/acap-updates", "device": ""},
            {},
            catalog=catalog,
        )


def test_catalog_folder_permission_failure(
    registry: DeviceRegistry, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Reject folder settings if its directory cannot be read."""
    monkeypatch.setattr(server.os, "scandir", MagicMock(side_effect=PermissionError))
    with pytest.raises(OperationError, match="Cannot read ACAP folder"):
        server._configure_server(
            registry,
            {
                "type": "server/configure",
                "interfaces": None,
                "acap_folder": str(tmp_path),
            },
        )


def test_snapshot_rejects_nonregular_growing_and_unreadable_packages(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Snapshot preflight rejects invalid source files and read failures."""
    path = tmp_path / "package.eap"
    path.touch()
    with (
        BytesIO() as snapshot,
        pytest.raises(server.PackageError, match="non-empty regular"),
    ):
        server._snapshot_acap(str(tmp_path), path.name, "a" * 64, snapshot)
    path.write_bytes(b"content")
    with monkeypatch.context() as patch:
        patch.setattr(server, "MAX_PACKAGE_SIZE", 4)
        patch.setattr(
            server.os,
            "fstat",
            MagicMock(return_value=MagicMock(st_mode=0o100644, st_size=1)),
        )
        with BytesIO() as snapshot, pytest.raises(server.PackageError, match="exceeds"):
            server._snapshot_acap(str(tmp_path), path.name, "a" * 64, snapshot)
    with monkeypatch.context() as patch:
        source = MagicMock()
        source.__enter__.return_value = source
        source.read.side_effect = OSError("private")
        patch.setattr(server, "open_package", lambda *_: source)
        patch.setattr(
            server.os,
            "fstat",
            MagicMock(return_value=MagicMock(st_mode=0o100644, st_size=1)),
        )
        with (
            BytesIO() as snapshot,
            pytest.raises(server.PackageError, match="check folder permissions"),
        ):
            server._snapshot_acap(str(tmp_path), path.name, "a" * 64, snapshot)


async def test_browse_server_folders(client: TestClient, tmp_path: Path) -> None:
    """Browse directories without including files or changing saved settings."""
    (tmp_path / "Zebra").mkdir()
    (tmp_path / "alpha").mkdir()
    (tmp_path / "file.eap").write_bytes(b"package")
    (tmp_path / "link").symlink_to(tmp_path / "alpha", target_is_directory=True)
    resolved = await asyncio.to_thread(tmp_path.resolve)
    socket = await connect(client)
    result = await command(socket, type="server/browse-folders", path=str(tmp_path))
    assert result["result"] == {
        "path": str(resolved),
        "parent": str(resolved.parent),
        "directories": [
            {"name": name, "path": str(resolved / name)}
            for name in ("alpha", "link", "Zebra")
        ],
    }
    result = await command(
        socket, type="server/browse-folders", path=str(tmp_path / "alpha")
    )
    assert result["result"]["parent"] == str(resolved)
    assert result["result"]["directories"] == []
    result = await command(socket, type="server/browse-folders", path="relative")
    assert result["error"]["code"] == "invalid_request"
    result = await command(
        socket, type="server/browse-folders", path=str(tmp_path / "missing")
    )
    assert result["error"]["message"] == (
        "Cannot browse this folder; check its path and permissions."
    )
    result = await command(socket, type="server/browse-folders", path=None)
    assert result["result"]["path"] == str(Path.home().resolve())
    await socket.close()


def test_folder_browser_reports_limits_and_permission_errors(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Report oversized and inaccessible directories instead of hiding entries."""
    (tmp_path / "one").mkdir()
    (tmp_path / "two").mkdir()
    monkeypatch.setattr(server, "MAX_FOLDER_ENTRIES", 1)
    with pytest.raises(OperationError, match="too many entries"):
        server._browse_folders(str(tmp_path))
    monkeypatch.setattr(server.os, "scandir", MagicMock(side_effect=PermissionError))
    with pytest.raises(OperationError, match="check its path and permissions"):
        server._browse_folders(str(tmp_path))


async def test_acap_updates_require_auth_confirmation_and_unchanged_file(
    client: TestClient,
    registry: DeviceRegistry,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Only hand the reviewed package snapshot to the verified update operation."""
    folder = tmp_path / "acaps"
    folder.mkdir()
    path = folder / "package.eap"
    create_package(path, signed=True)
    registry.update_web_settings(None, str(folder))
    socket = await connect(client)
    result = await command(socket, type="acap/scan")
    digest = result["result"]["packages"][0]["digest"]
    check = AsyncMock(return_value=[])
    monkeypatch.setattr(server.operations, "application_updates", check)
    assert await command(socket, type="device/acap-updates", device="SERIAL") == {
        "id": 1,
        "result": [],
    }
    assert check.await_args.args[1][0].digest == digest
    update = AsyncMock()
    monkeypatch.setattr(server.operations, "update_application", update)
    headers = {**HEADERS, "X-Axis-Token": TOKEN}
    body = {
        "device": "SERIAL",
        "filename": path.name,
        "digest": digest,
        "version": "1.0.0",
        "status": "Running",
        "vendor": "Vendor",
        "confirmed": True,
        "warnings": ["Vendor differs from the installed application."],
    }
    response = await client.post("/api/application-update", json=body, headers=HEADERS)
    assert response.status == 403
    response = await client.post(
        "/api/application-update", json={**body, "confirmed": False}, headers=headers
    )
    assert response.status == 400
    response = await client.post(
        "/api/application-update", json={**body, "warnings": "ignored"}, headers=headers
    )
    assert response.status == 400
    response = await client.post(
        "/api/application-update",
        json={**body, "filename": "../package.eap"},
        headers=headers,
    )
    assert response.status == 400
    update.assert_not_awaited()
    response = await client.post("/api/application-update", json=body, headers=headers)
    assert response.status == 200
    assert update.await_args.args[0].serial == "SERIAL"
    assert update.await_args.args[2].digest == digest
    assert update.await_args.kwargs["reviewed_warnings"] == (
        "Vendor differs from the installed application.",
    )
    assert update.await_args.kwargs["reviewed_vendor"] == "Vendor"
    response = await client.post(
        "/api/application-update", json={**body, "version": ""}, headers=headers
    )
    assert response.status == 200
    assert update.await_args.args[3] == ""
    update.side_effect = OperationError(
        "Installation outcome is unknown. Check applications before trying again.",
        outcome_unknown=True,
    )
    response = await client.post("/api/application-update", json=body, headers=headers)
    assert response.status == 400
    assert (await response.json())["error"]["outcome_unknown"] is True
    assert update.await_count == 3
    update.side_effect = OperationError(
        "Vendor ID mismatch.", outcome_unknown=True, device_code=27
    )
    response = await client.post("/api/application-update", json=body, headers=headers)
    assert (await response.json())["error"]["device_code"] == 27
    replace_app = AsyncMock()
    monkeypatch.setattr(server.operations, "replace_catalog_application", replace_app)
    replace_body = {**body, "remove": True, "install_warnings": []}
    response = await client.post(
        "/api/application-replace",
        json={**replace_body, "remove": "yes"},
        headers=headers,
    )
    assert response.status == 400
    replace_app.assert_not_awaited()
    response = await client.post(
        "/api/application-replace", json=replace_body, headers=headers
    )
    assert response.status == 200
    assert replace_app.await_args.kwargs["remove"] is True
    assert replace_app.await_args.kwargs["reviewed_install_warnings"] == ()
    create_package(path)
    response = await client.post("/api/application-update", json=body, headers=headers)
    assert response.status == 400
    assert "changed" in (await response.json())["error"]["message"]
    assert update.await_count == 4
    response = await client.post(
        "/api/application-replace", json=replace_body, headers=headers
    )
    assert response.status == 400
    assert replace_app.await_count == 1
    await socket.close()


async def test_catalog_write_validates_requests_and_serializes_uploads(
    client: TestClient,
    registry: DeviceRegistry,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Reject malformed requests, missing folders, and concurrent uploads."""
    headers = {**HEADERS, "X-Axis-Token": TOKEN}
    body = {
        "device": "SERIAL",
        "filename": "package.eap",
        "digest": "a" * 64,
        "version": "1.0",
        "status": "Running",
        "vendor": "Vendor",
        "warnings": [],
        "confirmed": True,
    }
    response = await client.post("/api/application-update", json=[], headers=headers)
    assert response.status == 400
    response = await client.post(
        "/api/application-update", json={**body, "status": ""}, headers=headers
    )
    assert response.status == 400
    response = await client.post("/api/application-update", json=body, headers=headers)
    assert "No ACAP folder" in (await response.json())["error"]["message"]

    folder = tmp_path / "acaps"
    folder.mkdir()
    path = folder / "package.eap"
    create_package(path, signed=True)
    registry.update_web_settings(None, str(folder))
    with path.open("rb") as package:
        body["digest"] = server.inspect_package(package, path.name).digest
    started = asyncio.Event()
    release = asyncio.Event()

    async def hold_update(*args: object, **kwargs: object) -> None:
        started.set()
        await release.wait()

    monkeypatch.setattr(server.operations, "update_application", hold_update)
    first = asyncio.create_task(
        client.post("/api/application-update", json=body, headers=headers)
    )
    try:
        await asyncio.wait_for(started.wait(), 2)
        response = await client.post(
            "/api/application-update", json=body, headers=headers
        )
        assert response.status == 409
        assert "upload is in progress" in (await response.json())["error"]["message"]
    finally:
        release.set()
        response = await first
        assert response.status == 200


async def test_catalog_write_rejects_folder_change_during_snapshot(
    client: TestClient,
    registry: DeviceRegistry,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Do not perform writes if the catalog folder changes after snapshotting."""
    folder = tmp_path / "acaps"
    folder.mkdir()
    path = folder / "package.eap"
    create_package(path, signed=True)
    registry.update_web_settings(None, str(folder))
    with path.open("rb") as package:
        digest = server.inspect_package(package, path.name).digest
    original = server._snapshot_acap

    def snapshot(*args: Any) -> Any:
        package = original(*args)
        registry.update_web_settings(None, None)
        return package

    monkeypatch.setattr(server, "_snapshot_acap", snapshot)
    install = AsyncMock()
    monkeypatch.setattr(server.operations, "install_catalog_application", install)
    response = await client.post(
        "/api/application-catalog-install",
        json={
            "device": "SERIAL",
            "filename": path.name,
            "digest": digest,
            "warnings": [],
            "confirmed": True,
        },
        headers={**HEADERS, "X-Axis-Token": TOKEN},
    )
    assert response.status == 400
    assert "folder changed" in (await response.json())["error"]["message"]
    install.assert_not_awaited()


async def test_acap_scan_reports_folder_failure(
    client: TestClient, registry: DeviceRegistry, tmp_path: Path
) -> None:
    """Expose a disappeared folder rather than reporting an empty catalog."""
    registry.update_web_settings(None, str(tmp_path / "missing"))
    socket = await connect(client)
    result = await command(socket, type="acap/scan")
    assert "Cannot read ACAP folder" in result["result"]["error"]
    result = await command(socket, type="device/acap-updates", device="SERIAL")
    assert result["error"]["code"] == "operation"
    await socket.close()


async def test_catalog_install_uses_reviewed_snapshot_and_confirmation(
    client: TestClient,
    registry: DeviceRegistry,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Require authentication, confirmation, and an unchanged package for catalog installs."""
    folder = tmp_path / "acaps"
    folder.mkdir()
    path = folder / "package.eap"
    create_package(path, signed=True)
    registry.update_web_settings(None, str(folder))
    socket = await connect(client)
    digest = (await command(socket, type="acap/scan"))["result"]["packages"][0][
        "digest"
    ]
    check = AsyncMock(return_value=[])
    monkeypatch.setattr(server.operations, "application_install_candidates", check)
    assert (
        await command(socket, type="device/acap-install-candidates", device="SERIAL")
    )["result"] == []
    assert check.await_args.args[1][0].digest == digest
    install = AsyncMock()
    monkeypatch.setattr(server.operations, "install_catalog_application", install)
    body = {
        "device": "SERIAL",
        "filename": path.name,
        "digest": digest,
        "confirmed": True,
        "warnings": ["AXIS OS compatibility is unknown."],
    }
    headers = {**HEADERS, "X-Axis-Token": TOKEN}
    response = await client.post(
        "/api/application-catalog-install", json=body, headers=HEADERS
    )
    assert response.status == 403
    response = await client.post(
        "/api/application-catalog-install",
        json={**body, "confirmed": False},
        headers=headers,
    )
    assert response.status == 400
    install.assert_not_awaited()
    response = await client.post(
        "/api/application-catalog-install", json=body, headers=headers
    )
    assert response.status == 200
    assert install.await_args.args[2].digest == digest
    assert install.await_args.kwargs["reviewed_warnings"] == (
        "AXIS OS compatibility is unknown.",
    )
    create_package(path)
    response = await client.post(
        "/api/application-catalog-install", json=body, headers=headers
    )
    assert response.status == 400
    assert "changed" in (await response.json())["error"]["message"]
    install.assert_awaited_once()
    await socket.close()


async def test_network_settings_report_inventory_failures(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Keep local interface errors distinct from device connection errors."""
    monkeypatch.setattr(
        server,
        "network_interfaces",
        MagicMock(
            side_effect=OperationError(
                "Cannot list local network interfaces.", kind=ErrorKind.CONNECTION
            )
        ),
    )
    socket = await connect(client)
    response = await command(socket, type="server/settings")
    assert response["error"]["message"] == "Cannot list local network interfaces."
    await socket.close()


async def test_changed_network_settings_do_not_reuse_startup_scan(
    aiohttp_client: Callable[..., Any],
    registry: DeviceRegistry,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A first client scan uses new settings, not an earlier in-flight scan."""
    started, finish = asyncio.Event(), asyncio.Event()

    async def discover(
        *,
        on_device: Callable[[dict[str, str]], Awaitable[None]] | None = None,
        interfaces: list[str] | None = None,
    ) -> list[dict[str, str]]:
        if interfaces is None:
            started.set()
            await finish.wait()
        return []

    mock = AsyncMock(side_effect=discover)
    monkeypatch.setattr(server, "discover_axis_devices", mock)
    monkeypatch.setattr(
        server,
        "network_interfaces",
        lambda: [NetworkInterface("lan", "LAN", ("192.0.2.10",), True)],
    )
    client = await aiohttp_client(
        server.create_app(registry, TOKEN, 8765, startup_discovery=True)
    )
    await asyncio.wait_for(started.wait(), 2)
    socket = await connect(client)
    await command(socket, type="server/configure", interfaces=["lan"])
    assert await command(socket, type="devices/discover", stream=True) == {
        "id": 1,
        "result": [],
    }
    assert mock.call_args.kwargs["interfaces"] == ["192.0.2.10"]
    finish.set()
    await socket.close()


async def test_startup_warning_is_replayed_to_late_client(
    aiohttp_client: Callable[..., Any],
    registry: DeviceRegistry,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An authenticated late client receives the startup scan warning."""
    registry.update_web_discovery_interfaces(["lan", "vpn"])
    monkeypatch.setattr(
        server,
        "network_interfaces",
        lambda: [NetworkInterface("lan", "LAN", ("192.0.2.10",), True)],
    )
    done = asyncio.Event()

    async def discover(**kwargs: object) -> list[dict[str, str]]:
        done.set()
        return []

    monkeypatch.setattr(server, "discover_axis_devices", discover)
    client = await aiohttp_client(
        server.create_app(registry, TOKEN, 8765, startup_discovery=True)
    )
    await asyncio.wait_for(done.wait(), 2)
    socket = await connect(client)
    await socket.send_json({"id": 2, "type": "devices/discover", "stream": True})
    assert (await socket.receive_json(timeout=2))["message"].endswith("vpn")
    assert await socket.receive_json(timeout=2) == {"id": 2, "result": []}
    await socket.close()


async def test_startup_warning_is_streamed_to_waiting_client(
    registry: DeviceRegistry, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Deliver warnings raised after an authenticated client subscribes."""
    release = asyncio.Event()

    async def discover(
        selected: list[str] | None,
        publish: Callable[[dict[str, str]], Awaitable[None]],
        warn: Callable[[str], Awaitable[None]],
    ) -> list[dict[str, str]]:
        await release.wait()
        await warn("An interface is unavailable.")
        return []

    monkeypatch.setattr(server, "_web_discovery", discover)
    startup = server._StartupDiscovery(registry)
    warn = AsyncMock()
    waiting = asyncio.create_task(startup.results(AsyncMock(), warn))
    await asyncio.sleep(0)
    release.set()
    assert await waiting == []
    warn.assert_awaited_once_with("An interface is unavailable.")


async def test_startup_discovery_is_shared_and_authorized_per_socket(
    aiohttp_client: Callable[..., Any],
    registry: DeviceRegistry,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Replay and stream a startup scan without authorizing provisional results."""
    first = {"name": "First", "host": "192.0.2.2", "macaddress": "00:40:8c:01:02:03"}
    second = {"name": "Second", "host": "192.0.2.3", "macaddress": "00:40:8c:01:02:04"}
    started, next_device, published, finish = (asyncio.Event() for _ in range(4))

    async def discover(
        *, on_device: Callable[[dict[str, str]], Awaitable[None]]
    ) -> list[dict[str, str]]:
        await on_device(first)
        started.set()
        await next_device.wait()
        await on_device(second)
        published.set()
        await finish.wait()
        return [first, second]

    mock = AsyncMock(side_effect=discover)
    monkeypatch.setattr(server, "discover_axis_devices", mock)
    client = await aiohttp_client(
        server.create_app(registry, TOKEN, 8765, startup_discovery=True)
    )
    await asyncio.wait_for(started.wait(), 2)
    socket = await connect(client)
    other = await connect(client)
    await socket.send_json({"id": 2, "type": "devices/discover", "stream": True})
    await other.send_json({"id": 3, "type": "devices/discover", "stream": True})
    assert (await socket.receive_json(timeout=2))["device"] == first
    assert (await other.receive_json(timeout=2))["device"] == first
    args = {
        "type": "devices/test-connection",
        "host": first["host"],
        "username": "root",
        "password": "test-password",
        "verify_ssl": True,
    }
    assert (await command(other, **args))["error"]["code"] == "validation"
    await socket.close()
    next_device.set()
    await asyncio.wait_for(published.wait(), 2)
    assert (await other.receive_json(timeout=2))["device"] == second
    identify = AsyncMock(
        return_value=DeviceRecord("NEW", ConnectionSettings("x", "x", "x"))
    )
    monkeypatch.setattr(server.operations, "identify", identify)
    finish.set()
    assert await other.receive_json(timeout=2) == {"id": 3, "result": [first, second]}
    assert await command(other, **args) == {"id": 1, "result": "NEW"}
    mock.assert_awaited_once()
    late = await connect(client)
    assert (await command(late, **args))["error"]["code"] == "validation"
    await late.send_json({"id": 4, "type": "devices/discover", "stream": True})
    assert (await late.receive_json(timeout=2))["device"] == first
    assert (await late.receive_json(timeout=2))["device"] == second
    assert await late.receive_json(timeout=2) == {"id": 4, "result": [first, second]}
    nonstream = await connect(client)
    assert await command(nonstream, type="devices/discover") == {
        "id": 1,
        "result": [first, second],
    }
    mock.assert_awaited_once()
    await nonstream.close()
    await late.send_json({"id": 5, "type": "devices/discover", "stream": True})
    assert (await late.receive_json(timeout=2))["device"] == first
    assert (await late.receive_json(timeout=2))["device"] == second
    assert await late.receive_json(timeout=2) == {"id": 5, "result": [first, second]}
    assert mock.await_count == 2
    await late.close()
    await other.close()


async def test_startup_discovery_expires_and_manual_scans_are_fresh(
    aiohttp_client: Callable[..., Any],
    registry: DeviceRegistry,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Completed old startup results are not reused, nor are manual scans."""
    startup_done = asyncio.Event()
    calls = 0

    async def discover(
        *, on_device: Callable[[dict[str, str]], Awaitable[None]]
    ) -> list[dict[str, str]]:
        nonlocal calls
        calls += 1
        entry = {
            "name": str(calls),
            "host": "192.0.2.2",
            "macaddress": "00:40:8c:01:02:03",
        }
        if calls == 1:
            startup_done.set()
        await on_device(entry)
        return [entry]

    monkeypatch.setattr(server, "discover_axis_devices", discover)
    monkeypatch.setattr(server, "STARTUP_DISCOVERY_MAX_AGE", 0.0)
    client = await aiohttp_client(
        server.create_app(registry, TOKEN, 8765, startup_discovery=True)
    )
    await asyncio.wait_for(startup_done.wait(), 2)
    socket = await connect(client)
    for expected in ("2", "3"):
        await socket.send_json({"id": 2, "type": "devices/discover", "stream": True})
        assert (await socket.receive_json(timeout=2))["device"]["name"] == expected
        assert (await socket.receive_json(timeout=2))["result"][0]["name"] == expected
    await socket.close()


async def test_startup_discovery_failure_and_shutdown(
    aiohttp_client: Callable[..., Any],
    registry: DeviceRegistry,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Report startup failures and cancel a running scan on application cleanup."""
    failure = AsyncMock(side_effect=OperationError("failed", kind=ErrorKind.CONNECTION))
    monkeypatch.setattr(server, "discover_axis_devices", failure)
    client = await aiohttp_client(
        server.create_app(registry, TOKEN, 8765, startup_discovery=True)
    )
    socket = await connect(client)
    response = await command(socket, type="devices/discover", stream=True)
    assert response["error"]["code"] == "connection"
    assert "Startup device discovery failed" in caplog.text
    await client.close()

    started, cancelled = asyncio.Event(), asyncio.Event()

    async def running(
        *, on_device: Callable[[dict[str, str]], Awaitable[None]]
    ) -> list[dict[str, str]]:
        started.set()
        try:
            await asyncio.Event().wait()
        finally:
            cancelled.set()
        return []

    monkeypatch.setattr(server, "discover_axis_devices", running)
    client = await aiohttp_client(
        server.create_app(registry, TOKEN, 8765, startup_discovery=True)
    )
    await asyncio.wait_for(started.wait(), 2)
    await client.close()
    assert cancelled.is_set()


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


@pytest.mark.parametrize(
    ("options", "port", "proto"),
    [({}, 0, "https"), ({"port": 8080, "web_proto": "http"}, 8080, "http")],
)
async def test_save_authenticates_discovered_target_without_overwriting(
    client: TestClient,
    registry: DeviceRegistry,
    monkeypatch: pytest.MonkeyPatch,
    wire_results: dict[str, object],
    options: dict[str, object],
    port: int,
    proto: str,
) -> None:
    """Require the current socket's scan and use live identity, not advertised serial."""
    monkeypatch.setattr(
        server,
        "discover_axis_devices",
        AsyncMock(return_value=wire_results["devices/discover"]),
    )

    async def identify(settings: ConnectionSettings) -> DeviceRecord:
        return DeviceRecord("LIVE-SERIAL", settings, model="Live model")

    login = AsyncMock(side_effect=identify)
    monkeypatch.setattr(server.operations, "identify", login)
    args = {
        "type": "devices/save",
        "host": "192.0.2.2",
        "username": "root",
        "password": "device-test-password",
        "alias": "Entrance",
        "verify_ssl": False,
        **options,
    }
    socket = await connect(client)
    assert (await command(socket, **args))["error"]["code"] == "validation"
    await command(socket, type="devices/discover")
    other_socket = await connect(client)
    assert (await command(other_socket, **args))["error"]["code"] == "validation"
    await other_socket.close()
    assert (await command(socket, **(args | {"verify_ssl": "false"})))["error"][
        "code"
    ] == "invalid_request"
    for invalid_connection, code in (
        ({"port": True}, "invalid_request"),
        ({"port": 65536}, "storage"),
        ({"web_proto": "ftp"}, "storage"),
        ({"web_proto": None}, "invalid_request"),
    ):
        response = await command(socket, **(args | invalid_connection))
        assert response["error"]["code"] == code
    login.assert_not_awaited()

    assert await command(socket, **args) == {"id": 1, "result": "LIVE-SERIAL"}
    record = registry.resolve("LIVE-SERIAL")
    assert record.alias == "Entrance"
    assert record.model == "Live model"
    assert record.discovery is not None
    assert record.discovery.macaddress == "00:40:8c:01:02:03"
    assert record.config == ConnectionSettings(
        "192.0.2.2", "root", "device-test-password", port=port, web_proto=proto
    )
    login.assert_awaited_once_with(record.config)
    assert (await command(socket, **(args | {"password": "replacement"})))["error"] == {
        "code": "storage",
        "message": "This device is already saved.",
    }
    assert registry.resolve("LIVE-SERIAL") == record
    assert "device-test-password" not in str(await command(socket, type="devices/list"))
    await socket.close()


async def test_connection_checks_do_not_save(
    client: TestClient,
    registry: DeviceRegistry,
    monkeypatch: pytest.MonkeyPatch,
    wire_results: dict[str, object],
) -> None:
    """Test discovered and saved connections using the same guards as saving."""
    monkeypatch.setattr(
        server,
        "discover_axis_devices",
        AsyncMock(return_value=wire_results["devices/discover"]),
    )
    before = registry.load()
    original = before["SERIAL"]
    config = original.config
    identify = AsyncMock(return_value=original)
    monkeypatch.setattr(server.operations, "identify", identify)
    socket = await connect(client)
    args = {
        "host": config.host,
        "port": config.port,
        "username": config.username,
        "password": "",
        "web_proto": config.web_proto,
        "verify_ssl": config.verify_ssl,
    }
    saved = args | {"type": "device/test-connection", "device": original.serial}
    response = await command(socket, **(saved | {"port": "443"}))
    assert response["error"]["code"] == "invalid_request"
    response = await command(socket, **(saved | {"host": "192.0.2.2"}))
    assert response["error"]["code"] == "validation"
    discovered = args | {
        "type": "devices/test-connection",
        "host": "192.0.2.2",
        "password": "test-password",
    }
    assert (await command(socket, **discovered))["error"]["code"] == "validation"
    identify.assert_not_awaited()

    assert await command(socket, **saved) == {"id": 1, "result": "SERIAL"}
    identify.assert_awaited_once_with(config)
    identify.return_value = DeviceRecord("OTHER", config)
    assert (await command(socket, **saved))["error"]["code"] == "conflict"
    await command(socket, type="devices/discover")
    assert await command(socket, **discovered) == {"id": 1, "result": "OTHER"}
    assert registry.load() == before
    await socket.close()


async def test_save_failure_does_not_change_registry(
    client: TestClient,
    registry: DeviceRegistry,
    monkeypatch: pytest.MonkeyPatch,
    wire_results: dict[str, object],
) -> None:
    """An HTTPS failure leaves the device unsaved and informs the user."""
    monkeypatch.setattr(
        server,
        "discover_axis_devices",
        AsyncMock(return_value=wire_results["devices/discover"]),
    )
    monkeypatch.setattr(
        server.operations,
        "identify",
        AsyncMock(
            side_effect=OperationError("Unavailable.", kind=ErrorKind.CONNECTION)
        ),
    )
    socket = await connect(client)
    await command(socket, type="devices/discover")
    result = await command(
        socket,
        type="devices/save",
        host="192.0.2.2",
        username="root",
        password="device-test-password",
        alias="",
        verify_ssl=True,
    )
    assert result["error"]["code"] == "connection"
    assert "port, protocol" in result["error"]["message"]
    assert list(registry.load()) == ["SERIAL"]
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
            doc_link="https://developer.axis.com/vapix/network-video/light-control/",
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
    await server._respond(socket, registry, {"id": 1, "type": "devices/list"}, {})
    socket.send_json.assert_awaited_once()


async def test_only_authenticated_clients_prevent_browser_launch(
    aiohttp_client: Callable[..., Any], registry: DeviceRegistry
) -> None:
    """A rejected connection must not count as an existing authorized tab."""
    event = server.Event()
    client = await aiohttp_client(server.create_app(registry, TOKEN, 8765, event))
    invalid = await client.ws_connect("/api/websocket", headers=HEADERS)
    await invalid.send_json({"token": "wrong"})
    await invalid.receive()
    assert not event.is_set()
    socket = await connect(client)
    assert event.is_set()
    await socket.close()


async def test_existing_tab_reconnects_after_server_restart(
    aiohttp_client: Callable[..., Any],
    registry: DeviceRegistry,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A retained token authenticates the tab after restart without opening a browser."""
    token = registry.web_access_token()
    first = await aiohttp_client(server.create_app(registry, token, 8765))
    socket = await first.ws_connect("/api/websocket", headers=HEADERS)
    await socket.send_json({"token": token})
    assert (await socket.receive_json())["type"] == "ready"
    await socket.close()
    await first.close()

    event = server.Event()
    second_token = DeviceRegistry(registry.path).web_access_token()
    second = await aiohttp_client(
        server.create_app(registry, second_token, 8765, event)
    )
    browser = MagicMock()
    monkeypatch.setattr(server, "_open_browser", browser)
    waiting = asyncio.create_task(
        asyncio.to_thread(
            server._open_if_no_client, "http://127.0.0.1:8765/#test", event
        )
    )
    socket = await second.ws_connect("/api/websocket", headers=HEADERS)
    await socket.send_json({"token": token})
    assert (await socket.receive_json())["type"] == "ready"
    await asyncio.wait_for(waiting, timeout=1)
    browser.assert_not_called()
    await socket.close()


@pytest.mark.parametrize("connected", [True, False])
def test_open_browser_only_without_reconnected_client(
    monkeypatch: pytest.MonkeyPatch, connected: bool
) -> None:
    """Wait for a verified client before deciding whether to open the link."""
    event = MagicMock()
    event.wait.return_value = connected
    browser = MagicMock()
    monkeypatch.setattr(server, "_open_browser", browser)
    server._open_if_no_client("http://127.0.0.1:8765/#test-token", event)
    event.wait.assert_called_once_with(server.BROWSER_RECONNECT_WAIT)
    if connected:
        browser.assert_not_called()
    else:
        browser.assert_called_once()


def test_server_starts_only_on_loopback(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    """Only after listening, print the private link and open it in a browser."""
    browser_thread = MagicMock()
    thread_factory = MagicMock(return_value=browser_thread)
    monkeypatch.setattr(server, "Thread", thread_factory)
    runner = MagicMock(side_effect=lambda *args, **kwargs: kwargs["print"]("listening"))
    monkeypatch.setattr(server.web, "run_app", runner)
    monkeypatch.setattr(
        server.DeviceRegistry, "web_access_token", lambda _: "temporary-token"
    )
    server.run_server(tmp_path / "test", 8766)
    assert "http://127.0.0.1:8766/#temporary-token" in capsys.readouterr().out
    assert runner.call_args.kwargs["host"] == "127.0.0.1"
    assert runner.call_args.kwargs["port"] == 8766
    event = thread_factory.call_args.kwargs["args"][1]
    assert isinstance(event, server.Event)
    thread_factory.assert_called_once_with(
        target=server._open_if_no_client,
        args=("http://127.0.0.1:8766/#temporary-token", event),
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
