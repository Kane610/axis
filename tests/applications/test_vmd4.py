"""Test Axis VMD4 API.

pytest --cov-report term-missing --cov=axis.applications.vmd4 tests/applications/test_vmd4.py
"""

import json

import pytest

from axis.interfaces.applications.vmd4 import Vmd4Handler


@pytest.fixture
def vmd4(axis_device) -> Vmd4Handler:
    """Return the vmd4 mock object."""
    return axis_device.vapix.vmd4


async def test_get_empty_configuration(respx_mock, vmd4: Vmd4Handler):
    """Test empty get_configuration."""
    route = respx_mock.post("/local/vmd/control.cgi").respond(
        json=GET_CONFIGURATION_EMPTY_RESPONSE,
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

    assert len(vmd4.values()) == 1


async def test_get_configuration(respx_mock, vmd4: Vmd4Handler):
    """Test get_supported_versions."""
    respx_mock.post("/local/vmd/control.cgi").respond(
        json=GET_CONFIGURATION_RESPONSE,
    )
    await vmd4.update()

    assert vmd4.initialized
    assert len(vmd4.values()) == 1

    assert len(vmd4["0"].profiles) == 1
    profile = vmd4["0"].profiles["1"]
    assert profile.id == "1"
    assert profile.name == "Profile 1"
    assert profile.camera == 1
    assert profile.triggers == [
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
    assert profile.filters == [
        {"data": 1, "active": True, "type": "timeShortLivedLimit"},
        {"data": 5, "active": True, "type": "distanceSwayingObject"},
        {"data": [5, 5], "active": True, "type": "sizePercentage"},
    ]


GET_CONFIGURATION_EMPTY_RESPONSE = {
    "apiVersion": "1.4",
    "method": "getConfiguration",
    "context": "Axis library",
    "data": {
        "cameras": [{"id": 1, "rotation": 0, "active": True}],
        "configurationStatus": 26,
        "profiles": [],
    },
}


GET_CONFIGURATION_RESPONSE = {
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

GET_CONFIGURATION_RESPONSE_error = {
    "apiVersion": "1.1",
    "method": "getConfiguration",
    "context": "Axis library",
    "error": {
        "code": "2000",
        "message": "The requested version of the application is not supported.",
    },
}
