"""Test Axis PIR sensor configuration API.

pytest --cov-report term-missing --cov=axis.interfaces.pir_sensor_configuration tests/test_pir_sensor_configuration.py
"""

from typing import TYPE_CHECKING
from unittest.mock import MagicMock

import pytest

from axis.models.pir_sensor_configuration import (
    GetSensitivityRequest,
    GetSupportedVersionsRequest,
    ListSensorsRequest,
    SetSensitivityRequest,
)

from tests.conftest import (
    MockApiRequestAssertions,
    MockApiResponseSpec,
    bind_mock_api_request,
)

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


@pytest.fixture
def mock_pir_request(mock_api_request):
    """Register PIR sensor mocks via ApiRequest classes."""

    def _register(api_request, json_data, *, content):
        return bind_mock_api_request(mock_api_request, api_request)(
            response=MockApiResponseSpec(json=json_data),
            assertions=MockApiRequestAssertions(content=content),
        )

    return _register


async def test_get_api_list(
    mock_pir_request,
    pir_sensor_configuration: PirSensorConfigurationHandler,
) -> None:
    """Test list_sensors call."""
    route = mock_pir_request(
        ListSensorsRequest,
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
        content=ListSensorsRequest(api_version="1.0").content,
    )
    await pir_sensor_configuration.update()

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/pirsensor.cgi"

    assert pir_sensor_configuration.initialized

    item = pir_sensor_configuration["0"]
    assert item.configurable
    assert item.sensitivity == 0.94117647409439087


async def test_get_sensitivity(
    mock_pir_request,
    pir_sensor_configuration: PirSensorConfigurationHandler,
) -> None:
    """Test list_sensors call."""
    route = mock_pir_request(
        GetSensitivityRequest,
        {
            "apiVersion": "1.0",
            "context": "Axis library",
            "method": "getSensitivity",
            "data": {
                "sensitivity": 1,
            },
        },
        content=GetSensitivityRequest(id=0, api_version="1.0").content,
    )
    assert await pir_sensor_configuration.get_sensitivity(id=0) == 1

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/pirsensor.cgi"


async def test_set_sensitivity(
    mock_pir_request,
    pir_sensor_configuration: PirSensorConfigurationHandler,
) -> None:
    """Test list_sensors call."""
    route = mock_pir_request(
        SetSensitivityRequest,
        {
            "apiVersion": "1.0",
            "context": "Axis library",
            "method": "setSensitivity",
        },
        content=SetSensitivityRequest(id=0, sensitivity=1, api_version="1.0").content,
    )
    await pir_sensor_configuration.set_sensitivity(id=0, sensitivity=1)

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/pirsensor.cgi"


async def test_supported_versions(
    mock_pir_request,
    pir_sensor_configuration: PirSensorConfigurationHandler,
) -> None:
    """Test list_sensors call."""
    route = mock_pir_request(
        GetSupportedVersionsRequest,
        {
            "apiVersion": "1.0",
            "context": "Axis library",
            "method": "getSupportedVersions",
            "data": {
                "apiVersions": ["1", "2"],
            },
        },
        content=GetSupportedVersionsRequest().content,
    )
    assert await pir_sensor_configuration.get_supported_versions() == ["1", "2"]

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/pirsensor.cgi"
