"""Share support checks and configuration loading for device analytics applications."""

from abc import abstractmethod

from ...models.api import ApiItem
from ...models.applications.application import ApplicationName, ApplicationStatus
from ..api_handler import ApiHandler, HandlerGroup


class ApplicationHandler[ApiItemT: ApiItem](ApiHandler[ApiItemT]):
    """Load an application's configuration when it is installed and running."""

    app_name: ApplicationName
    handler_groups = (HandlerGroup.APPLICATION,)

    @property
    def supported(self) -> bool:
        """Is application supported and in a usable state."""
        if self.vapix.applications.supported:
            return self.listed_in_applications
        return False

    @property
    def listed_in_applications(self) -> bool:
        """Check cached application data for this application's running state."""
        if app := self.vapix.applications.get(self.app_name):
            return app.status == ApplicationStatus.RUNNING
        return False

    async def _api_request(self) -> dict[str, ApiItemT]:
        """Read application configuration and store it under item ID 0."""
        return {"0": await self.get_configuration()}

    @abstractmethod
    async def get_configuration(self) -> ApiItemT:
        """Read application configuration; subclasses implement the feature's request."""
