"""Test Axis Fence Guard API.

pytest --cov-report term-missing --cov=axis.fence_guard tests/test_fence_guard.py
"""

from asynctest import Mock
import pytest

from axis.fence_guard import FenceGuard


@pytest.fixture
def fence_guard() -> FenceGuard:
    """Returns the fence_guard mock object."""
    mock_request = Mock()
    mock_request.return_value = ""
    return FenceGuard(mock_request)


def test_get_empty_configuration(fence_guard):
    """Test empty get_configuration"""
    fence_guard._request.return_value = response_get_configuration_empty
    fence_guard.update()
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


def test_get_configuration(fence_guard):
    """Test get_configuration"""
    fence_guard._request.return_value = response_get_configuration
    fence_guard.update()
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
