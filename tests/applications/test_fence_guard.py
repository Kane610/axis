"""Test Axis Fence Guard API.

pytest --cov-report term-missing --cov=axis.applications.fence_guard tests/applications/test_fence_guard.py
"""

import pytest
from unittest.mock import AsyncMock

from axis.applications.fence_guard import FenceGuard


@pytest.fixture
def fence_guard() -> FenceGuard:
    """Returns the fence_guard mock object."""
    mock_request = AsyncMock()
    mock_request.return_value = ""
    return FenceGuard(mock_request)


async def test_get_empty_configuration(fence_guard):
    """Test empty get_configuration"""
    fence_guard._request.return_value = response_get_configuration_empty
    await fence_guard.update()
    fence_guard._request.assert_called_with(
        "post",
        "/local/fenceguard/control.cgi",
        json={
            "method": "getConfiguration",
            "apiVersion": "1.3",
            "context": "Axis library",
        },
    )

    assert len(fence_guard.values()) == 0


async def test_get_configuration(fence_guard):
    """Test get_configuration"""
    fence_guard._request.return_value = response_get_configuration
    await fence_guard.update()
    fence_guard._request.assert_called_with(
        "post",
        "/local/fenceguard/control.cgi",
        json={
            "method": "getConfiguration",
            "apiVersion": "1.3",
            "context": "Axis library",
        },
    )

    assert len(fence_guard.values()) == 1

    profile1 = fence_guard["Camera1Profile1"]
    assert profile1.id == "Camera1Profile1"
    assert profile1.name == "Profile 1"
    assert profile1.camera == 1
    assert profile1.uid == 1
    assert profile1.filters == [
        {"active": True, "data": [5, 5], "type": "sizePercentage"},
        {"active": True, "data": 1, "type": "timeShortLivedLimit"},
    ]
    assert profile1.perspective is None
    assert profile1.triggers == [
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
