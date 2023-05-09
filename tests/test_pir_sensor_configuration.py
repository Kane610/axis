"""Test Axis PIR sensor configuration API.

pytest --cov-report term-missing --cov=axis.vapix.interfaces.pir_sensor_configuration tests/test_pir_sensor_configuration.py
"""

import json
from unittest.mock import MagicMock

import pytest
import respx

from axis.device import AxisDevice
from axis.vapix.interfaces.pir_sensor_configuration import PirSensorConfigurationHandler

from .conftest import HOST


@pytest.fixture
def pir_sensor_configuration(axis_device: AxisDevice) -> PirSensorConfigurationHandler:
    """Return the pir_sensor_configuration mock object."""
    axis_device.vapix.api_discovery = api_discovery_mock = MagicMock()
    api_discovery_mock.__getitem__().version = "1.0"
    return axis_device.vapix.pir_sensor_configuration


@respx.mock
async def test_get_api_list(
    pir_sensor_configuration: PirSensorConfigurationHandler,
) -> None:
    """Test list_sensors call."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/pirsensor.cgi").respond(
        json={
            "apiVersion": "1.0",
            "context": "Axis library",
            "method": "listSensors",
            "data": {
                "sensors": [
                    {
                        "id": 0,
                        "sensitivityConfigurable": True,
                        "sensitivity": 0.94117647409439087,
                    }
                ]
            },
        },
    )
    await pir_sensor_configuration.update()

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/pirsensor.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "method": "listSensors",
        "apiVersion": "1.0",
        "context": "Axis library",
    }

    items = await pir_sensor_configuration.list_sensors()
    assert len(items) == 1
    item = items[0]
    assert item.configurable
    assert item.sensitivity == 0.94117647409439087


@respx.mock
async def test_get_sensitivity(
    pir_sensor_configuration: PirSensorConfigurationHandler,
) -> None:
    """Test list_sensors call."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/pirsensor.cgi").respond(
        json={
            "apiVersion": "1.0",
            "context": "Axis library",
            "method": "getSensitivity",
            "data": {
                "sensitivity": 1,
            },
        },
    )
    assert await pir_sensor_configuration.get_sensitivity(id=0) == 1

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/pirsensor.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "method": "getSensitivity",
        "apiVersion": "1.0",
        "context": "Axis library",
        "params": {
            "id": 0,
        },
    }


@respx.mock
async def test_set_sensitivity(
    pir_sensor_configuration: PirSensorConfigurationHandler,
) -> None:
    """Test list_sensors call."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/pirsensor.cgi").respond(
        json={
            "apiVersion": "1.0",
            "context": "Axis library",
            "method": "setSensitivity",
        },
    )
    assert await pir_sensor_configuration.set_sensitivity(id=0, sensitivity=1) is None

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/pirsensor.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "method": "setSensitivity",
        "apiVersion": "1.0",
        "context": "Axis library",
        "params": {
            "id": 0,
            "sensitivity": 1,
        },
    }


@respx.mock
async def test_supported_versions(
    pir_sensor_configuration: PirSensorConfigurationHandler,
) -> None:
    """Test list_sensors call."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/pirsensor.cgi").respond(
        json={
            "apiVersion": "1.0",
            "context": "Axis library",
            "method": "getSupportedVersions",
            "data": {
                "apiVersions": ["1", "2"],
            },
        },
    )
    assert await pir_sensor_configuration.get_supported_versions() == ["1", "2"]

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/pirsensor.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "method": "getSupportedVersions",
        "context": "Axis library",
    }
