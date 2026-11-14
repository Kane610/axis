"""Focused tests for session-owned, presentation-free device operations."""

import asyncio
from base64 import b64encode
from dataclasses import dataclass
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock
from urllib.parse import quote, quote_plus

import pytest

from axis.cli import operations
from axis.cli.storage import ConnectionSettings, DeviceRecord
from axis.errors import PathNotFound, RequestError
from axis.interfaces.vapix import InterfaceState
from axis.models.configuration import AuthScheme, Configuration, WebProtocol
from axis.models.event import Event, EventOperation, EventTopic
from axis.models.pwdgrp_cgi import SecondaryGroup, User
from axis.rtsp import Signal

from tests.http_route_mock import Route

if TYPE_CHECKING:
    from axis.device import AxisDevice

    from tests.http_route_mock import HttpRouteMock

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable


@pytest.fixture
def record() -> DeviceRecord:
    """Provide complete persisted connection settings."""
    return DeviceRecord(
        serial="SERIAL",
        config=ConnectionSettings(
            host="camera.local", username="root", password="very-secret-value"
        ),
        alias="Front",
        model="Cached model",
    )


@pytest.fixture
def device(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Mock device transport, retaining real operation-owned aiohttp sessions."""
    instance = MagicMock()
    vapix = instance.vapix
    vapix.serial_number = "CURRENT"
    vapix.product_number = "M1234"
    vapix.product_full_name = "AXIS M1234"
    vapix.firmware_version = "12.1"
    vapix.initialize = AsyncMock()
    for handler in (
        vapix.basic_device_info,
        vapix.api_discovery,
        vapix.params,
        vapix.params.property_handler,
        vapix.params.brand_handler,
        vapix.event_instances,
    ):
        handler.update = AsyncMock(return_value=True)
        handler.items.return_value = {}
        handler.values.return_value = []
    vapix.users.list = AsyncMock(
        return_value={
            "alice": User("alice", admin=False, operator=False, viewer=True, ptz=False)
        }
    )
    vapix.users.create = AsyncMock()
    vapix.users.modify = AsyncMock()
    vapix.users.delete = AsyncMock()
    vapix.inspect_interfaces = AsyncMock(return_value={})
    instance.stream.connection_status_callback = []
    instance.stream.background_tasks = set()

    def construct(config: Configuration) -> MagicMock:
        instance.config = config
        instance.connector = config.session.connector
        return instance

    monkeypatch.setattr(operations, "AxisDevice", construct)
    return instance


async def test_identify_preserves_configuration_and_owns_session(
    record: DeviceRecord, device: MagicMock
) -> None:
    """All stored transport options survive normalization and the session closes."""
    record.config = ConnectionSettings(
        host="camera.local",
        username="root",
        password="very-secret-value",
        web_proto="https",
        verify_ssl=True,
        is_companion=True,
        auth_scheme="digest",
        websocket_enabled=True,
        websocket_force=True,
    )
    result = await operations.identify(record.config)
    assert result.serial == "CURRENT"
    assert result.model == "M1234"
    assert result.config is record.config
    assert result.config.port == 0
    assert result.config.web_proto == "https"
    assert device.config.port == 443
    assert device.config.web_proto is WebProtocol.HTTPS
    assert device.config.auth_scheme is AuthScheme.DIGEST
    assert device.config.verify_ssl is True
    assert device.connector._ssl is True
    assert device.config.is_companion is True
    assert device.config.websocket_enabled is True
    assert device.config.websocket_force is True
    assert device.config.session.closed
    device.vapix.basic_device_info.update.assert_awaited_once()
    device.vapix.params.property_handler.update.assert_not_awaited()


@pytest.mark.parametrize(
    ("protocol", "port", "resolved", "auth"),
    [("http", 0, 80, "auto"), ("https", 8443, 8443, "basic")],
)
async def test_identify_transport_options(
    record: DeviceRecord,
    device: MagicMock,
    protocol: str,
    port: int,
    resolved: int,
    auth: str,
) -> None:
    """Explicit ports, authentication, and disabled TLS verification are effective."""
    record.config.web_proto = protocol
    record.config.port = port
    record.config.auth_scheme = auth
    await operations.identify(record.config)
    assert device.config.port == resolved
    assert device.config.auth_scheme == auth
    assert device.connector._ssl is False


@pytest.mark.parametrize("basic", [False, PathNotFound("unsupported")])
async def test_identify_legacy_fallback(
    record: DeviceRecord, device: MagicMock, basic: bool | Exception
) -> None:
    """Older firmware falls back to properties and brand without CLI helpers."""
    if isinstance(basic, Exception):
        device.vapix.basic_device_info.update.side_effect = basic
    else:
        device.vapix.basic_device_info.update.return_value = basic
    device.vapix.params.brand_handler.update.side_effect = PathNotFound()
    assert (await operations.identify(record.config)).serial == "CURRENT"
    device.vapix.params.property_handler.update.assert_awaited_once()
    device.vapix.params.brand_handler.update.assert_awaited_once()
    assert device.config.session.closed


async def test_identify_unavailable(record: DeviceRecord, device: MagicMock) -> None:
    """Failed probes are errors rather than fictitious identification results."""
    device.vapix.basic_device_info.update.return_value = False
    device.vapix.params.property_handler.update.return_value = False
    with pytest.raises(operations.OperationError, match="identity is unavailable"):
        await operations.identify(record.config)
    assert device.config.session.closed


@pytest.mark.parametrize("serial", ["", " ", "UNKNOWN", "<unknown>", "none", "N/A"])
async def test_identify_rejects_unknown_serial(
    record: DeviceRecord, device: MagicMock, serial: str
) -> None:
    """Missing or explicitly unknown serial numbers cannot enter the registry."""
    device.vapix.serial_number = serial
    with pytest.raises(operations.OperationError, match="valid serial"):
        await operations.identify(record.config)


async def test_safe_failure(record: DeviceRecord, device: MagicMock) -> None:
    """Transport exception text and its credential-bearing cause are hidden."""
    device.vapix.basic_device_info.update.side_effect = RuntimeError(
        f"https://root:{record.config.password}@camera"
    )
    with pytest.raises(
        operations.OperationError, match="Device operation failed"
    ) as exc:
        await operations.identify(record.config)
    assert record.config.password not in str(exc.value)
    assert exc.value.__cause__ is None
    assert exc.value.__suppress_context__
    assert device.config.session.closed


async def test_configuration_failure_is_safe(record: DeviceRecord) -> None:
    """Invalid persisted settings do not expose values from configuration errors."""
    record.config.host = "https://camera/path"
    with pytest.raises(operations.OperationError, match="Device operation failed"):
        await operations.identify(record.config)


async def test_configuration_valueerror_redacts_exception(
    record: DeviceRecord, device: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Settings validation ValueErrors inside operations have safe error messages."""
    configuration = MagicMock(side_effect=ValueError(record.config.password))
    monkeypatch.setattr(operations, "Configuration", configuration)
    with pytest.raises(
        operations.OperationError, match="Device operation failed"
    ) as exc:
        await operations.identify(record.config)
    assert record.config.password not in str(exc.value)
    assert exc.value.__suppress_context__
    session = configuration.call_args.kwargs["session"]
    assert session.closed


async def test_health_reads_live_information(
    record: DeviceRecord,
    device: MagicMock,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Health refreshes identity and never writes output, even in CLI debug mode."""
    monkeypatch.setenv("AXIS_CLI_DEBUG", "1")
    assert await operations.health(record) == {
        "serial": "CURRENT",
        "model": "M1234",
        "product": "AXIS M1234",
        "firmware_version": "12.1",
    }
    device.vapix.basic_device_info.update.assert_awaited_once()
    assert capsys.readouterr() == ("", "")


@dataclass
class Payload:
    """A response with enum fields, nested secrets, and a private field."""

    status: SecondaryGroup
    data: object
    _internal: str = "private"

    @property
    def password(self) -> str:
        """Reject accidental property reflection."""
        raise AssertionError


async def test_serialization_redacts_nested_fields(
    record: DeviceRecord, device: MagicMock
) -> None:
    """Dataclass fields and enums are JSON-ready and nested credentials disappear."""
    device.vapix.params.items.return_value = {
        "settings": Payload(
            SecondaryGroup.VIEWER,
            {
                "value": (True, None, 2, 1.5, b"text"),
                "Password": "hidden",
                "root.Network.UserName": "root",
                "secret": "hidden",
                "api_key": "hidden",
                "session": "hidden",
                "config": "hidden",
                "_private": "hidden",
                "user": "root",
                "url": "https://another:other-secret@camera/",
                "comment": f"credential: {record.config.password}",
            },
        )
    }.items()
    assert await operations.parameters(record) == {
        "settings": {
            "status": "viewer",
            "data": {
                "value": [True, None, 2, 1.5, "text"],
                "url": "https://[redacted]@camera/",
                "comment": "credential: [redacted]",
            },
        }
    }


@pytest.mark.parametrize("payload", [object(), Payload])
async def test_unknown_response_is_not_stringified(
    record: DeviceRecord, device: MagicMock, payload: object
) -> None:
    """Opaque objects and classes cannot leak their representations."""
    device.vapix.params.items.return_value = {"0": payload}.items()
    with pytest.raises(operations.OperationError, match="Unsupported device response"):
        await operations.parameters(record)


async def test_list_apis(record: DeviceRecord, device: MagicMock) -> None:
    """API entries use canonical dataclass/enum serialization."""
    device.vapix.api_discovery.values.return_value = [
        Payload(SecondaryGroup.VIEWER, {"version": "1.1", "token": "hidden"})
    ]
    assert await operations.list_apis(record) == [
        {"status": "viewer", "data": {"version": "1.1"}}
    ]


async def test_list_interfaces(record: DeviceRecord, device: MagicMock) -> None:
    """Interface support comes directly from inspect_interfaces, not heuristics."""
    device.vapix.inspect_interfaces.return_value = {
        "light_control": InterfaceState(
            "light_control", "light-control", "1.0", False, True, True, True, True, 1
        )
    }
    assert await operations.list_interfaces(record) == [
        {
            "name": "light_control",
            "api_id": "light-control",
            "api_version": "1.0",
            "listed": False,
            "probe_attempted": True,
            "probe_succeeded": True,
            "supported": True,
            "initialized": True,
            "items": 1,
        }
    ]
    device.vapix.inspect_interfaces.assert_awaited_once_with(
        refresh_discovery=True, probe=True
    )


async def test_list_events(record: DeviceRecord, device: MagicMock) -> None:
    """Event definitions retain structured data rather than string booleans."""
    device.vapix.event_instances.values.return_value = [
        {"topic": "Motion", "stateful": True, "data": {"password": "hidden"}}
    ]
    assert await operations.list_events(record) == [
        {"topic": "Motion", "stateful": True, "data": {}}
    ]


@pytest.mark.parametrize(
    ("operation", "handler"),
    [
        (operations.list_apis, "api_discovery"),
        (operations.parameters, "params"),
        (operations.list_events, "event_instances"),
    ],
)
async def test_failed_read_is_error(
    record: DeviceRecord,
    device: MagicMock,
    operation: Callable[[DeviceRecord], Awaitable[object]],
    handler: str,
) -> None:
    """Permission or support failures are never silently converted to empty data."""
    getattr(device.vapix, handler).update.return_value = False
    with pytest.raises(operations.OperationError, match="unavailable"):
        await operation(record)


async def test_malformed_list_row(record: DeviceRecord, device: MagicMock) -> None:
    """List row shape guards reject scalar responses."""
    device.vapix.api_discovery.values.return_value = ["unexpected"]
    with pytest.raises(operations.OperationError, match="Unexpected device response"):
        await operations.list_apis(record)


@pytest.mark.parametrize("initialized", [True, False])
async def test_read_interface_uses_registered_handlers(
    record: DeviceRecord, device: MagicMock, initialized: bool
) -> None:
    """Read preserves initialization architecture and supports nested dot paths."""
    handler = MagicMock(initialized=initialized)
    handler.update = AsyncMock(return_value=True)
    handler.items.return_value = {
        "0": {"rows": [{"enabled": True, "password": "hidden"}]}
    }.items()
    device.vapix.interfaces.return_value = {"mqtt": handler}
    assert (
        await operations.read_interface(record, "mqtt", ".0..rows.0.enabled.") is True
    )
    device.vapix.initialize.assert_awaited_once()
    assert handler.update.await_count == (0 if initialized else 1)
    assert await operations.read_interface(record, "mqtt") == {
        "0": {"rows": [{"enabled": True}]}
    }


@pytest.mark.parametrize("name", ["initialize", "request", "__dict__", "unknown"])
async def test_interface_whitelist(
    record: DeviceRecord, device: MagicMock, name: str
) -> None:
    """Arbitrary VAPIX methods and private attributes cannot be invoked."""
    device.vapix.interfaces.return_value = {}
    with pytest.raises(operations.OperationError, match="Unknown device interface"):
        await operations.read_interface(record, name)
    device.vapix.initialize.assert_not_awaited()


async def test_interface_unavailable(record: DeviceRecord, device: MagicMock) -> None:
    """A failed targeted update is surfaced rather than reported as empty data."""
    handler = MagicMock(initialized=False)
    handler.update = AsyncMock(return_value=False)
    device.vapix.interfaces.return_value = {"mqtt": handler}
    with pytest.raises(operations.OperationError, match="interface is unavailable"):
        await operations.read_interface(record, "mqtt")


@pytest.mark.parametrize(
    ("path", "message"),
    [
        ("missing", "does not exist"),
        ("0.rows.3", "does not exist"),
        ("0.rows.-1", "does not exist"),
        ("0.rows.x", "does not exist"),
        ("0.rows.0.enabled.field", "cannot be traversed"),
        ("0.password", "does not exist"),
    ],
)
async def test_interface_path_guards(
    record: DeviceRecord, device: MagicMock, path: str, message: str
) -> None:
    """Traversal handles missing keys, invalid indexes, and non-container roots."""
    handler = MagicMock(initialized=True)
    handler.items.return_value = {
        "0": {"rows": [{"enabled": True}], "password": "hidden"}
    }.items()
    device.vapix.interfaces.return_value = {"mqtt": handler}
    with pytest.raises(operations.OperationError, match=message):
        await operations.read_interface(record, "mqtt", path)


async def test_list_accounts(record: DeviceRecord, device: MagicMock) -> None:
    """Account listing exposes identifiers and role flags, never passwords."""
    assert await operations.list_accounts(record) == {
        "alice": {
            "id": "alice",
            "admin": False,
            "operator": False,
            "viewer": True,
            "ptz": False,
        }
    }


async def test_accounts_named_like_sensitive_fields(
    record: DeviceRecord, device: MagicMock
) -> None:
    """Account identifiers are not mistaken for password or token field names."""
    device.vapix.users.list.return_value = {
        name: User(name, admin=False, operator=False, viewer=True, ptz=False)
        for name in ("password", "token", "username")
    }
    result = await operations.list_accounts(record)
    assert isinstance(result, dict)
    assert set(result) == {"password", "token", "username"}


@pytest.mark.parametrize(
    ("action", "username", "password", "privilege", "message"),
    [
        ("upsert", "alice", None, "viewer", "Unknown account action"),
        ("create", "", "valid", "viewer", "Username"),
        ("create", "a" * 15, "valid", "viewer", "Username"),
        ("create", "bad-name", "valid", "viewer", "Username"),
        ("create", "ålice", "valid", "viewer", "Username"),
        ("create", "bob", "valid", "superadmin", "Unknown account privilege"),
        ("create", "bob", None, "viewer", "requires a password"),
        ("create", "bob", "", "viewer", "Password must"),
        ("update", "alice", "a" * 65, "viewer", "Password must"),
        ("update", "alice", "\n", "viewer", "Password must"),
        ("update", "alice", "é", "viewer", "Password must"),
    ],
)
async def test_account_validation_before_network(
    record: DeviceRecord,
    device: MagicMock,
    action: str,
    username: str,
    password: str | None,
    privilege: str,
    message: str,
) -> None:
    """Unknown actions, invalid inputs, and unknown roles fail before connecting."""
    with pytest.raises(operations.OperationError, match=message):
        await operations.change_account(record, action, username, password, privilege)
    device.vapix.users.list.assert_not_awaited()


@pytest.mark.parametrize(
    ("privilege", "expected"),
    [
        ("viewer", SecondaryGroup.VIEWER),
        ("viewer_ptz", SecondaryGroup.VIEWER_PTZ),
        ("operator", SecondaryGroup.OPERATOR),
        ("operator_ptz", SecondaryGroup.OPERATOR_PTZ),
        ("admin", SecondaryGroup.ADMIN),
        ("admin_ptz", SecondaryGroup.ADMIN_PTZ),
    ],
)
async def test_create_account_privileges(
    record: DeviceRecord,
    device: MagicMock,
    privilege: str,
    expected: SecondaryGroup,
) -> None:
    """Each CLI privilege maps to the complete device secondary-group value."""
    await operations.change_account(record, "create", "bob", "new", privilege)
    device.vapix.users.create.assert_awaited_once_with("bob", pwd="new", sgrp=expected)
    device.vapix.users.modify.assert_not_awaited()


@pytest.mark.parametrize("password", [None, "updated", " " * 64])
async def test_update_account(
    record: DeviceRecord, device: MagicMock, password: str | None
) -> None:
    """Update can change just privileges without resetting the password."""
    await operations.change_account(record, "update", "alice", password, "operator")
    device.vapix.users.modify.assert_awaited_once_with(
        "alice", pwd=password, sgrp=SecondaryGroup.OPERATOR
    )
    device.vapix.users.create.assert_not_awaited()


async def test_delete_account(record: DeviceRecord, device: MagicMock) -> None:
    """Delete never calls create or modify."""
    await operations.change_account(record, "delete", "alice")
    device.vapix.users.delete.assert_awaited_once_with("alice")
    device.vapix.users.modify.assert_not_awaited()
    device.vapix.users.create.assert_not_awaited()


@pytest.mark.parametrize(
    ("action", "username", "message"),
    [
        ("create", "alice", "already exists"),
        ("update", "bob", "does not exist"),
        ("delete", "bob", "does not exist"),
    ],
)
async def test_account_existence_semantics(
    record: DeviceRecord, device: MagicMock, action: str, username: str, message: str
) -> None:
    """Create/update remain distinct even when the account existence disagrees."""
    with pytest.raises(operations.OperationError, match=message):
        await operations.change_account(record, action, username, "new")
    device.vapix.users.create.assert_not_awaited()
    device.vapix.users.modify.assert_not_awaited()
    device.vapix.users.delete.assert_not_awaited()


def _event(topic: str = "Motion") -> Event:
    return Event(
        id="1",
        is_tripped=True,
        operation=EventOperation.CHANGED,
        source="sensor",
        state="true",
        topic=topic,
        topic_base=EventTopic.UNKNOWN,
        data={"password": "hidden", "value": True},
    )


def _assert_listener_closed(device: MagicMock) -> None:
    device.event.subscribe.return_value.assert_called_once_with()
    device.stream.stop.assert_called_once_with()
    assert device.stream.connection_status_callback == []
    assert device.config.session.closed


@pytest.mark.parametrize(
    ("mode", "enabled", "forced"),
    [("auto", False, False), ("rtsp", False, False), ("event", True, True)],
)
async def test_listener_transport_and_terminal_failure(
    record: DeviceRecord,
    device: MagicMock,
    mode: str,
    enabled: bool,
    forced: bool,
) -> None:
    """Stored/explicit transport choices work and repeated failures terminate."""
    emitted: list[object] = []

    def start() -> None:
        callback = device.stream.connection_status_callback[0]
        callback(Signal.PLAYING)
        callback(Signal.PLAYING)
        callback(Signal.DATA)
        device.event.subscribe.call_args.args[0](_event())
        callback(Signal.FAILED)
        callback(Signal.FAILED)

    device.stream.start.side_effect = start
    with pytest.raises(operations.OperationError, match="connection failed"):
        await operations.listen(record, emitted.append, stream_mode=mode)
    assert device.config.websocket_enabled is enabled
    assert device.config.websocket_force is forced
    assert emitted == [
        {
            "id": "1",
            "is_tripped": True,
            "operation": "Changed",
            "source": "sensor",
            "state": "true",
            "topic": "Motion",
            "topic_base": "unknown",
            "data": {"value": True},
        }
    ]
    _assert_listener_closed(device)


async def test_auto_keeps_websocket_flags(
    record: DeviceRecord, device: MagicMock
) -> None:
    """Automatic mode does not silently turn off persisted forced WebSockets."""
    record.config.websocket_enabled = True
    record.config.websocket_force = True
    device.stream.start.side_effect = lambda: device.stream.connection_status_callback[
        0
    ](Signal.FAILED)
    with pytest.raises(operations.OperationError, match="connection failed"):
        await operations.listen(record, lambda _: None)
    assert device.config.websocket_enabled
    assert device.config.websocket_force
    _assert_listener_closed(device)


async def test_listener_topic_filter(record: DeviceRecord, device: MagicMock) -> None:
    """Topic filtering uses event.topic, never the unrelated source identifier."""
    emitted: list[object] = []

    def start() -> None:
        on_event = device.event.subscribe.call_args.args[0]
        on_event(_event("Other"))
        on_event(_event("Motion"))
        device.stream.connection_status_callback[0](Signal.FAILED)

    device.stream.start.side_effect = start
    with pytest.raises(operations.OperationError, match="connection failed"):
        await operations.listen(record, emitted.append, topic="Motion")
    assert len(emitted) == 1
    _assert_listener_closed(device)


@pytest.mark.parametrize("connected", [False, True])
async def test_listener_callback_failure(
    record: DeviceRecord, device: MagicMock, connected: bool
) -> None:
    """Callback failures are surfaced safely both during and after startup."""

    def emit(_: object) -> None:
        raise RuntimeError(record.config.password)

    def start() -> None:
        if connected:
            device.stream.connection_status_callback[0](Signal.PLAYING)
        device.event.subscribe.call_args.args[0](_event())

    device.stream.start.side_effect = start
    with pytest.raises(operations.OperationError, match="Event callback failed"):
        await operations.listen(record, emit)
    _assert_listener_closed(device)


async def test_listener_cancelled(record: DeviceRecord, device: MagicMock) -> None:
    """External cancellation propagates after unsubscribing and closing sessions."""
    started = asyncio.Event()

    def start() -> None:
        device.stream.connection_status_callback[0](Signal.PLAYING)
        started.set()

    device.stream.start.side_effect = start
    task = asyncio.create_task(operations.listen(record, lambda _: None))
    await started.wait()
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    _assert_listener_closed(device)


@pytest.mark.parametrize("task_state", ["none", "success", "cancelled", "failure"])
async def test_listener_startup_tasks(
    record: DeviceRecord,
    device: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
    task_state: str,
) -> None:
    """Stalled, failed, and cancelled transport tasks cannot strand the listener."""
    monkeypatch.setattr(operations, "STARTUP_TIMEOUT", 0.01)

    async def transport() -> None:
        if task_state == "failure":
            raise RuntimeError(record.config.password)
        if task_state == "cancelled":
            raise asyncio.CancelledError

    def start() -> None:
        if task_state != "none":
            device.stream.background_tasks.add(asyncio.create_task(transport()))

    device.stream.start.side_effect = start
    message = "connection failed" if task_state == "failure" else "startup timed out"
    with pytest.raises(operations.OperationError, match=message):
        await operations.listen(record, lambda _: None)
    assert all(task.done() for task in device.stream.background_tasks)
    _assert_listener_closed(device)


@pytest.mark.parametrize("stage", ["discovery", "start"])
async def test_listener_exception_cleanup(
    record: DeviceRecord, device: MagicMock, stage: str
) -> None:
    """Failures before transport startup still clean up registered callbacks."""
    target = (
        device.vapix.api_discovery.update
        if stage == "discovery"
        else device.stream.start
    )
    target.side_effect = RequestError(record.config.password)
    with pytest.raises(operations.OperationError, match="Device operation failed"):
        await operations.listen(record, lambda _: None)
    _assert_listener_closed(device)


async def test_listener_unknown_mode(record: DeviceRecord, device: MagicMock) -> None:
    """An invalid stream selector fails before making network requests."""
    with pytest.raises(operations.OperationError, match="Unknown event stream mode"):
        await operations.listen(record, lambda _: None, stream_mode="invalid")
    device.vapix.api_discovery.update.assert_not_awaited()


async def test_listener_discovery_timeout(
    record: DeviceRecord, device: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The startup deadline includes discovery, not just stream negotiation."""
    monkeypatch.setattr(operations, "STARTUP_TIMEOUT", 0.01)
    never = asyncio.Event()
    device.vapix.api_discovery.update.side_effect = never.wait
    with pytest.raises(operations.OperationError, match="startup timed out"):
        await operations.listen(record, lambda _: None)
    device.stream.start.assert_not_called()
    _assert_listener_closed(device)


async def test_listener_stop_failure_cleanup(
    record: DeviceRecord, device: MagicMock
) -> None:
    """Even a broken transport stop cannot prevent unsubscribe and session close."""
    device.stream.start.side_effect = lambda: device.stream.connection_status_callback[
        0
    ](Signal.FAILED)
    device.stream.stop.side_effect = RuntimeError(record.config.password)
    with pytest.raises(operations.OperationError, match="Device operation failed"):
        await operations.listen(record, lambda _: None)
    _assert_listener_closed(device)


@pytest.mark.parametrize("status", [200, 401])
async def test_accounts_real_http_boundary(
    record: DeviceRecord,
    axis_device: AxisDevice,
    http_route_mock: HttpRouteMock,
    status: int,
) -> None:
    """Real handlers use the configured host, port, auth, and account parser."""
    record.config.host = axis_device.config.host
    record.config.port = axis_device.config.port
    record.config.auth_scheme = "basic"
    route = http_route_mock.post("/axis-cgi/pwdgrp.cgi", data={"action": "get"})
    assert isinstance(route, Route)
    route.respond(
        text='admin="alice"\noperator="alice"\nviewer="alice"\nptz="alice"',
        status_code=status,
    )
    if status == 401:
        with pytest.raises(operations.OperationError, match="Device operation failed"):
            await operations.list_accounts(record)
    else:
        assert await operations.list_accounts(record) == {
            "alice": {
                "id": "alice",
                "admin": True,
                "operator": True,
                "viewer": True,
                "ptz": True,
            }
        }
    assert route.call_count == 1
    assert route.calls.last.request.headers["Authorization"].startswith("Basic ")


def test_public_normalization_credentials() -> None:
    """Public normalization redacts auth fields, encoded secrets, and URL user-info."""
    password = "s@fe p/ss"
    encoded = b64encode(f"root:{password}".encode()).decode()
    payload = {
        "rows": [
            {
                "PASSWORD": "hidden",
                "ToKeN": "hidden",
                "AuthHeader": "hidden",
                "nested.authentication": "hidden",
                "Cookie": "hidden",
                "root._private": "hidden",
                "raw": password,
                "quoted": quote(password, safe=""),
                "form": quote_plus(password),
                "basic": f"bAsIc {encoded}",
                "bearer": "Bearer abc",
                "url": "https://root:a@b@camera/",
                "user_url": "https://root@camera/",
            }
        ],
        f"key-{password}": "public",
    }
    assert operations.normalize_payload(payload, password) == {
        "rows": [
            {
                "raw": "[redacted]",
                "quoted": "[redacted]",
                "form": "[redacted]",
                "basic": "bAsIc [redacted]",
                "bearer": "Bearer [redacted]",
                "url": "https://[redacted]@camera/",
                "user_url": "https://[redacted]@camera/",
            }
        ],
        "key-[redacted]": "public",
    }


def test_public_normalization_malformed_data() -> None:
    """Public normalization exposes only OperationError for malformed objects."""
    payload: list[object] = []
    payload.append(payload)
    with pytest.raises(
        operations.OperationError, match="Invalid device response"
    ) as exc:
        operations.normalize_payload(payload)
    assert exc.value.__cause__ is None
    assert exc.value.__suppress_context__


def test_public_normalization_without_connection_password() -> None:
    """URLs and credential headers are protected even without known settings."""
    assert operations.normalize_payload(
        {
            "url": "http://other:password@camera/path",
            "header": "Basic dXNlcjpwYXNz",
            "AuthHeader": "hidden",
            "enabled": True,
        }
    ) == {
        "url": "http://[redacted]@camera/path",
        "header": "Basic [redacted]",
        "enabled": True,
    }


@pytest.mark.parametrize("operation", ["read", "parameters", "apis", "events"])
async def test_recursive_redaction_across_reads(
    record: DeviceRecord, device: MagicMock, operation: str
) -> None:
    """Every device read path uses the same public credential-safe normalization."""
    data = {
        "nested": [
            {
                "pAsSwOrD": "hidden",
                "AUTH": "hidden",
                "token": "hidden",
                "public": f"embedded={record.config.password}",
            }
        ]
    }
    if operation == "read":
        handler = MagicMock(initialized=True)
        handler.items.return_value = {"0": data}.items()
        device.vapix.interfaces.return_value = {"mqtt": handler}
        result = await operations.read_interface(record, "mqtt", "0")
    elif operation == "parameters":
        device.vapix.params.items.return_value = data.items()
        result = await operations.parameters(record)
    elif operation == "apis":
        device.vapix.api_discovery.values.return_value = [data]
        result = (await operations.list_apis(record))[0]
    else:
        device.vapix.event_instances.values.return_value = [data]
        result = (await operations.list_events(record))[0]
    assert result == {"nested": [{"public": "embedded=[redacted]"}]}


@pytest.mark.parametrize("failure", ["disconnect", "pipe"])
async def test_listener_failures_after_startup(
    record: DeviceRecord, device: MagicMock, failure: str
) -> None:
    """Disconnects and broken output pipes terminate after the listener is playing."""
    started = asyncio.Event()

    def start() -> None:
        device.stream.connection_status_callback[0](Signal.PLAYING)
        started.set()

    def emit(_: object) -> None:
        raise BrokenPipeError(record.config.password)

    device.stream.start.side_effect = start
    task = asyncio.create_task(operations.listen(record, emit))
    await started.wait()
    await asyncio.sleep(0)
    if failure == "disconnect":
        device.stream.connection_status_callback[0](Signal.FAILED)
        message = "connection failed"
    else:
        device.event.subscribe.call_args.args[0](_event())
        message = "Event callback failed"
    with pytest.raises(operations.OperationError, match=message):
        await task
    _assert_listener_closed(device)
