"""Test Axis VMD4 API.

pytest --cov-report term-missing --cov=axis.applications.vmd4 tests/applications/test_vmd4.py
"""

from typing import TYPE_CHECKING

from aiohttp import web
import pytest

if TYPE_CHECKING:
    from axis.interfaces.applications.vmd4 import Vmd4Handler


@pytest.fixture
def vmd4(axis_device_aiohttp) -> Vmd4Handler:
    """Return the vmd4 mock object."""
    return axis_device_aiohttp.vapix.vmd4


async def test_get_empty_configuration(aiohttp_server, vmd4: Vmd4Handler):
    """Test empty get_configuration."""
    requests: list[dict[str, object]] = []

    async def handle_request(request: web.Request) -> web.Response:
        requests.append(
            {
                "method": request.method,
                "path": request.path,
                "payload": await request.json(),
            }
        )
        return web.json_response(GET_CONFIGURATION_EMPTY_RESPONSE)

    app = web.Application()
    app.router.add_post("/local/vmd/control.cgi", handle_request)
    server = await aiohttp_server(app)
    vmd4.vapix.device.config.port = server.port

    await vmd4.update()

    assert requests
    assert requests[-1]["method"] == "POST"
    assert requests[-1]["path"] == "/local/vmd/control.cgi"
    assert requests[-1]["payload"] == {
        "method": "getConfiguration",
        "apiVersion": "1.2",
        "context": "Axis library",
    }

    assert len(vmd4.values()) == 1


async def test_get_configuration(aiohttp_server, vmd4: Vmd4Handler):
    """Test get_supported_versions."""

    async def handle_request(_: web.Request) -> web.Response:
        return web.json_response(GET_CONFIGURATION_RESPONSE)

    app = web.Application()
    app.router.add_post("/local/vmd/control.cgi", handle_request)
    server = await aiohttp_server(app)
    vmd4.vapix.device.config.port = server.port

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
