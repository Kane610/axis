"""Motion Guard API.

AXIS Motion Guard is a video motion detection application that detects
and triggers an alarm whenever an object, such as a person or vehicle,
moves within predefined areas in a camera's field of view.
"""

from ...models.applications.application import ApplicationName
from ...models.applications.motion_guard import (
    Configuration,
    GetConfigurationRequest,
)
from .application_handler import ApplicationHandler


class MotionGuardHandler(ApplicationHandler[Configuration]):
    """Read the Motion Guard application's configuration from an Axis device."""

    app_name = ApplicationName.MOTION_GUARD

    async def get_configuration(self) -> Configuration:
        """Read the Motion Guard application's configuration."""
        response = await self.vapix.api_request(GetConfigurationRequest())
        return response.data
