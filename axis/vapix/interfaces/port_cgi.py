"""Axis Vapix port management.

https://www.axis.com/vapix-library/#/subjects/t10037719/section/t10074527

I/O port API. Digital input and output ports.
General purpose I/O service API. Extends I/O port API with support for
    supervised I/Os and relay connectors.
Virtual input API.
"""

from ..models.port_cgi import (
    GetPortsRequest,
    GetPortsResponse,
    Port,
    PortAction,
    PortActionRequest,
    PortDirection,
)
from .api_handler import ApiHandler

PROPERTY = "Properties.API.HTTP.Version=3"


class Ports(ApiHandler[Port]):
    """Represents all ports of io/port.cgi."""

    async def _api_request(self) -> dict[str, Port]:
        """Get API data method defined by subclass."""
        return await self.get_ports()

    async def get_ports(self) -> dict[str, Port]:
        """Retrieve privilege rights for current user."""
        bytes_data = await self.vapix.new_request(GetPortsRequest())
        return GetPortsResponse.decode(bytes_data).data

    def process_ports(self) -> dict[str, Port]:
        """Process ports."""
        return GetPortsResponse.decode(self.vapix.params.ports).data

    async def action(self, id: str, action: PortAction) -> None:
        """Activate or deactivate an output."""
        if (port := self[id]) and port.direction != PortDirection.OUT:
            return
        await self.vapix.new_request(PortActionRequest(id, action.value))

    async def open(self, id: str) -> None:
        """Open port."""
        await self.action(id, PortAction.LOW)

    async def close(self, id: str) -> None:
        """Close port."""
        await self.action(id, PortAction.HIGH)
