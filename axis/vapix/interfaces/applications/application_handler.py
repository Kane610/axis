"""API handler for applications."""

from ...models.api import ApiItemT
from ...models.api_discovery import ApiId
from ...models.applications.application import ApplicationName, ApplicationStatus
from ..api_handler import ApiHandler


class ApplicationHandler(ApiHandler[ApiItemT]):
    """Generic application handler."""

    api_id = ApiId.UNKNOWN
    app_name: ApplicationName

    def supported(self) -> bool:
        """Is application supported and in a usable state."""
        if app := self.vapix.applications.get(self.app_name):
            return app.status == ApplicationStatus.RUNNING
        return False
