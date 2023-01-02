"""Axis Vapix port management.

https://www.axis.com/vapix-library/#/subjects/t10037719/section/t10074527

I/O port API. Digital input and output ports.
General purpose I/O service API. Extends I/O port API with support for
    supervised I/Os and relay connectors.
Virtual input API.
"""

from ..models.port_cgi import ACTION_HIGH  # noqa: F401
from ..models.port_cgi import ACTION_LOW  # noqa: F401
from ..models.port_cgi import DIRECTION_IN  # noqa: F401
from ..models.port_cgi import DIRECTION_OUT  # noqa: F401
from ..models.port_cgi import Port
from ..models.port_cgi import URL  # noqa: F401
from .api import APIItems

PROPERTY = "Properties.API.HTTP.Version=3"


class Ports(APIItems):
    """Represents all ports of io/port.cgi."""

    item_cls = Port
    path = ""

    def __init__(self, vapix) -> None:
        """Initialize port cgi manager."""
        super().__init__(vapix, vapix.params.ports)

    async def update(self) -> None:
        """Refresh data."""
        await self.vapix.params.update_ports()
        self.process_raw(self.vapix.params.ports)

    @staticmethod
    def pre_process_raw(ports: dict) -> dict:
        """Pre process ports for process raw.

        Index needs to be a string.
        """
        return {str(k): v for k, v in ports.items()}
