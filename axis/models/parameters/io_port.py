"""I/O port parameters from param.cgi."""

from dataclasses import dataclass
import enum
from typing import Any, NotRequired, Self, TypedDict

from .param_cgi import ParamItem


class PortInputParamT(TypedDict):
    """Input name and trigger condition returned by the param.cgi IOPort group."""

    Name: str
    Trig: str


class PortOutputParamT(TypedDict):
    """Output name, state, timing, and mode returned by the IOPort group."""

    Active: str
    Button: str
    DelayTime: str
    Mode: str
    Name: str
    PulseTime: str


class PortParamT(TypedDict):
    """Direction, usage, and optional input/output settings for one I/O port."""

    Configurable: NotRequired[bool]
    Direction: str
    Usage: str
    Input: NotRequired[PortInputParamT]
    Output: NotRequired[PortOutputParamT]


class PortAction(enum.StrEnum):
    """Electrical state used to activate or deactivate an output port."""

    HIGH = "/"
    LOW = "\\"
    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls, value: object) -> PortAction:
        """Return UNKNOWN when the device reports an unrecognized output action."""
        return cls.UNKNOWN


class PortDirection(enum.StrEnum):
    """Whether an I/O port is configured as an input or output."""

    IN = "input"
    OUT = "output"
    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls, value: object) -> PortDirection:
        """Return UNKNOWN when the device reports an unrecognized port direction."""
        return cls.UNKNOWN


@dataclass(frozen=True)
class IOPortParam(ParamItem):
    """One I/O port's direction, configurability, name, and trigger/state settings."""

    configurable: bool
    """Whether the device allows this port's settings to be changed."""

    direction: PortDirection
    """Whether the port is configured to act as an input or output.

    Read-only for non-configurable ports.
    """

    input_trigger: str
    """Input circuit state that causes the port to trigger.

    closed=The input port triggers when the circuit is closed.
    open=The input port triggers when the circuit is open.
    """

    name: str
    """Name configured for the input or output side of the port."""

    output_active: str
    """Output circuit state that the device treats as active.

    closed=The output port is active when the circuit is closed.
    open=The output port is active when the circuit is open.
    """

    @classmethod
    def decode(cls, data: tuple[str, PortParamT]) -> Self:
        """Convert a named IOPort group entry into a port model."""
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
        """Convert I<n> port entries and index them by numeric port ID."""
        return {
            v.id: v
            for v in cls.decode_to_list([(k[1:], v) for k, v in data[0].items()])
        }
