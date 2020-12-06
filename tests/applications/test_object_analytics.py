"""Test Axis Object Analytics API.

pytest --cov-report term-missing --cov=axis.applications.object_analytics tests/applications/test_object_analytics.py
"""

import json
import pytest

import respx

from axis.applications.object_analytics import ObjectAnalytics
from axis.configuration import Configuration
from axis.device import AxisDevice


@pytest.fixture
async def device() -> AxisDevice:
    """Returns the axis device.

    Clean up sessions automatically at the end of each test.
    """
    axis_device = AxisDevice(Configuration("host", username="root", password="pass"))
    yield axis_device
    await axis_device.vapix.close()


@pytest.fixture
def object_analytics(device) -> ObjectAnalytics:
    """Returns the object analytics mock object."""
    return ObjectAnalytics(device.vapix.request)


@respx.mock
async def test_get_no_configuration(object_analytics):
    """Test no response from get_configuration"""
    route = respx.post("http://host:80/local/objectanalytics/control.cgi").respond(
        json={},
        headers={"Content-Type": "application/json"},
    )
    await object_analytics.update()

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/local/objectanalytics/control.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "method": "getConfiguration",
        "apiVersion": "1.0",
        "context": "Axis library",
        "params": {},
    }

    assert len(object_analytics.values()) == 0


@respx.mock
async def test_get_empty_configuration(object_analytics):
    """Test empty get_configuration"""
    respx.post("http://host:80/local/objectanalytics/control.cgi").respond(
        json=response_get_configuration_empty,
        headers={"Content-Type": "application/json"},
    )
    await object_analytics.update()

    assert len(object_analytics.values()) == 0


@respx.mock
async def test_get_configuration(object_analytics):
    """Test get_configuration"""
    respx.post("http://host:80/local/objectanalytics/control.cgi").respond(
        json=response_get_configuration,
        headers={"Content-Type": "application/json"},
    )
    await object_analytics.update()

    assert len(object_analytics.values()) == 2

    scenario1 = object_analytics["Device1Scenario1"]
    assert scenario1.id == "Device1Scenario1"
    assert scenario1.name == "Scenario 1"
    assert scenario1.camera == [{"id": 1}]
    assert scenario1.uid == 1
    assert scenario1.filters == [
        {"distance": 5, "type": "distanceSwayingObject"},
        {"time": 1, "type": "timeShortLivedLimit"},
        {"height": 3, "type": "sizePercentage", "width": 3},
    ]
    assert scenario1.object_classifications == []
    assert scenario1.perspectives == []
    assert scenario1.presets == []
    assert scenario1.triggers == [
        {
            "type": "includeArea",
            "vertices": [
                [-0.97, -0.97],
                [-0.97, 0.97],
                [0.97, 0.97],
                [0.97, -0.97],
            ],
        }
    ]
    assert scenario1.trigger_type == "motion"

    scenario2 = object_analytics["Device1Scenario2"]
    assert scenario2.id == "Device1Scenario2"
    assert scenario2.name == "Scenario 2"
    assert scenario2.camera == [{"id": 1}]
    assert scenario2.uid == 2
    assert scenario2.filters == [
        {"time": 1, "type": "timeShortLivedLimit"},
        {"height": 3, "type": "sizePercentage", "width": 3},
    ]
    assert scenario2.object_classifications == [{"type": "human"}]
    assert scenario2.perspectives == []
    assert scenario2.presets == []
    assert scenario2.triggers == [
        {
            "alarmDirection": "leftToRight",
            "type": "fence",
            "vertices": [[0, -0.7], [0, 0.7]],
        }
    ]
    assert scenario2.trigger_type == "fence"


response_get_configuration_empty = {
    "apiVersion": "1.0",
    "context": "Axis library",
    "data": {
        "devices": [{"id": 1, "rotation": 180, "type": "camera"}],
        "metadataOverlay": [],
        "perspectives": [],
        "scenarios": [],
        "status": {},
    },
    "method": "getConfiguration",
}


response_get_configuration = {
    "apiVersion": "1.0",
    "context": "Axis library",
    "data": {
        "devices": [{"id": 1, "rotation": 180, "type": "camera"}],
        "metadataOverlay": [],
        "perspectives": [],
        "scenarios": [
            {
                "devices": [{"id": 1}],
                "filters": [
                    {"distance": 5, "type": "distanceSwayingObject"},
                    {"time": 1, "type": "timeShortLivedLimit"},
                    {"height": 3, "type": "sizePercentage", "width": 3},
                ],
                "id": 1,
                "name": "Scenario 1",
                "objectClassifications": [],
                "perspectives": [],
                "presets": [],
                "triggers": [
                    {
                        "type": "includeArea",
                        "vertices": [
                            [-0.97, -0.97],
                            [-0.97, 0.97],
                            [0.97, 0.97],
                            [0.97, -0.97],
                        ],
                    }
                ],
                "type": "motion",
            },
            {
                "devices": [{"id": 1}],
                "filters": [
                    {"time": 1, "type": "timeShortLivedLimit"},
                    {"height": 3, "type": "sizePercentage", "width": 3},
                ],
                "id": 2,
                "name": "Scenario 2",
                "objectClassifications": [{"type": "human"}],
                "perspectives": [],
                "presets": [],
                "triggers": [
                    {
                        "alarmDirection": "leftToRight",
                        "type": "fence",
                        "vertices": [[0, -0.7], [0, 0.7]],
                    }
                ],
                "type": "fence",
            },
        ],
        "status": {},
    },
    "method": "getConfiguration",
}
