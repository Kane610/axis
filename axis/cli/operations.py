"""Presentation-free, session-owned operations for VAPIX devices and events."""

import asyncio
from collections.abc import AsyncIterator, Callable, Mapping
from contextlib import asynccontextmanager, suppress
from dataclasses import fields, is_dataclass
from enum import Enum
import re
from typing import TYPE_CHECKING
from urllib.parse import quote, quote_plus

from aiohttp import ClientSession, TCPConnector

from axis.cli.storage import ConnectionSettings, DeviceRecord
from axis.device import AxisDevice
from axis.errors import AxisException
from axis.models.configuration import AuthScheme, Configuration, WebProtocol
from axis.models.pwdgrp_cgi import SecondaryGroup
from axis.rtsp import Signal

if TYPE_CHECKING:
    from axis.models.event import Event

STARTUP_TIMEOUT = 30.0
_PRIVILEGES = {
    "admin": SecondaryGroup.ADMIN,
    "admin_ptz": SecondaryGroup.ADMIN_PTZ,
    "operator": SecondaryGroup.OPERATOR,
    "operator_ptz": SecondaryGroup.OPERATOR_PTZ,
    "viewer": SecondaryGroup.VIEWER,
    "viewer_ptz": SecondaryGroup.VIEWER_PTZ,
}
_SENSITIVE = (
    "password",
    "passwd",
    "pwd",
    "secret",
    "token",
    "credential",
    "auth",
    "cookie",
    "privatekey",
    "apikey",
    "accesskey",
    "passphrase",
    "username",
)


class OperationError(Exception):
    """A device operation failed, with a message safe for presentation."""


@asynccontextmanager
async def _device(settings: ConnectionSettings) -> AsyncIterator[AxisDevice]:
    try:
        async with ClientSession(
            connector=TCPConnector(ssl=settings.verify_ssl)
        ) as session:
            yield AxisDevice(
                Configuration(
                    session=session,
                    host=settings.host,
                    username=settings.username,
                    password=settings.password,
                    port=settings.port,
                    web_proto=WebProtocol(settings.web_proto),
                    verify_ssl=settings.verify_ssl,
                    is_companion=settings.is_companion,
                    auth_scheme=AuthScheme(settings.auth_scheme),
                    websocket_enabled=settings.websocket_enabled,
                    websocket_force=settings.websocket_force,
                )
            )
    except OperationError:
        raise
    except Exception:  # noqa: BLE001 - boundary must not expose transport credentials
        msg = "Device operation failed."
        raise OperationError(msg) from None


def _private(key: str) -> bool:
    normalized = re.sub(r"[^a-z0-9]", "", key.lower())
    return (
        any(part.startswith("_") for part in key.split("."))
        or normalized in {"config", "configuration", "session", "auth", "user"}
        or any(part in normalized for part in _SENSITIVE)
    )


def _serialize(value: object, password: str = "") -> object:
    if isinstance(value, Enum):
        return _serialize(value.value, password)
    if is_dataclass(value) and not isinstance(value, type):
        return {
            field.name: _serialize(getattr(value, field.name), password)
            for field in fields(value)
            if not _private(field.name)
        }
    if isinstance(value, Mapping):
        return {
            _redact_text(str(key), password): _serialize(item, password)
            for key, item in value.items()
            if not _private(str(key))
        }
    if isinstance(value, (list, tuple, set, frozenset)):
        return [_serialize(item, password) for item in value]
    if isinstance(value, bytes):
        value = value.decode(errors="replace")
    if isinstance(value, str):
        return _redact_text(value, password)
    if value is None or isinstance(value, (bool, int, float)):
        return value
    msg = "Unsupported device response."
    raise OperationError(msg)


def _redact_text(value: str, password: str) -> str:
    value = re.sub(r"(://)[^/\s]+@", r"\1[redacted]@", value)
    value = re.sub(
        r"(?i)\b(Basic|Bearer)\s+[A-Za-z0-9+/._~-]+={0,2}",
        r"\1 [redacted]",
        value,
    )
    if password:
        for secret in {password, quote(password, safe=""), quote_plus(password)}:
            value = value.replace(secret, "[redacted]")
    return value


def normalize_payload(value: object, password: str = "") -> object:
    """Serialize public fields and recursively redact credentials.

    Supply the connection password to redact its raw and URL-encoded forms in
    arbitrary strings and keys. Credential field matching is case-insensitive;
    URL user-info and HTTP Basic/Bearer credentials are redacted independently.
    Unsupported or malformed data raises a safe OperationError.
    """
    try:
        return _serialize(value, password)
    except OperationError:
        raise
    except Exception:  # noqa: BLE001 - normalization is also a public safe boundary
        msg = "Invalid device response."
        raise OperationError(msg) from None


def _row(value: object, password: str) -> dict[str, object]:
    result = normalize_payload(value, password)
    if not isinstance(result, dict):
        msg = "Unexpected device response."
        raise OperationError(msg)
    return {str(key): item for key, item in result.items()}


async def _identity(device: AxisDevice) -> None:
    try:
        if await device.vapix.basic_device_info.update():
            return
    except AxisException:
        pass
    if not await device.vapix.params.property_handler.update():
        msg = "Device identity is unavailable."
        raise OperationError(msg)
    with suppress(AxisException):
        await device.vapix.params.brand_handler.update()


async def identify(settings: ConnectionSettings) -> DeviceRecord:
    """Identify a device using basic information or legacy parameters."""
    async with _device(settings) as device:
        await _identity(device)
        serial = device.vapix.serial_number.strip()
        if not serial or serial.lower() in {"unknown", "<unknown>", "none", "n/a"}:
            msg = "Device did not provide a valid serial number."
            raise OperationError(msg)
        return DeviceRecord(
            serial=serial,
            config=settings,
            model=device.vapix.product_number,
        )


async def health(record: DeviceRecord) -> dict[str, object]:
    """Read current basic device information, not cached registry metadata."""
    async with _device(record.config) as device:
        await _identity(device)
        return _row(
            {
                "serial": device.vapix.serial_number,
                "model": device.vapix.product_number,
                "product": device.vapix.product_full_name,
                "firmware_version": device.vapix.firmware_version,
            },
            record.config.password,
        )


async def list_apis(record: DeviceRecord) -> list[dict[str, object]]:
    """List API discovery entries."""
    async with _device(record.config) as device:
        if not await device.vapix.api_discovery.update():
            msg = "API discovery is unavailable."
            raise OperationError(msg)
        return [
            _row(api, record.config.password)
            for api in device.vapix.api_discovery.values()
        ]


async def list_interfaces(record: DeviceRecord) -> list[dict[str, object]]:
    """Inspect library interfaces using the canonical VAPIX support probes."""
    async with _device(record.config) as device:
        states = await device.vapix.inspect_interfaces(
            refresh_discovery=True, probe=True
        )
        return [_row(state, record.config.password) for state in states.values()]


def _traverse(value: object, path: str) -> object:
    for token in (part for part in path.split(".") if part):
        if isinstance(value, dict):
            if token not in value:
                msg = "Response path does not exist."
                raise OperationError(msg)
            value = value[token]
        elif isinstance(value, list):
            if not token.isdecimal() or int(token) >= len(value):
                msg = "Response path does not exist."
                raise OperationError(msg)
            value = value[int(token)]
        else:
            msg = "Response path cannot be traversed."
            raise OperationError(msg)
    return value


async def read_interface(
    record: DeviceRecord, name: str, path: str | None = None
) -> object:
    """Read a registered interface, optionally traversing its serialized data."""
    async with _device(record.config) as device:
        handler = device.vapix.interfaces().get(name)
        if handler is None:
            msg = "Unknown device interface."
            raise OperationError(msg)
        await device.vapix.initialize()
        if not handler.initialized and not await handler.update():
            msg = "Device interface is unavailable."
            raise OperationError(msg)
        payload = normalize_payload(dict(handler.items()), record.config.password)
        return _traverse(payload, path) if path else payload


async def parameters(record: DeviceRecord) -> object:
    """Read device parameters with credentials and private fields removed."""
    async with _device(record.config) as device:
        if not await device.vapix.params.update():
            msg = "Device parameters are unavailable."
            raise OperationError(msg)
        return normalize_payload(
            dict(device.vapix.params.items()), record.config.password
        )


async def list_events(record: DeviceRecord) -> list[dict[str, object]]:
    """Read event instance definitions using the library's namespace parser."""
    async with _device(record.config) as device:
        if not await device.vapix.event_instances.update():
            msg = "Device event definitions are unavailable."
            raise OperationError(msg)
        return [
            _row(event, record.config.password)
            for event in device.vapix.event_instances.values()
        ]


async def list_accounts(record: DeviceRecord) -> object:
    """List account names and privileges without passwords."""
    async with _device(record.config) as device:
        users = await device.vapix.users.list()
        return {
            username: normalize_payload(user, record.config.password)
            for username, user in users.items()
        }


async def change_account(
    record: DeviceRecord,
    action: str,
    username: str,
    password: str | None = None,
    privilege: str = "viewer",
) -> None:
    """Create, update, or delete an account without silently changing actions."""
    if action not in {"create", "update", "delete"}:
        msg = "Unknown account action."
        raise OperationError(msg)
    if re.fullmatch(r"[A-Za-z0-9]{1,14}", username) is None:
        msg = "Username must contain 1-14 ASCII letters or digits."
        raise OperationError(msg)
    if privilege not in _PRIVILEGES:
        msg = "Unknown account privilege."
        raise OperationError(msg)
    if action == "create" and password is None:
        msg = "Creating an account requires a password."
        raise OperationError(msg)
    if password is not None and (
        not 1 <= len(password) <= 64
        or any(not 32 <= ord(char) <= 126 for char in password)
    ):
        msg = "Password must contain 1-64 printable ASCII characters."
        raise OperationError(msg)
    async with _device(record.config) as device:
        users = await device.vapix.users.list()
        if action == "create":
            if username in users:
                msg = "Account already exists."
                raise OperationError(msg)
            await device.vapix.users.create(
                username, pwd=password or "", sgrp=_PRIVILEGES[privilege]
            )
        else:
            if username not in users:
                msg = "Account does not exist."
                raise OperationError(msg)
            if action == "update":
                await device.vapix.users.modify(
                    username, pwd=password, sgrp=_PRIVILEGES[privilege]
                )
            else:
                await device.vapix.users.delete(username)


async def listen(
    record: DeviceRecord,
    emit: Callable[[object], None],
    topic: str | None = None,
    stream_mode: str = "auto",
) -> None:
    """Emit serialized events until cancellation or a terminal stream failure.

    ``auto`` preserves stored WebSocket settings; ``rtsp`` disables WebSockets,
    and ``event`` forces the VAPIX WebSocket event transport. STARTUP_TIMEOUT
    limits the wait for the first healthy connection.
    """
    if stream_mode not in {"auto", "rtsp", "event"}:
        msg = "Unknown event stream mode."
        raise OperationError(msg)
    async with _device(record.config) as device:
        if stream_mode != "auto":
            device.config.websocket_enabled = stream_mode == "event"
            device.config.websocket_force = stream_mode == "event"
        loop = asyncio.get_running_loop()
        connected: asyncio.Future[None] = loop.create_future()
        finished: asyncio.Future[None] = loop.create_future()

        def fail(message: str) -> None:
            future = finished if connected.done() else connected
            if not future.done():
                future.set_exception(OperationError(message))

        def on_event(event: Event) -> None:
            if topic is not None and event.topic != topic:
                return
            try:
                emit(normalize_payload(event, record.config.password))
            except Exception:  # noqa: BLE001 - callbacks must not strand the listener
                fail("Event callback failed.")

        def on_signal(signal: Signal) -> None:
            if signal == Signal.FAILED:
                fail("Event stream connection failed.")
            elif signal == Signal.PLAYING and not connected.done():
                connected.set_result(None)

        def on_task(task: asyncio.Task[None]) -> None:
            if not task.cancelled() and task.exception() is not None:
                fail("Event stream connection failed.")

        unsubscribe = device.event.subscribe(on_event)
        device.stream.connection_status_callback.append(on_signal)
        tasks: tuple[asyncio.Task[None], ...] = ()
        try:
            try:
                async with asyncio.timeout(STARTUP_TIMEOUT):
                    await device.vapix.api_discovery.update()
                    device.enable_events()
                    device.stream.start()
                    tasks = tuple(device.stream.background_tasks)
                    for task in tasks:
                        task.add_done_callback(on_task)
                    await connected
            except TimeoutError:
                msg = "Event stream startup timed out."
                raise OperationError(msg) from None
            await finished
        finally:
            device.stream.connection_status_callback.remove(on_signal)
            tasks = tuple(set(tasks) | device.stream.background_tasks)
            try:
                device.stream.stop()
            finally:
                unsubscribe()
                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)
                for future in (connected, finished):
                    if not future.done():
                        future.cancel()
                    elif not future.cancelled():
                        future.exception()
