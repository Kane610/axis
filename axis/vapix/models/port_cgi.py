"""Axis Vapix port management.

https://www.axis.com/vapix-library/#/subjects/t10037719/section/t10074527

I/O port API. Digital input and output ports.
General purpose I/O service API. Extends I/O port API with support for
    supervised I/Os and relay connectors.
Virtual input API.
"""

from dataclasses import dataclass
import enum
from typing import Any, TypedDict

from typing_extensions import NotRequired, Self

from .api import ApiItem, ApiRequest, ApiResponse
from .param_cgi import params_to_dict


class InputPortT(TypedDict):
    """Input port representation."""

    Name: str
    Trig: str


class OutputPortT(TypedDict):
    """Output port representation."""

    Active: str
    Button: str
    DelayTime: str
    Mode: str
    Name: str
    PulseTime: str


class PortItemT(TypedDict):
    """Port representation."""

    Configurable: NotRequired[bool]
    Direction: str
    Usage: str
    Input: NotRequired[InputPortT]
    Output: NotRequired[OutputPortT]


class PortAction(enum.Enum):
    """Port action."""

    HIGH = "/"
    LOW = "\\"
    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls, value: object) -> "PortAction":
        """Set default enum member if an unknown value is provided."""
        return cls.UNKNOWN


class PortDirection(enum.Enum):
    """Port action."""

    IN = "input"
    OUT = "output"
    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls, value: object) -> "PortDirection":
        """Set default enum member if an unknown value is provided."""
        return cls.UNKNOWN


@dataclass
class Port(ApiItem):
    """Represents a IO port."""

    configurable: bool
    """Is port configurable."""

    direction: PortDirection
    """Port is configured to act as input or output.

    Read-only for non-configurable ports.
    """

    input_trig: str
    """When port should trigger.

    closed=The input port triggers when the circuit is closed.
    open=The input port triggers when the circuit is open.
    """

    name: str
    """Return name relevant to direction."""

    output_active: str
    """When is output port state active.

    closed=The output port is active when the circuit is closed.
    open=The output port is active when the circuit is open.
    """

    @classmethod
    def decode(cls, id: str, data: PortItemT) -> Self:
        """Decode dict to class object."""
        direction = PortDirection(data.get("Direction", "input"))
        name = (
            data.get("Input", {}).get("Name", "")
            if direction == PortDirection.IN
            else data.get("Output", {}).get("Name", "")
        )
        return cls(
            id=id,
            configurable=data.get("Configurable") == "yes",
            direction=direction,
            input_trig=data.get("Input", {}).get("Trig", ""),
            name=name,
            output_active=data.get("Output", {}).get("Active", ""),
        )

    @classmethod
    def from_dict(cls, data: dict[str, PortItemT]) -> dict[str, Self]:
        """Create objects from dict."""
        ports = [cls.decode(k, v) for k, v in data.items()]
        return {port.id: port for port in ports}


@dataclass
class GetPortsRequest(ApiRequest):
    """Request object for listing IO ports."""

    method = "get"
    path = "/axis-cgi/param.cgi?action=list&group=root.IOPort"
    content_type = "text/plain"


@dataclass
class GetPortsResponse(ApiResponse[dict[str, Port]]):
    """Response object for listing ports."""

    @classmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Create response object from bytes."""
        data = bytes_data.decode()
        ports = params_to_dict(data, "root.IOPort").get("root", {}).get("IOPort", {})
        return cls(Port.from_dict({k[1:]: v for k, v in ports.items()}))

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Create response object from dict."""
        return cls(Port.from_dict({k[1:]: v for k, v in data.items()}))


@dataclass
class ListOutputRequest(ApiRequest):
    """Request object for listing number of outputs."""

    method = "get"
    path = "/axis-cgi/param.cgi?action=list&group=root.Output"
    content_type = "text/plain"


@dataclass
class ListInputRequest(ApiRequest):
    """Request object for listing number of inputs."""

    method = "get"
    path = "/axis-cgi/param.cgi?action=list&group=root.Input"
    content_type = "text/plain"


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
