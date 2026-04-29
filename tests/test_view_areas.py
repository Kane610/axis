"""Test Axis view area API.

pytest --cov-report term-missing --cov=axis.view_areas tests/test_view_areas.py
"""

import json
from types import SimpleNamespace
from typing import TYPE_CHECKING
from unittest.mock import MagicMock

from aiohttp import web
import pytest

from axis.interfaces.view_areas import Geometry, ViewAreaHandler

if TYPE_CHECKING:
    from axis.device import AxisDevice


class _CallList(list):
    @property
    def last(self):
        return self[-1]


class _Route:
    def __init__(self, path: str) -> None:
        self.path = path
        self.called = False
        self.calls = _CallList()
        self._json: dict | list | None = None
        self._text: str | None = None
        self._content: bytes | None = None
        self._status_code = 200
        self._headers: dict[str, str] | None = None

    def respond(
        self,
        *,
        json: dict | list | None = None,
        text: str | None = None,
        content: bytes | None = None,
        status_code: int = 200,
        headers: dict[str, str] | None = None,
    ):
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


class _RespxMockShim:
    def __init__(self) -> None:
        self._routes: dict[tuple[str, str], _Route] = {}

    def post(self, path: str) -> _Route:
        route = _Route(path)
        self._routes[("POST", path)] = route
        return route

    def resolve(self, method: str, path: str) -> _Route | None:
        return self._routes.get((method, path))


@pytest.fixture
async def respx_mock(aiohttp_server, axis_device_aiohttp: AxisDevice):
    """Return a minimal respx-compatible shim backed by aiohttp_server."""
    mock = _RespxMockShim()

    async def handle_request(request: web.Request) -> web.Response:
        route = mock.resolve(request.method, request.path)
        if route is None:
            return web.Response(status=404)

        route.called = True
        content = await request.read()
        route.calls.append(
            SimpleNamespace(
                request=SimpleNamespace(
                    method=request.method,
                    url=SimpleNamespace(path=request.path),
                    content=content,
                )
            )
        )
        return route.make_response()

    app = web.Application()
    app.router.add_route("*", "/{tail:.*}", handle_request)
    server = await aiohttp_server(app)
    axis_device_aiohttp.vapix.device.config.port = server.port

    return mock


@pytest.fixture
def view_areas(axis_device_aiohttp: AxisDevice) -> ViewAreaHandler:
    """Return the view_areas mock object."""
    axis_device_aiohttp.vapix.api_discovery = api_discovery_mock = MagicMock()
    api_discovery_mock.__getitem__().version = "1.0"
    return axis_device_aiohttp.vapix.view_areas


async def test_list_view_areas(respx_mock, view_areas: ViewAreaHandler):
    """Test simple view area."""
    route = respx_mock.post("/axis-cgi/viewarea/info.cgi").respond(
        json={
            "apiVersion": "1.0",
            "context": "Axis library",
            "method": "list",
            "data": {
                "viewAreas": [
                    {
                        "id": 1000001,
                        "source": 0,
                        "camera": 1,
                        "configurable": True,
                        "canvasSize": {"horizontal": 2592, "vertical": 1944},
                        "rectangularGeometry": {
                            "horizontalOffset": 500,
                            "horizontalSize": 1000,
                            "verticalOffset": 600,
                            "verticalSize": 1200,
                        },
                        "minSize": {"horizontal": 64, "vertical": 64},
                        "maxSize": {"horizontal": 2592, "vertical": 1944},
                        "grid": {
                            "horizontalOffset": 0,
                            "horizontalSize": 1,
                            "verticalOffset": 0,
                            "verticalSize": 1,
                        },
                    },
                    {
                        "id": 1000002,
                        "source": 0,
                        "camera": 2,
                        "configurable": False,
                    },
                ]
            },
        }
    )
    await view_areas.update()

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/viewarea/info.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "method": "list",
        "apiVersion": "1.0",
        "context": "Axis library",
    }

    assert view_areas.initialized
    assert len(view_areas) == 2

    view_area = view_areas["1000001"]
    assert view_area.id == "1000001"
    assert view_area.source == 0
    assert view_area.camera == 1
    assert view_area.configurable

    assert view_area.canvas_size
    assert view_area.canvas_size.horizontal == 2592
    assert view_area.canvas_size.vertical == 1944

    assert view_area.rectangular_geometry
    assert view_area.rectangular_geometry.horizontal_offset == 500
    assert view_area.rectangular_geometry.horizontal_size == 1000
    assert view_area.rectangular_geometry.vertical_offset == 600
    assert view_area.rectangular_geometry.vertical_size == 1200

    assert view_area.min_size
    assert view_area.min_size.horizontal == 64
    assert view_area.min_size.vertical == 64

    assert view_area.max_size
    assert view_area.max_size.horizontal == 2592
    assert view_area.max_size.vertical == 1944

    assert view_area.grid
    assert view_area.grid.horizontal_offset == 0
    assert view_area.grid.horizontal_size == 1
    assert view_area.grid.vertical_offset == 0
    assert view_area.grid.vertical_size == 1

    view_area = view_areas["1000002"]
    assert view_area.id == "1000002"
    assert view_area.source == 0
    assert view_area.camera == 2
    assert not view_area.configurable

    assert view_area.canvas_size is None
    assert view_area.rectangular_geometry is None
    assert view_area.max_size is None
    assert view_area.min_size is None
    assert view_area.grid is None


async def test_get_supported_versions(respx_mock, view_areas: ViewAreaHandler):
    """Test get supported versions api."""
    route = respx_mock.post("/axis-cgi/viewarea/info.cgi").respond(
        json={
            "apiVersion": "1.0",
            "context": "",
            "method": "getSupportedVersions",
            "data": {"apiVersions": ["1.0"]},
        },
    )

    response = await view_areas.get_supported_versions()

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/viewarea/info.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "context": "Axis library",
        "method": "getSupportedVersions",
    }

    assert response == ["1.0"]


async def test_set_geometry_of_view_area(respx_mock, view_areas: ViewAreaHandler):
    """Test simple view area."""
    respx_mock.post("/axis-cgi/viewarea/configure.cgi").respond(
        json={
            "apiVersion": "1.0",
            "context": "Axis library",
            "method": "list",
            "data": {
                "viewAreas": [
                    {
                        "id": 1000001,
                        "source": 0,
                        "camera": 1,
                        "configurable": True,
                        "canvasSize": {"horizontal": 2592, "vertical": 1944},
                        "rectangularGeometry": {
                            "horizontalOffset": 1,
                            "horizontalSize": 2000,
                            "verticalOffset": 2,
                            "verticalSize": 1000,
                        },
                        "minSize": {"horizontal": 64, "vertical": 64},
                        "maxSize": {"horizontal": 2592, "vertical": 1944},
                        "grid": {
                            "horizontalOffset": 0,
                            "horizontalSize": 1,
                            "verticalOffset": 0,
                            "verticalSize": 1,
                        },
                    }
                ]
            },
        }
    )

    assert len(view_areas) == 0

    geometry = Geometry(1, 2000, 2, 1000)

    response = await view_areas.set_geometry(id=1000001, geometry=geometry)

    assert len(view_areas) == 0
    assert len(response) == 1

    view_area = response["1000001"]
    assert view_area.id == "1000001"
    assert view_area.source == 0
    assert view_area.camera == 1
    assert view_area.configurable

    assert view_area.canvas_size
    assert view_area.canvas_size.horizontal == 2592
    assert view_area.canvas_size.vertical == 1944

    assert view_area.rectangular_geometry
    assert view_area.rectangular_geometry.horizontal_offset == 1
    assert view_area.rectangular_geometry.horizontal_size == 2000
    assert view_area.rectangular_geometry.vertical_offset == 2
    assert view_area.rectangular_geometry.vertical_size == 1000

    assert view_area.min_size
    assert view_area.min_size.horizontal == 64
    assert view_area.min_size.vertical == 64

    assert view_area.max_size
    assert view_area.max_size.horizontal == 2592
    assert view_area.max_size.vertical == 1944

    assert view_area.grid
    assert view_area.grid.horizontal_offset == 0
    assert view_area.grid.horizontal_size == 1
    assert view_area.grid.vertical_offset == 0
    assert view_area.grid.vertical_size == 1


async def test_reset_geometry_of_view_area(respx_mock, view_areas: ViewAreaHandler):
    """Test simple view area."""
    respx_mock.post("/axis-cgi/viewarea/configure.cgi").respond(
        json={
            "apiVersion": "1.0",
            "context": "Axis library",
            "method": "list",
            "data": {
                "viewAreas": [
                    {
                        "id": 1000001,
                        "source": 0,
                        "camera": 1,
                        "configurable": True,
                        "canvasSize": {"horizontal": 2592, "vertical": 1944},
                        "rectangularGeometry": {
                            "horizontalOffset": 0,
                            "horizontalSize": 2592,
                            "verticalOffset": 0,
                            "verticalSize": 1944,
                        },
                        "minSize": {"horizontal": 64, "vertical": 64},
                        "maxSize": {"horizontal": 2592, "vertical": 1944},
                        "grid": {
                            "horizontalOffset": 0,
                            "horizontalSize": 1,
                            "verticalOffset": 0,
                            "verticalSize": 1,
                        },
                    }
                ]
            },
        }
    )

    assert len(view_areas) == 0

    response = await view_areas.reset_geometry(id=1000001)

    assert len(view_areas) == 0
    assert len(response) == 1

    view_area = response["1000001"]
    assert view_area.id == "1000001"
    assert view_area.source == 0
    assert view_area.camera == 1
    assert view_area.configurable

    assert view_area.canvas_size
    assert view_area.canvas_size.horizontal == 2592
    assert view_area.canvas_size.vertical == 1944

    assert view_area.rectangular_geometry
    assert view_area.rectangular_geometry.horizontal_offset == 0
    assert view_area.rectangular_geometry.horizontal_size == 2592
    assert view_area.rectangular_geometry.vertical_offset == 0
    assert view_area.rectangular_geometry.vertical_size == 1944

    assert view_area.min_size
    assert view_area.min_size.horizontal == 64
    assert view_area.min_size.vertical == 64

    assert view_area.max_size
    assert view_area.max_size.horizontal == 2592
    assert view_area.max_size.vertical == 1944

    assert view_area.grid
    assert view_area.grid.horizontal_offset == 0
    assert view_area.grid.horizontal_size == 1
    assert view_area.grid.vertical_offset == 0
    assert view_area.grid.vertical_size == 1


async def test_get_supported_config_versions(respx_mock, view_areas: ViewAreaHandler):
    """Test get supported versions api."""
    route = respx_mock.post("/axis-cgi/viewarea/configure.cgi").respond(
        json={
            "apiVersion": "1.0",
            "context": "",
            "method": "getSupportedVersions",
            "data": {"apiVersions": ["1.0"]},
        },
    )

    response = await view_areas.get_supported_config_versions()

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/viewarea/configure.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "context": "Axis library",
        "method": "getSupportedVersions",
    }

    assert response == ["1.0"]


async def test_general_error_101(respx_mock, view_areas: ViewAreaHandler):
    """Test handling error 101.

    HTTP code: 200 OK
    Content-type: application/json
    """
    respx_mock.post("/axis-cgi/viewarea/info.cgi").respond(
        json={
            "apiVersion": "1.0",
            "context": "",
            "method": "getSupportedVersions",
            "error": {
                "code": 101,
                "message": "The requested API version is not supported",
            },
        },
    )

    response = await view_areas.get_supported_versions()

    assert response == []


async def test_general_error_102(respx_mock, view_areas: ViewAreaHandler):
    """Test handling error 102.

    HTTP code: 200 OK
    Content-type: application/json
    """
    respx_mock.post("/axis-cgi/viewarea/info.cgi").respond(
        json={
            "apiVersion": "1.0",
            "context": "",
            "method": "getSupportedVersions",
            "error": {
                "code": 102,
                "message": "Method unsupported",
            },
        },
    )

    response = await view_areas.get_supported_versions()

    assert response == []


async def test_general_error_103(respx_mock, view_areas: ViewAreaHandler):
    """Test handling error 103.

    HTTP code: 200 OK
    Content-type: application/json
    """
    respx_mock.post("/axis-cgi/viewarea/info.cgi").respond(
        json={
            "apiVersion": "1.0",
            "context": "",
            "method": "getSupportedVersions",
            "error": {
                "code": 103,
                "message": "Internal error",
            },
        },
    )

    response = await view_areas.get_supported_versions()

    assert response == []


async def test_method_specific_error_200(respx_mock, view_areas: ViewAreaHandler):
    """Test handling error 200.

    HTTP code: 200 OK
    Content-type: application/json
    """
    respx_mock.post("/axis-cgi/viewarea/configure.cgi").respond(
        json={
            "apiVersion": "1.0",
            "context": "",
            "method": "getSupportedVersions",
            "error": {
                "code": 200,
                "message": "Invalid view area ID",
            },
        },
    )

    await view_areas.reset_geometry(1000001)


async def test_method_specific_error_201(respx_mock, view_areas: ViewAreaHandler):
    """Test handling error 201.

    HTTP code: 200 OK
    Content-type: application/json
    """
    respx_mock.post("/axis-cgi/viewarea/configure.cgi").respond(
        json={
            "apiVersion": "1.0",
            "context": "",
            "method": "getSupportedVersions",
            "error": {
                "code": 201,
                "message": "View area is not configurable",
            },
        },
    )

    await view_areas.reset_geometry(1000001)


async def test_method_specific_error_202(respx_mock, view_areas: ViewAreaHandler):
    """Test handling error 202.

    HTTP code: 200 OK
    Content-type: application/json
    """
    respx_mock.post("/axis-cgi/viewarea/configure.cgi").respond(
        json={
            "apiVersion": "1.0",
            "context": "",
            "method": "getSupportedVersions",
            "error": {
                "code": 202,
                "message": "Invalid geometry",
            },
        },
    )

    await view_areas.reset_geometry(1000001)
