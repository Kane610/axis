"""Test Vapix network API main class.

pytest --cov-report term-missing --cov=axis.vapix tests/test_vapix.py
"""

from types import SimpleNamespace
from typing import TYPE_CHECKING

from aiohttp import web
import httpx
import pytest

from axis.errors import (
    Forbidden,
    MethodNotAllowed,
    PathNotFound,
    RequestError,
    Unauthorized,
)
from axis.interfaces.api_handler import HandlerGroup
from axis.models.applications.application import ApplicationStatus
from axis.models.pwdgrp_cgi import SecondaryGroup
from axis.models.stream_profile import StreamProfile

from .applications.test_applications import (
    LIST_APPLICATIONS_RESPONSE as APPLICATIONS_RESPONSE,
)
from .applications.test_fence_guard import (
    GET_CONFIGURATION_RESPONSE as FENCE_GUARD_RESPONSE,
)
from .applications.test_loitering_guard import (
    GET_CONFIGURATION_RESPONSE as LOITERING_GUARD_RESPONSE,
)
from .applications.test_motion_guard import (
    GET_CONFIGURATION_RESPONSE as MOTION_GUARD_RESPONSE,
)
from .applications.test_vmd4 import GET_CONFIGURATION_RESPONSE as VMD4_RESPONSE
from .event_fixtures import EVENT_INSTANCES
from .parameters.test_param_cgi import PARAM_RESPONSE as PARAM_CGI_RESPONSE
from .test_api_discovery import GET_API_LIST_RESPONSE as API_DISCOVERY_RESPONSE
from .test_basic_device_info import (
    GET_ALL_PROPERTIES_RESPONSE as BASIC_DEVICE_INFO_RESPONSE,
)
from .test_light_control import GET_LIGHT_INFORMATION_RESPONSE as LIGHT_CONTROL_RESPONSE
from .test_port_management import GET_PORTS_RESPONSE as IO_PORT_MANAGEMENT_RESPONSE
from .test_stream_profiles import LIST_RESPONSE as STREAM_PROFILE_RESPONSE

if TYPE_CHECKING:
    from axis.device import AxisDevice
    from axis.interfaces.vapix import Vapix


class _CallList(list):
    @property
    def last(self):
        return self[-1]


class _Route:
    def __init__(self, method: str, path: str) -> None:
        self.method = method
        self.path = path
        self.called = False
        self.calls = _CallList()
        self.side_effect: object | None = None
        self._json: dict | list | None = None
        self._text: str | None = None
        self._content: bytes | None = None
        self._status_code = 200
        self._headers: dict[str, str] | None = None

    @property
    def call_count(self) -> int:
        return len(self.calls)

    def respond(
        self,
        *args: object,
        json: dict | list | None = None,
        text: str | None = None,
        content: bytes | None = None,
        status_code: int = 200,
        headers: dict[str, str] | None = None,
    ):
        if args:
            # Supports patterns like .respond(401)
            status_code = int(args[0])
        self._json = json
        self._text = text
        self._content = content
        self._status_code = status_code
        self._headers = headers
        return self

    def make_response(self) -> web.Response:
        if self._json is not None:
            return web.json_response(
                self._json,
                status=self._status_code,
                headers=self._headers,
            )
        if self._text is not None:
            return web.Response(
                text=self._text,
                status=self._status_code,
                headers=self._headers,
            )
        if self._content is not None:
            return web.Response(
                body=self._content,
                status=self._status_code,
                headers=self._headers,
            )
        return web.Response(status=self._status_code, headers=self._headers)


class _MultiRoute:
    def __init__(self, routes: list[_Route]) -> None:
        self._routes = routes

    def respond(self, *args: object, **kwargs: object):
        for route in self._routes:
            route.respond(*args, **kwargs)
        return self


class _RespxMockShim:
    def __init__(self) -> None:
        self._routes: dict[tuple[str, str], _Route] = {}
        self.calls = _CallList()

    def _add_route(self, method: str, path: str) -> _Route:
        if path == "":
            path = "/"
        key = (method, path)
        if key in self._routes:
            return self._routes[key]
        route = _Route(method, path)
        self._routes[key] = route
        return route

    def _register(
        self,
        method: str,
        path: str,
        *,
        path__in: tuple[str, ...] | None = None,
        **_: object,
    ) -> _Route | _MultiRoute:
        if path__in:
            routes = [self._add_route(method, alt_path) for alt_path in path__in]
            return _MultiRoute(routes)
        return self._add_route(method, path)

    def post(
        self,
        path: str,
        *,
        path__in: tuple[str, ...] | None = None,
        **kwargs: object,
    ) -> _Route | _MultiRoute:
        return self._register("POST", path, path__in=path__in, **kwargs)

    def get(self, path: str, **kwargs: object) -> _Route:
        route = self._register("GET", path, **kwargs)
        assert isinstance(route, _Route)
        return route

    def resolve(self, method: str, path: str) -> _Route | None:
        return self._routes.get((method, path))


def _raise_side_effect(side_effect: object, request: web.Request) -> None:

    if isinstance(side_effect, BaseException):
        if isinstance(
            side_effect,
            (httpx.TimeoutException, httpx.TransportError, httpx.RequestError),
        ):
            if request.transport is not None:
                request.transport.close()
            message = "request failed"
            raise ConnectionResetError(message)
        if isinstance(side_effect, Unauthorized):
            raise web.HTTPUnauthorized
        if isinstance(side_effect, Forbidden):
            raise web.HTTPForbidden
        if isinstance(side_effect, PathNotFound):
            raise web.HTTPNotFound
        if isinstance(side_effect, MethodNotAllowed):
            raise web.HTTPMethodNotAllowed(
                method=request.method, allowed_methods=[request.method]
            )
        raise side_effect
    if isinstance(side_effect, type) and issubclass(side_effect, BaseException):
        if issubclass(
            side_effect,
            (httpx.TimeoutException, httpx.TransportError, httpx.RequestError),
        ):
            if request.transport is not None:
                request.transport.close()
            message = "request failed"
            raise ConnectionResetError(message)
        if issubclass(side_effect, Unauthorized):
            raise web.HTTPUnauthorized
        if issubclass(side_effect, Forbidden):
            raise web.HTTPForbidden
        if issubclass(side_effect, PathNotFound):
            raise web.HTTPNotFound
        if issubclass(side_effect, MethodNotAllowed):
            raise web.HTTPMethodNotAllowed(
                method=request.method, allowed_methods=[request.method]
            )
        try:
            raise side_effect()
        except TypeError as err:
            message = "request failed"
            raise side_effect(message) from err
    if callable(side_effect):
        raise side_effect()


@pytest.fixture
async def respx_mock(
    aiohttp_server,
    axis_device_aiohttp: AxisDevice,
    axis_companion_device_aiohttp: AxisDevice,
):
    """Return a minimal respx-compatible shim backed by aiohttp_server."""
    mock = _RespxMockShim()

    async def handle_request(request: web.Request) -> web.Response:
        path = request.path
        route = mock.resolve(request.method, path)
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
                url=SimpleNamespace(path=path, params=params),
                content=content,
            )
        )
        route.calls.append(call)
        mock.calls.append(call)
        return route.make_response()

    app = web.Application()
    app.router.add_route("*", "/{tail:.*}", handle_request)
    server = await aiohttp_server(app)
    axis_device_aiohttp.vapix.device.config.port = server.port
    axis_companion_device_aiohttp.vapix.device.config.port = server.port

    return mock


@pytest.fixture
def vapix(axis_device_aiohttp: AxisDevice) -> Vapix:
    """Return the vapix object."""
    return axis_device_aiohttp.vapix


@pytest.fixture
def vapix_companion_device(axis_companion_device_aiohttp: AxisDevice) -> Vapix:
    """Return the vapix object."""
    return axis_companion_device_aiohttp.vapix


def test_vapix_not_initialized(vapix: Vapix) -> None:
    """Test Vapix class without initialising any data."""
    assert dict(vapix.basic_device_info.items()) == {}
    assert list(vapix.basic_device_info.keys()) == []
    assert list(vapix.basic_device_info.values()) == []
    assert vapix.basic_device_info.get("0") is None
    with pytest.raises(KeyError):
        assert vapix.basic_device_info["0"]
    assert iter(vapix.basic_device_info)
    assert vapix.firmware_version == ""
    assert vapix.product_number == ""
    assert vapix.product_type == ""
    assert vapix.serial_number == ""
    assert vapix.streaming_profiles == []
    assert not vapix.users.supported


def test_api_discovery_handlers_registration(vapix: Vapix) -> None:
    """Verify grouped API-discovery handlers matches the startup contract."""
    handlers = vapix._handlers_by_group(HandlerGroup.API_DISCOVERY)

    assert handlers == (
        vapix.basic_device_info,
        vapix.io_port_management,
        vapix.light_control,
        vapix.mqtt,
        vapix.pir_sensor_configuration,
        vapix.stream_profiles,
        vapix.view_areas,
    )


def test_application_handlers_registration(vapix: Vapix) -> None:
    """Verify grouped application handlers matches the startup contract."""
    handlers = vapix._handlers_by_group(HandlerGroup.APPLICATION)

    assert handlers == (
        vapix.fence_guard,
        vapix.loitering_guard,
        vapix.motion_guard,
        vapix.object_analytics,
        vapix.vmd4,
    )


def test_param_fallback_handlers_registration(vapix: Vapix) -> None:
    """Verify grouped param.cgi fallback handlers matches startup contract."""
    handlers = vapix._handlers_by_group(HandlerGroup.PARAM_CGI_FALLBACK)

    assert handlers == (vapix.light_control,)


def test_register_handler_is_idempotent(vapix: Vapix) -> None:
    """Verify duplicate registration does not change group membership."""
    before = vapix._handlers_by_group(HandlerGroup.API_DISCOVERY)

    vapix._register_handler(vapix.basic_device_info)

    assert vapix._handlers_by_group(HandlerGroup.API_DISCOVERY) == before


def test_grouped_handlers_order_is_stable(vapix: Vapix) -> None:
    """Verify grouped handlers preserve deterministic Vapix.__init__ order."""
    first = vapix._handlers_by_group(HandlerGroup.API_DISCOVERY)
    second = vapix._handlers_by_group(HandlerGroup.API_DISCOVERY)

    assert first == second


def test_unassigned_handlers_excluded_from_grouping(vapix: Vapix) -> None:
    """Verify handlers without matching group are not returned."""
    api_handlers = vapix._handlers_by_group(HandlerGroup.API_DISCOVERY)
    app_handlers = vapix._handlers_by_group(HandlerGroup.APPLICATION)
    param_fallback_handlers = vapix._handlers_by_group(HandlerGroup.PARAM_CGI_FALLBACK)

    assert vapix.api_discovery not in api_handlers
    assert vapix.params not in api_handlers
    assert vapix.event_instances not in api_handlers

    assert vapix.api_discovery not in app_handlers
    assert vapix.params not in app_handlers
    assert vapix.event_instances not in app_handlers

    assert vapix.api_discovery not in param_fallback_handlers
    assert vapix.params not in param_fallback_handlers
    assert vapix.event_instances not in param_fallback_handlers


async def test_initialize(respx_mock, vapix: Vapix):
    """Verify that you can initialize all APIs."""
    respx_mock.post("/axis-cgi/apidiscovery.cgi").respond(
        json=API_DISCOVERY_RESPONSE,
    )
    respx_mock.post("/axis-cgi/basicdeviceinfo.cgi").respond(
        json=BASIC_DEVICE_INFO_RESPONSE,
    )
    respx_mock.post("/axis-cgi/io/portmanagement.cgi").respond(
        json=IO_PORT_MANAGEMENT_RESPONSE,
    )
    respx_mock.post("/axis-cgi/lightcontrol.cgi").respond(
        json=LIGHT_CONTROL_RESPONSE,
    )
    respx_mock.post("/axis-cgi/streamprofile.cgi").respond(
        json=STREAM_PROFILE_RESPONSE,
    )
    respx_mock.post("/axis-cgi/viewarea/info.cgi").respond(
        json={
            "apiVersion": "1.0",
            "context": "",
            "method": "list",
            "data": {"viewAreas": []},
        }
    )

    respx_mock.post("/axis-cgi/param.cgi").respond(
        content=PARAM_CGI_RESPONSE.encode("iso-8859-1"),
        headers={"Content-Type": "text/plain; charset=iso-8859-1"},
    )
    respx_mock.post("/axis-cgi/applications/list.cgi").respond(
        text=APPLICATIONS_RESPONSE,
        headers={"Content-Type": "text/xml"},
    )
    respx_mock.post("/local/fenceguard/control.cgi").respond(
        json=FENCE_GUARD_RESPONSE,
    )
    respx_mock.post("/local/loiteringguard/control.cgi").respond(
        json=LOITERING_GUARD_RESPONSE,
    )
    respx_mock.post("/local/motionguard/control.cgi").respond(
        json=MOTION_GUARD_RESPONSE,
    )
    respx_mock.post("/local/vmd/control.cgi").respond(
        json=VMD4_RESPONSE,
    )

    await vapix.initialize()

    assert vapix.api_discovery.initialized
    assert vapix.basic_device_info.initialized
    assert vapix.light_control.initialized
    assert not vapix.mqtt.initialized
    assert vapix.stream_profiles.initialized
    assert vapix.view_areas.initialized

    assert vapix.firmware_version == "9.80.1"
    assert vapix.product_number == "M1065-LW"
    assert vapix.product_type == "Network Camera"
    assert vapix.serial_number == "ACCC12345678"

    assert vapix.fence_guard.initialized
    assert vapix.loitering_guard.initialized
    assert vapix.motion_guard.initialized
    assert not vapix.object_analytics.initialized
    assert vapix.vmd4.initialized


async def test_initialize_api_discovery(respx_mock, vapix: Vapix):
    """Verify that you can initialize API Discovery and that devicelist parameters."""
    respx_mock.post("/axis-cgi/apidiscovery.cgi").respond(
        json=API_DISCOVERY_RESPONSE,
    )
    respx_mock.post("/axis-cgi/basicdeviceinfo.cgi").respond(
        json=BASIC_DEVICE_INFO_RESPONSE,
    )
    respx_mock.post("/axis-cgi/io/portmanagement.cgi").respond(
        json=IO_PORT_MANAGEMENT_RESPONSE,
    )
    respx_mock.post("/axis-cgi/lightcontrol.cgi").respond(
        json=LIGHT_CONTROL_RESPONSE,
    )
    respx_mock.post("/axis-cgi/streamprofile.cgi").respond(
        json=STREAM_PROFILE_RESPONSE,
    )
    respx_mock.post("/axis-cgi/viewarea/info.cgi").respond(
        json={
            "apiVersion": "1.0",
            "context": "",
            "method": "list",
            "data": {"viewAreas": []},
        }
    )

    await vapix.initialize_api_discovery()

    assert vapix.api_discovery
    assert vapix.basic_device_info
    assert vapix.light_control
    assert vapix.mqtt is not None
    assert vapix.stream_profiles
    assert len(vapix.view_areas) == 0

    assert vapix.firmware_version == "9.80.1"
    assert vapix.product_number == "M1065-LW"
    assert vapix.product_type == "Network Camera"
    assert vapix.serial_number == "ACCC12345678"
    assert isinstance(vapix.streaming_profiles[0], StreamProfile)

    assert len(vapix.basic_device_info) == 1
    assert len(vapix.ports) == 1
    assert len(vapix.light_control) == 1
    assert len(vapix.mqtt) == 0
    assert len(vapix.stream_profiles) == 1


async def test_initialize_api_discovery_unauthorized(respx_mock, vapix: Vapix):
    """Test initialize api discovery doesnt break due to exception."""
    respx_mock.post("/axis-cgi/apidiscovery.cgi").respond(
        json=API_DISCOVERY_RESPONSE,
    )
    respx_mock.post(
        "",
        path__in=(
            "/axis-cgi/basicdeviceinfo.cgi",
            "/axis-cgi/io/portmanagement.cgi",
            "/axis-cgi/lightcontrol.cgi",
            "/axis-cgi/mqtt/client.cgi",
            "/axis-cgi/streamprofile.cgi",
            "/axis-cgi/viewarea/info.cgi",
        ),
    ).respond(status_code=401)

    await vapix.initialize_api_discovery()

    assert len(vapix.basic_device_info) == 0
    assert len(vapix.ports) == 0
    assert vapix.ports == vapix.io_port_management
    assert vapix.light_control is not None
    assert vapix.mqtt is not None
    assert len(vapix.stream_profiles) == 0


async def test_initialize_api_discovery_unsupported(respx_mock, vapix: Vapix):
    """Test initialize api discovery doesnt break due to exception."""
    respx_mock.post("/axis-cgi/apidiscovery.cgi").side_effect = PathNotFound

    await vapix.initialize_api_discovery()

    assert len(vapix.api_discovery) == 0


async def test_initialize_param_cgi(respx_mock, vapix: Vapix):
    """Verify that you can list parameters."""
    respx_mock.post("/axis-cgi/param.cgi").respond(
        content=PARAM_CGI_RESPONSE.encode("iso-8859-1"),
        headers={"Content-Type": "text/plain; charset=iso-8859-1"},
    )
    light_control_route = respx_mock.post("/axis-cgi/lightcontrol.cgi").respond(
        json=LIGHT_CONTROL_RESPONSE,
    )
    await vapix.initialize_param_cgi()

    assert light_control_route.called
    assert "Axis-Orig-Sw" not in respx_mock.calls.last.request.url.params
    assert vapix.firmware_version == "9.10.1"
    assert vapix.product_number == "M1065-LW"
    assert vapix.product_type == "Network Camera"
    assert vapix.serial_number == "ACCC12345678"
    assert len(vapix.streaming_profiles) == 2

    assert len(vapix.basic_device_info) == 0
    assert len(vapix.ports.values()) == 1
    assert len(vapix.light_control.values()) == 1
    assert len(vapix.mqtt) == 0
    assert len(vapix.stream_profiles) == 0
    assert len(vapix.params.stream_profile_handler) == 1

    assert vapix.users.supported


async def test_initialize_param_cgi_skips_fallback_when_discovery_supports_api(
    respx_mock, vapix: Vapix
):
    """Verify param fallback does not run for APIs supported by discovery."""
    respx_mock.post("/axis-cgi/apidiscovery.cgi").respond(
        json=API_DISCOVERY_RESPONSE,
    )
    respx_mock.post("/axis-cgi/basicdeviceinfo.cgi").respond(
        json=BASIC_DEVICE_INFO_RESPONSE,
    )
    respx_mock.post("/axis-cgi/io/portmanagement.cgi").respond(
        json=IO_PORT_MANAGEMENT_RESPONSE,
    )
    light_control_route = respx_mock.post("/axis-cgi/lightcontrol.cgi").respond(
        json=LIGHT_CONTROL_RESPONSE,
    )
    respx_mock.post("/axis-cgi/streamprofile.cgi").respond(
        json=STREAM_PROFILE_RESPONSE,
    )
    respx_mock.post("/axis-cgi/viewarea/info.cgi").respond(
        json={
            "apiVersion": "1.0",
            "context": "",
            "method": "list",
            "data": {"viewAreas": []},
        }
    )
    respx_mock.post("/axis-cgi/param.cgi").respond(
        content=PARAM_CGI_RESPONSE.encode("iso-8859-1"),
        headers={"Content-Type": "text/plain; charset=iso-8859-1"},
    )

    await vapix.initialize_api_discovery()
    assert light_control_route.call_count == 1

    await vapix.initialize_param_cgi()
    assert light_control_route.call_count == 1


async def test_initialize_param_cgi_for_companion_device(
    respx_mock, vapix_companion_device: Vapix
):
    """Verify that you can list parameters."""
    respx_mock.post("/axis-cgi/param.cgi").respond(
        content=PARAM_CGI_RESPONSE.encode("iso-8859-1"),
        headers={"Content-Type": "text/plain; charset=iso-8859-1"},
    )
    respx_mock.post("/axis-cgi/lightcontrol.cgi").respond(
        json=LIGHT_CONTROL_RESPONSE,
    )
    await vapix_companion_device.initialize_param_cgi()

    assert "Axis-Orig-Sw" in respx_mock.calls.last.request.url.params

    assert vapix_companion_device.firmware_version == "9.10.1"
    assert vapix_companion_device.product_number == "M1065-LW"
    assert vapix_companion_device.product_type == "Network Camera"
    assert vapix_companion_device.serial_number == "ACCC12345678"
    assert len(vapix_companion_device.streaming_profiles) == 2

    assert len(vapix_companion_device.basic_device_info) == 0
    assert len(vapix_companion_device.ports.values()) == 1
    assert len(vapix_companion_device.light_control.values()) == 1
    assert len(vapix_companion_device.mqtt) == 0
    assert len(vapix_companion_device.stream_profiles) == 0
    assert len(vapix_companion_device.params.stream_profile_handler) == 1

    assert vapix_companion_device.users.supported


async def test_initialize_params_no_data(respx_mock, vapix: Vapix):
    """Verify that you can list parameters."""
    param_route = respx_mock.post("/axis-cgi/param.cgi").respond(
        content="".encode("iso-8859-1"),
        headers={"Content-Type": "text/plain; charset=iso-8859-1"},
    )
    await vapix.initialize_param_cgi(preload_data=False)

    assert param_route.call_count == 4


async def test_initialize_applications(respx_mock, vapix: Vapix):
    """Verify you can list and retrieve descriptions of applications."""
    respx_mock.post("/axis-cgi/param.cgi").respond(
        content=PARAM_CGI_RESPONSE.encode("iso-8859-1"),
        headers={"Content-Type": "text/plain; charset=iso-8859-1"},
    )
    respx_mock.post("/axis-cgi/lightcontrol.cgi").respond(
        json=LIGHT_CONTROL_RESPONSE,
    )
    respx_mock.post("/axis-cgi/applications/list.cgi").respond(
        text=APPLICATIONS_RESPONSE,
        headers={"Content-Type": "text/xml"},
    )
    respx_mock.post("/local/fenceguard/control.cgi").respond(
        json=FENCE_GUARD_RESPONSE,
    )
    respx_mock.post("/local/loiteringguard/control.cgi").respond(
        json=LOITERING_GUARD_RESPONSE,
    )
    respx_mock.post("/local/motionguard/control.cgi").respond(
        json=MOTION_GUARD_RESPONSE,
    )
    respx_mock.post("/local/vmd/control.cgi").respond(
        json=VMD4_RESPONSE,
    )

    await vapix.initialize_param_cgi()
    await vapix.initialize_applications()

    assert vapix.applications
    assert len(vapix.applications.values()) == 7

    assert len(vapix.fence_guard) == 1
    assert len(vapix.loitering_guard) == 1
    assert len(vapix.motion_guard) == 1
    assert len(vapix.object_analytics) == 0
    assert len(vapix.vmd4.values()) == 1


@pytest.mark.parametrize("code", [401, 403])
async def test_initialize_applications_unauthorized(respx_mock, vapix: Vapix, code):
    """Verify initialize applications doesnt break on too low credentials."""
    respx_mock.post("/axis-cgi/param.cgi").respond(
        content=PARAM_CGI_RESPONSE.encode("iso-8859-1"),
        headers={"Content-Type": "text/plain; charset=iso-8859-1"},
    )
    respx_mock.post("/axis-cgi/lightcontrol.cgi").respond(
        json=LIGHT_CONTROL_RESPONSE,
    )
    respx_mock.post("/axis-cgi/applications/list.cgi").respond(status_code=code)

    await vapix.initialize_param_cgi()
    await vapix.initialize_applications()

    assert len(vapix.applications) == 0


async def test_initialize_applications_not_running(respx_mock, vapix: Vapix):
    """Verify you can list and retrieve descriptions of applications."""
    respx_mock.post("/axis-cgi/param.cgi").respond(
        content=PARAM_CGI_RESPONSE.encode("iso-8859-1"),
        headers={"Content-Type": "text/plain; charset=iso-8859-1"},
    )
    respx_mock.post("/axis-cgi/lightcontrol.cgi").respond(
        json=LIGHT_CONTROL_RESPONSE,
    )
    respx_mock.post("/axis-cgi/applications/list.cgi").respond(
        text=APPLICATIONS_RESPONSE.replace(
            ApplicationStatus.RUNNING, ApplicationStatus.STOPPED
        ),
        headers={"Content-Type": "text/xml"},
    )

    await vapix.initialize_param_cgi()
    await vapix.initialize_applications()

    assert not vapix.fence_guard.initialized
    assert not vapix.loitering_guard.initialized
    assert not vapix.motion_guard.initialized
    assert not vapix.object_analytics.initialized
    assert not vapix.vmd4.initialized


async def test_initialize_event_instances(respx_mock, vapix: Vapix):
    """Verify you can list and retrieve descriptions of applications."""
    respx_mock.post("/vapix/services").respond(
        text=EVENT_INSTANCES,
        headers={"Content-Type": "application/soap+xml; charset=utf-8"},
    )

    await vapix.initialize_event_instances()

    assert vapix.event_instances
    assert len(vapix.event_instances) == 44


async def test_applications_dont_load_without_params(respx_mock, vapix: Vapix):
    """Applications depends on param cgi to be loaded first."""
    param_route = respx_mock.post("/axis-cgi/param.cgi").respond(
        content="key=value".encode("iso-8859-1"),
        headers={"Content-Type": "text/plain; charset=iso-8859-1"},
    )
    applications_route = respx_mock.post("/axis-cgi/applications/list.cgi")

    await vapix.initialize_param_cgi(preload_data=False)
    await vapix.initialize_applications()

    assert param_route.call_count == 4
    assert not applications_route.called
    assert not vapix.object_analytics.supported


async def test_initialize_users_fails_due_to_low_credentials(respx_mock, vapix: Vapix):
    """Verify that you can list parameters."""
    respx_mock.post("/axis-cgi/pwdgrp.cgi").respond(401)
    await vapix.initialize_users()
    assert len(vapix.users.values()) == 0


async def test_load_user_groups(respx_mock, vapix: Vapix):
    """Verify that you can load user groups."""
    respx_mock.get("/axis-cgi/usergroup.cgi").respond(
        text="root\nroot admin operator ptz viewer\n",
        headers={"Content-Type": "text/plain"},
    )

    await vapix.load_user_groups()

    user = vapix.user_groups.get("0")
    assert user
    assert user.privileges == SecondaryGroup.ADMIN_PTZ
    assert user.admin
    assert user.operator
    assert user.viewer
    assert user.ptz
    assert vapix.access_rights == SecondaryGroup.ADMIN_PTZ


async def test_load_user_groups_from_pwdgrpcgi(respx_mock, vapix: Vapix):
    """Verify that you can load user groups from pwdgrp.cgi."""
    respx_mock.post("/axis-cgi/pwdgrp.cgi").respond(
        text="""users=
viewer="root"
operator="root"
admin="root"
root="root"
ptz=
""",
        headers={"Content-Type": "text/plain"},
    )
    user_group_route = respx_mock.get("/axis-cgi/usergroup.cgi").respond(
        text="root\nroot admin operator ptz viewer\n",
        headers={"Content-Type": "text/plain"},
    )

    await vapix.initialize_users()
    await vapix.load_user_groups()

    assert not user_group_route.called

    user = vapix.user_groups.get("0")
    assert user
    assert user.privileges == SecondaryGroup.ADMIN
    assert user.admin
    assert user.operator
    assert user.viewer
    assert not user.ptz
    assert vapix.access_rights == SecondaryGroup.ADMIN


async def test_load_user_groups_fails_when_not_supported(respx_mock, vapix: Vapix):
    """Verify that load user groups still initialize class even when not supported."""
    respx_mock.get("/axis-cgi/usergroup.cgi").respond(404)

    await vapix.load_user_groups()

    assert len(vapix.user_groups) == 0
    assert vapix.access_rights == SecondaryGroup.UNKNOWN


async def test_not_loading_user_groups_makes_access_rights_unknown(vapix: Vapix):
    """Verify that not loading user groups still returns a proper string."""
    assert vapix.access_rights == SecondaryGroup.UNKNOWN


@pytest.mark.parametrize(
    ("code", "error"),
    [
        (401, Unauthorized),
        (403, Forbidden),
        (404, PathNotFound),
        (405, MethodNotAllowed),
    ],
)
async def test_request_raises(respx_mock, vapix: Vapix, code, error):
    """Verify that a HTTP error raises the appropriate exception."""
    respx_mock.get("").respond(status_code=code)

    with pytest.raises(error):
        await vapix.request("get", "")


@pytest.mark.parametrize(
    "side_effect", [httpx.TimeoutException, httpx.TransportError, httpx.RequestError]
)
async def test_request_side_effects(respx_mock, vapix: Vapix, side_effect):
    """Test request side effects."""
    respx_mock.get("").side_effect = side_effect

    with pytest.raises(RequestError):
        await vapix.request("get", "")
