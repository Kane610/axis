"""Setup common test helpers."""

import asyncio
from collections import deque
from contextlib import suppress
import logging
from typing import TYPE_CHECKING

from aiohttp import ClientSession, web
import pytest

from axis.device import AxisDevice
from axis.models.configuration import Configuration

from tests.http_route_mock import HttpRouteMock, start_http_route_mock_server

if TYPE_CHECKING:
    from collections.abc import Callable

LOGGER = logging.getLogger(__name__)

HOST = "127.0.0.1"
USER = "root"
PASS = "pass"
RTSP_PORT = 8888


# ---------------------------------------------------------------------------
# Session fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
async def aiohttp_session() -> ClientSession:
    """Return a reusable aiohttp session for tests."""
    session = ClientSession()
    yield session
    await session.close()


# ---------------------------------------------------------------------------
# Device fixtures
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# HTTP mocking infrastructure
#
# Three layers, each suited to a different case:
#   aiohttp_request_capture  - raw handler/response testing with request log
#   aiohttp_mock_server      - direct handler or static-payload tests
#   http_route_mock          - route-registration tests (single device)
#   http_route_mock_factory  - route-registration tests (multi-device or explicit)
# ---------------------------------------------------------------------------


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
def aiohttp_mock_server(aiohttp_server):
    """Consolidated mock server factory eliminating boilerplate app/router setup.

    Supports single/multiple routes, request capture, automatic device port binding.
    Consolidates 53+ instances of web.Application() boilerplate across test suite.

    Usage examples:

    # Simple single route with request capture:
    server, requests = await aiohttp_mock_server(
        "/api/endpoint",
        handler=async_handler_func
    )

    # Multiple routes:
    server, requests = await aiohttp_mock_server(
        {"/path1": async_handler1, "/path2": async_handler2}
    )

    # With automatic device config binding (accepts AxisDevice or Vapix):
    server, requests = await aiohttp_mock_server(
        "/api/method",
        handler=async_handler_func,
        device=axis_device,  # auto-sets device.config.port
    )

    # Response specs (replaces manual handler definition):
    server, requests = await aiohttp_mock_server(
        {
            "/api/list": {"method": "POST", "response": {"data": []}},
            "/api/status": {"method": "GET", "response": "ok"},
        }
    )
    """

    async def _create_mock_server(
        routes: dict[str, dict[str, object]] | str,
        *,
        handler: (Callable[[web.Request], web.Response] | None) = None,
        method: str = "POST",
        response: dict[str, object] | str | bytes | None = None,
        status: int = 200,
        headers: dict[str, str] | None = None,
        device: object | None = None,
        capture_requests: bool = True,
        capture_payload: bool = False,
        capture_body: bool = False,
    ):
        """Create consolidated mock server with route specs and optional request capture.

        Args:
            routes: single path str or dict of {path: spec_dict or callable}
            handler: callable handler (if routes is string path)
            method: HTTP method for single route (default POST)
            response: response data for auto-handler (JSON dict, text str, or bytes)
            status: HTTP status code
            headers: response headers
            device: optional AxisDevice or Vapix to auto-bind server.port
            capture_requests: if True, return captured requests list
            capture_payload: if True, capture request body/JSON (eliminates manual payload reading)
            capture_body: if True, capture raw request bytes as "body"

        Returns:
            (server, requests_list) or (server, None) if capture_requests=False

        """
        requests: list[dict[str, object]] = [] if capture_requests else None

        def make_auto_handler(resp_data, resp_status, resp_headers):
            """Create handler from response spec (eliminates manual handler code)."""

            async def _auto_handler(request: web.Request) -> web.Response:
                if requests is not None:
                    req_entry: dict[str, object] = {
                        "method": request.method,
                        "path": request.path,
                        "query": request.query_string or "",
                    }
                    if capture_body and request.method in ("POST", "PUT", "PATCH"):
                        with suppress(ValueError, RuntimeError):
                            req_entry["body"] = await request.read()
                    # Capture request payload if enabled
                    if capture_payload and request.method in ("POST", "PUT", "PATCH"):
                        try:
                            if request.content_type == "application/json":
                                req_entry["payload"] = await request.json()
                            else:
                                # For other content types, capture as text
                                req_entry["payload"] = await request.text()
                        except ValueError, RuntimeError:
                            # Skip payload if reading fails (e.g., already consumed)
                            pass
                    requests.append(req_entry)

                if isinstance(resp_data, dict):
                    return web.json_response(resp_data, status=resp_status)
                if isinstance(resp_data, str):
                    return web.Response(
                        text=resp_data,
                        status=resp_status,
                        headers=resp_headers,
                    )
                if isinstance(resp_data, bytes):
                    return web.Response(
                        body=resp_data,
                        status=resp_status,
                        headers=resp_headers,
                    )
                return web.Response(status=resp_status, headers=resp_headers)

            return _auto_handler

        app = web.Application()

        # Handle single path string with handler arg
        if isinstance(routes, str):
            path = routes
            if handler is not None:
                app.router.add_route(method.upper(), path, handler)
            elif response is not None:
                app.router.add_route(
                    method.upper(),
                    path,
                    make_auto_handler(response, status, headers),
                )
        # Handle dict of routes
        else:
            for path, route_spec in routes.items():
                if callable(route_spec):
                    # route_spec is a handler function
                    app.router.add_post(path, route_spec)
                elif isinstance(route_spec, dict):
                    # route_spec is {method, response, status, headers}
                    route_method = route_spec.get("method", "POST").upper()
                    route_response = route_spec.get("response")
                    route_status = route_spec.get("status", 200)
                    route_headers = route_spec.get("headers")
                    if route_response is not None:
                        app.router.add_route(
                            route_method,
                            path,
                            make_auto_handler(
                                route_response, route_status, route_headers
                            ),
                        )

        server = await aiohttp_server(app)

        if device is not None:
            # Support AxisDevice, Vapix, and ApiHandler (handlers have .vapix.device)
            if hasattr(device, "vapix"):
                # It's an ApiHandler → device.vapix.device.config
                device.vapix.device.config.port = server.port
            elif hasattr(device, "device"):
                # It's a Vapix → device.device.config
                device.device.config.port = server.port
            else:
                # It's an AxisDevice → device.config
                device.config.port = server.port

        return server, requests

    return _create_mock_server


@pytest.fixture
def http_route_mock_factory(aiohttp_mock_server) -> HttpRouteMock:
    """Return an HttpRouteMock factory bound to one or more devices.

    Use for multi-device tests or when http_route_mock (single-device) is insufficient.

    Example::

        async def test_multi(http_route_mock_factory, device_a, device_b):
            mock = await http_route_mock_factory(device_a, device_b)
            mock.post("/axis-cgi/example.cgi").respond(json={"data": []})
    """

    async def _factory(*devices) -> HttpRouteMock:
        return await start_http_route_mock_server(aiohttp_mock_server, *devices)

    return _factory


@pytest.fixture
async def http_route_mock(
    http_route_mock_factory, axis_device_aiohttp: AxisDevice
) -> HttpRouteMock:
    """Single-device HttpRouteMock auto-bound to axis_device_aiohttp.

    Use for common route-registration tests against a single device.
    For multi-device tests use http_route_mock_factory instead.

    Example::

        async def test_example(http_route_mock):
            http_route_mock.post("/axis-cgi/example.cgi").respond(json={"data": []})
    """
    return await http_route_mock_factory(axis_device_aiohttp)


# ---------------------------------------------------------------------------
# Network protocol fixtures
# ---------------------------------------------------------------------------


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
