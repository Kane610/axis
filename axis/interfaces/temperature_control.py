"""VAPIX temperature control handler for Axis devices.

Implements the handler for the Axis VAPIX temperature control API, providing access to device temperature sensors, heaters, and fans through standardized endpoints.
Coordinates API requests and response parsing for temperature-related device features.
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
        """Get default temperature status data."""
        return await self.get_status_all()

    async def get_status_all(self) -> dict[str, TemperatureDevice]:
        """Retrieve current status for all temperature devices."""
        response = await self.vapix.api_request(GetStatusAllRequest())
        return response.data

    @property
    def sensors(self) -> dict[str, TemperatureSensor]:
        """Return all temperature sensors keyed by id."""
        return {k: v for k, v in self.items() if isinstance(v, TemperatureSensor)}

    @property
    def heaters(self) -> dict[str, TemperatureHeater]:
        """Return all heaters keyed by id."""
        return {k: v for k, v in self.items() if isinstance(v, TemperatureHeater)}

    @property
    def fans(self) -> dict[str, TemperatureFan]:
        """Return all fans keyed by id."""
        return {k: v for k, v in self.items() if isinstance(v, TemperatureFan)}

    def get_sensor(self, sensor_id: str) -> TemperatureSensor | None:
        """Return a specific sensor by id when available."""
        item = self.get(sensor_id)
        return item if isinstance(item, TemperatureSensor) else None

    def get_heater(self, heater_id: str) -> TemperatureHeater | None:
        """Return a specific heater by id when available."""
        item = self.get(heater_id)
        return item if isinstance(item, TemperatureHeater) else None

    def get_fan(self, fan_id: str) -> TemperatureFan | None:
        """Return a specific fan by id when available."""
        item = self.get(fan_id)
        return item if isinstance(item, TemperatureFan) else None

    @property
    def running_heaters(self) -> dict[str, TemperatureHeater]:
        """Return all currently running heaters keyed by id."""
        return {
            k: v
            for k, v in self.heaters.items()
            if v.status == TemperatureDeviceStatus.RUNNING
        }

    @property
    def running_fans(self) -> dict[str, TemperatureFan]:
        """Return all currently running fans keyed by id."""
        return {
            k: v
            for k, v in self.fans.items()
            if v.status == TemperatureDeviceStatus.RUNNING
        }

    @property
    def running_actuators(self) -> dict[str, TemperatureActuator]:
        """Return all currently running actuators (heaters and fans) keyed by id."""
        return {
            k: v
            for k, v in self.items()
            if isinstance(v, TemperatureActuator)
            and v.status == TemperatureDeviceStatus.RUNNING
        }
