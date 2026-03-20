"""Test websocket event client.

pytest --cov-report term-missing --cov=axis.websocket tests/test_websocket.py
"""

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import orjson

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
        timeout=5,
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
        timeout=5,
    )
