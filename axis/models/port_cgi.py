"""Axis Vapix port management.

I/O port API. Digital input and output ports.
General purpose I/O service API. Extends I/O port API with support for
    supervised I/Os and relay connectors.
Virtual input API.
"""

from dataclasses import dataclass

from .api import ApiRequest


@dataclass
class PortActionRequest(ApiRequest):
    r"""Request object for activate or deactivate an output.

    Use the <wait> option to activate/deactivate the port for a
        limited period of time.
    <Port ID> = Port name. Default: Name from Output.Name
    <a> = Action character. /=active, \=inactive
    <wait> = Delay before the next action. Unit: milliseconds
    Note: The :, / and \ characters must be percent-encoded in the URI.
        See Percent encoding.

    Example:
    -------
      To set output 1 to active, use 1:/.
      In the URI, the action argument becomes action=1%3A%2F

    """

    method = "get"
    path = "/axis-cgi/io/port.cgi"
    content_type = "text/plain"

    port: str
    action: str

    @property
    def params(self) -> dict[str, str]:
        """Request query parameters."""
        return {"action": f"{int(self.port) + 1}:{self.action}"}
