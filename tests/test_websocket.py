"""Test websocket event client.

pytest --cov-report term-missing --cov=axis.websocket tests/test_websocket.py
"""

import asyncio
from types import SimpleNamespace
from unittest.mock import ANY, AsyncMock, MagicMock, patch

import aiohttp
import orjson
import pytest

from axis.models.api_discovery import ApiId
from axis.rtsp import Signal, State
from axis.websocket import WebSocketClient


class MockWebSocket:
    """Simple async iterator that yields websocket messages."""

    def __init__(self, configure_response, stream_messages):
        """Initialize with configure ack/error response and stream messages."""
        self._messages = iter(stream_messages)
        self._configure_response = configure_response
        self.close = AsyncMock()
        self.send_json = AsyncMock()
        self.receive = AsyncMock(return_value=configure_response)

    def __aiter__(self):
        """Return iterator."""
        return self

    async def __anext__(self):
        """Return next websocket message."""
        try:
            return next(self._messages)
        except StopIteration as err:
            raise StopAsyncIteration from err


class BlockingWebSocket:
    """Websocket that blocks until released."""

    def __init__(self, configure_response):
        """Initialize blocking websocket."""
        self.close = AsyncMock()
        self.send_json = AsyncMock()
        self.receive = AsyncMock(return_value=configure_response)
        self._event = asyncio.Event()

    def __aiter__(self):
        """Return iterator."""
        return self

    async def __anext__(self):
        """Wait until released then stop iteration."""
        await self._event.wait()
        raise StopAsyncIteration

    def release(self) -> None:
        """Release blocked iterator."""
        self._event.set()


class ErrorWebSocket:
    """Websocket iterator that immediately raises a client error."""

    def __init__(self, exc: Exception):
        """Initialize with exception to raise from iterator."""
        self.close = AsyncMock()
        self.send_json = AsyncMock()
        self.receive = AsyncMock(return_value=_configure_ok_msg())
        self._exc = exc

    def __aiter__(self):
        """Return iterator."""
        return self

    async def __anext__(self):
        """Raise provided exception."""
        raise self._exc


def _configure_ok_msg() -> SimpleNamespace:
    """Build a successful events:configure response message."""
    return SimpleNamespace(
        type=aiohttp.WSMsgType.TEXT,
        data=orjson.dumps(
            {
                "apiVersion": "1.0",
                "context": "axis-py",
                "method": "events:configure",
                "data": {},
            }
        ).decode(),
    )


def _configure_error_msg() -> SimpleNamespace:
    """Build a failing events:configure response message."""
    return SimpleNamespace(
        type=aiohttp.WSMsgType.TEXT,
        data=orjson.dumps(
            {
                "apiVersion": "1.0",
                "context": "axis-py",
                "method": "events:configure",
                "error": {"code": 1100, "message": "Internal Error"},
            }
        ).decode(),
    )


def _notify_msg(
    topic: str, source_key: str, source_idx: str, data_key: str, value: str
):
    """Build an events:notify websocket message."""
    return SimpleNamespace(
        type=aiohttp.WSMsgType.TEXT,
        data=orjson.dumps(
            {
                "apiVersion": "1.0",
                "method": "events:notify",
                "params": {
                    "notification": {
                        "timestamp": "2024-01-01T00:00:00Z",
                        "topic": topic,
                        "message": {
                            "source": {source_key: source_idx},
                            "key": {},
                            "data": {data_key: value},
                        },
                    }
                },
            }
        ).decode(),
    )


async def test_websocket_stream_receives_data(axis_device):
    """Verify websocket client emits playing and data signals for events:notify."""
    callback = MagicMock()
    ws = MockWebSocket(
        _configure_ok_msg(),
        [
            _notify_msg("tns1:Device/Trigger/Relay", "port", "2", "active", "1"),
            SimpleNamespace(type=aiohttp.WSMsgType.CLOSED, data=None),
        ],
    )

    ws_session = AsyncMock()
    ws_session.ws_connect.return_value = ws

    axis_device.vapix.request = AsyncMock(return_value=b"token123")

    with patch("axis.websocket.aiohttp.ClientSession", return_value=ws_session):
        client = WebSocketClient(
            axis_device,
            "ws://127.0.0.1:80/vapix/ws-data-stream?sources=events",
            callback,
        )
        await client.start()
        await client._receiver_task

    assert callback.call_args_list[0].args[0] == Signal.PLAYING
    assert callback.call_args_list[1].args[0] == Signal.DATA
    assert callback.call_args_list[2].args[0] == Signal.FAILED
    assert client.data == {
        "topic": "tns1:Device/Trigger/Relay",
        "source": "port",
        "source_idx": "2",
        "type": "active",
        "value": "1",
    }
    assert client.session.state == State.STOPPED

    ws.send_json.assert_called_once_with(
        {
            "apiVersion": "1.0",
            "context": "axis-py",
            "method": "events:configure",
            "params": {"eventFilterList": [{"topicFilter": "//"}]},
        }
    )
    ws_session.ws_connect.assert_called_once_with(
        "ws://127.0.0.1:80/vapix/ws-data-stream?sources=events&wssession=token123",
        heartbeat=5,
        timeout=ANY,
    )


async def test_websocket_configure_failure(axis_device):
    """Verify websocket client reports failed configure."""
    callback = MagicMock()
    ws = MockWebSocket(_configure_error_msg(), [])
    ws_session = AsyncMock()
    ws_session.ws_connect.return_value = ws

    axis_device.vapix.request = AsyncMock(return_value=b"token123")

    with patch("axis.websocket.aiohttp.ClientSession", return_value=ws_session):
        client = WebSocketClient(
            axis_device,
            "ws://127.0.0.1:80/vapix/ws-data-stream?sources=events",
            callback,
        )
        await client.start()

    callback.assert_called_once_with(Signal.FAILED)
    assert client.session.state == State.STOPPED


async def test_websocket_stop_is_idempotent(axis_device):
    """Verify stop() can be called repeatedly without failed callback."""
    callback = MagicMock()
    ws = BlockingWebSocket(_configure_ok_msg())
    ws_session = AsyncMock()
    ws_session.ws_connect.return_value = ws
    axis_device.vapix.request = AsyncMock(return_value=b"token123")

    with patch("axis.websocket.aiohttp.ClientSession", return_value=ws_session):
        client = WebSocketClient(
            axis_device,
            "ws://127.0.0.1:80/vapix/ws-data-stream?sources=events",
            callback,
        )
        await client.start()
        client.stop()
        client.stop()
        ws.release()
        await asyncio.sleep(0)

    assert callback.call_count == 1
    assert callback.call_args_list[0].args[0] == Signal.PLAYING
    assert client.session.state == State.STOPPED


async def test_websocket_fallback_to_basic_auth_when_no_token(axis_device):
    """Verify websocket falls back to basic auth if wssession token is unavailable."""
    callback = MagicMock()
    ws = MockWebSocket(
        _configure_ok_msg(),
        [SimpleNamespace(type=aiohttp.WSMsgType.CLOSED, data=None)],
    )
    ws_session = AsyncMock()
    ws_session.ws_connect.return_value = ws
    axis_device.vapix.request = AsyncMock(side_effect=RuntimeError("no token"))

    with patch("axis.websocket.aiohttp.ClientSession", return_value=ws_session):
        client = WebSocketClient(
            axis_device,
            "ws://127.0.0.1:80/vapix/ws-data-stream?sources=events",
            callback,
        )
        await client.start()
        await client._receiver_task

    ws_session.ws_connect.assert_called_once_with(
        "ws://127.0.0.1:80/vapix/ws-data-stream?sources=events",
        heartbeat=5,
        timeout=ANY,
    )


async def test_websocket_supported_by_device_and_empty_data(axis_device):
    """Verify capability check and empty buffer data behavior."""
    assert not WebSocketClient.supported_by_device(axis_device)

    axis_device.vapix.api_discovery._items[ApiId.EVENT_STREAMING_OVER_WEBSOCKET] = (
        MagicMock()
    )

    assert WebSocketClient.supported_by_device(axis_device)

    client = WebSocketClient(
        axis_device,
        "ws://127.0.0.1:80/vapix/ws-data-stream?sources=events",
        MagicMock(),
    )
    assert client.data == {}


async def test_websocket_start_guard_returns_early(axis_device):
    """Verify start() short-circuits if already starting or non-stopped state."""
    callback = MagicMock()
    ws_session = AsyncMock()
    axis_device.vapix.request = AsyncMock(return_value=b"token123")

    with patch("axis.websocket.aiohttp.ClientSession", return_value=ws_session):
        client = WebSocketClient(
            axis_device,
            "ws://127.0.0.1:80/vapix/ws-data-stream?sources=events",
            callback,
        )

        client._starting = True
        await client.start()

        client._starting = False
        client.session.state = State.PLAYING
        await client.start()

    axis_device.vapix.request.assert_not_called()
    ws_session.ws_connect.assert_not_called()


async def test_websocket_start_awaits_close_task(axis_device):
    """Verify start() awaits an existing close task before reconnecting."""
    callback = MagicMock()
    ws = MockWebSocket(
        _configure_ok_msg(),
        [SimpleNamespace(type=aiohttp.WSMsgType.CLOSED, data=None)],
    )
    ws_session = AsyncMock()
    ws_session.ws_connect.return_value = ws
    axis_device.vapix.request = AsyncMock(return_value=b"token123")

    with patch("axis.websocket.aiohttp.ClientSession", return_value=ws_session):
        client = WebSocketClient(
            axis_device,
            "ws://127.0.0.1:80/vapix/ws-data-stream?sources=events",
            callback,
        )

        close_task = asyncio.create_task(asyncio.sleep(0))
        client._close_task = close_task
        await client.start()
        await client._receiver_task

    assert close_task.done()
    ws_session.ws_connect.assert_called_once()


async def test_websocket_connect_failure(axis_device):
    """Verify websocket client reports failed connect errors."""
    callback = MagicMock()
    ws_session = AsyncMock()
    ws_session.ws_connect.side_effect = aiohttp.ClientError("boom")

    axis_device.vapix.request = AsyncMock(return_value=b"token123")

    with patch("axis.websocket.aiohttp.ClientSession", return_value=ws_session):
        client = WebSocketClient(
            axis_device,
            "ws://127.0.0.1:80/vapix/ws-data-stream?sources=events",
            callback,
        )
        await client.start()

    callback.assert_called_once_with(Signal.FAILED)
    assert client.session.state == State.STOPPED
    assert client._ws is None
    assert client._ws_session is None


async def test_websocket_configure_with_no_ws(axis_device):
    """Verify configure returns cleanly when websocket is missing."""
    client = WebSocketClient(
        axis_device,
        "ws://127.0.0.1:80/vapix/ws-data-stream?sources=events",
        MagicMock(),
    )
    client._ws = None
    await client._configure()


async def test_websocket_configure_unexpected_message_type(axis_device):
    """Verify configure fails on non text/binary response."""
    ws = AsyncMock()
    ws.send_json = AsyncMock()
    ws.receive = AsyncMock(
        return_value=SimpleNamespace(type=aiohttp.WSMsgType.CLOSE, data=None)
    )

    client = WebSocketClient(
        axis_device,
        "ws://127.0.0.1:80/vapix/ws-data-stream?sources=events",
        MagicMock(),
    )
    client._ws = ws

    with pytest.raises(aiohttp.ClientError, match="Unexpected WS message type"):
        await client._configure()


async def test_websocket_receiver_returns_when_ws_is_none(axis_device):
    """Verify receiver exits immediately when websocket is not set."""
    callback = MagicMock()
    client = WebSocketClient(
        axis_device,
        "ws://127.0.0.1:80/vapix/ws-data-stream?sources=events",
        callback,
    )
    client._ws = None

    await client._receiver()

    callback.assert_not_called()


async def test_websocket_receiver_exception_signals_failed(axis_device):
    """Verify receiver exception path signals FAILED when not stopped."""
    callback = MagicMock()
    ws = ErrorWebSocket(aiohttp.ClientError("rx boom"))

    client = WebSocketClient(
        axis_device,
        "ws://127.0.0.1:80/vapix/ws-data-stream?sources=events",
        callback,
    )
    client._ws = ws
    client._ws_session = AsyncMock()
    client._stopped = False

    await client._receiver()

    assert callback.call_args_list[-1].args[0] == Signal.FAILED
    assert client.session.state == State.STOPPED


@pytest.mark.parametrize(
    "payload",
    [
        b"not-json",
        orjson.dumps({"method": "events:other", "params": {}}),
        orjson.dumps({"method": "events:notify", "params": {}}),
    ],
)
async def test_websocket_handle_message_ignores_irrelevant_payloads(
    axis_device, payload
):
    """Verify non-json/non-notify/empty-notification payloads are ignored."""
    callback = MagicMock()
    client = WebSocketClient(
        axis_device,
        "ws://127.0.0.1:80/vapix/ws-data-stream?sources=events",
        callback,
    )

    client._handle_message(payload)

    callback.assert_not_called()
    assert client.data == {}


async def test_websocket_stop_without_receiver_task(axis_device):
    """Verify stop() schedules close even when receiver task is missing."""
    client = WebSocketClient(
        axis_device,
        "ws://127.0.0.1:80/vapix/ws-data-stream?sources=events",
        MagicMock(),
    )
    client._receiver_task = None

    client.stop()

    assert client._close_task is not None
    await client._close_task


async def test_websocket_receiver_ignores_non_close_non_text_message(axis_device):
    """Verify receiver continues when message type is neither data nor close."""
    callback = MagicMock()
    ws = MockWebSocket(
        _configure_ok_msg(),
        [
            SimpleNamespace(type=aiohttp.WSMsgType.PING, data=None),
            SimpleNamespace(type=aiohttp.WSMsgType.CLOSED, data=None),
        ],
    )

    client = WebSocketClient(
        axis_device,
        "ws://127.0.0.1:80/vapix/ws-data-stream?sources=events",
        callback,
    )
    client._ws = ws
    client._ws_session = AsyncMock()

    await client._receiver()

    assert callback.call_args_list[-1].args[0] == Signal.FAILED


async def test_websocket_receiver_does_not_signal_failed_when_stopped(axis_device):
    """Verify receiver finalizer skips FAILED signal when already stopped."""
    callback = MagicMock()
    ws = MockWebSocket(
        _configure_ok_msg(),
        [SimpleNamespace(type=aiohttp.WSMsgType.CLOSED, data=None)],
    )

    client = WebSocketClient(
        axis_device,
        "ws://127.0.0.1:80/vapix/ws-data-stream?sources=events",
        callback,
    )
    client._ws = ws
    client._ws_session = AsyncMock()
    client._stopped = True

    await client._receiver()

    callback.assert_not_called()


async def test_websocket_close_with_no_session(axis_device):
    """Verify close() handles missing websocket session branch."""
    client = WebSocketClient(
        axis_device,
        "ws://127.0.0.1:80/vapix/ws-data-stream?sources=events",
        MagicMock(),
    )
    client._ws = None
    client._ws_session = None

    await client._close()

    assert client._ws is None
    assert client._ws_session is None
