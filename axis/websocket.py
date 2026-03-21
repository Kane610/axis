"""Websocket event stream transport for Axis devices.

Implements the VAPIX Event Streaming over WebSocket API:
https://developer.axis.com/vapix/network-video/event-streaming-over-websocket/

Authentication uses a short-lived session token obtained from wssession.cgi.
After connecting, an ``events:configure`` JSON-RPC call subscribes to events.
Incoming ``events:notify`` JSON messages are parsed into the internal event
dict format accepted by EventManager.handler().
"""

from __future__ import annotations

import asyncio
from collections import deque
import logging
from time import time
from typing import TYPE_CHECKING, Any

import aiohttp
import orjson

from .models.api_discovery import ApiId
from .models.event import (
    EVENT_SOURCE,
    EVENT_SOURCE_IDX,
    EVENT_TOPIC,
    EVENT_TYPE,
    EVENT_VALUE,
)
from .rtsp import Signal, State

if TYPE_CHECKING:
    from collections.abc import Callable

    from .device import AxisDevice

_LOGGER = logging.getLogger(__name__)

WEBSOCKET_PATH = "/vapix/ws-data-stream"
WSSESSION_PATH = "/axis-cgi/wssession.cgi"
API_VERSION = "1.0"
CONTEXT = "axis-py"
HEARTBEAT_INTERVAL = 15  # Send ping every 15 seconds to keep connection fresh
RECEIVE_TIMEOUT = (
    60  # Allow 60 seconds for device to respond (heartbeat + network margin)
)
BUFFER_SIZE = 200


def _parse_ws_notification(notification: dict[str, Any]) -> dict[str, Any]:
    """Parse a VAPIX events:notify notification into the internal event dict format.

    The websocket notification structure::

        {
            "topic": "tns1:Device/tnsaxis:IO/VirtualPort",
            "message": {
                "source": {"port": "1"},
                "key": {},
                "data": {"state": "0"}
            }
        }

    is mapped to the same dict keys used by Event._decode_from_dict().
    """
    topic = notification.get("topic", "")
    message = notification.get("message") or {}
    source_dict = message.get("source") or {}
    data_dict = message.get("data") or {}

    source, source_idx = next(iter(source_dict.items()), ("", ""))
    data_type, data_value = next(iter(data_dict.items()), ("", ""))

    return {
        EVENT_TOPIC: topic,
        EVENT_SOURCE: source,
        EVENT_SOURCE_IDX: str(source_idx),
        EVENT_TYPE: data_type,
        EVENT_VALUE: str(data_value),
    }


class WebSocketSession:
    """Session state for websocket event stream."""

    def __init__(self) -> None:
        """Initialize websocket session."""
        self.state: State = State.STOPPED


class WebSocketClient:
    """VAPIX websocket event stream client.

    Connects to ``/vapix/ws-data-stream?sources=events``, authenticates
    using a session token from ``/axis-cgi/wssession.cgi``, sends
    ``events:configure`` to subscribe, and converts ``events:notify``
    JSON messages into the internal event dict format.
    """

    def __init__(
        self,
        device: AxisDevice,
        url: str,
        callback: Callable[[Signal], None],
        event_filter_list: list[dict[str, str]] | None = None,
    ) -> None:
        """Create websocket transport.

        Args:
            device: Axis device with Vapix access for session-token auth.
            url: Base websocket URL, e.g. ``ws://host/vapix/ws-data-stream?sources=events``.
            callback: Invoked on Signal events (PLAYING, DATA, FAILED).
            event_filter_list: ONVIF topic/content filter list sent with
                ``events:configure``.  Defaults to ``[{"topicFilter": "//."}]``
                which subscribes to all events.

        """
        self.device = device
        self.url = url
        self.callback = callback
        self.event_filter_list: list[dict[str, str]] = event_filter_list or [
            {"topicFilter": "//."}
        ]
        self._configure_payload = {
            "apiVersion": API_VERSION,
            "context": CONTEXT,
            "method": "events:configure",
            "params": {"eventFilterList": self.event_filter_list},
        }
        self._ws_timeout = aiohttp.ClientWSTimeout(ws_receive=RECEIVE_TIMEOUT)

        self.loop = asyncio.get_running_loop()
        self.session = WebSocketSession()
        self._data: deque[dict[str, Any]] = deque(maxlen=BUFFER_SIZE)

        self._ws_session: aiohttp.ClientSession | None = None
        self._ws: aiohttp.ClientWebSocketResponse | None = None
        self._receiver_task: asyncio.Task[None] | None = None
        self._close_task: asyncio.Task[None] | None = None
        self._stopped = False
        self._starting = False
        self._start_time: float | None = None

    @classmethod
    def supported_by_device(cls, device: AxisDevice) -> bool:
        """Return True if the device advertises websocket event streaming."""
        return ApiId.EVENT_STREAMING_OVER_WEBSOCKET in device.vapix.api_discovery

    @property
    def data(self) -> dict[str, Any]:
        """Return and remove the next parsed event notification from the buffer."""
        try:
            return self._data.popleft()
        except IndexError:
            return {}

    async def _get_session_token(self) -> str | None:
        """Obtain a short-lived session token for websocket authentication.

        Calls GET /axis-cgi/wssession.cgi via the existing Vapix session
        (which already has proper digest/basic auth configured).  The returned
        token is valid for 15 seconds and must be used before it expires.
        """
        try:
            raw = await self.device.vapix.request("get", WSSESSION_PATH)
            return raw.decode("ascii").strip()
        except Exception as err:  # noqa: BLE001
            _LOGGER.debug("Could not obtain wssession token: %s", err)
            return None

    async def start(self) -> None:
        """Open the websocket connection, configure events, and start the receiver."""
        if self._starting or self.session.state != State.STOPPED:
            return

        self._starting = True
        self._stopped = False
        self.session.state = State.STARTING
        self._start_time = time()

        try:
            if self._close_task is not None:
                await asyncio.shield(self._close_task)

            token = await self._get_session_token()
            if token:
                connect_url = f"{self.url}&wssession={token}"
                self._ws_session = aiohttp.ClientSession()
            else:
                # Fall back to HTTP Basic auth in the upgrade handshake.
                connect_url = self.url
                self._ws_session = aiohttp.ClientSession(
                    auth=aiohttp.BasicAuth(
                        self.device.config.username,
                        self.device.config.password,
                    ),
                )

            self._ws = await self._ws_session.ws_connect(
                connect_url,
                heartbeat=HEARTBEAT_INTERVAL,
                timeout=self._ws_timeout,
            )
        except (aiohttp.ClientError, TimeoutError, OSError) as err:
            _LOGGER.warning("Websocket connect failed: %s", err)
            await self._close()
            self.session.state = State.STOPPED
            self._signal(Signal.FAILED)
            return
        finally:
            self._starting = False

        # Subscribe to events before reporting PLAYING.
        try:
            await self._configure()
        except (aiohttp.ClientError, TimeoutError, OSError, ValueError) as err:
            _LOGGER.warning("Websocket configure failed: %s", err)
            await self._close()
            self.session.state = State.STOPPED
            self._signal(Signal.FAILED)
            return

        self.session.state = State.PLAYING
        self._signal(Signal.PLAYING)
        self._receiver_task = self.loop.create_task(self._receiver())

    async def _configure(self) -> None:
        """Send events:configure and wait for the acknowledge response.

        Raises:
            aiohttp.ClientError: on transport errors or a non-OK configure response.
            TimeoutError: if the device does not respond within TIME_OUT_LIMIT seconds.
            ValueError: if the response JSON cannot be decoded.

        """
        if self._ws is None:
            return

        await self._send_configure_payload(self._configure_payload)

    async def _send_configure_payload(self, payload: dict[str, Any]) -> None:
        """Send a configure payload and validate the immediate response."""
        if self._ws is None:
            return

        await self._ws.send_json(payload)

        response_msg = await asyncio.wait_for(
            self._ws.receive(), timeout=RECEIVE_TIMEOUT
        )
        if response_msg.type != aiohttp.WSMsgType.TEXT:
            err_msg = f"Expected TEXT websocket frame during configure, got {response_msg.type}"
            raise aiohttp.ClientError(err_msg)

        response = orjson.loads(response_msg.data)
        if "error" in response:
            err_info = response["error"]
            err_msg = (
                f"events:configure error {err_info.get('code')}: "
                f"{err_info.get('message')}"
            )
            raise aiohttp.ClientError(err_msg)

    def stop(self) -> None:
        """Stop the websocket session."""
        if self._stopped:
            return

        self._stopped = True
        self.session.state = State.STOPPED

        if self._receiver_task is not None:
            self._receiver_task.cancel()
            self._receiver_task = None

        self._close_task = self.loop.create_task(self._close())

    async def _receiver(self) -> None:
        """Receive websocket messages and dispatch events:notify payloads."""
        if self._ws is None:
            return

        try:
            async for msg in self._ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    self._handle_message(msg.data)
                    continue

                if msg.type == aiohttp.WSMsgType.BINARY:
                    _LOGGER.warning("Unexpected binary websocket frame")
                    break

                if msg.type in (
                    aiohttp.WSMsgType.CLOSE,
                    aiohttp.WSMsgType.CLOSED,
                    aiohttp.WSMsgType.CLOSING,
                    aiohttp.WSMsgType.ERROR,
                ):
                    break

        except (aiohttp.ClientError, TimeoutError, OSError) as err:
            duration = (
                f"{time() - self._start_time:.1f}s" if self._start_time else "unknown"
            )
            _LOGGER.warning(
                "Websocket receive error (%s): %s | Connected for: %s | Buffered events: %d/%d",
                type(err).__name__,
                err,
                duration,
                len(self._data),
                BUFFER_SIZE,
                exc_info=True,
            )

        finally:
            self._start_time = None
            await self._close()
            self.session.state = State.STOPPED
            if not self._stopped:
                self._signal(Signal.FAILED)

    def _handle_message(self, data: str) -> None:
        """Parse a JSON websocket frame and dispatch events:notify messages."""
        try:
            msg = orjson.loads(data)
        except orjson.JSONDecodeError:
            _LOGGER.debug("Ignoring non-JSON websocket frame")
            return

        if msg.get("method") != "events:notify":
            return

        notification = (msg.get("params") or {}).get("notification") or {}
        if not notification:
            return

        parsed = _parse_ws_notification(notification)
        self._data.append(parsed)
        self._signal(Signal.DATA)

    async def _close(self) -> None:
        """Close websocket connection and session (idempotent)."""
        if self._ws is not None:
            await self._ws.close()
            self._ws = None

        if self._ws_session is not None:
            await self._ws_session.close()
            self._ws_session = None

    def _signal(self, signal: Signal) -> None:
        """Invoke the signal callback, swallowing any exceptions."""
        try:
            self.callback(signal)
        except Exception:  # pragma: no cover
            _LOGGER.exception("Websocket callback raised for signal %s", signal)
