"""Firmware management API.

Manage the firmware of the device. Only rebooting is supported here.

https://developer.axis.com/vapix/network-video/firmware-management-api/
"""

from dataclasses import dataclass
from typing import Any, Self

import orjson

from ..errors import ResponseError
from .api import CONTEXT, ApiRequest, ApiResponse

API_VERSION = "1.0"


@dataclass
class RebootResponse(ApiResponse[None]):
    """Response from rebooting the device."""

    data: None

    @classmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Decode response, raise ResponseError if the device reports an error."""
        msg = "Invalid firmware management response"
        try:
            data: Any = orjson.loads(bytes_data)
        except orjson.JSONDecodeError as err:
            raise ResponseError(msg) from err
        if not isinstance(data, dict):
            raise ResponseError(msg)
        if isinstance(error := data.get("error"), dict):
            msg = (
                f"Firmware management error {error.get('code')}: {error.get('message')}"
            )
            raise ResponseError(msg)
        return cls(data=None)


@dataclass
class RebootRequest(ApiRequest[RebootResponse]):
    """Request object for rebooting the device."""

    method = "post"
    path = "/axis-cgi/firmwaremanagement.cgi"
    content_type = "application/json"
    response_type = RebootResponse

    api_version: str = API_VERSION
    context: str = CONTEXT

    @property
    def content(self) -> bytes:
        """Initialize request data."""
        return orjson.dumps(
            {
                "apiVersion": self.api_version,
                "context": self.context,
                "method": "reboot",
            }
        )
