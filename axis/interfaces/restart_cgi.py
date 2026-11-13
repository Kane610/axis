"""Axis Vapix restart API.

Restart the device. Requires an administrator account. Superseded by the
firmware management API, use this on devices that don't list it.
"""

from ..models.api import ApiItem
from ..models.restart_cgi import RestartRequest
from .api_handler import ApiHandler


class RestartHandler(ApiHandler[ApiItem]):
    """Restart the device through restart.cgi."""

    async def restart(self) -> None:
        """Restart the device."""
        await self.vapix.api_request(RestartRequest())
