"""I/O Port Management API.

The I/O port management API makes it possible to retrieve
information about the ports and apply product dependent configurations
"""

from dataclasses import dataclass
from typing import Literal, NotRequired, Self, TypedDict

import orjson

from .api import CONTEXT, ApiItem, ApiRequest, ApiResponse

API_VERSION = "1.0"


class ErrorDataT(TypedDict):
    """Error data in response."""

    code: int
    message: str


class PortItemT(TypedDict):
    """Port representation."""

    port: str
    configurable: bool
    usage: str
    name: str
    direction: str
    state: str
    normalState: str


class PortDataT(TypedDict):
    """Port getPorts response."""

    numberOfPorts: int
    items: list[PortItemT]


class SequenceT(TypedDict):
    """Port sequence representation."""

    state: Literal["open", "closed"]
    time: int


class GetPortsResponseT(TypedDict):
    """Get ports response data."""

    apiVersion: str
    context: str
    method: str
    data: PortDataT
    error: NotRequired[ErrorDataT]


class ApiVersionsT(TypedDict):
    """List of supported API versions."""

    apiVersions: list[str]


class GetSupportedVersionsResponseT(TypedDict):
    """ListApis response."""

    apiVersion: str
    context: str
    method: str
    data: ApiVersionsT
    error: NotRequired[ErrorDataT]


error_codes = {
    1000: "Invalid parameter value specified",
    2002: "HTTP request type not supported. Only POST is supported",
    2003: "Requested API version is not supported",
    2004: "Method not supported",
    4000: "Invalid JSON",
    4002: "Required parameter missing or invalid",
    8000: "Internal error",
}


@dataclass
class PortConfiguration:
    """Port configuration used with set_ports interface."""

    port: str
    usage: str | None = None
    direction: str | None = None
    name: str | None = None
    normal_state: str | None = None
    state: str | None = None

    def to_dict(self) -> dict[str, str]:
        """Convert to dictionary with populated fields."""
        data: dict[str, str] = {"port": self.port}
        if self.usage is not None:
            data["usage"] = self.usage
        if self.direction is not None:
            data["direction"] = self.direction
        if self.name is not None:
            data["name"] = self.name
        if self.normal_state is not None:
            data["normalState"] = self.normal_state
        if self.state is not None:
            data["state"] = self.state
        return data


@dataclass
class Sequence:
    """Sequence class."""

    state: Literal["open", "closed"]
    time: int

    def to_dict(self) -> SequenceT:
        """Convert to dictionary."""
        return {"state": self.state, "time": self.time}


@dataclass
class PortSequence:
    """Port sequence class."""

    port: str
    sequence: list[Sequence]


@dataclass(frozen=True)
class Port(ApiItem):
    """I/O port management port."""

    configurable: bool
    """Is port configurable."""

    direction: str
    """Direction of port.

    <input|output>.
    """

    name: str
    """Name of port."""

    normal_state: str
    """Port normal state.

    <open|closed>.
    """

    state: str
    """State of port.

    <open|closed>.
    """

    usage: str
    """Usage of port."""

    @classmethod
    def decode(cls, data: PortItemT) -> Self:
        """Create object from dict."""
        return cls(
            id=data["port"],
            configurable=data["configurable"],
            direction=data["direction"],
            name=data["name"],
            normal_state=data["normalState"],
            state=data["state"],
            usage=data["usage"],
        )


@dataclass
class GetPortsRequest(ApiRequest):
    """Request object for listing ports."""

    method = "post"
    path = "/axis-cgi/io/portmanagement.cgi"
    content_type = "application/json"
    error_codes = error_codes

    api_version: str = API_VERSION
    context: str = CONTEXT

    @property
    def content(self) -> bytes:
        """Initialize request data."""
        return orjson.dumps(
            {
                "apiVersion": self.api_version,
                "context": self.context,
                "method": "getPorts",
            }
        )


@dataclass
class GetPortsResponse(ApiResponse[dict[str, Port]]):
    """Response object for listing ports."""

    api_version: str
    context: str
    method: str
    data: dict[str, Port]
    # error: ErrorDataT | None = None

    @classmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Prepare API description dictionary."""
        data: GetPortsResponseT = orjson.loads(bytes_data)
        return cls(
            api_version=data["apiVersion"],
            context=data["context"],
            method=data["method"],
            data=Port.decode_to_dict(data["data"].get("items", [])),
        )


@dataclass
class SetPortsRequest(ApiRequest):
    """Request object for configuring ports."""

    method = "post"
    path = "/axis-cgi/io/portmanagement.cgi"
    content_type = "application/json"
    error_codes = error_codes

    port_config: list[PortConfiguration] | PortConfiguration

    api_version: str = API_VERSION
    context: str = CONTEXT

    @property
    def content(self) -> bytes:
        """Initialize request data."""
        if not isinstance(self.port_config, list):
            self.port_config = [self.port_config]
        ports: list[dict[str, str]] = [port.to_dict() for port in self.port_config]
        return orjson.dumps(
            {
                "apiVersion": self.api_version,
                "context": self.context,
                "method": "setPorts",
                "params": {"ports": ports},
            }
        )


@dataclass
class SetStateSequenceRequest(ApiRequest):
    """Request object for configuring port sequence."""

    method = "post"
    path = "/axis-cgi/io/portmanagement.cgi"
    content_type = "application/json"
    error_codes = error_codes

    port: str
    sequence: list[Sequence]

    api_version: str = API_VERSION
    context: str = CONTEXT

    @property
    def content(self) -> bytes:
        """Initialize request data."""
        sequence = [item.to_dict() for item in self.sequence]
        return orjson.dumps(
            {
                "apiVersion": self.api_version,
                "context": self.context,
                "method": "setStateSequence",
                "params": {"port": self.port, "sequence": sequence},
            }
        )


@dataclass
class GetSupportedVersionsRequest(ApiRequest):
    """Request object for listing supported API versions."""

    method = "post"
    path = "/axis-cgi/io/portmanagement.cgi"
    content_type = "application/json"
    error_codes = error_codes

    context: str = CONTEXT

    @property
    def content(self) -> bytes:
        """Initialize request data."""
        return orjson.dumps(
            {
                "context": self.context,
                "method": "getSupportedVersions",
            }
        )


@dataclass
class GetSupportedVersionsResponse(ApiResponse[list[str]]):
    """Response object for supported versions."""

    api_version: str
    context: str
    method: str
    data: list[str]
    # error: ErrorDataT | None = None

    @classmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Prepare API description dictionary."""
        data: GetSupportedVersionsResponseT = orjson.loads(bytes_data)
        return cls(
            api_version=data["apiVersion"],
            context=data["context"],
            method=data["method"],
            data=data.get("data", {}).get("apiVersions", []),
        )
