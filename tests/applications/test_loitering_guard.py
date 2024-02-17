"""Test Axis Loitering Guard API.

pytest --cov-report term-missing --cov=axis.applications.loitering_guard tests/applications/test_loitering_guard.py
"""

import json

import pytest

from axis.vapix.interfaces.applications.loitering_guard import LoiteringGuardHandler


@pytest.fixture
def loitering_guard(axis_device) -> LoiteringGuardHandler:
    """Return the loitering guard mock object."""
    return axis_device.vapix.loitering_guard


async def test_get_empty_configuration(
    respx_mock, loitering_guard: LoiteringGuardHandler
):
    """Test empty get_configuration."""
    route = respx_mock.post("/local/loiteringguard/control.cgi").respond(
        json=GET_CONFIGURATION_EMPTY_RESPONSE,
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

    assert len(loitering_guard.values()) == 1


async def test_get_configuration(respx_mock, loitering_guard: LoiteringGuardHandler):
    """Test get_configuration."""
    respx_mock.post("/local/loiteringguard/control.cgi").respond(
        json=GET_CONFIGURATION_RESPONSE,
    )
    await loitering_guard.update()

    assert len(loitering_guard.values()) == 1

    assert len(loitering_guard["0"].profiles) == 1
    profile = loitering_guard["0"].profiles["1"]
    assert profile.id == "1"
    assert profile.name == "Profile 1"
    assert profile.camera == 1
    assert profile.filters == [
        {"active": True, "data": [5, 5], "type": "sizePercentage"},
        {"active": True, "data": 5, "type": "distanceSwayingObject"},
    ]
    assert profile.perspective == []
    assert profile.triggers == [
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


GET_CONFIGURATION_EMPTY_RESPONSE = {
    "data": {
        "cameras": [{"id": 1, "active": True, "rotation": 0}],
        "profiles": [],
        "configurationStatus": 1,
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
