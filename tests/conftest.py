"""Setup common test helpers."""

import asyncio
from collections import deque
from dataclasses import dataclass, field
import json as jsonlib
import logging
from typing import Any
from urllib.parse import urlencode

import aiohttp
from aiohttp import web
import pytest
from yarl import URL

from axis.device import AxisDevice
from axis.models.configuration import Configuration

LOGGER = logging.getLogger(__name__)

HOST = "127.0.0.1"
USER = "root"
PASS = "pass"
RTSP_PORT = 8888


class MockCallList(list["MockCall"]):
    """List-like container that exposes the latest call."""

    @property
    def last(self) -> MockCall:
        """Return latest call in collection."""
        return self[-1]


@dataclass(slots=True)
class MockURL:
    """HTTP URL details expected by tests."""

    path: str
    params: dict[str, str]
    query: bytes


@dataclass(slots=True)
class MockRequest:
    """Recorded HTTP request details expected by tests."""

    method: str
    url: MockURL
    headers: dict[str, str]
    content: bytes


@dataclass(slots=True)
class MockCall:
    """Container for a request made to a mocked route."""

    request: MockRequest


@dataclass(slots=True)
class MockResponseSpec:
    """Response details returned by mocked routes."""

    status_code: int = 200
    headers: dict[str, str] = field(default_factory=dict)
    content: bytes = b""


def _normalize_path_target(path: str) -> tuple[str, dict[str, str] | None]:
    """Normalize a route target into path and optional query dict."""
    if path.startswith(("http://", "https://")):
        parsed = URL(path)
        target_path = parsed.path
        query = dict(parsed.query)
    else:
        parsed = URL(path if path else "/")
        target_path = "" if path == "" else parsed.path
        query = dict(parsed.query)

    if target_path and not target_path.startswith("/"):
        target_path = f"/{target_path}"

    if path == "":
        target_path = ""

    return target_path, query if query else None


class AiohttpRoute:
    """Route registration compatible with the subset used in tests."""

    def __init__(
        self,
        method: str,
        path: str,
        *,
        path_in: tuple[str, ...] | list[str] | None = None,
    ) -> None:
        """Initialize route matcher and state."""
        self.method = method.upper()
        self.path = path
        self.path_in = set(path_in or [])
        self._normalized_path, self._normalized_query = _normalize_path_target(path)
        self.calls: MockCallList = MockCallList()
        self._response = MockResponseSpec()
        self._side_effect: Any = None

    @property
    def called(self) -> bool:
        """Indicate whether route has been called."""
        return bool(self.calls)

    @property
    def call_count(self) -> int:
        """Return number of calls for route."""
        return len(self.calls)

    @property
    def side_effect(self) -> Any:
        """Return configured side effect."""
        return self._side_effect

    @side_effect.setter
    def side_effect(self, value: Any) -> None:
        """Set side effect behavior for this route."""
        self._side_effect = value

    def mock(self, side_effect: Any) -> AiohttpRoute:
        """Set side effect and return route for chaining."""
        self._side_effect = side_effect
        return self

    def respond(
        self,
        status_code: int | None = None,
        *,
        json: Any | None = None,
        text: str | None = None,
        content: bytes | None = None,
        headers: dict[str, str] | None = None,
    ) -> AiohttpRoute:
        """Configure static response for this route."""
        response_headers = dict(headers or {})
        if json is not None:
            body = jsonlib.dumps(json).encode("utf-8")
            response_headers.setdefault("Content-Type", "application/json")
        elif text is not None:
            body = text.encode("utf-8")
        elif content is not None:
            body = content
        else:
            body = b""

        self._response = MockResponseSpec(
            status_code=200 if status_code is None else status_code,
            headers=response_headers,
            content=body,
        )
        self._side_effect = None
        return self

    def matches(self, method: str, path: str, query: dict[str, str]) -> bool:
        """Return whether route matches request details."""
        if method.upper() != self.method:
            return False

        if self.path_in:
            return path in self.path_in

        if self._normalized_path == "":
            return path in {"", "/"}

        if path != self._normalized_path:
            return False

        if self._normalized_query is None:
            return True

        return query == self._normalized_query

    def next_response(self) -> MockResponseSpec:
        """Resolve side effects and produce the next response."""
        outcome = self._side_effect
        if isinstance(outcome, list):
            if not outcome:
                return self._response
            item = outcome.pop(0)
            return self._convert_side_effect_item(item)

        if outcome is None:
            return self._response

        return self._convert_side_effect_item(outcome)

    def _convert_side_effect_item(self, item: Any) -> MockResponseSpec:
        """Convert side effect item to response or raise it."""
        if isinstance(item, MockResponseSpec):
            return item

        if isinstance(item, dict):
            status_code = int(item.get("status_code", 200))
            headers = dict(item.get("headers", {}))
            content = item.get("content", b"")
            if isinstance(content, str):
                content = content.encode("utf-8")
            return MockResponseSpec(
                status_code=status_code, headers=headers, content=content
            )

        if isinstance(item, type) and issubclass(item, Exception):
            raise item()

        if isinstance(item, Exception):
            raise item

        if callable(item):
            value = item()
            return self._convert_side_effect_item(value)

        return self._response


class AiohttpRespxMock:
    """aiohttp-backed mock router with a respx-like test API."""

    def __init__(self) -> None:
        """Initialize route collections."""
        self._routes: list[AiohttpRoute] = []
        self.calls: MockCallList = MockCallList()

    def __call__(self, base_url: str | None = None) -> AiohttpRespxMock:
        """Support no-op base_url calls used by tests."""
        return self

    def get(self, path: str, **kwargs: Any) -> AiohttpRoute:
        """Register a GET route."""
        return self._add_route("GET", path, **kwargs)

    def post(self, path: str, **kwargs: Any) -> AiohttpRoute:
        """Register a POST route."""
        return self._add_route("POST", path, **kwargs)

    def _add_route(self, method: str, path: str, **kwargs: Any) -> AiohttpRoute:
        """Create route and add it to this router."""
        path_in: tuple[str, ...] | list[str] | None = kwargs.get("path__in")
        route = AiohttpRoute(method, path, path_in=path_in)
        self._routes.append(route)
        return route

    async def handler(self, request: web.Request) -> web.Response:
        """Handle incoming aiohttp requests for all registered routes."""
        request_content = await request.read()
        request_path = request.rel_url.path
        request_query = dict(request.rel_url.query)
        route = self._find_route(request.method, request_path, request_query)

        if route is None:
            return web.Response(status=404, body=b"No mocked route matched")

        call = MockCall(
            request=MockRequest(
                method=request.method,
                url=MockURL(
                    path=request_path,
                    params=request_query,
                    query=urlencode(request_query).encode("utf-8"),
                ),
                headers=dict(request.headers),
                content=request_content,
            )
        )
        route.calls.append(call)
        self.calls.append(call)

        response = route.next_response()
        return web.Response(
            status=response.status_code,
            headers=response.headers,
            body=response.content,
        )

    def _find_route(
        self, method: str, path: str, query: dict[str, str]
    ) -> AiohttpRoute | None:
        """Find matching route in registration order."""
        for route in self._routes:
            if route.matches(method, path, query):
                return route
        return None


@pytest.fixture
async def respx_mock(aiohttp_server: Any) -> AiohttpRespxMock:
    """Provide aiohttp-backed mock router compatible with respx usage in tests."""
    router = AiohttpRespxMock()
    app = web.Application()
    app.router.add_route("*", "/{tail:.*}", router.handler)
    server = await aiohttp_server(app)

    router.server = server
    router.host = HOST
    router.port = server.port
    return router


@pytest.fixture
async def axis_device(respx_mock: AiohttpRespxMock) -> AxisDevice:
    """Return the axis device.

    Clean up sessions automatically at the end of each test.
    """
    session = aiohttp.ClientSession()
    axis_device = AxisDevice(
        Configuration(
            session,
            HOST,
            username=USER,
            password=PASS,
            port=respx_mock.port,
        )
    )
    yield axis_device
    await session.close()


@pytest.fixture
async def axis_companion_device(respx_mock: AiohttpRespxMock) -> AxisDevice:
    """Return the axis device.

    Clean up sessions automatically at the end of each test.
    """
    session = aiohttp.ClientSession()
    axis_device = AxisDevice(
        Configuration(
            session,
            HOST,
            username=USER,
            password=PASS,
            port=respx_mock.port,
            is_companion=True,
        )
    )
    yield axis_device
    await session.close()


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
