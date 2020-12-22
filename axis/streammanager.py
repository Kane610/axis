"""Python library to enable Axis devices to integrate with Home Assistant."""

import asyncio
import logging

from .configuration import Configuration
from .rtsp import RTSPClient, SIGNAL_DATA, SIGNAL_FAILED, SIGNAL_PLAYING, STATE_STOPPED

_LOGGER = logging.getLogger(__name__)

RTSP_URL = (
    "rtsp://{host}/axis-media/media.amp" "?video={video}&audio={audio}&event={event}"
)

RETRY_TIMER = 15


class StreamManager:
    """Setup, start, stop and retry stream."""

    def __init__(self, config: Configuration) -> None:
        """Setup stream manager."""
        self.config = config
        self.video = None  # Unsupported
        self.audio = None  # Unsupported
        self.event = None
        self.stream = None

        self.connection_status_callback = []

    @property
    def stream_url(self) -> str:
        """Build url for stream."""
        rtsp_url = RTSP_URL.format(
            host=self.config.host,
            video=self.video_query,
            audio=self.audio_query,
            event=self.event_query,
        )
        _LOGGER.debug(rtsp_url)
        return rtsp_url

    @property
    def video_query(self) -> int:
        """Generate video query, not supported."""
        return 0

    @property
    def audio_query(self) -> int:
        """Generate audio query, not supported."""
        return 0

    @property
    def event_query(self) -> str:
        """Generate event query."""
        return "on" if bool(self.event) else "off"

    def session_callback(self, signal: str) -> None:
        """Signalling from stream session.

        Data - new data available for processing.
        Playing - Connection is healthy.
        Retry - if there is no connection to device.
        """
        if signal == SIGNAL_DATA:
            self.event.update(self.data)

        elif signal == SIGNAL_FAILED:
            self.retry()

        if signal in [SIGNAL_PLAYING, SIGNAL_FAILED]:
            for callback in self.connection_status_callback:
                callback(signal)

    @property
    def data(self) -> str:
        """Get stream data."""
        return self.stream.rtp.data

    @property
    def state(self) -> str:
        """State of stream."""
        if not self.stream:
            return STATE_STOPPED
        return self.stream.session.state

    def start(self) -> None:
        """Start stream."""
        if not self.stream or self.stream.session.state == STATE_STOPPED:
            self.stream = RTSPClient(
                self.stream_url,
                self.config.host,
                self.config.username,
                self.config.password,
                self.session_callback,
            )
            asyncio.create_task(self.stream.start())

    def stop(self) -> None:
        """Stop stream."""
        if self.stream and self.stream.session.state != STATE_STOPPED:
            self.stream.stop()

    def retry(self) -> None:
        """No connection to device, retry connection after 15 seconds."""
        loop = asyncio.get_running_loop()
        self.stream = None
        loop.call_later(RETRY_TIMER, self.start)
        _LOGGER.debug("Reconnecting to %s", self.config.host)
