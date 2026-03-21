"""Test stream manager class.

pytest --cov-report term-missing --cov=axis.stream_manager tests/test_stream_manager.py
"""

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from axis.models.api_discovery import ApiId
from axis.rtsp import Signal, State
from axis.stream_manager import RETRY_TIMER, StreamManager

from .conftest import HOST
from .event_fixtures import AUDIO_INIT


@pytest.fixture
def stream_manager(axis_device) -> StreamManager:
    """Return the StreamManager mock object."""
    return axis_device.stream


@pytest.fixture
def stream_manager_companion(axis_companion_device) -> StreamManager:
    """Return the StreamManager mock object."""
    return axis_companion_device.stream


async def test_stream_url(stream_manager):
    """Verify stream url."""
    assert stream_manager.video_query == 0
    assert stream_manager.audio_query == 0
    assert stream_manager.event_query == "off"
    assert (
        stream_manager.stream_url
        == f"rtsp://{HOST}/axis-media/media.amp?video=0&audio=0&event=off"
    )

    stream_manager.event = True
    assert stream_manager.event_query == "on"
    assert (
        stream_manager.stream_url
        == f"rtsp://{HOST}/axis-media/media.amp?video=0&audio=0&event=on"
    )


async def test_stream_url_companion(stream_manager_companion):
    """Verify stream url."""
    assert stream_manager_companion.video_query == 0
    assert stream_manager_companion.audio_query == 0
    assert stream_manager_companion.event_query == "off"
    assert (
        stream_manager_companion.stream_url
        == f"rtsp://{HOST}/axis-media/media.amp?video=0&audio=0&event=off&Axis-Orig-Sw=true"
    )

    stream_manager_companion.event = True
    assert stream_manager_companion.event_query == "on"
    assert (
        stream_manager_companion.stream_url
        == f"rtsp://{HOST}/axis-media/media.amp?video=0&audio=0&event=on&Axis-Orig-Sw=true"
    )


async def test_websocket_url(stream_manager):
    """Verify websocket URL."""
    assert (
        stream_manager.websocket_url
        == f"ws://{HOST}:80/vapix/ws-data-stream?sources=events"
    )

    stream_manager.event = True
    assert (
        stream_manager.websocket_url
        == f"ws://{HOST}:80/vapix/ws-data-stream?sources=events"
    )


async def test_use_websocket_supported_api(stream_manager):
    """Verify API discovery controls websocket usage."""
    stream_manager.event = True
    assert not stream_manager.use_websocket

    stream_manager.device.vapix.api_discovery._items[
        ApiId.EVENT_STREAMING_OVER_WEBSOCKET
    ] = MagicMock()
    assert not stream_manager.use_websocket

    stream_manager.device.config.websocket_enabled = True
    assert stream_manager.use_websocket


@patch("axis.stream_manager.RTSPClient")
@patch("axis.stream_manager.WebSocketClient")
async def test_start_uses_websocket_when_supported(
    websocket_client, rtsp_client, stream_manager
):
    """Verify websocket transport is selected for supported event streams."""
    websocket_client.return_value.start = AsyncMock()
    stream_manager.event = True
    stream_manager.device.config.websocket_enabled = True
    stream_manager.device.vapix.api_discovery._items[
        ApiId.EVENT_STREAMING_OVER_WEBSOCKET
    ] = MagicMock()

    stream_manager.start()

    websocket_client.assert_called_once()
    rtsp_client.assert_not_called()


@patch("axis.stream_manager.RTSPClient")
@patch("axis.stream_manager.WebSocketClient")
async def test_initialize_stream(websocket_client, rtsp_client, stream_manager):
    """Test stream commands."""
    rtsp_client.return_value.start = AsyncMock()
    # Stream does not exist
    assert not stream_manager.stream  # Stream does not exist
    stream_manager.stop()  # Calling stop shouldn't do anything
    assert (
        stream_manager.state == State.STOPPED
    )  # Default state of stream manager is stopped

    # Stream is created
    stream_manager.start()  # Start creates stream object
    rtsp_client.assert_called()  # Stream object is based on RTSPClient
    stream_manager.stream.start.assert_called()  # RTSPClient start is called as well
    stream_manager.stream.stop.assert_not_called()  # Stop has never been called

    # Stream can't stop if in stopped state
    stream_manager.stream.session.state = (
        State.STOPPED  # Nothing happens if in stopped state
    )
    stream_manager.stop()  # Try to stop stream
    stream_manager.stream.stop.assert_not_called()  # Wrong state so not called

    # Stream can stop if in non stopped state
    stream_manager.stream.session.state = State.PLAYING  # State is now playing
    assert stream_manager.state == State.PLAYING  # State of stream manager is playing
    stream_manager.stop()  # Stop should work
    stream_manager.stream.stop.assert_called()  # RTSPClient stop can now be called

    # Data from rtspclient
    stream_manager.stream.data = AUDIO_INIT
    assert stream_manager.data == AUDIO_INIT

    # Session callback
    stream_manager.device.event.handler = MagicMock()
    stream_manager.device.event.subscribe(MagicMock())
    stream_manager.device.enable_events()
    mock_connection_status_callback = MagicMock()
    stream_manager.connection_status_callback.append(mock_connection_status_callback)

    # Signal new data is available through event callbacks update method
    stream_manager.session_callback(Signal.DATA)
    stream_manager.device.event.handler.assert_called_with(AUDIO_INIT)

    # Signal state is playing on the connection status callbacks
    stream_manager.session_callback(Signal.PLAYING)
    mock_connection_status_callback.assert_called_with(Signal.PLAYING)

    # Signal state is stopped and call try to reconnect
    with patch.object(stream_manager, "retry") as mock_retry:
        stream_manager.session_callback(Signal.FAILED)
        mock_retry.assert_called()
        mock_connection_status_callback.assert_called_with(Signal.FAILED)

    # Retry should schedule a retry timer and call stream manager start method
    mock_loop = MagicMock()
    with patch("axis.stream_manager.asyncio.get_running_loop", return_value=mock_loop):
        stream_manager.retry()
        assert stream_manager.stream is None
        mock_loop.call_later.assert_called_with(RETRY_TIMER, stream_manager.start)


async def test_data_property_websocket_stream(stream_manager):
    """Verify data property also supports websocket streams."""
    ws_event = {
        "topic": "tns1:Device/Trigger/Relay",
        "source": "port",
        "source_idx": "2",
        "type": "active",
        "value": "1",
    }
    stream_manager.stream = SimpleNamespace(
        data=ws_event,
        session=SimpleNamespace(state=State.PLAYING),
    )
    assert stream_manager.data == ws_event


async def test_data_property_without_stream_returns_empty_bytes(stream_manager):
    """Verify data property returns empty bytes when stream is missing."""
    stream_manager.stream = None
    assert stream_manager.data == b""


@patch("axis.stream_manager.RTSPClient")
@patch("axis.stream_manager.WebSocketClient")
async def test_start_returns_when_already_starting(
    websocket_client, rtsp_client, stream_manager
):
    """Verify start() no-ops while a start is already in progress."""
    stream_manager._starting = True

    stream_manager.start()

    websocket_client.assert_not_called()
    rtsp_client.assert_not_called()


async def test_cancel_retry_cancels_timer(stream_manager):
    """Verify cancel_retry() cancels an existing retry timer."""
    stream_manager.retry_timer = MagicMock()

    stream_manager.cancel_retry()

    stream_manager.retry_timer.cancel.assert_called_once()


@patch("axis.stream_manager.RTSPClient")
@patch("axis.stream_manager.WebSocketClient")
async def test_start_noop_when_stream_already_active(
    websocket_client, rtsp_client, stream_manager
):
    """Verify start() does nothing when an existing stream is already active."""
    stream_manager._starting = False
    stream_manager.stream = SimpleNamespace(
        session=SimpleNamespace(state=State.PLAYING),
        start=MagicMock(),
    )

    stream_manager.start()

    websocket_client.assert_not_called()
    rtsp_client.assert_not_called()


async def test_retry_without_active_stream_does_not_call_stop(stream_manager):
    """Verify retry() skips stop() when no stream is active."""
    existing_stream = SimpleNamespace(
        session=SimpleNamespace(state=State.STOPPED),
        stop=MagicMock(),
    )
    stream_manager.stream = existing_stream
    mock_loop = MagicMock()

    with patch("axis.stream_manager.asyncio.get_running_loop", return_value=mock_loop):
        stream_manager.retry()

    existing_stream.stop.assert_not_called()
    assert stream_manager.stream is None
    mock_loop.call_later.assert_called_once_with(RETRY_TIMER, stream_manager.start)
