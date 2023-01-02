"""Application API.

Use VAPIX® Application API to upload, control and manage applications and their license keys.
"""

from ...models.applications.application import Application
from ..api import APIItems

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
