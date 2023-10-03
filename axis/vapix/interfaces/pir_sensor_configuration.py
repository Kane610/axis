"""PIR sensor configuration api.

The PIR sensor configuration API helps you list and configure
the sensitivity of the PIR (passive infrared) sensors on your Axis device.
"""

from ..models.api_discovery import ApiId
from ..models.pir_sensor_configuration import (
    API_VERSION,
    GetSensitivityRequest,
    GetSensitivityResponse,
    GetSupportedVersionsRequest,
    GetSupportedVersionsResponse,
    ListSensorsRequest,
    ListSensorsResponse,
    ListSensorsT,
    PirSensorConfiguration,
    SetSensitivityRequest,
)
from .api_handler import ApiHandler2


class PirSensorConfigurationHandler(ApiHandler2[PirSensorConfiguration]):
    """PIR sensor configuration for Axis devices."""

    api_id = ApiId.PIR_SENSOR_CONFIGURATION
    default_api_version = API_VERSION

    async def _api_request(self) -> ListSensorsT:
        """Get default data of PIR sensor configuration."""
        return await self.list_sensors()

    async def list_sensors(self) -> ListSensorsT:
        """List all PIR sensors of device."""
        discovery_item = self.vapix.api_discovery[self.api_id.value]
        bytes_data = await self.vapix.new_request(
            ListSensorsRequest(discovery_item.version)
        )
        response = ListSensorsResponse.decode(bytes_data)
        return response.data

    async def get_sensitivity(self, id: int) -> float | None:
        """Retrieve configured sensitivity of specific sensor."""
        discovery_item = self.vapix.api_discovery[self.api_id.value]
        bytes_data = await self.vapix.new_request(
            GetSensitivityRequest(id, discovery_item.version)
        )
        response = GetSensitivityResponse.decode(bytes_data)
        return response.data

    async def set_sensitivity(self, id: int, sensitivity: float) -> None:
        """Configure sensitivity of specific sensor."""
        discovery_item = self.vapix.api_discovery[self.api_id.value]
        await self.vapix.new_request(
            SetSensitivityRequest(id, sensitivity, discovery_item.version)
        )

    async def get_supported_versions(self) -> list[str]:
        """List supported API versions."""
        bytes_data = await self.vapix.new_request(GetSupportedVersionsRequest())
        response = GetSupportedVersionsResponse.decode(bytes_data)
        return response.data
