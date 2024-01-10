"""Motion Guard API.

AXIS Motion Guard is a video motion detection application that detects
and triggers an alarm whenever an object, such as a person or vehicle,
moves within predefined areas in a camera’s field of view.
"""


from ...models.applications.api import ApplicationAPIItem
from ...models.applications.motion_guard import (
    Configuration,
    GetConfigurationRequest,
    GetConfigurationResponse,
)
from .api import ApplicationAPIItems
from .application_handler import ApplicationHandler

URL = "/local/motionguard/control.cgi"

API_VERSION = "1.3"

APPLICATION_NAME = "motionguard"

PARAM_CGI_KEY = "Properties.EmbeddedDevelopment.Version"
PARAM_CGI_VALUE = "2.13"


class MotionGuard(ApplicationAPIItems):
    """Motion Guard application on Axis devices."""

    api_version = API_VERSION
    name = APPLICATION_NAME

    item_cls = ApplicationAPIItem
    path = URL


class MotionGuardHandler(ApplicationHandler[Configuration]):
    """Motion guard handler for Axis devices."""

    app_name = "motionguard"

    async def _api_request(self) -> dict[str, Configuration]:
        """Get default configuration."""
        return {"0": await self.get_configuration()}

    async def get_configuration(self) -> Configuration:
        """Get configuration of VMD4 application."""
        bytes_data = await self.vapix.new_request(GetConfigurationRequest())
        response = GetConfigurationResponse.decode(bytes_data)
        return response.data
