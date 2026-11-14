"""Application API.

Use VAPIX® Application API to upload, control and manage applications
and their license keys.
"""

from packaging import version

from ...models.applications.application import (
    Application,
    ListApplicationsRequest,
)
from ..api_handler import ApiHandler

MINIMUM_VERSION = "1.20"


class ApplicationsHandler(ApiHandler[Application]):
    """List applications installed on the device, such as video analytics."""

    @property
    def listed_in_parameters(self) -> bool:
        """Check whether device parameters report a supported application platform version."""
        if self.vapix.params.property_handler.supported and (
            properties := self.vapix.params.property_handler.get("0")
        ):
            return version.parse(properties.embedded_development) >= version.parse(
                MINIMUM_VERSION
            )
        return False

    async def _api_request(self) -> dict[str, Application]:
        """Read installed applications for this handler's cached data."""
        return await self.list_applications()

    async def list_applications(self) -> dict[str, Application]:
        """Read the applications installed on the device."""
        response = await self.vapix.api_request(ListApplicationsRequest())
        return response.data
