"""Test Axis Fence Guard API.

pytest --cov-report term-missing --cov=axis.applications.fence_guard tests/applications/test_fence_guard.py
"""

from typing import TYPE_CHECKING

from aiohttp import web
import pytest

if TYPE_CHECKING:
    from axis.interfaces.applications.fence_guard import FenceGuardHandler


@pytest.fixture
def fence_guard(axis_device_aiohttp) -> FenceGuardHandler:
    """Return the fence guard mock object."""
    return axis_device_aiohttp.vapix.fence_guard


async def test_get_empty_configuration(aiohttp_server, fence_guard: FenceGuardHandler):
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
    app.router.add_post("/local/fenceguard/control.cgi", handle_request)
    server = await aiohttp_server(app)
    fence_guard.vapix.device.config.port = server.port

    await fence_guard.update()

    assert requests
    assert requests[-1]["method"] == "POST"
    assert requests[-1]["path"] == "/local/fenceguard/control.cgi"
    assert requests[-1]["payload"] == {
        "method": "getConfiguration",
        "apiVersion": "1.3",
        "context": "Axis library",
    }

    assert len(fence_guard.values()) == 1


async def test_get_configuration(aiohttp_server, fence_guard: FenceGuardHandler):
    """Test get_configuration."""

    async def handle_request(_: web.Request) -> web.Response:
        return web.json_response(GET_CONFIGURATION_RESPONSE)

    app = web.Application()
    app.router.add_post("/local/fenceguard/control.cgi", handle_request)
    server = await aiohttp_server(app)
    fence_guard.vapix.device.config.port = server.port

    await fence_guard.update()

    assert fence_guard.initialized
    assert len(fence_guard.values()) == 1

    assert len(fence_guard["0"].profiles) == 1
    profile = fence_guard["0"].profiles["1"]
    assert profile.id == "1"
    assert profile.name == "Profile 1"
    assert profile.camera == 1
    assert profile.filters == [
        {"active": True, "data": [5, 5], "type": "sizePercentage"},
        {"active": True, "data": 1, "type": "timeShortLivedLimit"},
    ]
    assert profile.perspective == []
    assert profile.triggers == [
        {
            "type": "fence",
            "data": [[0.0, -0.7], [0.0, 0.7]],
            "alarmDirection": "leftToRight",
        }
    ]


GET_CONFIGURATION_EMPTY_RESPONSE = {
    "data": {
        "cameras": [{"id": 1, "active": True, "rotation": 0}],
        "profiles": [],
        "configurationStatus": 9,
    },
    "apiVersion": "1.4",
    "method": "getConfiguration",
    "context": "Axis library",
}

GET_CONFIGURATION_RESPONSE = {
    "context": "Axis library",
    "apiVersion": "1.4",
    "method": "getConfiguration",
    "data": {
        "cameras": [{"id": 1, "active": True, "rotation": 0}],
        "profiles": [
            {
                "filters": [
                    {"active": True, "data": [5, 5], "type": "sizePercentage"},
                    {"active": True, "data": 1, "type": "timeShortLivedLimit"},
                ],
                "triggers": [
                    {
                        "type": "fence",
                        "data": [[0.0, -0.7], [0.0, 0.7]],
                        "alarmDirection": "leftToRight",
                    }
                ],
                "uid": 1,
                "name": "Profile 1",
                "camera": 1,
            }
        ],
        "configurationStatus": 0,
    },
}
