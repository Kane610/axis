"""Axis Vapix port management.

https://www.axis.com/vapix-library/#/subjects/t10037719/section/t10074527

I/O port API. Digital input and output ports.
General purpose I/O service API. Extends I/O port API with support for
    supervised I/Os and relay connectors.
Virtual input API.
"""

from typing import Callable

from ..models.port_cgi import ACTION_HIGH  # noqa: F401
from ..models.port_cgi import ACTION_LOW  # noqa: F401
from ..models.port_cgi import DIRECTION_IN  # noqa: F401
from ..models.port_cgi import DIRECTION_OUT  # noqa: F401
from ..models.port_cgi import Port
from ..models.port_cgi import URL  # noqa: F401
from .api import APIItems
from .param_cgi import Params

PROPERTY = "Properties.API.HTTP.Version=3"


class Ports(APIItems):
    """Represents all ports of io/port.cgi."""

    def __init__(self, param_cgi: Params, request: Callable) -> None:
        """Initialize port cgi manager."""
        self.param_cgi = param_cgi
        super().__init__(self.param_cgi.ports, request, None, Port)

    async def update(self) -> None:
        """Refresh data."""
        await self.param_cgi.update_ports()
        self.process_raw(self.param_cgi.ports)

    @staticmethod
    def pre_process_raw(ports: dict) -> dict:
        """Pre process ports for process raw.

        Index needs to be a string.
        """
        return {str(k): v for k, v in ports.items()}
