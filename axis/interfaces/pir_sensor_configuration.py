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
from .api_handler import ApiHandler, HandlerGroup


class PirSensorConfigurationHandler(ApiHandler[PirSensorConfiguration]):
    """PIR sensor configuration for Axis devices."""

    api_id = ApiId.PIR_SENSOR_CONFIGURATION
    default_api_version = API_VERSION
    handler_group = HandlerGroup.API_DISCOVERY

    async def _api_request(self) -> dict[str, PirSensorConfiguration]:
        """Get default data of PIR sensor configuration."""
        return await self.list_sensors()

    async def list_sensors(self) -> dict[str, PirSensorConfiguration]:
        """List all PIR sensors of device."""
        api_version = self.api_version
        bytes_data = await self.vapix.api_request(ListSensorsRequest(api_version))
        response = ListSensorsResponse.decode(bytes_data)
        return response.data

    async def get_sensitivity(self, id: int) -> float | None:
        """Retrieve configured sensitivity of specific sensor."""
        api_version = self.api_version
        bytes_data = await self.vapix.api_request(
            GetSensitivityRequest(id, api_version)
        )
        response = GetSensitivityResponse.decode(bytes_data)
        return response.data

    async def set_sensitivity(self, id: int, sensitivity: float) -> None:
        """Configure sensitivity of specific sensor."""
        api_version = self.api_version
        await self.vapix.api_request(
            SetSensitivityRequest(id, sensitivity, api_version)
        )

    async def get_supported_versions(self) -> list[str]:
        """List supported API versions."""
        bytes_data = await self.vapix.api_request(GetSupportedVersionsRequest())
        response = GetSupportedVersionsResponse.decode(bytes_data)
        return response.data
