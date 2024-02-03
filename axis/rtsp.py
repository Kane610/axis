"""Python library to enable Axis devices to integrate with Home Assistant."""

# PYTHON RTSP INSPIRATION
# https://github.com/timohoeting/python-mjpeg-over-rtsp-client/blob/master/rtsp_client.py
# https://github.com/perexg/satip-axe/blob/master/tools/multicast-rtp

import asyncio
from collections import deque
from collections.abc import Callable
import enum
import logging
import socket
from typing import Any

_LOGGER = logging.getLogger(__name__)

RTSP_PORT = 554


class Signal(enum.StrEnum):
    """What is the content of the callback."""

    DATA = "data"
    FAILED = "failed"
    PLAYING = "playing"


class State(enum.StrEnum):
    """State of the connection."""

    PAUSED = "paused"
    PLAYING = "playing"
    STARTING = "starting"
    STOPPED = "stopped"


TIME_OUT_LIMIT = 5


class RTSPClient(asyncio.Protocol):
    """RTSP transport, session handling, message generation."""

    def __init__(
        self,
        url: str,
        host: str,
        username: str,
        password: str,
        callback: Callable[[Signal], None],
    ) -> None:
        """RTSP."""
        self.loop = asyncio.get_running_loop()
        self.callback = callback

        self.rtp = RTPClient(self.loop, callback)

        self.session = RTSPSession(url, host, username, password)
        self.session.rtp_port = self.rtp.port
        self.session.rtcp_port = self.rtp.rtcp_port

        self.method = RTSPMethods(self.session)

        self.transport: asyncio.BaseTransport | None = None
        self.keep_alive_handle: asyncio.TimerHandle | None = None
        self.time_out_handle: asyncio.TimerHandle | None = None

    async def start(self) -> None:
        """Start RTSP session."""
        await self.rtp.start()

        try:
            await self.loop.create_connection(
                lambda: self, self.session.host, self.session.port
            )
        except OSError as err:
            _LOGGER.debug("RTSP got exception %s", err)
            self.stop()
            self.callback(Signal.FAILED)

    def stop(self) -> None:
        """Stop session."""
        self.session.stop()
        if self.transport:
            self.transport.write(self.method.message.encode())  # type: ignore [attr-defined]
            self.transport.close()
        self.rtp.stop()

        if self.keep_alive_handle is not None:
            self.keep_alive_handle.cancel()

        if self.time_out_handle is not None:
            self.time_out_handle.cancel()

    def connection_made(self, transport: asyncio.BaseTransport) -> None:
        """Connect to device is successful.

        Start configuring RTSP session.
        Schedule time out handle in case device doesn't respond.
        """
        self.transport = transport
        self.transport.write(self.method.message.encode())  # type: ignore [attr-defined]
        self.time_out_handle = self.loop.call_later(TIME_OUT_LIMIT, self.time_out)

    def data_received(self, data: bytes) -> None:
        """Got response on RTSP session.

        Manage time out handle since response came in a reasonable time.
        Update session parameters with latest response.
        If state is playing schedule keep-alive.
        """
        self.time_out_handle.cancel()  # type: ignore [union-attr]
        self.session.update(data.decode())

        if self.session.state == State.STARTING:
            self.transport.write(self.method.message.encode())  # type: ignore [union-attr]
            self.time_out_handle = self.loop.call_later(TIME_OUT_LIMIT, self.time_out)

        elif self.session.state == State.PLAYING:
            self.callback(Signal.PLAYING)

            if self.session.session_timeout != 0:
                interval = self.session.session_timeout - 5
                self.keep_alive_handle = self.loop.call_later(interval, self.keep_alive)

        else:
            self.stop()

    def keep_alive(self) -> None:
        """Keep RTSP session alive per negotiated time interval."""
        self.transport.write(self.method.message.encode())  # type: ignore [union-attr]
        self.time_out_handle = self.loop.call_later(TIME_OUT_LIMIT, self.time_out)

    def time_out(self) -> None:
        """If we don't get a response within time the RTSP request time out.

        This usually happens if device isn't available on specified IP.
        """
        _LOGGER.warning("Response timed out %s", self.session.host)
        self.stop()
        self.callback(Signal.FAILED)

    def connection_lost(self, exc: Exception | None) -> None:
        """Happens when device closes connection or stop() has been called."""
        _LOGGER.debug("RTSP session lost connection")


class RTPClient:
    """Data connection to device.

    When data is received send a signal on callback to whoever is interested.
    """

    def __init__(
        self, loop: Any, callback: Callable[[Signal], None] | None = None
    ) -> None:
        """Configure and bind socket.

        We need to bind the port for RTSP before setting up the endpoint
        since it will block until a connection has been set up and
        the port is needed for setting up the RTSP session.
        """
        self.loop = loop
        self.client = self.UDPClient(callback)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("", 0))
        self.port = self.sock.getsockname()[1]
        self.rtcp_port = self.port + 1

    async def start(self) -> None:
        """Start RTP client."""
        await self.loop.create_datagram_endpoint(lambda: self.client, sock=self.sock)

    def stop(self) -> None:
        """Close transport from receiving any more packages."""
        if self.client.transport:
            self.client.transport.close()

    @property
    def data(self) -> bytes:
        """Refer to most recently received data."""
        try:
            return self.client.data.popleft()
        except IndexError:
            return b""

    class UDPClient:
        """Datagram recepient for device data."""

        def __init__(self, callback: Callable[[Signal], None] | None) -> None:
            """Signal events to subscriber using callback."""
            self.callback = callback
            self.data: deque[bytes] = deque()
            self.transport: asyncio.BaseTransport | None = None

        def connection_made(self, transport: asyncio.BaseTransport) -> None:
            """Execute when port is up and listening.

            Save reference to transport for future control.
            """
            _LOGGER.debug("Stream listener online")
            self.transport = transport

        def connection_lost(self, exc: Exception | None) -> None:
            """Signal retry if RTSP session fails to get a response."""
            _LOGGER.debug("Stream recepient offline")

        def datagram_received(self, data: bytes, addr: Any) -> None:
            """Signals when new data is available."""
            if self.callback:
                self.data.append(data[12:])
                self.callback(Signal.DATA)


class RTSPSession:
    """All RTSP session data.

    Stores device stream configuration and session data.
    """

    def __init__(self, url: str, host: str, username: str, password: str) -> None:
        """Session parameters."""
        self._basic_auth: str | None = None
        self.sequence = 0

        self.url = url
        self.host = host
        self.port = RTSP_PORT
        self.username = username
        self.password = password
        self.user_agent = "HASS Axis"
        self.rtp_port = None
        self.rtcp_port = None
        self.methods = [
            "OPTIONS",
            "DESCRIBE",
            "SETUP",
            "PLAY",
            "KEEP-ALIVE",
            "TEARDOWN",
        ]

        # Information as part of ack from device
        self.rtsp_version: int | None = None
        self.status_code: int | None = None
        self.status_text: str | None = None
        self.sequence_ack: int | None = None
        self.date: str | None = None
        self.methods_ack: list[str] | None = None
        self.basic = False
        self.digest = False
        self.realm: str | None = None
        self.nonce: str | None = None
        self.stale: bool | None = None
        self.content_type: str | None = None
        self.content_base: str | None = None
        self.content_length: int | None = None
        self.session_id: str | None = None
        self.session_timeout = 0
        self.transport_ack: str | None = None
        self.range: str | None = None
        self.rtp_info: str | None = None
        self.sdp: list[str] | None = None
        self.control_url: str | None = None

    @property
    def method(self) -> str:
        """Which method the sequence number corresponds to.

        0 - OPTIONS
        1 - DESCRIBE
        2 - SETUP
        3 - PLAY
        4 - KEEP-ALIVE (OPTIONS)
        5 - TEARDOWN
        """
        return self.methods[self.sequence]

    @property
    def state(self) -> State:
        """Which state the session is in.

        Starting - all messages needed to get stream started.
        Playing - keep-alive messages every self.session_timeout.
        """
        if self.method in ["OPTIONS", "DESCRIBE", "SETUP", "PLAY"]:
            return State.STARTING
        if self.method in ["KEEP-ALIVE"]:
            return State.PLAYING
        return State.STOPPED

    def update(self, response: str) -> None:
        """Update session information from device response.

        Increment sequence number when starting stream, not when playing.
        If device requires authentication resend previous message with auth.
        """
        data = response.splitlines()
        _LOGGER.debug("Received data %s from %s", data, self.host)
        while data:
            line = data.pop(0)
            if "RTSP/1.0" in line:
                self.rtsp_version = int(line.split(" ")[0][5])
                self.status_code = int(line.split(" ")[1])
                self.status_text = line.split(" ")[2]
            elif "CSeq" in line:
                self.sequence_ack = int(line.split(": ")[1])
            elif "Date" in line:
                self.date = line.split(": ")[1]
            elif "Public" in line:
                self.methods_ack = line.split(": ")[1].split(", ")
            elif "WWW-Authenticate: Basic" in line:
                self.basic = True
                self.realm = line.split('"')[1]
            elif "WWW-Authenticate: Digest" in line:
                self.digest = True
                self.realm = line.split('"')[1]
                self.nonce = line.split('"')[3]
                self.stale = line.split("stale=")[1] == "TRUE"
            elif "Content-Type" in line:
                self.content_type = line.split(": ")[1]
            elif "Content-Base" in line:
                self.content_base = line.split(": ")[1]
            elif "Content-Length" in line:
                self.content_length = int(line.split(": ")[1])
            elif "Session" in line:
                self.session_id = line.split(": ")[1].split(";")[0]
                if "=" in line:
                    self.session_timeout = int(line.split(": ")[1].split("=")[1])
            elif "Transport" in line:
                self.transport_ack = line.split(": ")[1]
            elif "Range" in line:
                self.range = line.split(": ")[1]
            elif "RTP-Info" in line:
                self.rtp_info = line.split(": ")[1]
            elif not line:
                if data:
                    self.sdp = data
                    break
        if self.sdp:
            stream_found = False
            for param in self.sdp:
                if not stream_found and "m=application" in param:
                    stream_found = True
                elif stream_found and "a=control:rtsp" in param:
                    self.control_url = param.split(":", 1)[1]
                    break

        if self.status_code == 200:
            if self.state == State.STARTING:
                self.sequence += 1
        elif self.status_code == 401:
            # Device requires authorization, do not increment to next method
            pass
        else:
            # If device configuration is correct we should never get here
            _LOGGER.debug(
                "%s RTSP %s %s", self.host, self.status_code, self.status_text
            )

    def generate_digest(self) -> str:
        """RFC 2617."""
        from hashlib import md5

        ha1 = f"{self.username}:{self.realm}:{self.password}"
        HA1 = md5(ha1.encode("UTF-8")).hexdigest()
        ha2 = f"{self.method}:{self.url}"
        HA2 = md5(ha2.encode("UTF-8")).hexdigest()
        encrypt_response = f"{HA1}:{self.nonce}:{HA2}"
        response = md5(encrypt_response.encode("UTF-8")).hexdigest()

        digest_auth = "Digest "
        digest_auth += f'username="{self.username}", '
        digest_auth += f'realm="{self.realm}", '
        digest_auth += 'algorithm="MD5", '
        digest_auth += f'nonce="{self.nonce}", '
        digest_auth += f'uri="{self.url}", '
        digest_auth += f'response="{response}"'
        return digest_auth

    def generate_basic(self) -> str:
        """RFC 2617."""
        from base64 import b64encode

        if not self._basic_auth:
            creds = f"{self.username}:{self.password}"
            self._basic_auth = "Basic "
            self._basic_auth += b64encode(creds.encode("UTF-8")).decode("UTF-8")
        return self._basic_auth

    def stop(self) -> None:
        """Set session to stopped."""
        self.sequence = 5


class RTSPMethods:
    """Generate RTSP messages based on session data."""

    def __init__(self, session: RTSPSession) -> None:
        """Define message methods."""
        self.session = session
        self.message_methods: dict[str, Callable[[], str]] = {
            "OPTIONS": self.OPTIONS,
            "DESCRIBE": self.DESCRIBE,
            "SETUP": self.SETUP,
            "PLAY": self.PLAY,
            "KEEP-ALIVE": self.KEEP_ALIVE,
            "TEARDOWN": self.TEARDOWN,
        }

    @property
    def message(self) -> str:
        """Return RTSP method based on sequence number from session."""
        message = self.message_methods[self.session.method]()
        _LOGGER.debug(message)
        return message

    def KEEP_ALIVE(self) -> str:
        """Keep-Alive messages doesn't need authentication."""
        return self.OPTIONS(False)

    def OPTIONS(self, authenticate: bool = True) -> str:
        """Request options device supports."""
        message = f"OPTIONS {self.session.url} RTSP/1.0\r\n"
        message += self.sequence
        message += self.authentication if authenticate else ""
        message += self.user_agent
        message += self.session_id
        message += "\r\n"
        return message

    def DESCRIBE(self) -> str:
        """Request description of what services RTSP server make available."""
        message = f"DESCRIBE {self.session.url} RTSP/1.0\r\n"
        message += self.sequence
        message += self.authentication
        message += self.user_agent
        message += "Accept: application/sdp\r\n"
        message += "\r\n"
        return message

    def SETUP(self) -> str:
        """Set up stream transport."""
        message = f"SETUP {self.session.control_url} RTSP/1.0\r\n"
        message += self.sequence
        message += self.authentication
        message += self.user_agent
        message += self.transport
        message += "\r\n"
        return message

    def PLAY(self) -> str:
        """RTSP session is ready to send data."""
        message = f"PLAY {self.session.url} RTSP/1.0\r\n"
        message += self.sequence
        message += self.authentication
        message += self.user_agent
        message += self.session_id
        message += "\r\n"
        return message

    def TEARDOWN(self) -> str:
        """Tell device to tear down session."""
        message = f"TEARDOWN {self.session.url} RTSP/1.0\r\n"
        message += self.sequence
        message += self.authentication
        message += self.user_agent
        message += self.session_id
        message += "\r\n"
        return message

    @property
    def sequence(self) -> str:
        """Generate sequence string."""
        return f"CSeq: {str(self.session.sequence)}\r\n"

    @property
    def authentication(self) -> str:
        """Generate authentication string."""
        if self.session.digest:
            authentication = self.session.generate_digest()
        elif self.session.basic:
            authentication = self.session.generate_basic()
        else:
            return ""
        return f"Authorization: {authentication}\r\n"

    @property
    def user_agent(self) -> str:
        """Generate user-agent string."""
        return f"User-Agent: {self.session.user_agent}\r\n"

    @property
    def session_id(self) -> str:
        """Generate session string."""
        if self.session.session_id:
            return f"Session: {self.session.session_id}\r\n"
        return ""

    @property
    def transport(self) -> str:
        """Generate transport string."""
        return f"Transport: RTP/AVP;unicast;client_port={self.session.rtp_port}-{self.session.rtcp_port}\r\n"
