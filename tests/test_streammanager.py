"""Test stream manager class.

pytest --cov-report term-missing --cov=axis.streammanager tests/test_streammanager.py
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from axis.rtsp import (
    SIGNAL_DATA,
    SIGNAL_FAILED,
    SIGNAL_PLAYING,
    STATE_PLAYING,
    STATE_STOPPED,
)
from axis.streammanager import RETRY_TIMER, StreamManager

from .conftest import HOST


@pytest.fixture
def stream_manager(axis_device) -> StreamManager:
    """Returns the streammanager mock object."""
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


@patch("axis.streammanager.RTSPClient")
async def test_initialize_stream(rtsp_client, stream_manager):
    """Test stream commands."""
    rtsp_client.return_value.start = AsyncMock()
    # Stream does not exist
    assert not stream_manager.stream  # Stream does not exist
    stream_manager.stop()  # Calling stop shouldn't do anything
    assert (
        stream_manager.state == STATE_STOPPED
    )  # Default state of stream manager is stopped

    # Stream is created
    stream_manager.start()  # Start creates stream object
    rtsp_client.assert_called()  # Stream object is based on RTSPClient
    stream_manager.stream.start.assert_called()  # RTSPClient start is called as well
    stream_manager.stream.stop.assert_not_called()  # Stop has never been called

    # Stream can't stop if in stopped state
    stream_manager.stream.session.state = (
        STATE_STOPPED  # Nothing happens if in stopped state
    )
    stream_manager.stop()  # Try to stop stream
    stream_manager.stream.stop.assert_not_called()  # Wrong state so not called

    # Stream can stop if in non stopped state
    stream_manager.stream.session.state = STATE_PLAYING  # State is now playing
    assert stream_manager.state == STATE_PLAYING  # State of stream manager is playing
    stream_manager.stop()  # Stop should work
    stream_manager.stream.stop.assert_called()  # RTSPClient stop can now be called

    # Data from rtspclient
    stream_manager.stream.rtp.data = "Summerwheen"
    assert stream_manager.data == "Summerwheen"

    # Session callback
    mock_event_callback = MagicMock()
    stream_manager.event = mock_event_callback
    mock_connection_status_callback = MagicMock()
    stream_manager.connection_status_callback.append(mock_connection_status_callback)

    # Signal new data is available through event callbacks update method
    stream_manager.session_callback(SIGNAL_DATA)
    mock_event_callback.update.assert_called_with("Summerwheen")

    # Signal state is playing on the connection status callbacks
    stream_manager.session_callback(SIGNAL_PLAYING)
    mock_connection_status_callback.assert_called_with(SIGNAL_PLAYING)

    # Signal state is stopped and call try to reconnect
    with patch.object(stream_manager, "retry") as mock_retry:
        stream_manager.session_callback(SIGNAL_FAILED)
        mock_retry.assert_called()
        mock_connection_status_callback.assert_called_with(SIGNAL_FAILED)

    # Retry should schedule a retry timer and call stream manager start method
    mock_loop = MagicMock()
    with patch("axis.streammanager.asyncio.get_running_loop", return_value=mock_loop):
        stream_manager.retry()
        assert stream_manager.stream is None
        mock_loop.call_later.assert_called_with(RETRY_TIMER, stream_manager.start)
