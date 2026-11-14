"""Models for the legacy VAPIX port.cgi output-control endpoint.

This model sets the active or inactive state of one physical output port.
Newer port and virtual-input APIs have separate models.
"""

from dataclasses import dataclass

from .api import ApiRequest, ApiResponse, BytesResponse


@dataclass
class PortActionRequest(ApiRequest[ApiResponse[bytes]]):
    r"""Activate or deactivate a physical output through port.cgi.

    The supplied port number is zero-based; the endpoint's port ID is one-based.
    The action is "/" for active or "\" for inactive. The HTTP client encodes the
    colon and action character when it builds the query string.
    """

    method = "get"
    path = "/axis-cgi/io/port.cgi"
    content_type = "text/plain"
    response_type = BytesResponse

    port: str
    action: str

    @property
    def params(self) -> dict[str, str]:
        """Return the one-based port ID and action in port.cgi's query value."""
        return {"action": f"{int(self.port) + 1}:{self.action}"}
