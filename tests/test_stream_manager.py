"""Test stream manager class.

pytest --cov-report term-missing --cov=axis.stream_manager tests/test_stream_manager.py
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from axis.rtsp import Signal, State
from axis.stream_manager import RETRY_TIMER, StreamManager

from .conftest import HOST
from .event_fixtures import AUDIO_INIT


@pytest.fixture
def stream_manager(axis_device) -> StreamManager:
    """Return the StreamManager mock object."""
    return axis_device.stream


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


@patch("axis.stream_manager.RTSPClient")
async def test_initialize_stream(rtsp_client, stream_manager):
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
    stream_manager.stream.rtp.data = AUDIO_INIT
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
