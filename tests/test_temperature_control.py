"""Test Axis Temperature Control API."""

from typing import TYPE_CHECKING

import pytest

from axis.models.api_discovery import Api
from axis.models.temperature_control import (
    GetStatusAllRequest,
    TemperatureControlStatus,
    TemperatureDeviceStatus,
    TemperatureDeviceType,
)

from tests.conftest import (
    MockApiRequestAssertions,
    bind_mock_api_request,
)

if TYPE_CHECKING:
    from axis.device import AxisDevice
    from axis.interfaces.temperature_control import TemperatureControlHandler


STATUS_ALL_RESPONSE = """Sensor.S0.Name=Main
Sensor.S0.Celsius=43.50
Sensor.S0.Fahrenheit=110.30
Heater.H0.Status=Running[85%]
Heater.H0.TimeUntilStop=95
Fan.F0.Status=Stopped
Fan.F0.TimeUntilStop=0
"""


@pytest.fixture
async def temperature_control(axis_device: AxisDevice) -> TemperatureControlHandler:
    """Return the temperature_control handler."""
    axis_device.vapix.api_discovery._items = {
        api.id: api
        for api in [
            Api.decode(
                {
                    "id": "temperaturecontrol",
                    "version": "1.0",
                    "name": "Temperature control",
                    "docLink": "https://developer.axis.com/vapix/network-video/temperature-control/",
                }
            )
        ]
    }
    return axis_device.vapix.temperature_control


@pytest.fixture
def mock_temperature_request(mock_api_request):
    """Register temperature route mocks via explicit ApiRequest classes."""
    bound_request = bind_mock_api_request(mock_api_request, GetStatusAllRequest)

    def _register(text_data: str):
        return bound_request(
            text_data,
            assertions=MockApiRequestAssertions(params={"action": "statusall"}),
        )

    return _register


async def test_update(
    mock_temperature_request,
    temperature_control: TemperatureControlHandler,
) -> None:
    """Test update method for statusall endpoint."""
    route = mock_temperature_request(STATUS_ALL_RESPONSE)

    await temperature_control.update()

    assert route.called
    assert route.calls.last.request.method == "GET"
    assert route.calls.last.request.url.path == "/axis-cgi/temperaturecontrol.cgi"
    assert route.calls.last.request.url.params == {"action": "statusall"}
    assert temperature_control.initialized

    sensor = temperature_control["Sensor.S0"]
    assert isinstance(sensor, TemperatureControlStatus)
    assert sensor.device_type == TemperatureDeviceType.SENSOR
    assert sensor.name == "Main"
    assert sensor.celsius == 43.5
    assert sensor.fahrenheit == 110.3

    heater = temperature_control["Heater.H0"]
    assert isinstance(heater, TemperatureControlStatus)
    assert heater.device_type == TemperatureDeviceType.HEATER
    assert heater.status == TemperatureDeviceStatus.RUNNING
    assert heater.status_raw == "Running[85%]"
    assert heater.intensity == 85
    assert heater.time_until_stop == 95

    fan = temperature_control["Fan.F0"]
    assert isinstance(fan, TemperatureControlStatus)
    assert fan.device_type == TemperatureDeviceType.FAN
    assert fan.status == TemperatureDeviceStatus.STOPPED
    assert fan.intensity is None
    assert fan.time_until_stop == 0


async def test_get_status_all_unknown_and_partial_data(
    mock_temperature_request,
    temperature_control: TemperatureControlHandler,
) -> None:
    """Test parser behavior for unknown states and malformed numbers."""
    route = mock_temperature_request(
        """Heater.H1.Status=Running[X]
Heater.H1.TimeUntilStop=bad
Sensor.S1.Celsius=NaNValue
Sensor.S1.Fahrenheit=100.5
Fan.F9.Status=Fan Failure
"""
    )

    data = await temperature_control.get_status_all()

    assert route.called

    heater = data["Heater.H1"]
    assert isinstance(heater, TemperatureControlStatus)
    assert heater.status == TemperatureDeviceStatus.RUNNING
    assert heater.intensity is None
    assert heater.time_until_stop is None

    sensor = data["Sensor.S1"]
    assert sensor.celsius is None
    assert sensor.fahrenheit == 100.5

    fan = data["Fan.F9"]
    assert fan.status == TemperatureDeviceStatus.FAILURE


async def test_grouped_accessors(
    mock_temperature_request,
    temperature_control: TemperatureControlHandler,
) -> None:
    """Test grouped typed accessors for sensors, heaters and fans."""
    mock_temperature_request(STATUS_ALL_RESPONSE)

    await temperature_control.update()

    sensors = temperature_control.sensors
    heaters = temperature_control.heaters
    fans = temperature_control.fans

    assert list(sensors) == ["Sensor.S0"]
    assert list(heaters) == ["Heater.H0"]
    assert list(fans) == ["Fan.F0"]

    assert isinstance(sensors["Sensor.S0"], TemperatureControlStatus)
    assert isinstance(heaters["Heater.H0"], TemperatureControlStatus)
    assert isinstance(fans["Fan.F0"], TemperatureControlStatus)


async def test_item_accessors(
    mock_temperature_request,
    temperature_control: TemperatureControlHandler,
) -> None:
    """Test single-item typed accessors for sensors, heaters and fans."""
    mock_temperature_request(STATUS_ALL_RESPONSE)

    await temperature_control.update()

    sensor = temperature_control.get_sensor("Sensor.S0")
    heater = temperature_control.get_heater("Heater.H0")
    fan = temperature_control.get_fan("Fan.F0")

    assert isinstance(sensor, TemperatureControlStatus)
    assert isinstance(heater, TemperatureControlStatus)
    assert isinstance(fan, TemperatureControlStatus)

    assert temperature_control.get_sensor("Sensor.Missing") is None
    assert temperature_control.get_heater("Fan.F0") is None
    assert temperature_control.get_fan("Heater.H0") is None


async def test_running_actuator_accessors(
    mock_temperature_request,
    temperature_control: TemperatureControlHandler,
) -> None:
    """Test convenience accessors for currently running heaters and fans."""
    mock_temperature_request(
        """Sensor.S0.Name=Main
Heater.H0.Status=Running[85%]
Heater.H1.Status=Stopped
Fan.F0.Status=Running
Fan.F1.Status=Stopped
"""
    )

    await temperature_control.update()

    running_heaters = temperature_control.running_heaters
    running_fans = temperature_control.running_fans

    assert list(running_heaters) == ["Heater.H0"]
    assert list(running_fans) == ["Fan.F0"]

    assert isinstance(running_heaters["Heater.H0"], TemperatureControlStatus)
    assert isinstance(running_fans["Fan.F0"], TemperatureControlStatus)
