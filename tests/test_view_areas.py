"""Test Axis view area API.

pytest --cov-report term-missing --cov=axis.view_areas tests/test_view_areas.py
"""

import json
import pytest

import respx

from axis.vapix.interfaces.view_areas import Geometry, URL_CONFIG, URL_INFO, ViewAreas

from .conftest import HOST


@pytest.fixture
def view_areas(axis_device) -> ViewAreas:
    """Returns the view_areas mock object."""
    return ViewAreas(axis_device.vapix)


@respx.mock
@pytest.mark.asyncio
async def test_list_view_areas(view_areas):
    """Test simple view area."""
    route = respx.post(f"http://{HOST}:80{URL_INFO}").respond(
        json={
            "apiVersion": "1.0",
            "context": "Axis library",
            "method": "list",
            "data": {
                "viewAreas": [
                    {
                        "id": 1000008,
                        "source": 0,
                        "camera": 8,
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
                    },
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
                        "id": 1000007,
                        "source": 0,
                        "camera": 7,
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
                    },
                    {
                        "id": 1000006,
                        "source": 0,
                        "camera": 6,
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
                    },
                    {
                        "id": 1000005,
                        "source": 0,
                        "camera": 5,
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
                    },
                    {
                        "id": 1000004,
                        "source": 0,
                        "camera": 4,
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
                    },
                    {
                        "id": 1000003,
                        "source": 0,
                        "camera": 3,
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
                    },
                    {
                        "id": 1000002,
                        "source": 0,
                        "camera": 2,
                        "configurable": True,
                        "canvasSize": {"horizontal": 2592, "vertical": 1944},
                        "rectangularGeometry": {
                            "horizontalOffset": 783,
                            "horizontalSize": 683,
                            "verticalOffset": 122,
                            "verticalSize": 512,
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
                ]
            },
        }
    )
    await view_areas.update()

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == URL_INFO
    assert json.loads(route.calls.last.request.content) == {
        "method": "list",
        "apiVersion": "1.0",
        "context": "Axis library",
    }

    assert len(view_areas) == 8

    view_area = view_areas["1000001"]
    assert view_area.id == "1000001"
    assert view_area.source == 0
    assert view_area.camera == 1
    assert view_area.configurable

    assert view_area.canvas_size.horizontal == 2592
    assert view_area.canvas_size.vertical == 1944

    assert view_area.rectangular_geometry.horizontalOffset == 500
    assert view_area.rectangular_geometry.horizontalSize == 1000
    assert view_area.rectangular_geometry.verticalOffset == 600
    assert view_area.rectangular_geometry.verticalSize == 1200

    assert view_area.min_size.horizontal == 64
    assert view_area.min_size.vertical == 64

    assert view_area.max_size.horizontal == 2592
    assert view_area.max_size.vertical == 1944

    assert view_area.grid.horizontalOffset == 0
    assert view_area.grid.horizontalSize == 1
    assert view_area.grid.verticalOffset == 0
    assert view_area.grid.verticalSize == 1


@respx.mock
@pytest.mark.asyncio
async def test_get_supported_versions(view_areas):
    """Test get supported versions api."""
    route = respx.post(f"http://{HOST}:80{URL_INFO}").respond(
        json={
            "apiVersion": "1.0",
            "method": "getSupportedVersions",
            "data": {"apiVersions": ["1.0"]},
        },
    )

    response = await view_areas.get_supported_versions()

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/viewarea/info.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "method": "getSupportedVersions"
    }

    assert response["data"] == {"apiVersions": ["1.0"]}


@respx.mock
@pytest.mark.asyncio
async def test_set_geometry_of_view_area(view_areas):
    """Test simple view area."""
    respx.post(f"http://{HOST}:80{URL_CONFIG}").respond(
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

    await view_areas.set_geometry(geometry, view_area_id=1000001)

    assert len(view_areas) == 1

    view_area = view_areas["1000001"]
    assert view_area.id == "1000001"
    assert view_area.source == 0
    assert view_area.camera == 1
    assert view_area.configurable

    assert view_area.canvas_size.horizontal == 2592
    assert view_area.canvas_size.vertical == 1944

    assert view_area.rectangular_geometry.horizontalOffset == 1
    assert view_area.rectangular_geometry.horizontalSize == 2000
    assert view_area.rectangular_geometry.verticalOffset == 2
    assert view_area.rectangular_geometry.verticalSize == 1000

    assert view_area.min_size.horizontal == 64
    assert view_area.min_size.vertical == 64

    assert view_area.max_size.horizontal == 2592
    assert view_area.max_size.vertical == 1944

    assert view_area.grid.horizontalOffset == 0
    assert view_area.grid.horizontalSize == 1
    assert view_area.grid.verticalOffset == 0
    assert view_area.grid.verticalSize == 1


@respx.mock
@pytest.mark.asyncio
async def test_set_geometry_of_view_area_using_view_area(view_areas):
    """Test simple view area."""
    respx.post(f"http://{HOST}:80{URL_INFO}").respond(
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
                    }
                ]
            },
        }
    )
    respx.post(f"http://{HOST}:80{URL_CONFIG}").respond(
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
    await view_areas.update()

    assert len(view_areas) == 1

    geometry = Geometry(1, 2000, 2, 1000)

    await view_areas.set_geometry(geometry, view_area=view_areas["1000001"])

    assert len(view_areas) == 1

    view_area = view_areas["1000001"]
    assert view_area.id == "1000001"
    assert view_area.source == 0
    assert view_area.camera == 1
    assert view_area.configurable

    assert view_area.canvas_size.horizontal == 2592
    assert view_area.canvas_size.vertical == 1944

    assert view_area.rectangular_geometry.horizontalOffset == 1
    assert view_area.rectangular_geometry.horizontalSize == 2000
    assert view_area.rectangular_geometry.verticalOffset == 2
    assert view_area.rectangular_geometry.verticalSize == 1000

    assert view_area.min_size.horizontal == 64
    assert view_area.min_size.vertical == 64

    assert view_area.max_size.horizontal == 2592
    assert view_area.max_size.vertical == 1944

    assert view_area.grid.horizontalOffset == 0
    assert view_area.grid.horizontalSize == 1
    assert view_area.grid.verticalOffset == 0
    assert view_area.grid.verticalSize == 1


@respx.mock
@pytest.mark.asyncio
async def test_reset_geometry_of_view_area(view_areas):
    """Test simple view area."""
    respx.post(f"http://{HOST}:80{URL_CONFIG}").respond(
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

    await view_areas.reset_geometry(view_area_id=1000001)

    assert len(view_areas) == 1

    view_area = view_areas["1000001"]
    assert view_area.id == "1000001"
    assert view_area.source == 0
    assert view_area.camera == 1
    assert view_area.configurable

    assert view_area.canvas_size.horizontal == 2592
    assert view_area.canvas_size.vertical == 1944

    assert view_area.rectangular_geometry.horizontalOffset == 0
    assert view_area.rectangular_geometry.horizontalSize == 2592
    assert view_area.rectangular_geometry.verticalOffset == 0
    assert view_area.rectangular_geometry.verticalSize == 1944

    assert view_area.min_size.horizontal == 64
    assert view_area.min_size.vertical == 64

    assert view_area.max_size.horizontal == 2592
    assert view_area.max_size.vertical == 1944

    assert view_area.grid.horizontalOffset == 0
    assert view_area.grid.horizontalSize == 1
    assert view_area.grid.verticalOffset == 0
    assert view_area.grid.verticalSize == 1


@respx.mock
@pytest.mark.asyncio
async def test_reset_geometry_of_view_area_using_view_area(view_areas):
    """Test simple view area."""
    respx.post(f"http://{HOST}:80{URL_INFO}").respond(
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
                    }
                ]
            },
        }
    )
    respx.post(f"http://{HOST}:80{URL_CONFIG}").respond(
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
    await view_areas.update()

    assert len(view_areas) == 1

    await view_areas.reset_geometry(view_area=view_areas["1000001"])

    view_area = view_areas["1000001"]
    assert view_area.id == "1000001"
    assert view_area.source == 0
    assert view_area.camera == 1
    assert view_area.configurable

    assert view_area.canvas_size.horizontal == 2592
    assert view_area.canvas_size.vertical == 1944

    assert view_area.rectangular_geometry.horizontalOffset == 0
    assert view_area.rectangular_geometry.horizontalSize == 2592
    assert view_area.rectangular_geometry.verticalOffset == 0
    assert view_area.rectangular_geometry.verticalSize == 1944

    assert view_area.min_size.horizontal == 64
    assert view_area.min_size.vertical == 64

    assert view_area.max_size.horizontal == 2592
    assert view_area.max_size.vertical == 1944

    assert view_area.grid.horizontalOffset == 0
    assert view_area.grid.horizontalSize == 1
    assert view_area.grid.verticalOffset == 0
    assert view_area.grid.verticalSize == 1


@respx.mock
@pytest.mark.asyncio
async def test_get_supported_config_versions(view_areas):
    """Test get supported versions api."""
    route = respx.post(f"http://{HOST}:80{URL_CONFIG}").respond(
        json={
            "apiVersion": "1.0",
            "method": "getSupportedVersions",
            "data": {"apiVersions": ["1.0"]},
        },
    )

    response = await view_areas.get_supported_config_versions()

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/viewarea/configure.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "method": "getSupportedVersions"
    }

    assert response["data"] == {"apiVersions": ["1.0"]}


@respx.mock
@pytest.mark.asyncio
async def test_general_error_101(view_areas):
    """Test handling error 101.

    HTTP code: 200 OK
    Content-type: application/json
    """
    respx.post(f"http://{HOST}:80{URL_INFO}").respond(
        json={
            "apiVersion": "1.0",
            "method": "getSupportedVersions",
            "error": {
                "code": 101,
                "message": "The requested API version is not supported",
            },
        },
    )

    response = await view_areas.get_supported_versions()

    assert response == {}


@respx.mock
@pytest.mark.asyncio
async def test_general_error_102(view_areas):
    """Test handling error 102.

    HTTP code: 200 OK
    Content-type: application/json
    """
    respx.post(f"http://{HOST}:80{URL_INFO}").respond(
        json={
            "apiVersion": "1.0",
            "method": "getSupportedVersions",
            "error": {
                "code": 102,
                "message": "Method unsupported",
            },
        },
    )

    response = await view_areas.get_supported_versions()

    assert response == {}


@respx.mock
@pytest.mark.asyncio
async def test_general_error_103(view_areas):
    """Test handling error 103.

    HTTP code: 200 OK
    Content-type: application/json
    """
    respx.post(f"http://{HOST}:80{URL_INFO}").respond(
        json={
            "apiVersion": "1.0",
            "method": "getSupportedVersions",
            "error": {
                "code": 103,
                "message": "Internal error",
            },
        },
    )

    response = await view_areas.get_supported_versions()

    assert response == {}


@respx.mock
@pytest.mark.asyncio
async def test_method_specific_error_200(view_areas):
    """Test handling error 200.

    HTTP code: 200 OK
    Content-type: application/json
    """
    respx.post(f"http://{HOST}:80{URL_CONFIG}").respond(
        json={
            "apiVersion": "1.0",
            "method": "getSupportedVersions",
            "error": {
                "code": 200,
                "message": "Invalid view area ID",
            },
        },
    )

    await view_areas.reset_geometry(1000001)


@respx.mock
@pytest.mark.asyncio
async def test_method_specific_error_201(view_areas):
    """Test handling error 201.

    HTTP code: 200 OK
    Content-type: application/json
    """
    respx.post(f"http://{HOST}:80{URL_CONFIG}").respond(
        json={
            "apiVersion": "1.0",
            "method": "getSupportedVersions",
            "error": {
                "code": 201,
                "message": "View area is not configurable",
            },
        },
    )

    await view_areas.reset_geometry(1000001)


@respx.mock
@pytest.mark.asyncio
async def test_method_specific_error_202(view_areas):
    """Test handling error 202.

    HTTP code: 200 OK
    Content-type: application/json
    """
    respx.post(f"http://{HOST}:80{URL_CONFIG}").respond(
        json={
            "apiVersion": "1.0",
            "method": "getSupportedVersions",
            "error": {
                "code": 202,
                "message": "Invalid geometry",
            },
        },
    )

    await view_areas.reset_geometry(1000001)
