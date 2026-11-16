"""Read the Object Analytics application's configuration through its VAPIX API."""

from ...models.applications.application import ApplicationName
from ...models.applications.object_analytics import (
    Configuration,
    GetConfigurationRequest,
)
from .application_handler import ApplicationHandler


class ObjectAnalyticsHandler(ApplicationHandler[Configuration]):
    """Read Object Analytics settings from an Axis device."""

    app_name = ApplicationName.OBJECT_ANALYTICS

    async def get_configuration(self) -> Configuration:
        """Get configuration of object analytics application."""
        response = await self.vapix.api_request(GetConfigurationRequest())
        return response.data
