"""Serve a local web interface for discovering, saving, and reading Axis devices."""

import asyncio
from datetime import UTC, datetime
from importlib.resources import files
import json
import logging
import secrets
import sys
from threading import Thread
from typing import TYPE_CHECKING, Any
import webbrowser

from aiohttp import WSMsgType, web

from axis.application import operations
from axis.application.discovery import discover_axis_devices
from axis.application.errors import ErrorKind, OperationError, StorageError
from axis.application.records import ConnectionSettings, DiscoverySnapshot
from axis.application.storage import DeviceRegistry

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable
    from pathlib import Path

LOGGER = logging.getLogger(__name__)
MAX_MESSAGE_SIZE = 16384
MAX_PENDING = 8
COMMAND_TIMEOUT = 60


async def _save_discovered(
    registry: DeviceRegistry,
    message: dict[str, Any],
    discovered: dict[str, DiscoverySnapshot],
) -> str:
    host = message.get("host")
    username = message.get("username")
    password = message.get("password")
    alias = message.get("alias")
    verify_ssl = message.get("verify_ssl")
    if (
        not isinstance(host, str)
        or not isinstance(username, str)
        or not isinstance(password, str)
        or not password
        or not isinstance(alias, str)
        or type(verify_ssl) is not bool
    ):
        raise ValueError
    snapshot = discovered.get(host)
    if snapshot is None:
        msg = "Scan the local network and select a device before saving."
        raise OperationError(msg, kind=ErrorKind.VALIDATION)
    record = await operations.identify(
        ConnectionSettings(
            host=snapshot.host,
            username=username.strip(),
            password=password,
            web_proto="https",
            verify_ssl=verify_ssl,
        )
    )
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
    if command == "devices/save":
        return await _save_discovered(registry, message, discovered)
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
        elif message.get("type") == "devices/save" and err.kind == ErrorKind.CONNECTION:
            error_message = "Cannot reach the device over HTTPS. Check the discovered address and certificate settings."
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
