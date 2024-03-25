"""I/O port parameters from param.cgi."""

from dataclasses import dataclass
import enum
from typing import Any, NotRequired, Self, TypedDict

from .param_cgi import ParamItem


class PortInputParamT(TypedDict):
    """Input port representation."""

    Name: str
    Trig: str


class PortOutputParamT(TypedDict):
    """Output port representation."""

    Active: str
    Button: str
    DelayTime: str
    Mode: str
    Name: str
    PulseTime: str


class PortParamT(TypedDict):
    """Port representation."""

    Configurable: NotRequired[bool]
    Direction: str
    Usage: str
    Input: NotRequired[PortInputParamT]
    Output: NotRequired[PortOutputParamT]


class PortAction(enum.StrEnum):
    """Port action."""

    HIGH = "/"
    LOW = "\\"
    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls, value: object) -> "PortAction":
        """Set default enum member if an unknown value is provided."""
        return cls.UNKNOWN


class PortDirection(enum.StrEnum):
    """Port action."""

    IN = "input"
    OUT = "output"
    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls, value: object) -> "PortDirection":
        """Set default enum member if an unknown value is provided."""
        return cls.UNKNOWN


@dataclass(frozen=True)
class IOPortParam(ParamItem):
    """Represents a IO port."""

    configurable: bool
    """Is port configurable."""

    direction: PortDirection
    """Port is configured to act as input or output.

    Read-only for non-configurable ports.
    """

    input_trigger: str
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
    def decode(cls, data: tuple[str, PortParamT]) -> Self:
        """Decode dict to class object."""
        id, raw = data
        direction = PortDirection(raw.get("Direction", "input"))
        name = (
            raw.get("Input", {}).get("Name", "")
            if direction == PortDirection.IN
            else raw.get("Output", {}).get("Name", "")
        )
        return cls(
            id=id,
            configurable=raw.get("Configurable") is True,
            direction=direction,
            input_trigger=raw.get("Input", {}).get("Trig", ""),
            name=name,
            output_active=raw.get("Output", {}).get("Active", ""),
        )

    @classmethod
    def decode_to_dict(cls, data: list[Any]) -> dict[str, Self]:
        """Create objects from dict."""
        return {
            v.id: v
            for v in cls.decode_to_list([(k[1:], v) for k, v in data[0].items()])
        }
