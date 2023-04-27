"""PIR sensor configuration api.

The PIR sensor configuration API helps you list and configure
the sensitivity of the PIR (passive infrared) sensors on your Axis device.
"""
from ..models.api_discovery import ApiId
from ..models.pir_sensor_configuration import (
    GetSensitivityRequest,
    GetSupportedVersionsRequest,
    ListSensorsRequest,
    ListSensorsT,
    PirSensorConfiguration,
    SetSensitivityRequest,
)
from .api_handler import ApiHandler


class PirSensorConfigurationHandler(ApiHandler[PirSensorConfiguration]):
    """PIR sensor configuration for Axis devices."""

    api_id = ApiId.PIR_SENSOR_CONFIGURATION
    api_request = ListSensorsRequest()

    async def update(self) -> None:
        """Refresh data."""
        self._items = await self.list_sensors()

    async def list_sensors(self) -> ListSensorsT:
        """List all PIR sensors of device."""
        assert self.vapix.api_discovery
        discovery_item = self.vapix.api_discovery[self.api_id.value]
        api_request = ListSensorsRequest(discovery_item.version)
        raw = await self.vapix.request2(api_request)
        return api_request.process_raw(raw)

    async def get_sensitivity(self, id: int) -> float:
        """Retrieve configured sensitivity of specific sensor."""
        assert self.vapix.api_discovery
        discovery_item = self.vapix.api_discovery[self.api_id.value]
        api_request = GetSensitivityRequest(id, discovery_item.version)
        raw = await self.vapix.request2(api_request)
        return api_request.process_raw(raw)

    async def set_sensitivity(self, id: int, sensitivity: float) -> None:
        """Configure sensitivity of specific sensor."""
        assert self.vapix.api_discovery
        discovery_item = self.vapix.api_discovery[self.api_id.value]
        api_request = SetSensitivityRequest(id, sensitivity, discovery_item.version)
        raw = await self.vapix.request2(api_request)
        return api_request.process_raw(raw)

    async def get_supported_versions(self) -> list[str]:
        """List suppoerted API versions."""
        api_request = GetSupportedVersionsRequest()
        raw = await self.vapix.request2(api_request)
        return api_request.process_raw(raw)
