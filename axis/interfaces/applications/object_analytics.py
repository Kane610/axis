"""Object Analytics API.

AXIS Object Analytics.
"""

from ...models.applications.application import ApplicationName
from ...models.applications.object_analytics import (
    Configuration,
    GetConfigurationRequest,
    GetConfigurationResponse,
)
from .application_handler import ApplicationHandler


class ObjectAnalyticsHandler(ApplicationHandler[Configuration]):
    """Object analytics handler for Axis devices."""

    app_name = ApplicationName.OBJECT_ANALYTICS

    async def get_configuration(self) -> Configuration:
        """Get configuration of object analytics application."""
        bytes_data = await self.vapix.api_request(GetConfigurationRequest())
        response = GetConfigurationResponse.decode(bytes_data)
        return response.data
