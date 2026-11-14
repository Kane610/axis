"""Read temperature sensor, heater, and fan status through VAPIX temperature control.

Status properties use cached data from the most recent handler update; they
do not poll the device automatically.
"""

from ..models.api_discovery import ApiId
from ..models.temperature_control import (
    API_VERSION,
    GetStatusAllRequest,
    TemperatureActuator,
    TemperatureDevice,
    TemperatureDeviceStatus,
    TemperatureFan,
    TemperatureHeater,
    TemperatureSensor,
)
from .api_handler import ApiHandler, HandlerGroup


class TemperatureControlHandler(ApiHandler[TemperatureDevice]):
    """Temperature control status for Axis devices."""

    api_id = ApiId.TEMPERATURE_CONTROL
    default_api_version = API_VERSION
    handler_groups = (HandlerGroup.API_DISCOVERY,)

    async def _api_request(self) -> dict[str, TemperatureDevice]:
        """Read temperature-device status for this handler's cached data."""
        return await self.get_status_all()

    async def get_status_all(self) -> dict[str, TemperatureDevice]:
        """Retrieve current status for all temperature devices."""
        response = await self.vapix.api_request(GetStatusAllRequest())
        return response.data

    @property
    def sensors(self) -> dict[str, TemperatureSensor]:
        """Return cached temperature sensors keyed by ID."""
        return {k: v for k, v in self.items() if isinstance(v, TemperatureSensor)}

    @property
    def heaters(self) -> dict[str, TemperatureHeater]:
        """Return cached heaters keyed by ID."""
        return {k: v for k, v in self.items() if isinstance(v, TemperatureHeater)}

    @property
    def fans(self) -> dict[str, TemperatureFan]:
        """Return cached fans keyed by ID."""
        return {k: v for k, v in self.items() if isinstance(v, TemperatureFan)}

    def get_sensor(self, sensor_id: str) -> TemperatureSensor | None:
        """Return a cached sensor by ID, or None if it has not been loaded."""
        item = self.get(sensor_id)
        return item if isinstance(item, TemperatureSensor) else None

    def get_heater(self, heater_id: str) -> TemperatureHeater | None:
        """Return a cached heater by ID, or None if it has not been loaded."""
        item = self.get(heater_id)
        return item if isinstance(item, TemperatureHeater) else None

    def get_fan(self, fan_id: str) -> TemperatureFan | None:
        """Return a cached fan by ID, or None if it has not been loaded."""
        item = self.get(fan_id)
        return item if isinstance(item, TemperatureFan) else None

    @property
    def running_heaters(self) -> dict[str, TemperatureHeater]:
        """Return cached heaters whose most recently reported status is running."""
        return {
            k: v
            for k, v in self.heaters.items()
            if v.status == TemperatureDeviceStatus.RUNNING
        }

    @property
    def running_fans(self) -> dict[str, TemperatureFan]:
        """Return cached fans whose most recently reported status is running."""
        return {
            k: v
            for k, v in self.fans.items()
            if v.status == TemperatureDeviceStatus.RUNNING
        }

    @property
    def running_actuators(self) -> dict[str, TemperatureActuator]:
        """Return cached heaters and fans whose most recently reported status is running."""
        return {
            k: v
            for k, v in self.items()
            if isinstance(v, TemperatureActuator)
            and v.status == TemperatureDeviceStatus.RUNNING
        }
