"""Setup common test helpers."""

import asyncio
from collections import deque
import logging
from typing import TYPE_CHECKING

from aiohttp import ClientSession, web
import pytest

from axis.device import AxisDevice
from axis.models.configuration import Configuration

if TYPE_CHECKING:
    from collections.abc import Callable

LOGGER = logging.getLogger(__name__)

HOST = "127.0.0.1"
USER = "root"
PASS = "pass"
RTSP_PORT = 8888


@pytest.fixture
async def aiohttp_session() -> ClientSession:
    """Return a reusable aiohttp session for tests."""
    session = ClientSession()
    yield session
    await session.close()


@pytest.fixture
async def axis_device_aiohttp(aiohttp_session: ClientSession) -> AxisDevice:
    """Return an AxisDevice backed by aiohttp ClientSession."""
    return AxisDevice(
        Configuration(aiohttp_session, HOST, username=USER, password=PASS)
    )


@pytest.fixture
async def axis_companion_device_aiohttp(aiohttp_session: ClientSession) -> AxisDevice:
    """Return a companion AxisDevice backed by aiohttp ClientSession."""
    return AxisDevice(
        Configuration(
            aiohttp_session,
            HOST,
            username=USER,
            password=PASS,
            is_companion=True,
        )
    )


@pytest.fixture
def aiohttp_request_capture() -> tuple[
    list[dict[str, str]], Callable[..., Callable[[web.Request], web.Response]]
]:
    """Return request log and a handler factory for aiohttp_server routes."""
    requests: list[dict[str, str]] = []

    def make_handler(
        *,
        status: int = 200,
        body: bytes = b"",
        text: str | None = None,
        headers: dict[str, str] | None = None,
    ):
        async def _handler(request: web.Request) -> web.Response:
            requests.append(
                {
                    "method": request.method,
                    "path": request.path,
                    "query": request.query_string,
                }
            )
            if text is not None:
                return web.Response(status=status, text=text, headers=headers)

            return web.Response(status=status, body=body, headers=headers)

        return _handler

    return requests, make_handler


@pytest.fixture
async def axis_device(aiohttp_session: ClientSession) -> AxisDevice:
    """Return the axis device.

    Clean up sessions automatically at the end of each test.
    """
    return AxisDevice(
        Configuration(aiohttp_session, HOST, username=USER, password=PASS)
    )


@pytest.fixture
async def axis_companion_device(aiohttp_session: ClientSession) -> AxisDevice:
    """Return the axis device.

    Clean up sessions automatically at the end of each test.
    """
    return AxisDevice(
        Configuration(
            aiohttp_session,
            HOST,
            username=USER,
            password=PASS,
            is_companion=True,
        )
    )


class TcpServerProtocol(asyncio.Protocol):
    """Simple socket server that responds with preset responses."""

    def __init__(self) -> None:
        """Initialize TCP protocol server."""
        self._response_queue: deque[str] = deque()
        self.requests: list[str] = []
        self.next_request_received = asyncio.Event()

    def register_response(self, response: str) -> None:
        """Take a single response as an argument and queue it."""
        self._response_queue.append(response)

    def register_responses(self, responses: list[str]) -> None:
        """Take a list of responses as an argument and queue them."""
        self._response_queue.extend(responses)

    def connection_made(self, transport) -> None:
        """Successful connection."""
        peername = transport.get_extra_info("peername")
        LOGGER.info("Server connection from %s", peername)
        self.transport = transport

    def data_received(self, data: bytes) -> None:
        """Received a request from a client.

        If test is waiting on next request to be received it can now continue.
        """
        message = data.decode()
        self.requests.append(message)
        LOGGER.info("Server received: %s", repr(message))
        self.next_request_received.set()

    def send_response(self, response: str) -> None:
        """Send response to client.

        Clear event so test can wait on next request to be received.
        """
        LOGGER.info("Server response: %s", repr(response))
        self.transport.write(response.encode())
        self.next_request_received.clear()

    def step_response(self) -> None:
        """Send next response in queue."""
        response = self._response_queue.popleft()
        self.send_response(response)

    @property
    def last_request(self) -> str:
        """Return last request."""
        return self.requests[-1]

    def stop(self) -> None:
        """Stop server."""
        self.transport.close()


@pytest.fixture
async def rtsp_server() -> TcpServerProtocol:
    """Return the RTSP server."""
    loop = asyncio.get_running_loop()
    mock_server = TcpServerProtocol()
    server = await loop.create_server(lambda: mock_server, HOST, RTSP_PORT)

    async def run_server():
        """Run server until transport is closed."""
        async with server:
            await server.serve_forever()

    server_task = loop.create_task(run_server())

    yield mock_server

    server_task.cancel()
