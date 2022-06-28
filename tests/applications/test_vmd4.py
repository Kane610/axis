"""Test Axis VMD4 API.

pytest --cov-report term-missing --cov=axis.applications.vmd4 tests/applications/test_vmd4.py
"""

import json
import pytest

import respx

from axis.vapix.applications.vmd4 import Vmd4

from ..conftest import HOST


@pytest.fixture
def vmd4(axis_device) -> Vmd4:
    """Returns the vmd4 mock object."""
    return Vmd4(axis_device.vapix.request)


@respx.mock
@pytest.mark.asyncio
async def test_get_empty_configuration(vmd4):
    """Test empty get_configuration"""
    route = respx.post(f"http://{HOST}:80/local/vmd/control.cgi").respond(
        json=response_get_configuration_empty,
    )
    await vmd4.update()

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/local/vmd/control.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "method": "getConfiguration",
        "apiVersion": "1.2",
        "context": "Axis library",
    }

    assert len(vmd4.values()) == 0


@respx.mock
@pytest.mark.asyncio
async def test_get_configuration(vmd4):
    """Test get_supported_versions"""
    respx.post(f"http://{HOST}:80/local/vmd/control.cgi").respond(
        json=response_get_configuration,
    )
    await vmd4.update()

    assert len(vmd4.values()) == 1

    vmd4 = vmd4["Camera1Profile1"]
    assert vmd4.id == "Camera1Profile1"
    assert vmd4.name == "Profile 1"
    assert vmd4.camera == 1
    assert vmd4.uid == 1
    assert vmd4.triggers == [
        {
            "type": "includeArea",
            "data": [
                [-0.97, -0.97],
                [-0.97, 0.97],
                [0.97, 0.97],
                [0.97, -0.97],
            ],
        }
    ]
    assert vmd4.filters == [
        {"data": 1, "active": True, "type": "timeShortLivedLimit"},
        {"data": 5, "active": True, "type": "distanceSwayingObject"},
        {"data": [5, 5], "active": True, "type": "sizePercentage"},
    ]


@respx.mock
@pytest.mark.asyncio
async def test_get_configuration_error(vmd4):
    """Test empty get_configuration.

    await _request returns an empty dict on error.
    """
    respx.post(f"http://{HOST}:80/local/vmd/control.cgi").respond(
        json={},
    )
    await vmd4.update()

    assert len(vmd4.values()) == 0


response_get_configuration_empty = {
    "apiVersion": "1.4",
    "method": "getConfiguration",
    "context": "Axis library",
    "data": {
        "cameras": [{"id": 1, "rotation": 0, "active": True}],
        "configurationStatus": 26,
        "profiles": [],
    },
}


response_get_configuration = {
    "apiVersion": "1.4",
    "method": "getConfiguration",
    "context": "Axis library",
    "data": {
        "cameras": [{"id": 1, "rotation": 0, "active": True}],
        "configurationStatus": 2,
        "profiles": [
            {
                "filters": [
                    {"data": 1, "active": True, "type": "timeShortLivedLimit"},
                    {"data": 5, "active": True, "type": "distanceSwayingObject"},
                    {"data": [5, 5], "active": True, "type": "sizePercentage"},
                ],
                "camera": 1,
                "triggers": [
                    {
                        "type": "includeArea",
                        "data": [
                            [-0.97, -0.97],
                            [-0.97, 0.97],
                            [0.97, 0.97],
                            [0.97, -0.97],
                        ],
                    }
                ],
                "name": "Profile 1",
                "uid": 1,
            }
        ],
    },
}

response_get_configuration_error = {
    "apiVersion": "1.1",
    "method": "getConfiguration",
    "context": "Axis library",
    "error": {
        "code": "2000",
        "message": "The requested version of the application is not supported.",
    },
}
