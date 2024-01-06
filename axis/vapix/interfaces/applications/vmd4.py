"""VMD4 API."""

from ...models.api_discovery import ApiId
from ...models.applications.api import ApplicationAPIItem
from ...models.applications.vmd4 import (
    Configuration,
    GetConfigurationRequest,
    GetConfigurationResponse,
)
from ..api_handler import ApiHandler
from .api import ApplicationAPIItems

URL = "/local/vmd/control.cgi"

API_VERSION = "1.2"

APPLICATION_NAME = "vmd"

PARAM_CGI_KEY = "Properties.EmbeddedDevelopment.Version"
PARAM_CGI_VALUE = "2.12"


class Vmd4(ApplicationAPIItems):
    """VMD4 on Axis devices."""

    api_version = API_VERSION
    name = APPLICATION_NAME

    item_cls = ApplicationAPIItem
    path = URL


class Vmd4Handler(ApiHandler[Configuration]):
    """VMD4 handler for Axis devices."""

    api_id = ApiId.UNKNOWN

    async def _api_request(self) -> dict[str, Configuration]:
        """Get default configuration."""
        return {"0": await self.get_configuration()}

    async def get_configuration(self) -> Configuration:
        """Get configuration of VMD4 application."""
        bytes_data = await self.vapix.new_request(GetConfigurationRequest())
        response = GetConfigurationResponse.decode(bytes_data)
        return response.data
