"""Test Axis PIR sensor configuration API.

pytest --cov-report term-missing --cov=axis.interfaces.pir_sensor_configuration tests/test_pir_sensor_configuration.py
"""

from typing import TYPE_CHECKING
from unittest.mock import MagicMock

import pytest

if TYPE_CHECKING:
    from axis.device import AxisDevice
    from axis.interfaces.pir_sensor_configuration import PirSensorConfigurationHandler


@pytest.fixture
def pir_sensor_configuration(
    axis_device: AxisDevice,
) -> PirSensorConfigurationHandler:
    """Return the pir_sensor_configuration mock object."""
    axis_device.vapix.api_discovery = api_discovery_mock = MagicMock()
    api_discovery_mock.__getitem__().version = "1.0"
    return axis_device.vapix.pir_sensor_configuration


async def _setup_pirsensor_route(
    aiohttp_mock_server,
    pir_sensor_configuration: PirSensorConfigurationHandler,
    response_json: dict[str, object],
) -> list[dict[str, object]]:
    _server, requests = await aiohttp_mock_server(
        "/axis-cgi/pirsensor.cgi",
        method="POST",
        response=response_json,
        device=pir_sensor_configuration,
        capture_payload=True,
    )
    return requests


async def test_get_api_list(
    aiohttp_mock_server,
    pir_sensor_configuration: PirSensorConfigurationHandler,
) -> None:
    """Test list_sensors call."""
    requests = await _setup_pirsensor_route(
        aiohttp_mock_server,
        pir_sensor_configuration,
        {
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

    assert requests
    assert requests[-1]["method"] == "POST"
    assert requests[-1]["path"] == "/axis-cgi/pirsensor.cgi"
    assert requests[-1]["payload"] == {
        "method": "listSensors",
        "apiVersion": "1.0",
        "context": "Axis library",
    }

    assert pir_sensor_configuration.initialized

    item = pir_sensor_configuration["0"]
    assert item.configurable
    assert item.sensitivity == 0.94117647409439087


async def test_get_sensitivity(
    aiohttp_mock_server,
    pir_sensor_configuration: PirSensorConfigurationHandler,
) -> None:
    """Test list_sensors call."""
    requests = await _setup_pirsensor_route(
        aiohttp_mock_server,
        pir_sensor_configuration,
        {
            "apiVersion": "1.0",
            "context": "Axis library",
            "method": "getSensitivity",
            "data": {
                "sensitivity": 1,
            },
        },
    )
    assert await pir_sensor_configuration.get_sensitivity(id=0) == 1

    assert requests
    assert requests[-1]["method"] == "POST"
    assert requests[-1]["path"] == "/axis-cgi/pirsensor.cgi"
    assert requests[-1]["payload"] == {
        "method": "getSensitivity",
        "apiVersion": "1.0",
        "context": "Axis library",
        "params": {
            "id": 0,
        },
    }


async def test_set_sensitivity(
    aiohttp_mock_server,
    pir_sensor_configuration: PirSensorConfigurationHandler,
) -> None:
    """Test list_sensors call."""
    requests = await _setup_pirsensor_route(
        aiohttp_mock_server,
        pir_sensor_configuration,
        {
            "apiVersion": "1.0",
            "context": "Axis library",
            "method": "setSensitivity",
        },
    )
    await pir_sensor_configuration.set_sensitivity(id=0, sensitivity=1)

    assert requests
    assert requests[-1]["method"] == "POST"
    assert requests[-1]["path"] == "/axis-cgi/pirsensor.cgi"
    assert requests[-1]["payload"] == {
        "method": "setSensitivity",
        "apiVersion": "1.0",
        "context": "Axis library",
        "params": {
            "id": 0,
            "sensitivity": 1,
        },
    }


async def test_supported_versions(
    aiohttp_mock_server,
    pir_sensor_configuration: PirSensorConfigurationHandler,
) -> None:
    """Test list_sensors call."""
    requests = await _setup_pirsensor_route(
        aiohttp_mock_server,
        pir_sensor_configuration,
        {
            "apiVersion": "1.0",
            "context": "Axis library",
            "method": "getSupportedVersions",
            "data": {
                "apiVersions": ["1", "2"],
            },
        },
    )
    assert await pir_sensor_configuration.get_supported_versions() == ["1", "2"]

    assert requests
    assert requests[-1]["method"] == "POST"
    assert requests[-1]["path"] == "/axis-cgi/pirsensor.cgi"
    assert requests[-1]["payload"] == {
        "method": "getSupportedVersions",
        "context": "Axis library",
    }
