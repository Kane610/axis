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
    PirSensorConfiguration,
    SetSensitivityRequest,
)
from .api_handler import ApiHandler


class PirSensorConfigurationHandler(ApiHandler[PirSensorConfiguration]):
    """PIR sensor configuration for Axis devices."""

    api_id = ApiId.PIR_SENSOR_CONFIGURATION
    default_api_version = API_VERSION

    async def _api_request(self) -> dict[str, PirSensorConfiguration]:
        """Get default data of PIR sensor configuration."""
        return await self.list_sensors()

    async def list_sensors(self) -> dict[str, PirSensorConfiguration]:
        """List all PIR sensors of device."""
        discovery_item = self.vapix.api_discovery[self.api_id]
        bytes_data = await self.vapix.api_request(
            ListSensorsRequest(discovery_item.version)
        )
        response = ListSensorsResponse.decode(bytes_data)
        return response.data

    async def get_sensitivity(self, id: int) -> float | None:
        """Retrieve configured sensitivity of specific sensor."""
        discovery_item = self.vapix.api_discovery[self.api_id]
        bytes_data = await self.vapix.api_request(
            GetSensitivityRequest(id, discovery_item.version)
        )
        response = GetSensitivityResponse.decode(bytes_data)
        return response.data

    async def set_sensitivity(self, id: int, sensitivity: float) -> None:
        """Configure sensitivity of specific sensor."""
        discovery_item = self.vapix.api_discovery[self.api_id]
        await self.vapix.api_request(
            SetSensitivityRequest(id, sensitivity, discovery_item.version)
        )

    async def get_supported_versions(self) -> list[str]:
        """List supported API versions."""
        bytes_data = await self.vapix.api_request(GetSupportedVersionsRequest())
        response = GetSupportedVersionsResponse.decode(bytes_data)
        return response.data
