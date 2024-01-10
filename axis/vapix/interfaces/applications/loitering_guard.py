"""Loitering Guard API.

AXIS Loitering Guard tracks moving objects such as people and vehicles,
and triggers an alarm if they have been in a predefined area for too long.
"""


from ...models.applications.api import ApplicationAPIItem
from ...models.applications.vmd4 import (
    Configuration,
    GetConfigurationRequest,
    GetConfigurationResponse,
)
from .api import ApplicationAPIItems
from .application_handler import ApplicationHandler

URL = "/local/loiteringguard/control.cgi"

API_VERSION = "1.3"

APPLICATION_NAME = "loiteringguard"

PARAM_CGI_KEY = "Properties.EmbeddedDevelopment.Version"
PARAM_CGI_VALUE = "2.13"


class LoiteringGuard(ApplicationAPIItems):
    """Loitering Guard application on Axis devices."""

    api_version = API_VERSION
    name = APPLICATION_NAME

    item_cls = ApplicationAPIItem
    path = URL


class LoiteringGuardHandler(ApplicationHandler[Configuration]):
    """Loitering guard handler for Axis devices."""

    app_name = "loiteringguard"

    async def _api_request(self) -> dict[str, Configuration]:
        """Get default configuration."""
        return {"0": await self.get_configuration()}

    async def get_configuration(self) -> Configuration:
        """Get configuration of VMD4 application."""
        bytes_data = await self.vapix.new_request(GetConfigurationRequest())
        response = GetConfigurationResponse.decode(bytes_data)
        return response.data
