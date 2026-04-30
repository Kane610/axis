"""HTTP route mock backed by aiohttp_mock_server for migrated tests.

Route registration and dispatch behavior lives here.
Fixture exposure (http_route_mock_factory, http_route_mock) lives in conftest.py.
"""

from types import SimpleNamespace

from aiohttp import web
import httpx

from axis.errors import Forbidden, MethodNotAllowed, PathNotFound, Unauthorized

from tests.mock_device_binding import bind_device_port
from tests.mock_response_builder import build_response


class CallList(list):
    """List of captured calls with a respx-like `.last` shortcut."""

    @property
    def last(self):
        """Return the most recent captured call."""
        return self[-1]


class Route:
    """Single route registration and response behavior."""

    def __init__(self, method: str, path: str) -> None:
        """Initialize a route registration for one method/path pair."""
        self.method = method
        self.path = path
        self.called = False
        self.calls = CallList()
        self.side_effect: object | None = None
        self._json: dict | list | None = None
        self._text: str | None = None
        self._content: bytes | None = None
        self._status_code = 200
        self._headers: dict[str, str] | None = None

    @property
    def call_count(self) -> int:
        """Return number of times this route was invoked."""
        return len(self.calls)

    def respond(
        self,
        *args: object,
        json: dict | list | None = None,
        text: str | None = None,
        content: bytes | None = None,
        status_code: int = 200,
        headers: dict[str, str] | None = None,
        **_: object,
    ):
        """Configure static response for route.

        Supports `.respond(401)` shorthand and keyword args.
        """
        if args:
            status_code = int(args[0])
        self._json = json
        self._text = text
        self._content = content
        self._status_code = status_code
        self._headers = headers
        return self

    def make_response(self) -> web.Response:
        """Build aiohttp response from configured route state."""
        response_data = self._json
        if response_data is None:
            response_data = self._text
        if response_data is None:
            response_data = self._content
        return build_response(
            response_data,
            status=self._status_code,
            headers=self._headers,
        )


class MultiRoute:
    """Route bundle used for path__in registrations."""

    def __init__(self, routes: list[Route]) -> None:
        """Initialize grouped routes for bulk response configuration."""
        self._routes = routes

    def respond(self, *args: object, **kwargs: object):
        """Apply same response configuration to all grouped routes."""
        for route in self._routes:
            route.respond(*args, **kwargs)
        return self


class HttpRouteMock:
    """HTTP route mock backed by aiohttp test server."""

    def __init__(self) -> None:
        """Initialize route registry and global call history."""
        self._routes: dict[tuple[str, str], Route] = {}
        self.calls = CallList()

    def _add_route(self, method: str, path: str) -> Route:
        if path == "":
            path = "/"
        key = (method, path)
        if key in self._routes:
            return self._routes[key]
        route = Route(method, path)
        self._routes[key] = route
        return route

    def _register(
        self,
        method: str,
        path: str,
        *,
        path__in: tuple[str, ...] | None = None,
        **_: object,
    ) -> Route | MultiRoute:
        if path__in:
            routes = [self._add_route(method, alt_path) for alt_path in path__in]
            return MultiRoute(routes)
        return self._add_route(method, path)

    def post(
        self,
        path: str,
        *,
        path__in: tuple[str, ...] | None = None,
        **kwargs: object,
    ) -> Route | MultiRoute:
        """Register POST route."""
        return self._register("POST", path, path__in=path__in, **kwargs)

    def get(self, path: str, **kwargs: object) -> Route:
        """Register GET route."""
        route = self._register("GET", path, **kwargs)
        assert isinstance(route, Route)
        return route

    def resolve(self, method: str, path: str) -> Route | None:
        """Resolve route for incoming request."""
        return self._routes.get((method, path))


def _matches_exception_type(candidate: object, exc_type: type[BaseException]) -> bool:
    return isinstance(candidate, exc_type) or (
        isinstance(candidate, type) and issubclass(candidate, exc_type)
    )


def _raise_known_http_error(side_effect: object, request: web.Request) -> bool:
    if _matches_exception_type(side_effect, Unauthorized):
        raise web.HTTPUnauthorized
    if _matches_exception_type(side_effect, Forbidden):
        raise web.HTTPForbidden
    if _matches_exception_type(side_effect, PathNotFound):
        raise web.HTTPNotFound
    if _matches_exception_type(side_effect, MethodNotAllowed):
        raise web.HTTPMethodNotAllowed(
            method=request.method, allowed_methods=[request.method]
        )
    return False


def _raise_transport_failure(side_effect: object, request: web.Request) -> bool:
    if (
        _matches_exception_type(side_effect, httpx.TimeoutException)
        or _matches_exception_type(
            side_effect,
            httpx.TransportError,
        )
        or _matches_exception_type(side_effect, httpx.RequestError)
    ):
        if request.transport is not None:
            request.transport.close()
        message = "request failed"
        raise ConnectionResetError(message)
    return False


def _raise_side_effect(side_effect: object, request: web.Request) -> None:
    _raise_transport_failure(side_effect, request)
    _raise_known_http_error(side_effect, request)

    if isinstance(side_effect, BaseException):
        raise side_effect

    if isinstance(side_effect, type) and issubclass(side_effect, BaseException):
        try:
            raise side_effect()
        except TypeError as err:
            message = "request failed"
            raise side_effect(message) from err

    if callable(side_effect):
        raise side_effect()


async def start_http_route_mock_server(
    aiohttp_mock_server,
    *devices,
) -> HttpRouteMock:
    """Start catch-all aiohttp server that dispatches to HttpRouteMock routes."""
    mock = HttpRouteMock()

    async def handle_request(request: web.Request) -> web.Response:
        route = mock.resolve(request.method, request.path)
        if route is None:
            return web.Response(status=404)

        if route.side_effect is not None:
            _raise_side_effect(route.side_effect, request)

        route.called = True
        content = await request.read()
        params = dict(request.rel_url.query)
        call = SimpleNamespace(
            request=SimpleNamespace(
                method=request.method,
                url=SimpleNamespace(path=request.path, params=params),
                content=content,
            )
        )
        route.calls.append(call)
        mock.calls.append(call)
        return route.make_response()

    server, _requests = await aiohttp_mock_server(
        "/{tail:.*}",
        handler=handle_request,
        method="*",
        capture_requests=False,
    )

    for device in devices:
        bind_device_port(device, server.port)

    return mock
