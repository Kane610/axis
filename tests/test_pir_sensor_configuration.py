"""Test Axis PIR sensor configuration API.

pytest --cov-report term-missing --cov=axis.vapix.interfaces.pir_sensor_configuration tests/test_pir_sensor_configuration.py
"""

import json

import pytest
import respx

from axis.device import AxisDevice
from axis.vapix.interfaces.pir_sensor_configuration import PirSensorConfiguration

from .conftest import HOST


@pytest.fixture
def pir_sensor_configuration(axis_device: AxisDevice) -> PirSensorConfiguration:
    """Return the pir_sensor_configuration mock object."""
    return axis_device.vapix.pir_sensor_configuration


@respx.mock
@pytest.mark.asyncio
async def test_get_api_list(pir_sensor_configuration: PirSensorConfiguration):
    """Test list_sensors call."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/pirsensor.cgi").respond(
        json=response_list_sensors,
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


response_list_sensors = {
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
}
