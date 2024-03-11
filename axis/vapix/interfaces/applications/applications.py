"""Application API.

Use VAPIX® Application API to upload, control and manage applications
and their license keys.
"""

from packaging import version

from ...models.applications.application import (
    Application,
    ListApplicationsRequest,
    ListApplicationsResponse,
)
from ..api_handler import ApiHandler

MINIMUM_VERSION = "1.20"


class ApplicationsHandler(ApiHandler[Application]):
    """API Discovery for Axis devices."""

    @property
    def listed_in_parameters(self) -> bool:
        """Is application supported and in a usable state."""
        if self.vapix.params.property_handler.supported and (
            properties := self.vapix.params.property_handler.get("0")
        ):
            return version.parse(properties.embedded_development) >= version.parse(
                MINIMUM_VERSION
            )
        return False

    async def _api_request(self) -> dict[str, Application]:
        """Get default data of API discovery."""
        return await self.list_applications()

    async def list_applications(self) -> dict[str, Application]:
        """List all APIs registered on API Discovery service."""
        bytes_data = await self.vapix.api_request(ListApplicationsRequest())
        response = ListApplicationsResponse.decode(bytes_data)
        return response.data
