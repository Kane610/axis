"""Application API.

Use VAPIX® Application API to upload, control and manage applications and their license keys.
"""

from ...models.api_discovery import ApiId
from ...models.applications.application import (
    Application,
    ListApplicationsRequest,
    ListApplicationsResponse,
)
from ..api_handler import ApiHandler

URL = "/axis-cgi/applications"
URL_CONTROL = f"{URL}/control.cgi"
URL_LICENSE = f"{URL}/license.cgi"
URL_LIST = f"{URL}/list.cgi"
URL_UPLOAD = f"{URL}/upload.cgi"

PARAM_CGI_KEY = "Properties.EmbeddedDevelopment.Version"
PARAM_CGI_VALUE = "1.20"

APPLICATION_STATE_RUNNING = "Running"
APPLICATION_STATE_STOPPED = "Stopped"


class ApplicationsHandler(ApiHandler[Application]):
    """API Discovery for Axis devices."""

    api_id = ApiId.UNKNOWN

    async def _api_request(self) -> dict[str, Application]:
        """Get default data of API discovery."""
        return await self.get_api_list()

    async def get_api_list(self) -> dict[str, Application]:
        """List all APIs registered on API Discovery service."""
        bytes_data = await self.vapix.new_request(ListApplicationsRequest())
        response = ListApplicationsResponse.decode(bytes_data)
        return response.data
