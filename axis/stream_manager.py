"""Python library to enable Axis devices to integrate with Home Assistant."""

import asyncio
import logging
from typing import TYPE_CHECKING, Any

from .models.configuration import WebProtocol
from .rtsp import RTSPClient, Signal, State
from .websocket import WebSocketClient

if TYPE_CHECKING:
    from collections.abc import Callable

    from .device import AxisDevice
    from .stream_transport import StreamTransport

_LOGGER = logging.getLogger(__name__)

RTSP_URL = "rtsp://{host}/axis-media/media.amp?video={video}&audio={audio}&event={event}{axis_orig_sw}"
WEBSOCKET_PATH = "/vapix/ws-data-stream"

RETRY_TIMER = 15


class StreamManager:
    """Setup, start, stop and retry stream."""

    def __init__(
        self,
        device: AxisDevice,
        event_filter_list: list[dict[str, str]] | None = None,
    ) -> None:
        """Initialize stream manager."""
        self.device = device
        self.video = None  # Unsupported
        self.audio = None  # Unsupported
        self.event = False
        self.event_filter_list = event_filter_list
        self.stream: StreamTransport | None = None

        self.connection_status_callback: list[Callable[[Signal], None]] = []
        self.background_tasks: set[asyncio.Task[None]] = set()
        self.retry_timer: asyncio.TimerHandle | None = None
        self._starting = False
        self._websocket_temporarily_disabled = False

    @property
    def stream_url(self) -> str:
        """Build url for stream."""
        rtsp_url = RTSP_URL.format(
            host=self.device.config.host,
            video=self.video_query,
            audio=self.audio_query,
            event=self.event_query,
            axis_orig_sw="&Axis-Orig-Sw=true"
            if self.device.config.is_companion
            else "",
        )
        _LOGGER.debug(rtsp_url)
        return rtsp_url

    @property
    def websocket_url(self) -> str:
        """Build websocket URL for the VAPIX event stream endpoint."""
        ws_proto = "wss" if self.device.config.web_proto == WebProtocol.HTTPS else "ws"
        url = (
            f"{ws_proto}://{self.device.config.host}:{self.device.config.port}"
            f"{WEBSOCKET_PATH}?sources=events"
        )
        _LOGGER.debug(url)
        return url

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

    @property
    def use_websocket(self) -> bool:
        """Use websocket transport when event websocket API is available."""
        if not self.event:
            return False
        if (
            self._websocket_temporarily_disabled
            and not self.device.config.websocket_force
        ):
            return False
        if self.device.config.websocket_force:
            return True
        return (
            self.device.config.websocket_enabled
            and WebSocketClient.supported_by_device(self.device)
        )

    def _handle_websocket_failure(self) -> None:
        """Disable websocket for runtime when TLS certificate validation fails."""
        if self.device.config.websocket_force:
            return

        if self.stream is None:
            return

        if not getattr(self.stream, "should_disable_runtime_websocket", False):
            return

        if not self._websocket_temporarily_disabled:
            _LOGGER.warning(
                "Disabling websocket events for %s until restart after certificate verification failure",
                self.device.config.host,
            )

        self._websocket_temporarily_disabled = True

    @property
    def _is_stream_stopped(self) -> bool:
        """Return True when stream is missing or currently stopped."""
        return not self.stream or self.stream.session.state == State.STOPPED

    def _build_stream(self) -> StreamTransport:
        """Build transport based on device capabilities and manager settings."""
        if self.use_websocket:
            return WebSocketClient(
                self.device,
                self.websocket_url,
                self.session_callback,
                event_filter_list=self.event_filter_list,
            )

        return RTSPClient(
            self.stream_url,
            self.device.config.host,
            self.device.config.username,
            self.device.config.password,
            self.session_callback,
        )

    def set_event_filter_list(self, event_filter_list: list[dict[str, str]]) -> None:
        """Set optional websocket event filter list for future stream sessions."""
        self.event_filter_list = event_filter_list

    def session_callback(self, signal: Signal) -> None:
        """Signalling from stream session.

        Data - new data available for processing.
        Playing - Connection is healthy.
        Retry - if there is no connection to device.
        """
        if signal == Signal.DATA and self.event:
            self.device.event.handler(self.data)

        elif signal == Signal.FAILED:
            self._handle_websocket_failure()
            self.retry()

        if signal in (Signal.PLAYING, Signal.FAILED):
            for callback in self.connection_status_callback:
                callback(signal)

    @property
    def data(self) -> bytes | dict[str, Any]:
        """Get stream data."""
        if not self.stream:
            return b""
        return self.stream.data

    @property
    def state(self) -> State:
        """State of stream."""
        if not self.stream:
            return State.STOPPED
        return self.stream.session.state

    def start(self) -> None:
        """Start stream."""
        if self._starting:
            return

        if self._is_stream_stopped:
            self._starting = True
            self.stream = self._build_stream()
            task = asyncio.create_task(self.stream.start())
            self.background_tasks.add(task)

            def _on_done(done_task: asyncio.Task[None]) -> None:
                self.background_tasks.discard(done_task)
                self._starting = False

            task.add_done_callback(_on_done)

    def stop(self) -> None:
        """Stop stream."""
        self._starting = False
        if self.stream and not self._is_stream_stopped:
            self.stream.stop()
        self.cancel_retry()

    def retry(self) -> None:
        """No connection to device, retry connection after 15 seconds."""
        self.cancel_retry()
        if self.stream and not self._is_stream_stopped:
            self.stream.stop()

        loop = asyncio.get_running_loop()
        self.stream = None
        self._starting = False
        self.retry_timer = loop.call_later(RETRY_TIMER, self.start)
        _LOGGER.debug("Reconnecting to %s", self.device.config.host)

    def cancel_retry(self) -> None:
        """Cancel scheduled retry."""
        if self.retry_timer is not None:
            self.retry_timer.cancel()
