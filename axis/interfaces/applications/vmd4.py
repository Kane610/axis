"""Read Axis Video Motion Detection 4 (VMD4) configuration through its application API."""

from ...models.applications.application import ApplicationName
from ...models.applications.vmd4 import (
    Configuration,
    GetConfigurationRequest,
)
from .application_handler import ApplicationHandler


class Vmd4Handler(ApplicationHandler[Configuration]):
    """Read Video Motion Detection 4 settings from an Axis device."""

    app_name = ApplicationName.VMD4

    async def get_configuration(self) -> Configuration:
        """Get configuration of VMD4 application."""
        response = await self.vapix.api_request(GetConfigurationRequest())
        return response.data
