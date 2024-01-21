"""API Discovery api.

The AXIS API Discovery service makes it possible to retrieve information
about what APIs are supported per device.
"""

from ...errors import PathNotFound
from ..models.api_discovery import (
    API_VERSION,
    Api,
    ApiId,
    GetAllApisResponse,
    GetSupportedVersionsRequest,
    GetSupportedVersionsResponse,
    ListApisRequest,
    ListApisT,
)
from .api_handler import ApiHandler


class ApiDiscoveryHandler(ApiHandler[Api]):
    """API Discovery for Axis devices."""

    api_id = ApiId.API_DISCOVERY
    default_api_version = API_VERSION

    async def do_update(self, skip_support_check=False) -> bool:
        """Try update of API."""
        try:
            return await super().do_update(skip_support_check)
        except PathNotFound:  # Device doesn't support the endpoint
            pass
        return False

    async def _api_request(self) -> dict[str, Api]:
        """Get default data of API discovery."""
        return await self.get_api_list()

    async def get_api_list(self) -> ListApisT:
        """List all APIs registered on API Discovery service."""
        bytes_data = await self.vapix.api_request(ListApisRequest())
        response = GetAllApisResponse.decode(bytes_data)
        return {api.id: api for api in response.data}

    async def get_supported_versions(self) -> list[str]:
        """List supported API versions."""
        bytes_data = await self.vapix.api_request(GetSupportedVersionsRequest())
        response = GetSupportedVersionsResponse.decode(bytes_data)
        return response.data
