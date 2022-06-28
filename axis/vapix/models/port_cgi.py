"""Axis Vapix port management.

https://www.axis.com/vapix-library/#/subjects/t10037719/section/t10074527

I/O port API. Digital input and output ports.
General purpose I/O service API. Extends I/O port API with support for
    supervised I/Os and relay connectors.
Virtual input API.
"""

from typing import Callable
from urllib.parse import quote

PROPERTY = "Properties.API.HTTP.Version=3"

URL = "/axis-cgi/io/port.cgi"

ACTION_HIGH = "/"
ACTION_LOW = "\\"

DIRECTION_IN = "input"
DIRECTION_OUT = "output"


class Port:
    """Represents a port."""

    def __init__(self, id: str, raw: dict, request: Callable) -> None:
        """Initialize port."""
        self.id = id
        self.raw = raw
        self._request = request

    @property
    def configurable(self) -> bool:
        """Is port configurable."""
        return self.raw.get("Configurable", False)

    @property
    def direction(self) -> str:
        """Port is configured to act as input or output.

        Read-only for non-configurable ports.
        """
        return self.raw.get("Direction", DIRECTION_IN)

    @property
    def input_trig(self) -> str:
        """When port should trigger.

        closed=The input port triggers when the circuit is closed.
        open=The input port triggers when the circuit is open.
        """
        return self.raw.get("Input.Trig", "")

    @property
    def name(self) -> str:
        """Return name relevant to direction."""
        if self.direction == DIRECTION_IN:
            return self.raw.get("Input.Name", "")
        return self.raw.get("Output.Name", "")

    @property
    def output_active(self) -> str:
        """When is output port state active.

        closed=The output port is active when the circuit is closed.
        open=The output port is active when the circuit is open.
        """
        return self.raw.get("Output.Active", "")

    async def action(self, action: str) -> None:
        r"""Activate or deactivate an output.

        Use the <wait> option to activate/deactivate the port for a
            limited period of time.
        <Port ID> = Port name. Default: Name from Output.Name
        <a> = Action character. /=active, \=inactive
        <wait> = Delay before the next action. Unit: milliseconds
        Note: The :, / and \ characters must be percent-encoded in the URI.
            See Percent encoding.
        Example:
            To set output 1 to active, use 1:/.
            In the URI, the action argument becomes action=1%3A%2F
        """
        if not self.direction == DIRECTION_OUT:
            return

        port_action = quote(f"{int(self.id) + 1}:{action}", safe="")
        url = URL + f"?action={port_action}"

        await self._request("get", url)

    async def open(self) -> None:
        """Open port."""
        await self.action(ACTION_LOW)

    async def close(self) -> None:
        """Close port."""
        await self.action(ACTION_HIGH)
