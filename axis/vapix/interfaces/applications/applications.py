"""Application API.

Use VAPIX® Application API to upload, control and manage applications
and their license keys.
"""

from packaging import version

from ...models.api_discovery import ApiId
from ...models.applications.application import (
    Application,
    ListApplicationsRequest,
    ListApplicationsResponse,
)
from ..api_handler import ApiHandler

PARAM_CGI_KEY = "Properties.EmbeddedDevelopment.Version"
MINIMUM_VERSION = PARAM_CGI_VALUE = "1.20"


class ApplicationsHandler(ApiHandler[Application]):
    """API Discovery for Axis devices."""

    api_id = ApiId.UNKNOWN

    def supported(self) -> bool:
        """Is application supported and in a usable state."""
        if self.vapix.params.property_handler.supported() and (
            prop := self.vapix.params.property_handler["0"]
        ):
            return version.parse(prop.embedded_development) >= version.parse(
                MINIMUM_VERSION
            )
        return False

    async def _api_request(self) -> dict[str, Application]:
        """Get default data of API discovery."""
        return await self.get_api_list()

    async def get_api_list(self) -> dict[str, Application]:
        """List all APIs registered on API Discovery service."""
        bytes_data = await self.vapix.new_request(ListApplicationsRequest())
        response = ListApplicationsResponse.decode(bytes_data)
        return response.data
