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
from threading import Thread
from typing import TYPE_CHECKING, Any
import webbrowser

from aiohttp import WSMsgType, web

from axis.application import operations
from axis.application.discovery import discover_axis_devices
from axis.application.errors import ErrorKind, OperationError, StorageError
from axis.application.records import ConnectionSettings, DeviceRecord, DiscoverySnapshot
from axis.application.storage import DeviceRegistry

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable
    from pathlib import Path

LOGGER = logging.getLogger(__name__)
MAX_MESSAGE_SIZE = 16384
MAX_PENDING = 8
COMMAND_TIMEOUT = 60


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
    registry: DeviceRegistry,
    message: dict[str, Any],
    discovered: dict[str, DiscoverySnapshot],
) -> object:
    command = message.get("type")
    if command == "devices/list":
        return [
            operations.normalize_payload(record.summary())
            for record in registry.load().values()
        ]
    if command == "devices/discover":
        discovered.clear()
        started = datetime.now(UTC)
        results = await discover_axis_devices()
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
) -> None:
    request_id = message["id"]
    is_discovery = message.get("type") == "devices/discover"
    try:
        async with asyncio.timeout(COMMAND_TIMEOUT):
            result = await _execute(registry, message, discovered)
    except StorageError as err:
        response = {"id": request_id, "error": {"code": "storage", "message": str(err)}}
    except OperationError as err:
        error_message = str(err)
        if is_discovery:
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
        elif err.kind == ErrorKind.CONNECTION:
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


def create_app(registry: DeviceRegistry, token: str, port: int) -> web.Application:
    """Create a loopback-only web application."""
    app = web.Application(client_max_size=MAX_MESSAGE_SIZE)
    authority = f"127.0.0.1:{port}"
    origin = f"http://{authority}"

    sockets: set[web.WebSocketResponse] = set()

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
                task = asyncio.create_task(
                    _respond(socket, registry, message, discovered),
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


def run_server(config_path: Path, port: int) -> None:
    """Run the local server and open its private URL once it is listening."""
    token = secrets.token_urlsafe(32)
    url = f"http://127.0.0.1:{port}/#{token}"

    def on_listening(_message: str) -> None:
        print(f"Open this private URL in your browser: {url}", flush=True)  # noqa: T201
        Thread(target=_open_browser, args=(url,), daemon=True).start()

    web.run_app(
        create_app(DeviceRegistry(config_path), token, port),
        host="127.0.0.1",
        port=port,
        print=on_listening,
    )
