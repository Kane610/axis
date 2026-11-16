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
    """Read digital I/O port settings and control outputs through io/port.cgi."""

    @property
    def listed_in_parameters(self) -> bool:
        """Is API listed in parameters."""
        return self.vapix.params.io_port_handler.listed_in_parameters

    async def _api_request(self) -> dict[str, IOPortParam]:
        """Refresh I/O port settings through the parameter handler."""
        return await self.get_ports()

    async def get_ports(self) -> dict[str, IOPortParam]:
        """Refresh and return the device's digital I/O port settings."""
        await self.vapix.params.io_port_handler.update()
        return self.process_ports()

    def load_ports(self) -> None:
        """Copy already loaded I/O port parameters into this handler's cached data."""
        self._items.update(self.process_ports())

    def process_ports(self) -> dict[str, IOPortParam]:
        """Return a copy of the parameter handler's cached I/O port data."""
        return dict(self.vapix.params.io_port_handler.items())

    async def action(self, id: str, action: PortAction) -> None:
        """Activate or deactivate an output."""
        if (port := self[id]) and port.direction != PortDirection.OUT:
            return
        await self.vapix.api_request(PortActionRequest(id, action))

    async def open(self, id: str) -> None:
        """Set an output port to its low state."""
        await self.action(id, PortAction.LOW)

    async def close(self, id: str) -> None:
        """Set an output port to its high state."""
        await self.action(id, PortAction.HIGH)
