"""Firmware management API.

Listed in API discovery from AXIS OS 7.40, it replaces restart.cgi for
rebooting. Requires an administrator account.
"""

from ..models.api import ApiItem
from ..models.api_discovery import ApiId
from ..models.firmware_management import API_VERSION, RebootRequest
from .api_handler import ApiHandler


class FirmwareManagementHandler(ApiHandler[ApiItem]):
    """Firmware management of a device."""

    api_id = ApiId.FIRMWARE_MANAGER
    default_api_version = API_VERSION

    async def reboot(self) -> None:
        """Reboot the device."""
        await self.vapix.api_request(RebootRequest())
