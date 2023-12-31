"""Axis Vapix port management.

https://www.axis.com/vapix-library/#/subjects/t10037719/section/t10074527

I/O port API. Digital input and output ports.
General purpose I/O service API. Extends I/O port API with support for
    supervised I/Os and relay connectors.
Virtual input API.
"""

from ..models.parameters.io_port import IOPortParam, PortAction, PortDirection
from ..models.port_cgi import PortActionRequest
from .api_handler import ApiHandler

PROPERTY = "Properties.API.HTTP.Version=3"


class Ports(ApiHandler[IOPortParam]):
    """Represents all ports of io/port.cgi."""

    async def _api_request(self) -> dict[str, IOPortParam]:
        """Get API data method defined by subclass."""
        return await self.get_ports()

    async def get_ports(self) -> dict[str, IOPortParam]:
        """Retrieve privilege rights for current user."""
        await self.vapix.params.io_port_handler.update()
        return self.process_ports()

    def process_ports(self) -> dict[str, IOPortParam]:
        """Process ports."""
        return dict(self.vapix.params.io_port_handler.items())

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
