"""Serve a local web interface for discovering, saving, and reading Axis devices."""

import asyncio
from dataclasses import replace
from datetime import UTC, datetime
from importlib.resources import files
import json
import logging
import os
from pathlib import Path
import re
import secrets
import stat
import sys
from tempfile import TemporaryFile
from threading import Event, Thread
from typing import IO, TYPE_CHECKING, Any
from urllib.parse import unquote
import webbrowser

from aiohttp import WSMsgType, web

from axis.application import operations
from axis.application.acap_catalog import (
    MAX_PACKAGE_SIZE,
    Package,
    PackageError,
    inspect_package,
    open_package,
    scan_folder,
)
from axis.application.discovery import DiscoveredDevice, discover_axis_devices
from axis.application.errors import ErrorKind, OperationError, StorageError
from axis.application.records import ConnectionSettings, DeviceRecord, DiscoverySnapshot
from axis.application.storage import DeviceRegistry
from axis.web.network import NetworkInterface, network_interfaces

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable
LOGGER = logging.getLogger(__name__)
MAX_MESSAGE_SIZE = 16384
MAX_APPLICATION_PACKAGE_SIZE = 1024 * 1024 * 1024
MAX_APPLICATION_LICENSE_SIZE = 1024 * 1024
APPLICATION_UPLOAD_TIMEOUT = 1800
MAX_PENDING = 8
COMMAND_TIMEOUT = 60
BROWSER_RECONNECT_WAIT = 3.0
STARTUP_DISCOVERY_MAX_AGE = 15.0
ACAP_SCAN_INTERVAL = 300
MAX_FOLDER_ENTRIES = 10000


class _AcapCatalog:
    """Keep local package inspection off the event loop."""

    def __init__(self, registry: DeviceRegistry) -> None:
        self.registry = registry
        self.lock = asyncio.Lock()
        self.folder: str | None = None
        self.initialized = False
        self.result: dict[str, Any] = {"packages": [], "errors": [], "error": ""}
        self.pending: asyncio.Task[dict[str, Any]] | None = None

    async def scan(self) -> dict[str, Any]:
        for _ in range(2):
            if self.pending is None or self.pending.done():
                self.pending = asyncio.create_task(self._scan())
            result = await asyncio.shield(self.pending)
            if result["folder"] == self.registry.web_acap_folder():
                return result
        msg = "ACAP folder changed during scanning. Try again."
        raise OperationError(msg, kind=ErrorKind.CONFLICT)

    async def _scan(self) -> dict[str, Any]:
        async with self.lock:
            folder = self.registry.web_acap_folder()
            try:
                result = await asyncio.to_thread(scan_folder, folder)
            except PackageError as exc:
                LOGGER.warning("ACAP catalog scan failed: %s", exc)
                result = {"packages": [], "errors": [], "error": str(exc)}
            else:
                result["error"] = ""
            if self.registry.web_acap_folder() != folder:
                self.initialized = False
            else:
                self.folder = folder
                self.result = result
                self.initialized = True
            return {"folder": folder, **result}

    async def read(self) -> dict[str, Any]:
        if not self.initialized or self.folder != self.registry.web_acap_folder():
            return await self.scan()
        return {"folder": self.folder, **self.result}

    async def run(self) -> None:
        while True:
            try:
                await self.scan()
            except StorageError, OperationError:
                LOGGER.warning("ACAP catalog could not read server settings.")
            await asyncio.sleep(ACAP_SCAN_INTERVAL)


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
    selected: list[str] | None,
    interfaces: list[NetworkInterface],
    acap_folder: str | None,
) -> dict[str, object]:
    known = {item.name for item in interfaces}
    return {
        "selected": selected,
        "acap_folder": acap_folder,
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


def _browse_folders(path: str | None) -> dict[str, object]:
    """List directories on the server without reading their contents."""
    if path is not None and (
        not isinstance(path, str) or not path or not Path(path).is_absolute()
    ):
        raise ValueError
    try:
        folder = (Path(path) if path is not None else Path.home()).resolve(strict=True)
        directories = []
        with os.scandir(folder) as entries:
            for count, entry in enumerate(entries, start=1):
                if count > MAX_FOLDER_ENTRIES:
                    msg = "This folder contains too many entries to browse."
                    raise OperationError(msg, kind=ErrorKind.VALIDATION)
                if entry.is_dir():
                    directories.append(
                        {"name": entry.name, "path": str(folder / entry.name)}
                    )
    except (OSError, RuntimeError) as exc:
        msg = "Cannot browse this folder; check its path and permissions."
        raise OperationError(msg, kind=ErrorKind.VALIDATION) from exc
    directories.sort(key=lambda entry: entry["name"].casefold())
    return {
        "path": str(folder),
        "parent": str(folder.parent) if folder.parent != folder else None,
        "directories": directories,
    }


def _configure_server(registry: DeviceRegistry, message: dict[str, Any]) -> object:
    if message["type"] == "server/settings":
        return _server_settings(
            registry.web_discovery_interfaces(),
            network_interfaces(),
            registry.web_acap_folder(),
        )
    selected = message.get("interfaces")
    folder = message.get("acap_folder", registry.web_acap_folder())
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
    if folder is not None:
        if (
            not isinstance(folder, str)
            or not folder.strip()
            or not Path(folder).is_absolute()
        ):
            raise ValueError
        try:
            if not Path(folder).is_dir():
                msg = "ACAP folder does not exist or is not a directory."
                raise OperationError(msg, kind=ErrorKind.VALIDATION)
            with os.scandir(folder):
                pass
        except OSError as exc:
            msg = "Cannot read ACAP folder; check its path and permissions."
            raise OperationError(
                msg,
                kind=ErrorKind.VALIDATION,
            ) from exc
    registry.update_web_settings(selected, folder)
    return _server_settings(selected, interfaces, folder)


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


async def _execute(  # noqa: PLR0911 - commands have distinct responses
    socket: web.WebSocketResponse,
    registry: DeviceRegistry,
    message: dict[str, Any],
    discovered: dict[str, DiscoverySnapshot],
    startup: _StartupDiscovery | None = None,
    catalog: _AcapCatalog | None = None,
) -> object:
    command = message.get("type")
    if command == "devices/list":
        return [
            operations.normalize_payload(record.summary())
            for record in registry.load().values()
        ]
    if command in ("server/settings", "server/configure"):
        return _configure_server(registry, message)
    if command == "server/browse-folders":
        return await asyncio.to_thread(_browse_folders, message.get("path"))
    if command in (
        "acap/catalog",
        "acap/scan",
        "device/acap-updates",
        "device/acap-install-candidates",
    ):
        if catalog is None:
            raise ValueError
        result = await (catalog.scan() if command == "acap/scan" else catalog.read())
        if command in ("acap/catalog", "acap/scan"):
            return result
        if result["error"]:
            raise OperationError(result["error"], kind=ErrorKind.OPERATION)
        identifier = message.get("device")
        if not isinstance(identifier, str) or not identifier:
            raise ValueError
        packages = [Package(**entry) for entry in result["packages"]]
        if command == "device/acap-updates":
            return await operations.application_updates(
                registry.resolve(identifier), packages
            )
        return await operations.application_install_candidates(
            registry.resolve(identifier), packages
        )
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
    return await _saved_operation(registry, command, message)


async def _saved_operation(  # noqa: PLR0911 - each command returns its own response
    registry: DeviceRegistry, command: object, message: dict[str, Any]
) -> object:
    identifier = message.get("device")
    if (
        not isinstance(command, str)
        or command
        not in {
            "device/health",
            "device/architecture",
            "device/apis",
            "device/interfaces",
            "device/read",
            "device/restart",
            "device/applications",
            "device/application-action",
            "device/application-sdks",
            "device/application-support",
            "device/application-policy",
            "device/application-policy-set",
            "device/application-license-remove",
        }
        or not isinstance(identifier, str)
        or not identifier
    ):
        raise ValueError
    record = registry.resolve(identifier)
    if command == "device/application-support":
        return await operations.application_support(record)
    if command == "device/application-action":
        action = message.get("action")
        package = message.get("package")
        version = message.get("version")
        status = message.get("status")
        if (
            action not in ("start", "stop", "restart", "remove")
            or not isinstance(package, str)
            or not isinstance(version, str)
            or not isinstance(status, str)
            or message.get("confirmed") is not True
        ):
            msg = (
                "Application actions require a valid target and explicit confirmation."
            )
            raise OperationError(msg, kind=ErrorKind.VALIDATION)
        await operations.control_application(
            record, action, package, version, status, confirmed=True
        )
        return None
    if command == "device/application-sdks":
        return await operations.application_sdks(record)
    if command == "device/application-policy":
        return await operations.application_policy(record)
    if command == "device/application-policy-set":
        previous, value = message.get("previous"), message.get("value")
        if (
            type(previous) is not bool
            or type(value) is not bool
            or message.get("confirmed") is not True
        ):
            msg_0 = "Policy changes require confirmation."
            raise OperationError(msg_0, kind=ErrorKind.VALIDATION)
        await operations.set_application_policy(record, previous, value, confirmed=True)
        return None
    if command == "device/application-license-remove":
        package, version, status, license_status = (
            message.get("package"),
            message.get("version"),
            message.get("status"),
            message.get("license_status"),
        )
        if (
            not isinstance(package, str)
            or not isinstance(version, str)
            or not isinstance(status, str)
            or not isinstance(license_status, str)
            or message.get("confirmed") is not True
        ):
            msg_0 = "License changes require confirmation."
            raise OperationError(msg_0, kind=ErrorKind.VALIDATION)
        await operations.manage_application_license(
            record, package, version, status, license_status, confirmed=True
        )
        return None
    if command == "device/restart":
        if message.get("confirmed") is not True:
            msg = "Device restart requires explicit confirmation."
            raise OperationError(msg, kind=ErrorKind.VALIDATION)
        await operations.restart_device(record, confirmed=True)
        return None
    if command in ("device/health", "device/architecture"):
        result = (
            await operations.read_health(record)
            if command == "device/health"
            else await operations.read_architecture(record)
        )
        return operations.normalize_payload(result)
    if command in ("device/apis", "device/applications"):
        return (
            await operations.list_apis(record)
            if command == "device/apis"
            else await operations.list_applications(record)
        )
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
    catalog: _AcapCatalog | None = None,
) -> None:
    request_id = message["id"]
    is_discovery = message.get("type") == "devices/discover"
    try:
        async with asyncio.timeout(COMMAND_TIMEOUT):
            result = await _execute(
                socket, registry, message, discovered, startup, catalog
            )
    except StorageError as err:
        response = {"id": request_id, "error": {"code": "storage", "message": str(err)}}
    except OperationError as err:
        error_message = str(err)
        if err.outcome_unknown:
            error_message = str(err)
        elif is_discovery and err.kind != ErrorKind.VALIDATION:
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
        if err.outcome_unknown:
            response["error"]["outcome_unknown"] = True
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
                    else "ACAP scan is still running. Try again shortly."
                    if message.get("type") in ("acap/catalog", "acap/scan")
                    else "Browsing the folder timed out. Try again."
                    if message.get("type") == "server/browse-folders"
                    else "Restart outcome is unknown. Check the device before trying again."
                    if message.get("type") == "device/restart"
                    else "Application action outcome is unknown. Check the application before trying again."
                    if message.get("type") == "device/application-action"
                    else "Policy change outcome is unknown. Check the policy before trying again."
                    if message.get("type") == "device/application-policy-set"
                    else "License change outcome is unknown. Check the application before trying again."
                    if message.get("type") == "device/application-license-remove"
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


def _snapshot_acap(
    folder: str, filename: str, digest: str, snapshot: IO[bytes]
) -> Package:
    """Copy the reviewed package into an immutable private upload snapshot."""
    try:
        with open_package(folder, filename) as source:
            info = os.fstat(source.fileno())
            if (
                not stat.S_ISREG(info.st_mode)
                or not 0 < info.st_size <= MAX_PACKAGE_SIZE
            ):
                msg = "Package must be a non-empty regular file up to 1 GiB."
                raise PackageError(msg)
            size = 0
            while chunk := source.read(262144):
                size += len(chunk)
                if size > MAX_PACKAGE_SIZE:
                    msg = "Package exceeds the 1 GiB size limit."
                    raise PackageError(msg)
                snapshot.write(chunk)
        snapshot.seek(0)
        package = inspect_package(snapshot, filename)
        if package.digest != digest:
            msg = "Package changed. Refresh before updating."
            raise PackageError(msg)
        snapshot.seek(0)
        return package
    except OSError as exc:
        msg = "Cannot read the package; check folder permissions."
        raise PackageError(msg) from exc


def create_app(  # noqa: C901
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
    upload_lock = asyncio.Lock()
    catalog = _AcapCatalog(registry)
    initial: _StartupDiscovery | None = None
    catalog_task: asyncio.Task[None] | None = None

    async def start_catalog(application: web.Application) -> None:
        nonlocal catalog_task
        catalog_task = asyncio.create_task(catalog.run())

    async def stop_catalog(application: web.Application) -> None:
        if catalog_task is not None:
            catalog_task.cancel()
            await asyncio.gather(catalog_task, return_exceptions=True)
        if catalog.pending is not None and not catalog.pending.done():
            catalog.pending.cancel()
            await asyncio.gather(catalog.pending, return_exceptions=True)

    app.on_startup.append(start_catalog)
    app.on_cleanup.append(stop_catalog)

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

    async def upload_application(request: web.Request) -> web.Response:  # noqa: PLR0911
        supplied = request.headers.get("X-Axis-Token", "")
        if (
            request.headers.get("Origin") != origin
            or not supplied.isascii()
            or not secrets.compare_digest(supplied, token)
        ):
            raise web.HTTPForbidden
        if upload_lock.locked():
            return web.json_response(
                {"error": {"message": "Another application upload is in progress."}},
                status=409,
            )
        try:
            device_id = unquote(
                request.headers.get("X-Axis-Device", ""), errors="strict"
            )
            filename = unquote(
                request.headers.get("X-Axis-Filename", ""), errors="strict"
            )
            size = request.content_length
            if (
                not device_id
                or request.headers.get("X-Axis-Confirmed") != "true"
                or not filename.lower().endswith(".eap")
                or "/" in filename
                or "\\" in filename
                or len(filename) > 255
                or size is None
                or not 0 < size <= MAX_APPLICATION_PACKAGE_SIZE
            ):
                raise ValueError
            record = registry.resolve(device_id)
        except StorageError as exc:
            return web.json_response({"error": {"message": str(exc)}}, status=400)
        except ValueError:
            return web.json_response(
                {
                    "error": {
                        "message": "Choose a non-empty .eap file up to 1024 MB (1 GiB) and confirm the installation."
                    }
                },
                status=400,
            )
        async with upload_lock:
            try:
                with TemporaryFile() as package:
                    received = 0
                    async with asyncio.timeout(APPLICATION_UPLOAD_TIMEOUT):
                        async for chunk in request.content.iter_chunked(262144):
                            received += len(chunk)
                            if (
                                received > size
                                or received > MAX_APPLICATION_PACKAGE_SIZE
                            ):
                                raise ValueError
                            await asyncio.to_thread(package.write, chunk)
                    if received != size:
                        raise ValueError
                    await asyncio.to_thread(package.seek, 0)
                    await operations.install_application(
                        record, package, confirmed=True
                    )
            except ValueError:
                return web.json_response(
                    {
                        "error": {
                            "message": "The package upload was incomplete or too large."
                        }
                    },
                    status=400,
                )
            except OSError, TimeoutError:
                return web.json_response(
                    {
                        "error": {
                            "message": "Could not receive the application package."
                        }
                    },
                    status=400,
                )
            except OperationError as exc:
                return web.json_response(
                    {
                        "error": {
                            "message": str(exc),
                            "outcome_unknown": exc.outcome_unknown,
                        }
                    },
                    status=400,
                )
        return web.json_response({"result": None})

    async def catalog_application(request: web.Request) -> web.Response:
        installing = request.path == "/api/application-catalog-install"
        supplied = request.headers.get("X-Axis-Token", "")
        if (
            request.headers.get("Origin") != origin
            or not supplied.isascii()
            or not secrets.compare_digest(supplied, token)
        ):
            raise web.HTTPForbidden
        try:
            data = await request.json()
            if not isinstance(data, dict):
                raise ValueError
            device_id, filename, digest, version, status = (
                data.get("device"),
                data.get("filename"),
                data.get("digest"),
                data.get("version"),
                data.get("status"),
            )
            warnings = data.get("warnings")
            vendor = data.get("vendor")
            if (
                not isinstance(device_id, str)
                or not device_id
                or not isinstance(filename, str)
                or not filename
                or not isinstance(digest, str)
                or not re.fullmatch(r"[a-f0-9]{64}", digest)
                or not isinstance(warnings, list)
                or len(warnings) > 10
                or any(
                    not isinstance(warning, str) or len(warning) > 256
                    for warning in warnings
                )
                or data.get("confirmed") is not True
            ):
                raise ValueError
            update_details: tuple[str, str, str] | None = None
            if not installing:
                if (
                    not isinstance(version, str)
                    or not isinstance(status, str)
                    or not status
                    or not isinstance(vendor, str)
                ):
                    raise ValueError
                update_details = version, status, vendor
            folder = registry.web_acap_folder()
            if folder is None:
                msg = "No ACAP folder is configured."
                raise PackageError(msg)
            record = registry.resolve(device_id)
        except (ValueError, StorageError, PackageError) as exc:
            return web.json_response(
                {"error": {"message": str(exc) or "Invalid catalog request."}},
                status=400,
            )
        if upload_lock.locked():
            return web.json_response(
                {"error": {"message": "Another application upload is in progress."}},
                status=409,
            )
        async with upload_lock:
            try:
                with TemporaryFile() as snapshot:
                    package = await asyncio.to_thread(
                        _snapshot_acap, folder, filename, digest, snapshot
                    )
                    if registry.web_acap_folder() != folder:
                        msg = "ACAP folder changed. Refresh before continuing."
                        raise PackageError(msg)
                    if update_details is None:
                        await operations.install_catalog_application(
                            record,
                            snapshot,
                            package,
                            confirmed=True,
                            reviewed_warnings=tuple(warnings),
                        )
                    else:
                        version, status, vendor = update_details
                        await operations.update_application(
                            record,
                            snapshot,
                            package,
                            version,
                            status,
                            confirmed=True,
                            reviewed_warnings=tuple(warnings),
                            reviewed_vendor=vendor,
                        )
            except (PackageError, StorageError) as exc:
                return web.json_response({"error": {"message": str(exc)}}, status=400)
            except OperationError as exc:
                return web.json_response(
                    {
                        "error": {
                            "message": str(exc),
                            "outcome_unknown": exc.outcome_unknown,
                        }
                    },
                    status=400,
                )
        return web.json_response({"result": None})

    async def upload_license(request: web.Request) -> web.Response:
        supplied = request.headers.get("X-Axis-Token", "")
        if (
            request.headers.get("Origin") != origin
            or not supplied.isascii()
            or not secrets.compare_digest(supplied, token)
        ):
            raise web.HTTPForbidden
        if upload_lock.locked():
            return web.json_response(
                {"error": {"message": "Another application upload is in progress."}},
                status=409,
            )
        try:
            device_id = unquote(
                request.headers.get("X-Axis-Device", ""), errors="strict"
            )
            package = unquote(
                request.headers.get("X-Axis-Package", ""), errors="strict"
            )
            version = unquote(
                request.headers.get("X-Axis-Version", ""), errors="strict"
            )
            status = unquote(request.headers.get("X-Axis-Status", ""), errors="strict")
            license_status = unquote(
                request.headers.get("X-Axis-License-Status", ""), errors="strict"
            )
            size = request.content_length
            if (
                not device_id
                or not package
                or request.headers.get("X-Axis-Confirmed") != "true"
                or size is None
                or not 0 < size <= MAX_APPLICATION_LICENSE_SIZE
            ):
                raise ValueError
            record = registry.resolve(device_id)
        except StorageError as exc:
            return web.json_response({"error": {"message": str(exc)}}, status=400)
        except ValueError:
            return web.json_response(
                {
                    "error": {
                        "message": "Choose a non-empty license file up to 1 MiB and confirm the upload."
                    }
                },
                status=400,
            )
        async with upload_lock:
            try:
                with TemporaryFile() as license_file:
                    received = 0
                    async with asyncio.timeout(APPLICATION_UPLOAD_TIMEOUT):
                        async for chunk in request.content.iter_chunked(65536):
                            received += len(chunk)
                            if (
                                received > size
                                or received > MAX_APPLICATION_LICENSE_SIZE
                            ):
                                raise ValueError
                            await asyncio.to_thread(license_file.write, chunk)
                    if received != size:
                        raise ValueError
                    await asyncio.to_thread(license_file.seek, 0)
                    await operations.manage_application_license(
                        record,
                        package,
                        version,
                        status,
                        license_status,
                        license_file,
                        confirmed=True,
                    )
            except ValueError, OSError, TimeoutError:
                return web.json_response(
                    {"error": {"message": "Could not receive the license file."}},
                    status=400,
                )
            except OperationError as exc:
                return web.json_response(
                    {
                        "error": {
                            "message": str(exc),
                            "outcome_unknown": exc.outcome_unknown,
                        }
                    },
                    status=400,
                )
        return web.json_response({"result": None})

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
                    _respond(socket, registry, message, discovered, startup, catalog),
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
    app.router.add_post("/api/application-upload", upload_application)
    app.router.add_post("/api/application-update", catalog_application)
    app.router.add_post("/api/application-catalog-install", catalog_application)
    app.router.add_post("/api/application-license", upload_license)
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
