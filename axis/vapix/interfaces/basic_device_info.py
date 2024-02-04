"""Basic Device Info api.

AXIS Basic device information API can be used to retrieve
 simple information about the product.
This information is used to identify basic properties of the product.
"""

from ..models.api_discovery import ApiId
from ..models.basic_device_info import (
    API_VERSION,
    DeviceInformation,
    GetAllPropertiesRequest,
    GetAllPropertiesResponse,
    GetSupportedVersionsRequest,
    GetSupportedVersionsResponse,
)
from .api_handler import ApiHandler


class BasicDeviceInfoHandler(ApiHandler[DeviceInformation]):
    """Basic device information for Axis devices."""

    api_id = ApiId.BASIC_DEVICE_INFO
    default_api_version = API_VERSION

    async def _api_request(self) -> dict[str, DeviceInformation]:
        """Get default data of basic device information."""
        return await self.get_all_properties()

    async def get_all_properties(self) -> dict[str, DeviceInformation]:
        """List all properties of basic device info."""
        discovery_item = self.vapix.api_discovery[self.api_id]
        bytes_data = await self.vapix.api_request(
            GetAllPropertiesRequest(discovery_item.version)
        )
        response = GetAllPropertiesResponse.decode(bytes_data)
        return {"0": response.data}

    async def get_supported_versions(self) -> list[str]:
        """List supported API versions."""
        bytes_data = await self.vapix.api_request(GetSupportedVersionsRequest())
        response = GetSupportedVersionsResponse.decode(bytes_data)
        return response.data
