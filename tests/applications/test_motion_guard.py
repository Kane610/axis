"""Test Axis Motion Guard API.

pytest --cov-report term-missing --cov=axis.applications.motion_guard tests/applications/test_motion_guard.py
"""

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from axis.interfaces.applications.motion_guard import MotionGuardHandler


@pytest.fixture
def motion_guard(axis_device) -> MotionGuardHandler:
    """Return the motion guard mock object."""
    return axis_device.vapix.motion_guard


async def test_get_empty_configuration(
    aiohttp_mock_server, motion_guard: MotionGuardHandler
):
    """Test empty get_configuration."""
    _server, requests = await aiohttp_mock_server(
        "/local/motionguard/control.cgi",
        response=GET_CONFIGURATION_EMPTY_RESPONSE,
        device=motion_guard,
        capture_payload=True,
    )

    await motion_guard.update()

    assert requests
    assert requests[-1]["method"] == "POST"
    assert requests[-1]["path"] == "/local/motionguard/control.cgi"
    assert requests[-1]["payload"] == {
        "method": "getConfiguration",
        "apiVersion": "1.3",
        "context": "Axis library",
    }

    assert len(motion_guard.values()) == 1


async def test_get_configuration(aiohttp_mock_server, motion_guard: MotionGuardHandler):
    """Test get_configuration."""
    await aiohttp_mock_server(
        "/local/motionguard/control.cgi",
        response=GET_CONFIGURATION_RESPONSE,
        device=motion_guard,
        capture_requests=False,
    )

    await motion_guard.update()

    assert motion_guard.initialized
    assert len(motion_guard.values()) == 1

    assert len(motion_guard["0"].profiles) == 1
    profile = motion_guard["0"].profiles["1"]
    assert profile.id == "1"
    assert profile.name == "Profile 1"
    assert profile.camera == 1
    assert profile.filters == [
        {"active": True, "data": 1, "type": "timeShortLivedLimit"},
        {"active": True, "data": 5, "type": "distanceSwayingObject"},
        {"active": True, "data": [5, 5], "type": "sizePercentage"},
        {
            "type": "sizePerspective",
            "data": [75, 75],
            "active": False,
            "areHumansSelected": True,
        },
    ]
    assert profile.perspective == [
        {"data": [[-0.7715, -0.1182], [-0.7715, 0.0824]], "height": 65, "type": "bar"},
        {"data": [[0.2833, -0.8853], [0.2833, 0.5287]], "height": 193, "type": "bar"},
    ]
    assert profile.triggers == [
        {
            "data": [
                [-0.5544, -0.7951],
                [-0.4444, 0.288],
                [0.5767, 0.4835],
                [0.3933, -0.6547],
            ],
            "type": "includeArea",
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
    "data": {
        "cameras": [{"id": 1, "active": True, "rotation": 0}],
        "profiles": [
            {
                "filters": [
                    {"active": True, "data": 1, "type": "timeShortLivedLimit"},
                    {"active": True, "data": 5, "type": "distanceSwayingObject"},
                    {"active": True, "data": [5, 5], "type": "sizePercentage"},
                    {
                        "type": "sizePerspective",
                        "data": [75, 75],
                        "active": False,
                        "areHumansSelected": True,
                    },
                ],
                "triggers": [
                    {
                        "type": "includeArea",
                        "data": [
                            [-0.5544, -0.7951],
                            [-0.4444, 0.288],
                            [0.5767, 0.4835],
                            [0.3933, -0.6547],
                        ],
                    }
                ],
                "perspective": [
                    {
                        "type": "bar",
                        "data": [[-0.7715, -0.1182], [-0.7715, 0.0824]],
                        "height": 65,
                    },
                    {
                        "type": "bar",
                        "data": [[0.2833, -0.8853], [0.2833, 0.5287]],
                        "height": 193,
                    },
                ],
                "name": "Profile 1",
                "uid": 1,
                "camera": 1,
            }
        ],
        "configurationStatus": 8,
    },
    "apiVersion": "1.4",
    "method": "getConfiguration",
    "context": "Axis library",
}
