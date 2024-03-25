"""Loitering Guard API.

AXIS Loitering Guard tracks moving objects such as people and vehicles,
and triggers an alarm if they have been in a predefined area for too long.
"""

from ...models.applications.application import ApplicationName
from ...models.applications.loitering_guard import (
    Configuration,
    GetConfigurationRequest,
    GetConfigurationResponse,
)
from .application_handler import ApplicationHandler


class LoiteringGuardHandler(ApplicationHandler[Configuration]):
    """Loitering guard handler for Axis devices."""

    app_name = ApplicationName.LOITERING_GUARD

    async def get_configuration(self) -> Configuration:
        """Get configuration of VMD4 application."""
        bytes_data = await self.vapix.api_request(GetConfigurationRequest())
        response = GetConfigurationResponse.decode(bytes_data)
        return response.data
