"""Virtual input API.

Activate and deactivate virtual input ports, which can be used as start event
or condition in the device's action rules.

https://developer.axis.com/vapix/network-video/input-and-outputs/#virtual-input-api
"""

from ..models.api import ApiItem
from ..models.virtual_input import (
    ActivateVirtualInputRequest,
    DeactivateVirtualInputRequest,
)
from .api_handler import ApiHandler


class VirtualInputHandler(ApiHandler[ApiItem]):
    """Control virtual input ports of a device."""

    @property
    def listed_in_parameters(self) -> bool:
        """Is virtual input supported."""
        if prop := self.vapix.params.property_handler.get("0"):
            return prop.virtual_input
        return False

    async def activate(self, port: int) -> bool:
        """Activate virtual input port, return True if the state changed."""
        response = await self.vapix.api_request(ActivateVirtualInputRequest(port))
        return response.data

    async def deactivate(self, port: int) -> bool:
        """Deactivate virtual input port, return True if the state changed."""
        response = await self.vapix.api_request(DeactivateVirtualInputRequest(port))
        return response.data
