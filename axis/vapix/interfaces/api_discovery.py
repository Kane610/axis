"""API Discovery api.

The AXIS API Discovery service makes it possible to retrieve information
about what APIs are supported per device.
"""

from ..models.api_discovery import (
    Api,
    ApiId,
    GetSupportedVersionsRequest,
    ListApisRequest,
    ListApisT,
)
from .api_handler import ApiHandler

URL = "/axis-cgi/apidiscovery.cgi"


class ApiDiscoveryHandler(ApiHandler[Api]):
    """API Discovery for Axis devices."""

    api_id = ApiId.API_DISCOVERY
    api_request = ListApisRequest()

    async def get_api_list(self) -> ListApisT:
        """List all APIs registered on API Discovery service."""
        assert self.vapix.api_discovery
        discovery_item = self.vapix.api_discovery[self.api_id.value]
        assert hasattr(discovery_item, "version")
        return await self.vapix.request2(ListApisRequest(discovery_item.version))

    async def get_supported_versions(self) -> list[str]:
        """List supported API versions."""
        return await self.vapix.request2(GetSupportedVersionsRequest())
