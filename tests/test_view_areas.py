"""Test Axis view area API.

pytest --cov-report term-missing --cov=axis.view_areas tests/test_view_areas.py
"""

from typing import TYPE_CHECKING
from unittest.mock import MagicMock

import pytest

from axis.interfaces.view_areas import Geometry, ViewAreaHandler
from axis.models.view_area import (
    GetSupportedConfigVersionsRequest,
    GetSupportedVersionsRequest,
    ListViewAreasRequest,
    ResetGeometryRequest,
    SetGeometryRequest,
)

from tests.conftest import (
    MockApiRequestAssertions,
    MockApiResponseSpec,
    bind_mock_api_request,
)

if TYPE_CHECKING:
    from axis.device import AxisDevice


@pytest.fixture
def view_areas(axis_device: AxisDevice) -> ViewAreaHandler:
    """Return the view_areas mock object."""
    axis_device.vapix.api_discovery = api_discovery_mock = MagicMock()
    api_discovery_mock.__getitem__().version = "1.0"
    return axis_device.vapix.view_areas


@pytest.fixture
def mock_view_area_request(mock_api_request):
    """Register view area route mocks via ApiRequest classes."""

    def _register(api_request, json_data, *, content):
        return bind_mock_api_request(mock_api_request, api_request)(
            response=MockApiResponseSpec(json=json_data),
            assertions=MockApiRequestAssertions(content=content),
        )

    return _register


async def test_list_view_areas(mock_view_area_request, view_areas: ViewAreaHandler):
    """Test simple view area."""
    route = mock_view_area_request(
        ListViewAreasRequest,
        {
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
        },
        content=ListViewAreasRequest(api_version="1.0").content,
    )
    await view_areas.update()

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/viewarea/info.cgi"

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


async def test_get_supported_versions(
    mock_view_area_request, view_areas: ViewAreaHandler
):
    """Test get supported versions api."""
    route = mock_view_area_request(
        GetSupportedVersionsRequest,
        {
            "apiVersion": "1.0",
            "context": "",
            "method": "getSupportedVersions",
            "data": {"apiVersions": ["1.0"]},
        },
        content=GetSupportedVersionsRequest().content,
    )

    response = await view_areas.get_supported_versions()

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/viewarea/info.cgi"

    assert response == ["1.0"]


async def test_set_geometry_of_view_area(
    mock_view_area_request, view_areas: ViewAreaHandler
):
    """Test simple view area."""
    mock_view_area_request(
        SetGeometryRequest,
        {
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
        },
        content=SetGeometryRequest(
            id=1000001,
            geometry=Geometry(1, 2000, 2, 1000),
            api_version="1.0",
        ).content,
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


async def test_reset_geometry_of_view_area(
    mock_view_area_request, view_areas: ViewAreaHandler
):
    """Test simple view area."""
    mock_view_area_request(
        ResetGeometryRequest,
        {
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
        },
        content=ResetGeometryRequest(id=1000001, api_version="1.0").content,
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


async def test_get_supported_config_versions(
    mock_view_area_request, view_areas: ViewAreaHandler
):
    """Test get supported versions api."""
    route = mock_view_area_request(
        GetSupportedConfigVersionsRequest,
        {
            "apiVersion": "1.0",
            "context": "",
            "method": "getSupportedVersions",
            "data": {"apiVersions": ["1.0"]},
        },
        content=GetSupportedConfigVersionsRequest().content,
    )

    response = await view_areas.get_supported_config_versions()

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/viewarea/configure.cgi"

    assert response == ["1.0"]


async def test_general_error_101(http_route_mock, view_areas: ViewAreaHandler):
    """Test handling error 101.

    HTTP code: 200 OK
    Content-type: application/json
    """
    http_route_mock.post("/axis-cgi/viewarea/info.cgi").respond(
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


async def test_general_error_102(http_route_mock, view_areas: ViewAreaHandler):
    """Test handling error 102.

    HTTP code: 200 OK
    Content-type: application/json
    """
    http_route_mock.post("/axis-cgi/viewarea/info.cgi").respond(
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


async def test_general_error_103(http_route_mock, view_areas: ViewAreaHandler):
    """Test handling error 103.

    HTTP code: 200 OK
    Content-type: application/json
    """
    http_route_mock.post("/axis-cgi/viewarea/info.cgi").respond(
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


async def test_method_specific_error_200(http_route_mock, view_areas: ViewAreaHandler):
    """Test handling error 200.

    HTTP code: 200 OK
    Content-type: application/json
    """
    http_route_mock.post("/axis-cgi/viewarea/configure.cgi").respond(
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


async def test_method_specific_error_201(http_route_mock, view_areas: ViewAreaHandler):
    """Test handling error 201.

    HTTP code: 200 OK
    Content-type: application/json
    """
    http_route_mock.post("/axis-cgi/viewarea/configure.cgi").respond(
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


async def test_method_specific_error_202(http_route_mock, view_areas: ViewAreaHandler):
    """Test handling error 202.

    HTTP code: 200 OK
    Content-type: application/json
    """
    http_route_mock.post("/axis-cgi/viewarea/configure.cgi").respond(
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
