"""Virtual input API.

Virtual inputs let clients trigger actions in the device, by using a virtual
input port as start event or condition in an action rule. Ports are numbered
from 1, the number of ports depends on the device (64 by default, 32 on some).

https://developer.axis.com/vapix/network-video/input-and-outputs/#virtual-input-api
"""

from dataclasses import dataclass
from typing import Literal, NotRequired, Self, TypedDict
from xml.parsers.expat import ExpatError

import xmltodict

from ..errors import ResponseError
from .api import ApiRequest, ApiResponse

SCHEMA_VERSION = "1"

INVALID_RESPONSE = "Invalid virtual input response"

NAMESPACES = {"http://www.axis.com/vapix/http_cgi/virtualinput1": None}


class GeneralErrorT(TypedDict):
    """Error reported by the device."""

    ErrorCode: str
    ErrorDescription: str


class ErrorT(TypedDict):
    """Error container."""

    GeneralError: GeneralErrorT


class StateChangedT(TypedDict):
    """Result of activating or deactivating a port."""

    StateChanged: Literal["true", "false"]


class SuccessT(TypedDict):
    """Success container, holding one of the results."""

    ActivateSuccess: NotRequired[StateChangedT]
    DeactivateSuccess: NotRequired[StateChangedT]


class VirtualInputResponseT(TypedDict):
    """Virtual input response, holding either success or error."""

    Success: NotRequired[SuccessT]
    Error: NotRequired[ErrorT]


@dataclass
class VirtualInputResponse(ApiResponse[bool]):
    """Response from activating or deactivating a virtual input.

    Data is True if the port state was changed.
    """

    data: bool

    @classmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Decode response, raise ResponseError if the device reports an error."""
        try:
            data: dict[str, VirtualInputResponseT] = xmltodict.parse(
                bytes_data,
                dict_constructor=dict,
                namespaces=NAMESPACES,
                process_namespaces=True,
            )
        except ExpatError as err:
            raise ResponseError(INVALID_RESPONSE) from err

        response = data.get("VirtualInputResponse")
        if not isinstance(response, dict):
            raise ResponseError(INVALID_RESPONSE)

        if isinstance(error := response.get("Error"), dict):
            if not isinstance(general_error := error.get("GeneralError"), dict):
                raise ResponseError(INVALID_RESPONSE)
            msg = (
                f"Virtual input error {general_error.get('ErrorCode')}: "
                f"{general_error.get('ErrorDescription')}"
            )
            raise ResponseError(msg)

        success = response.get("Success")
        if not isinstance(success, dict) or not isinstance(
            result := success.get("ActivateSuccess", success.get("DeactivateSuccess")),
            dict,
        ):
            raise ResponseError(INVALID_RESPONSE)

        if (state_changed := result.get("StateChanged")) not in ("true", "false"):
            raise ResponseError(INVALID_RESPONSE)

        return cls(data=state_changed == "true")


@dataclass
class ActivateVirtualInputRequest(ApiRequest[VirtualInputResponse]):
    """Request object for activating a virtual input port."""

    method = "get"
    path = "/axis-cgi/virtualinput/activate.cgi"
    content_type = "text/xml"
    response_type = VirtualInputResponse

    port: int

    @property
    def params(self) -> dict[str, str]:
        """Request query parameters."""
        return {"schemaversion": SCHEMA_VERSION, "port": str(self.port)}


@dataclass
class DeactivateVirtualInputRequest(ApiRequest[VirtualInputResponse]):
    """Request object for deactivating a virtual input port."""

    method = "get"
    path = "/axis-cgi/virtualinput/deactivate.cgi"
    content_type = "text/xml"
    response_type = VirtualInputResponse

    port: int

    @property
    def params(self) -> dict[str, str]:
        """Request query parameters."""
        return {"schemaversion": SCHEMA_VERSION, "port": str(self.port)}
