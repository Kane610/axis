"""Test Axis Object Analytics API.

pytest --cov-report term-missing --cov=axis.applications.object_analytics tests/applications/test_object_analytics.py
"""

import json

import pytest
import respx

from axis.vapix.interfaces.applications.object_analytics import (
    ObjectAnalyticsHandler,
)
from axis.vapix.models.applications.object_analytics import ScenarioType

from ..conftest import HOST


@pytest.fixture
def object_analytics(axis_device) -> ObjectAnalyticsHandler:
    """Return the object analytics mock object."""
    return axis_device.vapix.object_analytics


@respx.mock
async def test_get_no_configuration(object_analytics):
    """Test no response from get_configuration."""
    route = respx.post(f"http://{HOST}:80/local/objectanalytics/control.cgi").respond(
        json={},
    )
    with pytest.raises(KeyError):
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
    """Test empty get_configuration."""
    respx.post(f"http://{HOST}:80/local/objectanalytics/control.cgi").respond(
        json=response_get_configuration_empty,
    )
    await object_analytics.update()

    assert len(object_analytics.values()) == 1


@respx.mock
async def test_get_configuration(object_analytics):
    """Test get_configuration."""
    respx.post(f"http://{HOST}:80/local/objectanalytics/control.cgi").respond(
        json=response_get_configuration,
    )
    await object_analytics.update()

    assert len(object_analytics.values()) == 1
    configuration = object_analytics["0"]

    assert configuration.id == "object analytics"
    assert configuration.devices == [{"id": 1, "rotation": 180, "type": "camera"}]
    assert configuration.metadata_overlay == []
    assert configuration.perspectives == []
    assert configuration.scenarios["1"].id == "1"
    assert configuration.scenarios["1"].devices == [{"id": 1}]
    assert configuration.scenarios["1"].filters == [
        {"distance": 5, "type": "distanceSwayingObject"},
        {"time": 1, "type": "timeShortLivedLimit"},
        {"height": 3, "type": "sizePercentage", "width": 3},
    ]
    assert configuration.scenarios["1"].name == "Scenario 1"
    assert configuration.scenarios["1"].object_classifications == []
    assert configuration.scenarios["1"].perspectives == []
    assert configuration.scenarios["1"].presets == []
    assert configuration.scenarios["1"].triggers == [
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
    assert configuration.scenarios["1"].type == ScenarioType.MOTION

    assert configuration.scenarios["2"].devices == [{"id": 1}]
    assert configuration.scenarios["2"].filters == [
        {"time": 1, "type": "timeShortLivedLimit"},
        {"height": 3, "type": "sizePercentage", "width": 3},
    ]
    assert configuration.scenarios["2"].id == "2"
    assert configuration.scenarios["2"].name == "Scenario 2"
    assert configuration.scenarios["2"].object_classifications == [{"type": "human"}]
    assert configuration.scenarios["2"].perspectives == []
    assert configuration.scenarios["2"].presets == []
    assert configuration.scenarios["2"].triggers == [
        {
            "alarmDirection": "leftToRight",
            "type": "fence",
            "vertices": [[0, -0.7], [0, 0.7]],
        }
    ]
    assert configuration.scenarios["2"].type == ScenarioType.FENCE


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
