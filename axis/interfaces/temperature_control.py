"""Temperature control API."""

from ..models.api_discovery import ApiId
from ..models.temperature_control import (
    API_VERSION,
    ActuatorTemperatureControlStatus,
    GetStatusAllRequest,
    SensorTemperatureControlStatus,
    TemperatureControlStatus,
    TemperatureDeviceStatus,
    TemperatureDeviceType,
)
from .api_handler import ApiHandler, HandlerGroup


class TemperatureControlHandler(ApiHandler[TemperatureControlStatus]):
    """Temperature control status for Axis devices."""

    api_id = ApiId.TEMPERATURE_CONTROL
    default_api_version = API_VERSION
    handler_groups = (HandlerGroup.API_DISCOVERY,)

    async def _api_request(self) -> dict[str, TemperatureControlStatus]:
        """Get default temperature status data."""
        return await self.get_status_all()

    async def get_status_all(self) -> dict[str, TemperatureControlStatus]:
        """Retrieve current status for all temperature devices."""
        response = await self.vapix.api_request(GetStatusAllRequest())
        return response.data

    @property
    def sensors(self) -> dict[str, SensorTemperatureControlStatus]:
        """Return all temperature sensors keyed by id."""
        return {
            item_id: item
            for item_id, item in self.items()
            if item.device_type == TemperatureDeviceType.SENSOR
            and isinstance(item, SensorTemperatureControlStatus)
        }

    @property
    def heaters(self) -> dict[str, ActuatorTemperatureControlStatus]:
        """Return all heaters keyed by id."""
        return {
            item_id: item
            for item_id, item in self.items()
            if item.device_type == TemperatureDeviceType.HEATER
            and isinstance(item, ActuatorTemperatureControlStatus)
        }

    @property
    def fans(self) -> dict[str, ActuatorTemperatureControlStatus]:
        """Return all fans keyed by id."""
        return {
            item_id: item
            for item_id, item in self.items()
            if item.device_type == TemperatureDeviceType.FAN
            and isinstance(item, ActuatorTemperatureControlStatus)
        }

    def get_sensor(self, sensor_id: str) -> SensorTemperatureControlStatus | None:
        """Return a specific sensor by id when available."""
        sensor = self.get(sensor_id)
        if not isinstance(sensor, SensorTemperatureControlStatus):
            return None
        return sensor

    def get_heater(self, heater_id: str) -> ActuatorTemperatureControlStatus | None:
        """Return a specific heater by id when available."""
        heater = self.get(heater_id)
        if (
            not isinstance(heater, ActuatorTemperatureControlStatus)
            or heater.device_type != TemperatureDeviceType.HEATER
        ):
            return None
        return heater

    def get_fan(self, fan_id: str) -> ActuatorTemperatureControlStatus | None:
        """Return a specific fan by id when available."""
        fan = self.get(fan_id)
        if (
            not isinstance(fan, ActuatorTemperatureControlStatus)
            or fan.device_type != TemperatureDeviceType.FAN
        ):
            return None
        return fan

    @property
    def running_heaters(self) -> dict[str, ActuatorTemperatureControlStatus]:
        """Return all currently running heaters keyed by id."""
        return {
            item_id: item
            for item_id, item in self.heaters.items()
            if item.status == TemperatureDeviceStatus.RUNNING
        }

    @property
    def running_fans(self) -> dict[str, ActuatorTemperatureControlStatus]:
        """Return all currently running fans keyed by id."""
        return {
            item_id: item
            for item_id, item in self.fans.items()
            if item.status == TemperatureDeviceStatus.RUNNING
        }
