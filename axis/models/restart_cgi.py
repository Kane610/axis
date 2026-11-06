"""Restart API."""

from dataclasses import dataclass

from .api import ApiRequest, ApiResponse, BytesResponse


@dataclass
class RestartRequest(ApiRequest[ApiResponse[bytes]]):
    """Request object for restarting the device."""

    method = "get"
    path = "/axis-cgi/restart.cgi"
    content_type = "text/plain"
    response_type = BytesResponse
