"""Request the legacy VAPIX endpoint that restarts an Axis device."""

from dataclasses import dataclass

from .api import ApiRequest, ApiResponse, BytesResponse


@dataclass
class RestartRequest(ApiRequest[ApiResponse[bytes]]):
    """Send a restart command to the device through restart.cgi."""

    method = "get"
    path = "/axis-cgi/restart.cgi"
    content_type = "text/plain"
    response_type = BytesResponse
