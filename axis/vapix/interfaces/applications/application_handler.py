"""API handler for applications."""

from abc import abstractmethod

from ...models.api import ApiItemT
from ...models.applications.application import ApplicationName, ApplicationStatus
from ..api_handler import ApiHandler


class ApplicationHandler(ApiHandler[ApiItemT]):
    """Generic application handler."""

    app_name: ApplicationName

    @property
    def supported(self) -> bool:
        """Is application supported and in a usable state."""
        if self.vapix.applications.supported:
            return self.listed_in_applications
        return False

    @property
    def listed_in_applications(self) -> bool:
        """Is app name listed among applications."""
        if app := self.vapix.applications.get(self.app_name):
            return app.status == ApplicationStatus.RUNNING
        return False

    async def _api_request(self) -> dict[str, ApiItemT]:
        """Get default configuration."""
        return {"0": await self.get_configuration()}

    @abstractmethod
    async def get_configuration(self) -> ApiItemT:
        """Get default configuration."""
