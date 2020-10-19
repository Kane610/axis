"""Test Axis Loitering Guard API.

pytest --cov-report term-missing --cov=axis.loitering_guard tests/test_loitering_guard.py
"""

import pytest
from unittest.mock import AsyncMock

from axis.applications.loitering_guard import LoiteringGuard


@pytest.fixture
def loitering_guard() -> LoiteringGuard:
    """Returns the loitering_guard mock object."""
    mock_request = AsyncMock()
    mock_request.return_value = ""
    return LoiteringGuard(mock_request)


async def test_get_empty_configuration(loitering_guard):
    """Test empty get_configuration"""
    loitering_guard._request.return_value = response_get_configuration_empty
    await loitering_guard.update()
    loitering_guard._request.assert_called_with(
        "post",
        "/local/loiteringguard/control.cgi",
        json={
            "method": "getConfiguration",
            "apiVersion": "1.3",
            "context": "Axis library",
        },
    )

    assert len(loitering_guard.values()) == 0


async def test_get_configuration(loitering_guard):
    """Test get_configuration"""
    loitering_guard._request.return_value = response_get_configuration
    await loitering_guard.update()
    loitering_guard._request.assert_called_with(
        "post",
        "/local/loiteringguard/control.cgi",
        json={
            "method": "getConfiguration",
            "apiVersion": "1.3",
            "context": "Axis library",
        },
    )

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
            "data": [[-0.97, -0.97], [-0.97, 0.97], [0.97, 0.97], [0.97, -0.97],],
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

