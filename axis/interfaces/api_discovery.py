"""Find the APIs and versions an Axis device advertises through VAPIX API Discovery.

The AXIS API Discovery service makes it possible to retrieve information
about what APIs are supported per device.
"""

from ..models.api_discovery import (
    API_VERSION,
    Api,
    ApiId,
    GetSupportedVersionsRequest,
    ListApisRequest,
)
from .api_handler import ApiHandler


class ApiDiscoveryHandler(ApiHandler[Api]):
    """Read the device's advertised API list and supported discovery-service versions."""

    api_id = ApiId.API_DISCOVERY
    default_api_version = API_VERSION

    @property
    def listed_in_api_discovery(self) -> bool:
        """Allow discovery itself to be queried before any API list has been loaded."""
        return True

    async def _api_request(self) -> dict[str, Api]:
        """Read the advertised API list for this handler's cached data."""
        return await self.get_api_list()

    async def get_api_list(self) -> dict[str, Api]:
        """List all APIs registered on API Discovery service."""
        response = await self.vapix.api_request(ListApisRequest())
        return response.data

    async def get_supported_versions(self) -> list[str]:
        """List supported API versions."""
        response = await self.vapix.api_request(GetSupportedVersionsRequest())
        return response.data
