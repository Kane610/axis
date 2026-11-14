"""Models for the VAPIX I/O Port Management API.

The API lists physical I/O ports, changes their settings, and configures
timed sequences of output states.
"""

from dataclasses import dataclass
from typing import Literal, NotRequired, Self, TypedDict

import orjson

from .api import CONTEXT, ApiItem, ApiRequest, ApiResponse, BytesResponse

API_VERSION = "1.0"


class ErrorDataT(TypedDict):
    """Error code and message returned by the I/O Port Management API."""

    code: int
    message: str


class PortItemT(TypedDict):
    """State, direction, name, and usage fields for one physical I/O port."""

    port: str
    configurable: bool
    usage: str
    name: str
    direction: str
    state: str
    normalState: str


class PortDataT(TypedDict):
    """Port count and port entries returned by getPorts."""

    numberOfPorts: int
    items: list[PortItemT]


class SequenceT(TypedDict):
    """One output state and its duration in a port sequence."""

    state: Literal["open", "closed"]
    time: int


class GetPortsResponseT(TypedDict):
    """JSON envelope returned by getPorts."""

    apiVersion: str
    context: str
    method: str
    data: PortDataT
    error: NotRequired[ErrorDataT]


class ApiVersionsT(TypedDict):
    """I/O Port Management API versions supported by the device."""

    apiVersions: list[str]


class GetSupportedVersionsResponseT(TypedDict):
    """JSON envelope returned by getSupportedVersions."""

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
    """Optional settings to apply to one physical I/O port."""

    port: str
    usage: str | None = None
    direction: str | None = None
    name: str | None = None
    normal_state: str | None = None
    state: str | None = None

    def to_dict(self) -> dict[str, str]:
        """Serialize the port and only the settings supplied by the caller."""
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
    """One open or closed output state and how long it should last."""

    state: Literal["open", "closed"]
    time: int

    def to_dict(self) -> SequenceT:
        """Serialize this state step for the API request."""
        return {"state": self.state, "time": self.time}


@dataclass
class PortSequence:
    """An ordered sequence of output states for one port."""

    port: str
    sequence: list[Sequence]


@dataclass(frozen=True)
class Port(ApiItem):
    """Physical I/O port state and configuration reported by getPorts."""

    configurable: bool
    """Whether the device allows this port's configuration to be changed."""

    direction: str
    """Whether the port is an input or output.

    <input|output>.
    """

    name: str
    """Name of port."""

    normal_state: str
    """Circuit state treated as normal for this port.

    <open|closed>.
    """

    state: str
    """Current circuit state reported for this port.

    <open|closed>.
    """

    usage: str
    """Configured role of the port, as reported by the device."""

    @classmethod
    def decode(cls, data: PortItemT) -> Self:
        """Convert one getPorts entry into a port model."""
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
class GetPortsResponse(ApiResponse[dict[str, Port]]):
    """Physical I/O ports returned by getPorts, indexed by port ID."""

    api_version: str
    context: str
    method: str
    data: dict[str, Port]
    # error: ErrorDataT | None = None

    @classmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Parse and index the port entries in the getPorts response."""
        data: GetPortsResponseT = orjson.loads(bytes_data)
        return cls(
            api_version=data["apiVersion"],
            context=data["context"],
            method=data["method"],
            data=Port.decode_to_dict(data["data"].get("items", [])),
        )


@dataclass
class GetPortsRequest(ApiRequest[GetPortsResponse]):
    """Request the physical I/O ports and their current settings."""

    method = "post"
    path = "/axis-cgi/io/portmanagement.cgi"
    content_type = "application/json"
    response_type = GetPortsResponse
    error_codes = error_codes

    api_version: str = API_VERSION
    context: str = CONTEXT

    @property
    def content(self) -> bytes:
        """Encode a getPorts request as JSON."""
        return orjson.dumps(
            {
                "apiVersion": self.api_version,
                "context": self.context,
                "method": "getPorts",
            }
        )


@dataclass
class SetPortsRequest(ApiRequest[ApiResponse[bytes]]):
    """Apply one or more physical I/O port configuration changes."""

    method = "post"
    path = "/axis-cgi/io/portmanagement.cgi"
    content_type = "application/json"
    response_type = BytesResponse
    error_codes = error_codes

    port_config: list[PortConfiguration] | PortConfiguration

    api_version: str = API_VERSION
    context: str = CONTEXT

    @property
    def content(self) -> bytes:
        """Encode the supplied port settings as a setPorts request."""
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
class SetStateSequenceRequest(ApiRequest[ApiResponse[bytes]]):
    """Set the sequence of timed output states for a physical port."""

    method = "post"
    path = "/axis-cgi/io/portmanagement.cgi"
    content_type = "application/json"
    response_type = BytesResponse
    error_codes = error_codes

    port: str
    sequence: list[Sequence]

    api_version: str = API_VERSION
    context: str = CONTEXT

    @property
    def content(self) -> bytes:
        """Encode the ordered output-state steps as a setStateSequence request."""
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
class GetSupportedVersionsResponse(ApiResponse[list[str]]):
    """I/O Port Management API versions supported by the device."""

    api_version: str
    context: str
    method: str
    data: list[str]
    # error: ErrorDataT | None = None

    @classmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Parse the supported-version list from the response envelope."""
        data: GetSupportedVersionsResponseT = orjson.loads(bytes_data)
        return cls(
            api_version=data["apiVersion"],
            context=data["context"],
            method=data["method"],
            data=data.get("data", {}).get("apiVersions", []),
        )


@dataclass
class GetSupportedVersionsRequest(ApiRequest[GetSupportedVersionsResponse]):
    """Request the I/O Port Management API versions supported by the device."""

    method = "post"
    path = "/axis-cgi/io/portmanagement.cgi"
    content_type = "application/json"
    response_type = GetSupportedVersionsResponse
    error_codes = error_codes

    context: str = CONTEXT

    @property
    def content(self) -> bytes:
        """Encode a getSupportedVersions request as JSON."""
        return orjson.dumps(
            {
                "context": self.context,
                "method": "getSupportedVersions",
            }
        )
