"""VMD4 API."""

from ...models.applications.vmd4 import (
    Configuration,
    GetConfigurationRequest,
    GetConfigurationResponse,
)
from .application_handler import ApplicationHandler


class Vmd4Handler(ApplicationHandler[Configuration]):
    """VMD4 handler for Axis devices."""

    app_name = "vmd"

    async def _api_request(self) -> dict[str, Configuration]:
        """Get default configuration."""
        return {"0": await self.get_configuration()}

    async def get_configuration(self) -> Configuration:
        """Get configuration of VMD4 application."""
        bytes_data = await self.vapix.new_request(GetConfigurationRequest())
        response = GetConfigurationResponse.decode(bytes_data)
        return response.data
