"""Fence Guard API.

AXIS Fence Guard allows you to set up virtual fences in a camera's field of view
to protect an area from intrusion. The application automatically triggers an alarm
when it detects a moving object, such as a person or vehicle, crossing a user-defined
virtual line.
"""

from ...models.applications.application import ApplicationName
from ...models.applications.fence_guard import (
    Configuration,
    GetConfigurationRequest,
    GetConfigurationResponse,
)
from .application_handler import ApplicationHandler


class FenceGuardHandler(ApplicationHandler[Configuration]):
    """Fence guard handler for Axis devices."""

    app_name = ApplicationName.FENCE_GUARD

    async def get_configuration(self) -> Configuration:
        """Get configuration of VMD4 application."""
        bytes_data = await self.vapix.api_request(GetConfigurationRequest())
        response = GetConfigurationResponse.decode(bytes_data)
        return response.data
