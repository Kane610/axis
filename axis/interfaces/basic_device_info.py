"""Read device identity and firmware through the VAPIX Basic Device Information API."""

from ..models.api_discovery import ApiId
from ..models.basic_device_info import (
    API_VERSION,
    DeviceInformation,
    GetAllPropertiesRequest,
    GetSupportedVersionsRequest,
)
from .api_handler import ApiHandler, HandlerGroup


class BasicDeviceInfoHandler(ApiHandler[DeviceInformation]):
    """Basic device information for Axis devices."""

    api_id = ApiId.BASIC_DEVICE_INFO
    default_api_version = API_VERSION
    handler_groups = (HandlerGroup.API_DISCOVERY,)

    async def _api_request(self) -> dict[str, DeviceInformation]:
        """Read product information for this handler's cached data."""
        return await self.get_all_properties()

    async def get_all_properties(self) -> dict[str, DeviceInformation]:
        """Read all basic product properties and return them under item ID 0."""
        response = await self.vapix.api_request(
            GetAllPropertiesRequest(self.api_version)
        )
        return {"0": response.data}

    async def get_supported_versions(self) -> list[str]:
        """List supported API versions."""
        response = await self.vapix.api_request(GetSupportedVersionsRequest())
        return response.data
