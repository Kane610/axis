"""Shared fixtures for device tests and mock HTTP servers."""

from __future__ import annotations

import asyncio
from collections import deque
from contextlib import suppress
from dataclasses import dataclass
import logging
from typing import TYPE_CHECKING, Any
from urllib.parse import urlencode

from aiohttp import ClientSession, web
import pytest

from axis.device import AxisDevice
from axis.models.configuration import Configuration

from tests.http_route_mock import HttpRouteMock, Route, start_http_route_mock_server
from tests.mock_device_binding import bind_device_port
from tests.mock_response_builder import build_response

if TYPE_CHECKING:
    from collections.abc import Callable

    from axis.models.api import ApiRequest

LOGGER = logging.getLogger(__name__)

HOST = "127.0.0.1"
USER = "root"
PASS = "pass"
RTSP_PORT = 8888

MOCK_API_REQUEST_SUPPORTED_METHODS = frozenset({"GET", "POST"})
MOCK_API_REQUEST_DIRECT_CONTENT_TYPES = frozenset(
    {"application/json", "text/plain", "text/xml"}
)
MOCK_API_REQUEST_EXPLICIT_RESPONSE_CONTENT_TYPES = frozenset({"application/soap+xml"})


# ---------------------------------------------------------------------------
# Session fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
async def session() -> ClientSession:
    """Return a reusable aiohttp session for tests."""
    session = ClientSession()
    yield session
    await session.close()


# ---------------------------------------------------------------------------
# Device fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
async def axis_device(session: ClientSession) -> AxisDevice:
    """Return an AxisDevice backed by aiohttp ClientSession."""
    return AxisDevice(Configuration(session, HOST, username=USER, password=PASS))


@pytest.fixture
async def axis_companion_device(session: ClientSession) -> AxisDevice:
    """Return a companion AxisDevice backed by aiohttp ClientSession."""
    return AxisDevice(
        Configuration(
            session,
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
#   aiohttp_mock_server      - direct handler or static-payload tests
#   http_route_mock          - route-registration tests (single device)
#   http_route_mock_factory  - route-registration tests (multi-device or explicit)
#
# Selection guidance:
#   - Prefer http_route_mock when tests interact through vapix route methods.
#   - Use http_route_mock_factory when a test needs explicit mock lifetime control
#     or binds routes to more than one AxisDevice instance.
#   - Use aiohttp_mock_server for low-level handler assertions, payload capture,
#     or custom request processing not modeled by route registration.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class MockApiResponseSpec:
    """Explicit response configuration for mock_api_request.

    Use this when the response shape should not be inferred from the request
    content type, or when a request class uses an explicit-only content type
    such as SOAP/XML envelopes.
    """

    json: dict[str, Any] | list[Any] | None = None
    text: str | None = None
    content: bytes | None = None
    status_code: int = 200
    headers: dict[str, str] | None = None


@dataclass(frozen=True)
class MockApiRequestAssertions:
    """Optional request assertions for mock_api_request.

    Prefer these hooks when a test should verify params, headers, or encoded
    request bodies without dropping down to raw route-level plumbing.
    """

    content: bytes | str | dict[str, str] | None = None
    params: dict[str, str] | None = None
    headers: dict[str, str] | None = None


@pytest.fixture(name="mock_api_request")
def api_request_fixture(
    http_route_mock: HttpRouteMock,
) -> Callable[..., Route]:
    """Register an HTTP mock route for an ApiRequest class.

    The fixture supports GET and POST requests with JSON, plain-text, or XML
    content types. Pass an explicit response spec for other content types.
    Use it for tests focused on one request model. Use ``http_route_mock`` for
    multiple routes, custom side effects, or transport-level behavior.
    """
    supported_methods = {
        "GET": http_route_mock.get,
        "POST": http_route_mock.post,
    }

    def _respond_from_spec(route: Route, response: MockApiResponseSpec) -> Route:
        payload_count = sum(
            value is not None
            for value in (response.json, response.text, response.content)
        )
        if payload_count > 1:
            msg = (
                "MockApiResponseSpec accepts only one payload kind: "
                "json, text, or content"
            )
            raise ValueError(msg)

        return route.respond(
            json=response.json,
            text=response.text,
            content=response.content,
            status_code=response.status_code,
            headers=response.headers,
        )

    def _normalize_expected_content(
        content: bytes | str | dict[str, str] | None,
    ) -> bytes | None:
        if content is None:
            return None
        if isinstance(content, bytes):
            return content
        if isinstance(content, str):
            return content.encode()
        return urlencode(content).encode()

    def _apply_assertions(route: Route, assertions: MockApiRequestAssertions) -> None:
        expected_content = _normalize_expected_content(assertions.content)

        def _validate_request(request: Any) -> None:
            if (
                assertions.params is not None
                and request.url.params != assertions.params
            ):
                msg = f"Expected params {assertions.params}, got {request.url.params}"
                raise AssertionError(msg)

            if assertions.headers is not None:
                for header_name, expected_value in assertions.headers.items():
                    actual_value = request.headers.get(header_name)
                    if actual_value != expected_value:
                        msg = (
                            f"Expected header {header_name}={expected_value}, "
                            f"got {actual_value}"
                        )
                        raise AssertionError(msg)

            if expected_content is not None and request.content != expected_content:
                msg = f"Expected content {expected_content!r}, got {request.content!r}"
                raise AssertionError(msg)

        route.expect_request(_validate_request)

    def _register_route(
        api_request: type[ApiRequest],
        response_data: Any = None,
        *,
        response: MockApiResponseSpec | None = None,
        assertions: MockApiRequestAssertions | None = None,
    ) -> Route:
        if not isinstance(api_request.method, str) or not api_request.method.strip():
            msg = "ApiRequest.method must be a non-empty string"
            raise ValueError(msg)

        method = api_request.method.strip().upper()
        if method not in MOCK_API_REQUEST_SUPPORTED_METHODS:
            msg = (
                f"Unsupported method: {api_request.method}. "
                f"Supported methods: {', '.join(sorted(supported_methods))}"
            )
            raise ValueError(msg)

        content_type = api_request.content_type
        if (
            response is None
            and content_type not in MOCK_API_REQUEST_DIRECT_CONTENT_TYPES
        ):
            msg = (
                f"Unsupported content type: {content_type}. "
                "Provide an explicit MockApiResponseSpec response for unsupported "
                "content types. Direct mapping supports: "
                f"{', '.join(sorted(MOCK_API_REQUEST_DIRECT_CONTENT_TYPES))}"
            )
            raise ValueError(msg)

        if response is not None and response_data is not None:
            msg = "Pass either response_data or response, not both"
            raise ValueError(msg)

        route = supported_methods[method](api_request.path)
        if response is not None:
            route = _respond_from_spec(route, response)
        elif content_type == "application/json":
            route = route.respond(json=response_data)
        elif content_type in {"text/plain", "text/xml"}:
            route = route.respond(text=response_data)
        else:
            msg = "Unsupported fixture state"
            raise RuntimeError(msg)

        if assertions is not None:
            _apply_assertions(route, assertions)

        return route

    return _register_route


def bind_mock_api_request(
    mock_api_request: Callable[..., Route],
    api_request: type[ApiRequest],
) -> Callable[..., Route]:
    """Return a helper that registers responses for one ApiRequest class.

    This lets each test module expose a small, clearly named request fixture.
    """

    def _bound(
        response_data: Any = None,
        *,
        response: MockApiResponseSpec | None = None,
        assertions: MockApiRequestAssertions | None = None,
    ) -> Route:
        return mock_api_request(
            api_request,
            response_data,
            response=response,
            assertions=assertions,
        )

    return _bound


class TcpServerProtocol(asyncio.Protocol):
    """TCP test server that records requests and sends queued responses."""

    def __init__(self) -> None:
        """Create an empty response queue and request notification event."""
        self._response_queue: deque[str] = deque()
        self.requests: list[str] = []
        self.next_request_received = asyncio.Event()

    def register_response(self, response: str) -> None:
        """Queue one response for the next client request."""
        self._response_queue.append(response)

    def register_responses(self, responses: list[str]) -> None:
        """Queue responses in the order they should be sent."""
        self._response_queue.extend(responses)

    def connection_made(self, transport) -> None:
        """Save the transport when a client connects."""
        peername = transport.get_extra_info("peername")
        LOGGER.info("Server connection from %s", peername)
        self.transport = transport

    def data_received(self, data: bytes) -> None:
        """Record received request data and notify any waiting test."""
        message = data.decode()
        self.requests.append(message)
        LOGGER.info("Server received: %s", repr(message))
        self.next_request_received.set()

    def send_response(self, response: str) -> None:
        """Send a response and clear the request notification event."""
        LOGGER.info("Server response: %s", repr(response))
        self.transport.write(response.encode())
        self.next_request_received.clear()

    def step_response(self) -> None:
        """Send and remove the next queued response."""
        response = self._response_queue.popleft()
        self.send_response(response)

    @property
    def last_request(self) -> str:
        """Return the most recently received request."""
        return self.requests[-1]

    def stop(self) -> None:
        """Close the client transport."""
        self.transport.close()


@pytest.fixture
def aiohttp_mock_server(aiohttp_server):
    """Start an HTTP mock server with optional request capture and device binding.

    A single route can use a handler or a fixed response. Multiple routes can be
    supplied as a mapping. Passing a device updates its configured port to match
    the server. Route specifications may also define a method and response.

    Example with a handler:
    server, requests = await aiohttp_mock_server(
        "/api/endpoint",
        handler=async_handler_func
    )

    Example with multiple routes:
    server, requests = await aiohttp_mock_server(
        {"/path1": async_handler1, "/path2": async_handler2}
    )

    Example with automatic device port binding:
    server, requests = await aiohttp_mock_server(
        "/api/method",
        handler=async_handler_func,
        device=axis_device,  # auto-sets device.config.port
    )

    Example with response specifications:
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
        """Start the server and optionally record requests and their bodies.

        Args:
            routes: One path or a mapping of paths to handlers or response specs.
            handler: Handler to use when ``routes`` is a single path.
            method: Method to use for a single route (defaults to POST).
            response: Fixed JSON, text, or byte response for the route.
            status: HTTP status code for the response.
            headers: Headers to include in the response.
            device: Device whose configured port should match the mock server.
            capture_requests: Whether to return a list of received requests.
            capture_payload: Whether to capture parsed request payloads.
            capture_body: Whether to capture raw request bytes.

        Returns:
            The running server and captured requests, or ``None`` for requests
            when capture is disabled.

        """
        requests: list[dict[str, object]] | None = [] if capture_requests else None

        def make_auto_handler(resp_data, resp_status, resp_headers):
            """Build a handler that returns the configured response."""

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
                        except (ValueError, RuntimeError) as err:
                            # Skip payload if reading fails (e.g., already consumed)
                            LOGGER.debug(
                                "Skipping payload capture due to read error: %s", err
                            )
                    requests.append(req_entry)

                return build_response(
                    resp_data,
                    status=resp_status,
                    headers=resp_headers,
                )

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
            bind_device_port(device, server.port)

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
    http_route_mock_factory, axis_device: AxisDevice
) -> HttpRouteMock:
    """Single-device HttpRouteMock auto-bound to axis_device.

    Use for common route-registration tests against a single device.
    For multi-device tests use http_route_mock_factory instead.

    Example::

        async def test_example(http_route_mock):
            http_route_mock.post("/axis-cgi/example.cgi").respond(json={"data": []})
    """
    return await http_route_mock_factory(axis_device)


# ---------------------------------------------------------------------------
# Network protocol fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
async def rtsp_server() -> TcpServerProtocol:
    """Start a local TCP server that sends queued RTSP responses."""
    loop = asyncio.get_running_loop()
    mock_server = TcpServerProtocol()
    server = await loop.create_server(lambda: mock_server, HOST, RTSP_PORT)

    async def run_server():
        """Serve RTSP requests until the test closes the server."""
        async with server:
            await server.serve_forever()

    server_task = loop.create_task(run_server())

    yield mock_server

    server_task.cancel()
