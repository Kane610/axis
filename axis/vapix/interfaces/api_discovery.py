"""API Discovery api.

The AXIS API Discovery service makes it possible to retrieve information
about what APIs are supported per device.
"""

from ..models.api_discovery import (
    API_VERSION,
    Api,
    ApiId,
    GetSupportedVersionsRequest,
    ListApisRequest,
    ListApisT,
)
from .api_handler import ApiHandler2


class ApiDiscoveryHandler(ApiHandler2[Api]):
    """API Discovery for Axis devices."""

    api_id = ApiId.API_DISCOVERY
    default_api_version = API_VERSION

    async def _api_request(self) -> dict[str, Api]:
        """Get default data of API discovery."""
        return await self.get_api_list()

    async def get_api_list(self) -> ListApisT:
        """List all APIs registered on API Discovery service."""
        version = self.api_version or API_VERSION
        response = await self.vapix.request3(ListApisRequest(version))
        return {api.id: api for api in response.data}

    async def get_supported_versions(self) -> list[str]:
        """List supported API versions."""
        response = await self.vapix.request3(GetSupportedVersionsRequest())
        return response.data
