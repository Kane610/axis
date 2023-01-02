"""Test Axis Loitering Guard API.

pytest --cov-report term-missing --cov=axis.applications.loitering_guard tests/applications/test_loitering_guard.py
"""

import json

import pytest
import respx

from axis.vapix.interfaces.applications.loitering_guard import LoiteringGuard

from ..conftest import HOST


@pytest.fixture
def loitering_guard(axis_device) -> LoiteringGuard:
    """Return the loitering guard mock object."""
    return LoiteringGuard(axis_device.vapix)


@respx.mock
@pytest.mark.asyncio
async def test_get_empty_configuration(loitering_guard):
    """Test empty get_configuration."""
    route = respx.post(f"http://{HOST}:80/local/loiteringguard/control.cgi").respond(
        json=response_get_configuration_empty,
    )
    await loitering_guard.update()

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/local/loiteringguard/control.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "method": "getConfiguration",
        "apiVersion": "1.3",
        "context": "Axis library",
    }

    assert len(loitering_guard.values()) == 0


@respx.mock
@pytest.mark.asyncio
async def test_get_configuration(loitering_guard):
    """Test get_configuration."""
    respx.post(f"http://{HOST}:80/local/loiteringguard/control.cgi").respond(
        json=response_get_configuration,
    )
    await loitering_guard.update()

    assert len(loitering_guard.values()) == 1

    profile1 = loitering_guard["Camera1Profile1"]
    assert profile1.id == "Camera1Profile1"
    assert profile1.name == "Profile 1"
    assert profile1.camera == 1
    assert profile1.uid == 1
    assert profile1.filters == [
        {"active": True, "data": [5, 5], "type": "sizePercentage"},
        {"active": True, "data": 5, "type": "distanceSwayingObject"},
    ]
    assert profile1.perspective is None
    assert profile1.triggers == [
        {
            "type": "loiteringArea",
            "data": [
                [-0.97, -0.97],
                [-0.97, 0.97],
                [0.97, 0.97],
                [0.97, -0.97],
            ],
            "conditions": [
                {"type": "individual", "data": 120, "active": True},
                {"type": "group", "data": 160, "active": False},
            ],
        }
    ]


response_get_configuration_empty = {
    "data": {
        "cameras": [{"id": 1, "active": True, "rotation": 0}],
        "profiles": [],
        "configurationStatus": 1,
    },
    "apiVersion": "1.4",
    "method": "getConfiguration",
    "context": "Axis library",
}

response_get_configuration = {
    "data": {
        "cameras": [{"id": 1, "active": True, "rotation": 0}],
        "profiles": [
            {
                "filters": [
                    {"active": True, "data": [5, 5], "type": "sizePercentage"},
                    {"active": True, "data": 5, "type": "distanceSwayingObject"},
                ],
                "triggers": [
                    {
                        "type": "loiteringArea",
                        "data": [
                            [-0.97, -0.97],
                            [-0.97, 0.97],
                            [0.97, 0.97],
                            [0.97, -0.97],
                        ],
                        "conditions": [
                            {"type": "individual", "data": 120, "active": True},
                            {"type": "group", "data": 160, "active": False},
                        ],
                    }
                ],
                "uid": 1,
                "camera": 1,
                "name": "Profile 1",
            }
        ],
        "configurationStatus": 0,
    },
    "apiVersion": "1.4",
    "method": "getConfiguration",
    "context": "Axis library",
}
