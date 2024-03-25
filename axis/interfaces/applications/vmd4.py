"""VMD4 API."""

from ...models.applications.application import ApplicationName
from ...models.applications.vmd4 import (
    Configuration,
    GetConfigurationRequest,
    GetConfigurationResponse,
)
from .application_handler import ApplicationHandler


class Vmd4Handler(ApplicationHandler[Configuration]):
    """VMD4 handler for Axis devices."""

    app_name = ApplicationName.VMD4

    async def get_configuration(self) -> Configuration:
        """Get configuration of VMD4 application."""
        bytes_data = await self.vapix.api_request(GetConfigurationRequest())
        response = GetConfigurationResponse.decode(bytes_data)
        return response.data
