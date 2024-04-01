"""Python library to enable Axis devices to integrate with Home Assistant."""

import asyncio
import logging
from typing import TYPE_CHECKING

from .rtsp import RTSPClient, Signal, State

if TYPE_CHECKING:
    from collections.abc import Callable

    from .device import AxisDevice

_LOGGER = logging.getLogger(__name__)

RTSP_URL = (
    "rtsp://{host}/axis-media/media.amp?video={video}&audio={audio}&event={event}"
)

RETRY_TIMER = 15


class StreamManager:
    """Setup, start, stop and retry stream."""

    def __init__(self, device: "AxisDevice") -> None:
        """Initialize stream manager."""
        self.device = device
        self.video = None  # Unsupported
        self.audio = None  # Unsupported
        self.event = False
        self.stream: RTSPClient | None = None

        self.connection_status_callback: list[Callable[[Signal], None]] = []
        self.background_tasks: set[asyncio.Task[None]] = set()
        self.retry_timer: asyncio.TimerHandle | None = None

    @property
    def stream_url(self) -> str:
        """Build url for stream."""
        rtsp_url = RTSP_URL.format(
            host=self.device.config.host,
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
        return "on" if self.event else "off"

    def session_callback(self, signal: Signal) -> None:
        """Signalling from stream session.

        Data - new data available for processing.
        Playing - Connection is healthy.
        Retry - if there is no connection to device.
        """
        if signal == Signal.DATA and self.event:
            self.device.event.handler(self.data)

        elif signal == Signal.FAILED:
            self.retry()

        if signal in [Signal.PLAYING, Signal.FAILED]:
            for callback in self.connection_status_callback:
                callback(signal)

    @property
    def data(self) -> bytes:
        """Get stream data."""
        return self.stream.rtp.data  # type: ignore[union-attr]

    @property
    def state(self) -> State:
        """State of stream."""
        if not self.stream:
            return State.STOPPED
        return self.stream.session.state

    def start(self) -> None:
        """Start stream."""
        if not self.stream or self.stream.session.state == State.STOPPED:
            self.stream = RTSPClient(
                self.stream_url,
                self.device.config.host,
                self.device.config.username,
                self.device.config.password,
                self.session_callback,
            )
            task = asyncio.create_task(self.stream.start())
            self.background_tasks.add(task)
            task.add_done_callback(self.background_tasks.discard)

    def stop(self) -> None:
        """Stop stream."""
        if self.stream and self.stream.session.state != State.STOPPED:
            self.stream.stop()
        self.cancel_retry()

    def retry(self) -> None:
        """No connection to device, retry connection after 15 seconds."""
        self.cancel_retry()
        loop = asyncio.get_running_loop()
        self.stream = None
        self.retry_timer = loop.call_later(RETRY_TIMER, self.start)
        _LOGGER.debug("Reconnecting to %s", self.device.config.host)

    def cancel_retry(self) -> None:
        """Cancel scheduled retry."""
        if self.retry_timer is not None:
            self.retry_timer.cancel()
