"""Setup common test helpers."""

import asyncio
from collections import deque
import logging

from httpx import AsyncClient
import pytest
import respx

from axis.device import AxisDevice
from axis.models.configuration import Configuration

LOGGER = logging.getLogger(__name__)

HOST = "127.0.0.1"
USER = "root"
PASS = "pass"
RTSP_PORT = 8888


@pytest.fixture
async def axis_device(respx_mock: respx.router.MockRouter) -> AxisDevice:
    """Return the axis device.

    Clean up sessions automatically at the end of each test.
    """
    respx_mock(base_url=f"http://{HOST}:80")
    session = AsyncClient(verify=False)
    axis_device = AxisDevice(Configuration(session, HOST, username=USER, password=PASS))
    yield axis_device
    await session.aclose()


@pytest.fixture
async def axis_companion_device(respx_mock: respx.router.MockRouter) -> AxisDevice:
    """Return the axis device.

    Clean up sessions automatically at the end of each test.
    """
    respx_mock(base_url=f"http://{HOST}:80")
    session = AsyncClient(verify=False)
    axis_device = AxisDevice(
        Configuration(session, HOST, username=USER, password=PASS, is_companion=True)
    )
    yield axis_device
    await session.aclose()


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
