"""Application API.

Use VAPIX® Application API to upload, control and manage applications and their license keys.
"""

from ...models.api_discovery import ApiId
from ...models.applications.application import (
    App,
    Application,
    ListApplicationsRequest,
    ListApplicationsResponse,
)
from ..api import APIItems
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


class Applications(APIItems):
    """Applications on Axis devices."""

    item_cls = Application
    path = URL

    async def update(self) -> None:
        """Refresh data."""
        raw = await self.list()
        self.process_raw(raw)

    @staticmethod
    def pre_process_raw(raw: dict) -> dict:
        """Return a dictionary of applications."""
        if not raw:
            return {}

        if "application" not in raw.get("reply", {}):
            return {}

        raw_applications = raw["reply"]["application"]

        applications = {}

        if not isinstance(raw_applications, list):
            applications[raw_applications["@Name"]] = raw_applications

        else:
            for raw_application in raw_applications:
                applications[raw_application["@Name"]] = raw_application

        return applications

    async def list(self) -> dict:
        """Retrieve information about installed applications."""
        return await self.vapix.request("post", URL_LIST)


class ApplicationHandler(ApiHandler[App]):
    """API Discovery for Axis devices."""

    api_id = ApiId.UNKNOWN

    async def _api_request(self) -> dict[str, App]:
        """Get default data of API discovery."""
        return await self.get_api_list()

    async def get_api_list(self) -> dict[str, App]:
        """List all APIs registered on API Discovery service."""
        bytes_data = await self.vapix.new_request(ListApplicationsRequest())
        response = ListApplicationsResponse.decode(bytes_data)
        return response.data
