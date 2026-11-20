"""Serve a local web interface for discovering, saving, and reading Axis devices."""

import asyncio
from dataclasses import replace
from datetime import UTC, datetime
from importlib.resources import files
import json
import logging
import re
import secrets
import sys
from threading import Event, Thread
from typing import TYPE_CHECKING, Any
import webbrowser

from aiohttp import WSMsgType, web

from axis.application import operations
from axis.application.discovery import DiscoveredDevice, discover_axis_devices
from axis.application.errors import ErrorKind, OperationError, StorageError
from axis.application.records import ConnectionSettings, DeviceRecord, DiscoverySnapshot
from axis.application.storage import DeviceRegistry
from axis.web.network import NetworkInterface, network_interfaces

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable
    from pathlib import Path

LOGGER = logging.getLogger(__name__)
MAX_MESSAGE_SIZE = 16384
MAX_PENDING = 8
COMMAND_TIMEOUT = 60
BROWSER_RECONNECT_WAIT = 3.0
STARTUP_DISCOVERY_MAX_AGE = 15.0


class _StartupDiscovery:
    """Share the initial scan with authenticated pages without sharing their sessions."""

    def __init__(self, registry: DeviceRegistry) -> None:
        self.started = datetime.now(UTC)
        self.started_at = asyncio.get_running_loop().time()
        self.selected = registry.web_discovery_interfaces()
        self.entries: dict[str, DiscoveredDevice] = {}
        self.warning = ""
        self.subscribers: set[asyncio.Queue[DiscoveredDevice | str | None]] = set()
        self.task = asyncio.create_task(
            _web_discovery(self.selected, self.publish, self.publish_warning)
        )
        self.task.add_done_callback(self.finished)

    async def publish(self, entry: DiscoveredDevice) -> None:
        self.entries[entry["host"]] = entry
        for subscriber in self.subscribers:
            subscriber.put_nowait(entry)

    async def publish_warning(self, warning: str) -> None:
        self.warning = warning
        for subscriber in self.subscribers:
            subscriber.put_nowait(warning)

    def finished(self, task: asyncio.Task[list[DiscoveredDevice]]) -> None:
        if not task.cancelled() and task.exception() is not None:
            LOGGER.warning("Startup device discovery failed.")
        for subscriber in self.subscribers:
            subscriber.put_nowait(None)

    def fresh(self) -> bool:
        return (
            not self.task.done()
            or asyncio.get_running_loop().time() - self.started_at
            <= STARTUP_DISCOVERY_MAX_AGE
        )

    async def results(
        self,
        publish: Callable[[DiscoveredDevice], Awaitable[None]],
        warn: Callable[[str], Awaitable[None]],
    ) -> list[DiscoveredDevice]:
        queue: asyncio.Queue[DiscoveredDevice | str | None] = asyncio.Queue()
        self.subscribers.add(queue)
        try:
            if self.warning:
                await warn(self.warning)
            for entry in list(self.entries.values()):
                await publish(entry)
            if not self.task.done():
                while (queued := await queue.get()) is not None:
                    if isinstance(queued, str):
                        await warn(queued)
                    else:
                        await publish(queued)
            return await asyncio.shield(self.task)
        finally:
            self.subscribers.discard(queue)


def _initial_scan_for_request(
    startup: _StartupDiscovery | None,
    first: bool,
    message: dict[str, Any],
) -> _StartupDiscovery | None:
    if (
        first
        and message.get("type") == "devices/discover"
        and startup is not None
        and startup.fresh()
    ):
        return startup
    return None


async def _web_discovery(
    selected: list[str] | None,
    publish: Callable[[DiscoveredDevice], Awaitable[None]] | None,
    warn: Callable[[str], Awaitable[None]],
) -> list[DiscoveredDevice]:
    if selected is None:
        return (
            await discover_axis_devices(on_device=publish)
            if publish is not None
            else await discover_axis_devices()
        )
    available = {item.name: item for item in network_interfaces()}
    addresses = [
        address
        for name in selected
        if name in available and available[name].available
        for address in available[name].addresses
    ]
    unavailable = [
        name
        for name in selected
        if name not in available or not available[name].available
    ]
    if unavailable:
        warning = "Selected interfaces are down or unavailable: " + ", ".join(
            unavailable
        )
        LOGGER.warning("%s", warning)
        await warn(warning)
    if not addresses:
        msg = "No selected network interface is up with an IPv4 address."
        raise OperationError(msg, kind=ErrorKind.VALIDATION)
    return await discover_axis_devices(interfaces=addresses, on_device=publish)


def _server_settings(
    selected: list[str] | None, interfaces: list[NetworkInterface]
) -> dict[str, object]:
    known = {item.name for item in interfaces}
    return {
        "selected": selected,
        "interfaces": [
            {
                "name": item.name,
                "label": item.label,
                "addresses": item.addresses,
                "up": item.up,
            }
            for item in interfaces
        ]
        + [
            {"name": name, "label": name, "addresses": [], "up": None}
            for name in selected or []
            if name not in known
        ],
    }


def _configure_server(registry: DeviceRegistry, message: dict[str, Any]) -> object:
    if message["type"] == "server/settings":
        return _server_settings(
            registry.web_discovery_interfaces(), network_interfaces()
        )
    selected = message.get("interfaces")
    if "interfaces" not in message or (
        selected is not None
        and (
            not isinstance(selected, list)
            or not selected
            or any(not isinstance(name, str) or not name.strip() for name in selected)
            or len(set(selected)) != len(selected)
        )
    ):
        raise ValueError
    interfaces = network_interfaces()
    available = {item.name for item in interfaces}
    available.update(registry.web_discovery_interfaces() or [])
    if selected is not None and not set(selected) <= available:
        raise ValueError
    registry.update_web_discovery_interfaces(selected)
    return _server_settings(selected, interfaces)


async def _configure_saved(registry: DeviceRegistry, message: dict[str, Any]) -> object:
    identifier = message.get("device")
    if not isinstance(identifier, str) or not identifier:
        raise ValueError
    original = registry.resolve(identifier)
    if message["type"] == "device/settings":
        return {
            "device": operations.normalize_payload(original.summary()),
            "username": original.config.username,
        }

    host = message.get("host")
    port = message.get("port")
    username = message.get("username")
    password = message.get("password")
    proto = message.get("web_proto")
    verify_ssl = message.get("verify_ssl")
    if (
        not isinstance(host, str)
        or not isinstance(username, str)
        or not isinstance(password, str)
        or not isinstance(proto, str)
        or type(port) is not int
        or type(verify_ssl) is not bool
    ):
        raise ValueError
    config = replace(
        original.config,
        host=host.strip(),
        port=port,
        username=username.strip(),
        password=password or original.config.password,
        web_proto=proto,
        verify_ssl=verify_ssl,
    )
    if message["type"] == "device/test-connection":
        await _verify_settings(original, config, password)
        return original.serial

    alias = message.get("alias")
    if not isinstance(alias, str):
        raise ValueError
    alias = alias.strip()
    default_name = (
        (original.discovery.name.strip() if original.discovery else "")
        or original.model.strip()
        or original.serial
    )
    if alias == default_name:
        alias = ""
    replace(original, alias=alias, config=config)
    changed = config != original.config
    if changed:
        await _verify_settings(original, config, password)
    record = registry.update_settings(original, config, alias)
    return {
        "device": operations.normalize_payload(record.summary()),
        "connection_changed": changed,
    }


async def _verify_settings(
    original: DeviceRecord, config: ConnectionSettings, password: str
) -> None:
    if not re.fullmatch(r"[a-zA-Z0-9._-]+|\[[0-9a-fA-F:.]+\]", config.host):
        msg = "Enter a hostname or IP address without a scheme, port, or path."
        raise OperationError(msg, kind=ErrorKind.VALIDATION)
    previous = original.config
    if not password and (
        (config.host, config.port, config.web_proto)
        != (previous.host, previous.port, previous.web_proto)
        or (previous.verify_ssl and not config.verify_ssl)
    ):
        msg = "Re-enter the device password to change its address, port, protocol, or relax certificate verification."
        raise OperationError(msg, kind=ErrorKind.VALIDATION)
    identified = await operations.identify(config)
    if identified.serial != original.serial:
        msg = "The new settings reached a different device. Your saved settings were not changed."
        raise OperationError(msg, kind=ErrorKind.CONFLICT)


async def _connect_discovered(
    registry: DeviceRegistry,
    message: dict[str, Any],
    discovered: dict[str, DiscoverySnapshot],
) -> str:
    host = message.get("host")
    username = message.get("username")
    password = message.get("password")
    testing = message["type"] == "devices/test-connection"
    alias = "" if testing else message.get("alias")
    verify_ssl = message.get("verify_ssl")
    port = message.get("port", 0)
    proto = message.get("web_proto", "https")
    if (
        not isinstance(host, str)
        or not isinstance(username, str)
        or not isinstance(password, str)
        or not password
        or not isinstance(alias, str)
        or type(verify_ssl) is not bool
        or type(port) is not int
        or not isinstance(proto, str)
    ):
        raise ValueError
    snapshot = discovered.get(host)
    if snapshot is None:
        msg = "Scan the local network and select a device first."
        raise OperationError(msg, kind=ErrorKind.VALIDATION)
    record = await operations.identify(
        ConnectionSettings(
            host=snapshot.host,
            username=username.strip(),
            password=password,
            port=port,
            web_proto=proto,
            verify_ssl=verify_ssl,
        )
    )
    if testing:
        return record.serial
    record.alias = alias.strip()
    record.discovery = snapshot
    registry.upsert(record, create_only=True)
    return record.serial


async def _execute(
    socket: web.WebSocketResponse,
    registry: DeviceRegistry,
    message: dict[str, Any],
    discovered: dict[str, DiscoverySnapshot],
    startup: _StartupDiscovery | None = None,
) -> object:
    command = message.get("type")
    if command == "devices/list":
        return [
            operations.normalize_payload(record.summary())
            for record in registry.load().values()
        ]
    if command in ("server/settings", "server/configure"):
        return _configure_server(registry, message)
    if command == "devices/discover":
        discovered.clear()
        selected = registry.web_discovery_interfaces()
        if startup is not None and startup.selected != selected:
            startup = None
        started = startup.started if startup is not None else datetime.now(UTC)

        async def publish(entry: DiscoveredDevice) -> None:
            if message.get("stream") is True:
                await socket.send_json(
                    {"id": message["id"], "type": "discovery/device", "device": entry}
                )

        async def warn(warning: str) -> None:
            if message.get("stream") is True:
                await socket.send_json(
                    {
                        "id": message["id"],
                        "type": "discovery/warning",
                        "message": warning,
                    }
                )

        if startup is not None:
            results = await startup.results(publish, warn)
        else:
            results = await _web_discovery(
                selected,
                publish if message.get("stream") is True else None,
                warn,
            )
        snapshots = {
            entry["host"]: DiscoverySnapshot(
                host=entry["host"],
                last_seen=started,
                macaddress=entry["macaddress"],
                name=entry["name"],
            )
            for entry in results
        }
        discovered.clear()
        discovered.update(snapshots)
        return results
    if command in ("devices/save", "devices/test-connection"):
        return await _connect_discovered(registry, message, discovered)
    if command in ("device/settings", "device/configure", "device/test-connection"):
        return await _configure_saved(registry, message)
    return await _read_saved(registry, command, message)


async def _read_saved(
    registry: DeviceRegistry, command: object, message: dict[str, Any]
) -> object:
    identifier = message.get("device")
    if (
        not isinstance(command, str)
        or command
        not in {
            "device/health",
            "device/apis",
            "device/interfaces",
            "device/read",
        }
        or not isinstance(identifier, str)
        or not identifier
    ):
        raise ValueError
    record = registry.resolve(identifier)
    if command == "device/health":
        snapshot = await operations.read_health(record)
        return operations.normalize_payload(snapshot)
    if command == "device/apis":
        return await operations.list_apis(record)
    if command == "device/interfaces":
        return await operations.list_interfaces(record)
    name = message.get("name")
    if not isinstance(name, str) or not name:
        raise ValueError
    return await operations.read_interface(record, name)


async def _respond(
    socket: web.WebSocketResponse,
    registry: DeviceRegistry,
    message: dict[str, Any],
    discovered: dict[str, DiscoverySnapshot],
    startup: _StartupDiscovery | None = None,
) -> None:
    request_id = message["id"]
    is_discovery = message.get("type") == "devices/discover"
    try:
        async with asyncio.timeout(COMMAND_TIMEOUT):
            result = await _execute(socket, registry, message, discovered, startup)
    except StorageError as err:
        response = {"id": request_id, "error": {"code": "storage", "message": str(err)}}
    except OperationError as err:
        error_message = str(err)
        if is_discovery and err.kind != ErrorKind.VALIDATION:
            error_message = "Device discovery failed. Check this computer's local network access and try again."
        elif (
            message.get("type")
            in (
                "devices/save",
                "device/configure",
                "devices/test-connection",
                "device/test-connection",
            )
            and err.kind == ErrorKind.CONNECTION
        ):
            error_message = "Cannot reach the device. Check the address, port, protocol, and certificate settings."
        elif err.kind == ErrorKind.CONNECTION and message.get("type") not in (
            "server/settings",
            "server/configure",
        ):
            error_message = (
                "Cannot reach the device. Check that it is powered on, that this "
                "computer can reach its network, and that its saved address and port are correct."
            )
        elif err.kind == ErrorKind.TIMEOUT:
            error_message = "The device did not respond in time. Check its connection and try again."
        response = {
            "id": request_id,
            "error": {"code": err.kind.value, "message": error_message},
        }
    except ValueError:
        response = {
            "id": request_id,
            "error": {
                "code": "invalid_request",
                "message": "Invalid command or arguments.",
            },
        }
    except TimeoutError:
        response = {
            "id": request_id,
            "error": {
                "code": "timeout",
                "message": (
                    "Device discovery timed out. Try again."
                    if is_discovery
                    else "The device did not respond in time. Check its connection and try again."
                ),
            },
        }
    except Exception:  # noqa: BLE001 - prevent transport exceptions exposing secrets
        LOGGER.error("Unexpected web operation failure.")
        response = {
            "id": request_id,
            "error": {"code": "internal", "message": "Device request failed."},
        }
    else:
        response = {"id": request_id, "result": result}
    if not socket.closed:
        try:
            await socket.send_json(response)
        except ConnectionError:
            LOGGER.debug("Web client disconnected before receiving a response.")


def create_app(
    registry: DeviceRegistry,
    token: str,
    port: int,
    client_connected: Event | None = None,
    *,
    startup_discovery: bool = False,
) -> web.Application:
    """Create a loopback-only web application."""
    app = web.Application(client_max_size=MAX_MESSAGE_SIZE)
    authority = f"127.0.0.1:{port}"
    origin = f"http://{authority}"

    sockets: set[web.WebSocketResponse] = set()
    initial: _StartupDiscovery | None = None

    async def start_discovery(application: web.Application) -> None:
        nonlocal initial
        initial = _StartupDiscovery(registry)

    async def stop_discovery(application: web.Application) -> None:
        if initial is not None:
            initial.task.cancel()
            await asyncio.gather(initial.task, return_exceptions=True)

    if startup_discovery:
        app.on_startup.append(start_discovery)
        app.on_cleanup.append(stop_discovery)

    @web.middleware
    async def guard(
        request: web.Request,
        handler: Callable[[web.Request], Awaitable[web.StreamResponse]],
    ) -> web.StreamResponse:
        if request.host != authority:
            raise web.HTTPForbidden
        response = await handler(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Content-Security-Policy"] = (
            f"default-src 'self'; connect-src 'self' ws://{authority}; "
            "style-src 'self' 'unsafe-inline'; object-src 'none'; "
            "base-uri 'none'; frame-ancestors 'none'; form-action 'none'"
        )
        return response

    app.middlewares.append(guard)

    async def index(request: web.Request) -> web.Response:
        return web.Response(
            body=files("axis.web").joinpath("static", "index.html").read_bytes(),
            content_type="text/html",
        )

    async def script(request: web.Request) -> web.Response:
        return web.Response(
            body=files("axis.web").joinpath("static", "app.js").read_bytes(),
            content_type="application/javascript",
        )

    async def websocket(request: web.Request) -> web.WebSocketResponse:
        if request.headers.get("Origin") != origin:
            raise web.HTTPForbidden
        socket = web.WebSocketResponse(max_msg_size=MAX_MESSAGE_SIZE, heartbeat=30)
        await socket.prepare(request)
        sockets.add(socket)
        pending: dict[int, asyncio.Task[None]] = {}
        discovered: dict[str, DiscoverySnapshot] = {}
        first_discovery = True

        def forget(task: asyncio.Task[None]) -> None:
            pending.pop(int(task.get_name()), None)

        try:
            try:
                async with asyncio.timeout(5):
                    auth = await socket.receive_json()
            except TimeoutError, ValueError, TypeError:
                await socket.close(code=1008, message=b"Authentication required")
                return socket
            supplied = auth.get("token") if isinstance(auth, dict) else None
            if (
                not isinstance(supplied, str)
                or not supplied.isascii()
                or not secrets.compare_digest(supplied, token)
            ):
                await socket.close(code=1008, message=b"Authentication required")
                return socket
            await socket.send_json({"type": "ready", "version": 1})
            if client_connected is not None:
                client_connected.set()
            async for incoming in socket:
                if incoming.type != WSMsgType.TEXT:
                    await socket.close(code=1003, message=b"Text messages required")
                    break
                try:
                    message = json.loads(incoming.data)
                except ValueError:
                    await socket.close(code=1008, message=b"Invalid message")
                    break
                if (
                    not isinstance(message, dict)
                    or type(message.get("id")) is not int
                    or message["id"] < 0
                ):
                    await socket.close(code=1008, message=b"Invalid message")
                    break
                if message["id"] in pending:
                    await socket.close(code=1008, message=b"Duplicate request ID")
                    break
                if len(pending) >= MAX_PENDING:
                    await socket.send_json(
                        {
                            "id": message["id"],
                            "error": {"code": "busy", "message": "Too many requests."},
                        }
                    )
                    continue
                startup = _initial_scan_for_request(initial, first_discovery, message)
                first_discovery = (
                    first_discovery and message.get("type") != "devices/discover"
                )
                task = asyncio.create_task(
                    _respond(socket, registry, message, discovered, startup),
                    name=str(message["id"]),
                )
                pending[message["id"]] = task
                task.add_done_callback(forget)
        finally:
            tasks = tuple(pending.values())
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
            sockets.discard(socket)
        return socket

    async def shutdown(application: web.Application) -> None:
        if client_connected is not None:
            client_connected.set()
        for socket in tuple(sockets):
            await socket.close(code=1001, message=b"Server shutting down")

    app.router.add_get("/", index)
    app.router.add_get("/app.js", script)
    app.router.add_get("/api/websocket", websocket)
    app.on_shutdown.append(shutdown)
    return app


def _open_browser(url: str) -> None:
    try:
        opened = webbrowser.open(url)
    except OSError, webbrowser.Error:
        opened = False
    if not opened:
        print("Could not open a browser; use the private URL above.", file=sys.stderr)  # noqa: T201


def _open_if_no_client(url: str, client_connected: Event) -> None:
    if not client_connected.wait(BROWSER_RECONNECT_WAIT):
        _open_browser(url)


def run_server(config_path: Path, port: int) -> None:
    """Run the local server and open its private URL if no existing tab connects."""
    registry = DeviceRegistry(config_path)
    token = registry.web_access_token()
    client_connected = Event()
    url = f"http://127.0.0.1:{port}/#{token}"

    def on_listening(_message: str) -> None:
        print(f"Open this private URL in your browser: {url}", flush=True)  # noqa: T201
        Thread(
            target=_open_if_no_client, args=(url, client_connected), daemon=True
        ).start()

    web.run_app(
        create_app(registry, token, port, client_connected, startup_discovery=True),
        host="127.0.0.1",
        port=port,
        print=on_listening,
    )
