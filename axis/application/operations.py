"""Read device information, manage accounts, and receive events for Axis applications.

These async functions can be used by the CLI or other applications without
terminal prompts. Each operation opens its HTTP connection and closes it when
finished; an event listener keeps its connection until stopped or disconnected.
"""

import asyncio
from collections.abc import AsyncGenerator, Callable, Mapping
from contextlib import asynccontextmanager, suppress
from dataclasses import fields, is_dataclass, replace
from datetime import UTC, datetime
from enum import Enum
import re
from typing import TYPE_CHECKING
from urllib.parse import quote, quote_plus

from aiohttp import ClientSession, TCPConnector

from axis.application.accounts import (
    _PRIVILEGES,
    AccountChange,
    AccountChangeResult,
    _validate_account,
    _validate_password,
    prepare_account_change,
    validate_account_username,
)
from axis.application.errors import ErrorKind, OperationError, _failure
from axis.application.records import ConnectionSettings, DeviceRecord, HealthSnapshot
from axis.device import AxisDevice
from axis.errors import AxisException
from axis.models.configuration import AuthScheme, Configuration, WebProtocol
from axis.rtsp import Signal

if TYPE_CHECKING:
    from axis.models.event import Event

__all__ = [
    "STARTUP_TIMEOUT",
    "OperationError",
    "apply_account_change",
    "change_account",
    "health",
    "identify",
    "list_accounts",
    "list_apis",
    "list_events",
    "list_interfaces",
    "listen",
    "normalize_payload",
    "parameters",
    "prepare_account_change",
    "read_health",
    "read_interface",
    "validate_account_username",
]

STARTUP_TIMEOUT = 30.0
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


@asynccontextmanager
async def _device(settings: ConnectionSettings) -> AsyncGenerator[AxisDevice]:
    try:
        settings = replace(settings)
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
    except Exception as exc:  # noqa: BLE001 - safe application boundary
        raise _failure(exc) from None


def _private(key: str) -> bool:
    normalized = re.sub(r"[^a-z0-9]", "", key.lower())
    return (
        any(part.startswith("_") for part in key.split("."))
        or normalized in {"config", "configuration", "session", "auth", "user"}
        or any(part in normalized for part in _SENSITIVE)
    )


def _serialize(value: object, password: str = "") -> object:
    if isinstance(value, datetime):
        value = value.isoformat()
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
    raise OperationError(msg, kind=ErrorKind.RESPONSE)


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
    """Convert device data into JSON-compatible values and hide login details.

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
        raise OperationError(msg, kind=ErrorKind.RESPONSE) from None


def _row(value: object, password: str) -> dict[str, object]:
    result = normalize_payload(value, password)
    if not isinstance(result, dict):
        msg = "Unexpected device response."
        raise OperationError(msg, kind=ErrorKind.RESPONSE)
    return {str(key): item for key, item in result.items()}


async def _identity(device: AxisDevice) -> None:
    try:
        if await device.vapix.basic_device_info.update():
            return
    except AxisException:
        pass
    if not await device.vapix.params.property_handler.update():
        msg = "Device identity is unavailable."
        raise OperationError(msg, kind=ErrorKind.UNSUPPORTED)
    with suppress(AxisException):
        await device.vapix.params.brand_handler.update()


async def identify(settings: ConnectionSettings) -> DeviceRecord:
    """Read a device's serial and model, falling back to parameters on older devices."""
    async with _device(settings) as device:
        await _identity(device)
        serial = device.vapix.serial_number.strip()
        if not serial or serial.lower() in {"unknown", "<unknown>", "none", "n/a"}:
            msg = "Device did not provide a valid serial number."
            raise OperationError(msg, kind=ErrorKind.RESPONSE)
        return DeviceRecord(
            serial=serial,
            config=settings,
            model=device.vapix.product_number,
        )


def _text(value: object, password: str) -> str:
    if not isinstance(value, str):
        msg = "Unexpected device identity response."
        raise OperationError(msg, kind=ErrorKind.RESPONSE)
    return _redact_text(value, password)


async def read_health(record: DeviceRecord) -> HealthSnapshot:
    """Read serial, model, product, and firmware, recording the target and read time."""
    target = record.summary()
    async with _device(record.config) as device:
        await _identity(device)
        password = device.config.password
        return HealthSnapshot(
            firmware_version=_text(device.vapix.firmware_version, password),
            model=_text(device.vapix.product_number, password),
            observed_at=datetime.now(UTC),
            product=_text(device.vapix.product_full_name, password),
            serial=_text(device.vapix.serial_number, password),
            target=target,
        )


async def health(record: DeviceRecord) -> dict[str, object]:
    """Return serial, model, product, and firmware in the CLI's existing dictionary format."""
    snapshot = await read_health(record)
    return {
        "serial": snapshot.serial,
        "model": snapshot.model,
        "product": snapshot.product,
        "firmware_version": snapshot.firmware_version,
    }


async def list_apis(record: DeviceRecord) -> list[dict[str, object]]:
    """Ask the device which APIs and versions it advertises."""
    async with _device(record.config) as device:
        if not await device.vapix.api_discovery.update():
            msg = "API discovery is unavailable."
            raise OperationError(msg, kind=ErrorKind.UNSUPPORTED)
        return [
            _row(api, device.config.password)
            for api in device.vapix.api_discovery.values()
        ]


async def list_interfaces(record: DeviceRecord) -> list[dict[str, object]]:
    """Check which library handlers the device advertises or responds to."""
    async with _device(record.config) as device:
        states = await device.vapix.inspect_interfaces(
            refresh_discovery=True, probe=True
        )
        return [_row(state, device.config.password) for state in states.values()]


def _traverse(value: object, path: str) -> object:
    for token in (part for part in path.split(".") if part):
        if isinstance(value, dict):
            if token not in value:
                msg = "Response path does not exist."
                raise OperationError(msg, kind=ErrorKind.VALIDATION)
            value = value[token]
        elif isinstance(value, list):
            if not token.isdecimal() or int(token) >= len(value):
                msg = "Response path does not exist."
                raise OperationError(msg, kind=ErrorKind.VALIDATION)
            value = value[int(token)]
        else:
            msg = "Response path cannot be traversed."
            raise OperationError(msg, kind=ErrorKind.VALIDATION)
    return value


async def read_interface(
    record: DeviceRecord, name: str, path: str | None = None
) -> object:
    """Read a handler's data, optionally selecting a value with a dotted path."""
    async with _device(record.config) as device:
        handler = device.vapix.interfaces().get(name)
        if handler is None:
            msg = "Unknown device interface."
            raise OperationError(msg, kind=ErrorKind.UNSUPPORTED)
        await device.vapix.initialize()
        if not handler.initialized and not await handler.update():
            msg = "Device interface is unavailable."
            raise OperationError(msg, kind=ErrorKind.UNSUPPORTED)
        payload = normalize_payload(dict(handler.items()), device.config.password)
        return _traverse(payload, path) if path else payload


async def parameters(record: DeviceRecord) -> object:
    """Read device parameters with credentials and private fields removed."""
    async with _device(record.config) as device:
        if not await device.vapix.params.update():
            msg = "Device parameters are unavailable."
            raise OperationError(msg, kind=ErrorKind.UNSUPPORTED)
        return normalize_payload(
            dict(device.vapix.params.items()), device.config.password
        )


async def list_events(record: DeviceRecord) -> list[dict[str, object]]:
    """List the event types and sources advertised by the device."""
    async with _device(record.config) as device:
        if not await device.vapix.event_instances.update():
            msg = "Device event definitions are unavailable."
            raise OperationError(msg, kind=ErrorKind.UNSUPPORTED)
        return [
            _row(event, device.config.password)
            for event in device.vapix.event_instances.values()
        ]


async def list_accounts(record: DeviceRecord) -> object:
    """List account names and privileges without passwords."""
    async with _device(record.config) as device:
        users = await device.vapix.users.list()
        return {
            username: normalize_payload(user, device.config.password)
            for username, user in users.items()
        }


async def change_account(
    record: DeviceRecord,
    action: str,
    username: str,
    password: str | None = None,
    privilege: str = "viewer",
    *,
    expected_serial: str | None = None,
) -> None:
    """Create, update, or delete an account without a separate review step.

    Retained for existing callers. New applications should prepare an account
    change and use apply_account_change to enforce authorization and target checks.
    """
    _validate_account(action, username, privilege)
    _validate_password(action, password)
    async with _device(record.config) as device:
        if expected_serial is not None:
            await _identity(device)
            if device.vapix.serial_number.strip() != expected_serial:
                msg = "Connected device identity differs from the reviewed target."
                raise OperationError(msg, kind=ErrorKind.CONFLICT)
        users = await device.vapix.users.list()
        if action == "create":
            if username in users:
                msg = "Account already exists."
                raise OperationError(msg, kind=ErrorKind.CONFLICT)
        elif username not in users:
            msg = "Account does not exist."
            raise OperationError(msg, kind=ErrorKind.CONFLICT)
        try:
            if action == "create":
                await device.vapix.users.create(
                    username, pwd=password or "", sgrp=_PRIVILEGES[privilege]
                )
            elif action == "update":
                await device.vapix.users.modify(
                    username, pwd=password, sgrp=_PRIVILEGES[privilege]
                )
            else:
                await device.vapix.users.delete(username)
        except OperationError:
            raise
        except Exception as exc:  # noqa: BLE001 - no secrets or automatic write retries
            raise _failure(exc, outcome_unknown=True) from None


async def apply_account_change(
    record: DeviceRecord,
    intent: AccountChange,
    password: str | None = None,
    *,
    authorized: bool = False,
    confirmed: bool = False,
) -> AccountChangeResult:
    """Apply an approved account change after checking its device and password intent."""
    if authorized is not True:
        msg = "Account changes require explicit authorization."
        raise OperationError(msg, kind=ErrorKind.VALIDATION)
    if intent.action == "delete" and confirmed is not True:
        msg = "Account deletion requires confirmation."
        raise OperationError(msg, kind=ErrorKind.VALIDATION)
    if not intent.target.same_target(record.summary()):
        msg = "Reviewed device target changed; prepare and review the action again."
        raise OperationError(msg, kind=ErrorKind.CONFLICT)
    if intent.password_change != (password is not None):
        msg = "Password input does not match the reviewed intention."
        raise OperationError(msg, kind=ErrorKind.VALIDATION)
    snapshot = replace(record, config=replace(record.config))
    await change_account(
        snapshot,
        intent.action,
        intent.username,
        password,
        intent.privilege,
        expected_serial=intent.target.serial,
    )
    return AccountChangeResult(intent)


async def listen(
    record: DeviceRecord,
    emit: Callable[[object], None],
    topic: str | None = None,
    stream_mode: str = "auto",
) -> None:
    """Send each received event to a callback until cancelled or the stream fails.

    ``auto`` preserves stored WebSocket settings; ``rtsp`` disables WebSockets,
    and ``event`` forces the VAPIX WebSocket event transport. STARTUP_TIMEOUT
    limits the wait for the first healthy connection.
    """
    if stream_mode not in {"auto", "rtsp", "event"}:
        msg = "Unknown event stream mode."
        raise OperationError(msg, kind=ErrorKind.VALIDATION)
    async with _device(record.config) as device:
        if stream_mode != "auto":
            device.config.websocket_enabled = stream_mode == "event"
            device.config.websocket_force = stream_mode == "event"
        loop = asyncio.get_running_loop()
        connected: asyncio.Future[None] = loop.create_future()
        finished: asyncio.Future[None] = loop.create_future()

        def fail(message: str, kind: ErrorKind = ErrorKind.CONNECTION) -> None:
            future = finished if connected.done() else connected
            if not future.done():
                future.set_exception(OperationError(message, kind=kind))

        def on_event(event: Event) -> None:
            if topic is not None and event.topic != topic:
                return
            try:
                emit(normalize_payload(event, device.config.password))
            except Exception:  # noqa: BLE001 - callbacks must not strand the listener
                fail("Event callback failed.", ErrorKind.OPERATION)

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
                raise OperationError(msg, kind=ErrorKind.TIMEOUT) from None
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
