"""Test Axis Fence Guard API.

pytest --cov-report term-missing --cov=axis.applications.fence_guard tests/applications/test_fence_guard.py
"""

import json

import pytest
import respx

from axis.vapix.interfaces.applications.fence_guard import FenceGuardHandler

from ..conftest import HOST


@pytest.fixture
def fence_guard(axis_device) -> FenceGuardHandler:
    """Return the fence guard mock object."""
    return axis_device.vapix.fence_guard


@respx.mock
@pytest.mark.asyncio
async def test_get_empty_configuration(fence_guard: FenceGuardHandler):
    """Test empty get_configuration."""
    route = respx.post(f"http://{HOST}:80/local/fenceguard/control.cgi").respond(
        json=response_get_configuration_empty,
    )
    await fence_guard.update()

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/local/fenceguard/control.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "method": "getConfiguration",
        "apiVersion": "1.3",
        "context": "Axis library",
    }

    assert len(fence_guard.values()) == 1


@respx.mock
@pytest.mark.asyncio
async def test_get_configuration(fence_guard: FenceGuardHandler):
    """Test get_configuration."""
    respx.post(f"http://{HOST}:80/local/fenceguard/control.cgi").respond(
        json=response_get_configuration,
    )
    await fence_guard.update()

    assert len(fence_guard.values()) == 1

    assert len(fence_guard["0"].profiles) == 1
    profile = fence_guard["0"].profiles["Profile 1"]
    assert profile.id == "Profile 1"
    assert profile.name == "Profile 1"
    assert profile.camera == 1
    assert profile.uid == 1
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


response_get_configuration_empty = {
    "data": {
        "cameras": [{"id": 1, "active": True, "rotation": 0}],
        "profiles": [],
        "configurationStatus": 9,
    },
    "apiVersion": "1.4",
    "method": "getConfiguration",
    "context": "Axis library",
}

response_get_configuration = {
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
