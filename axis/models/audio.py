"""Audio api.

The Audio API helps you transmit audio to your Axis device.
"""

from dataclasses import dataclass
from typing import NotRequired, Self

from typing_extensions import TypedDict

from .api import ApiItem

API_VERSION = "1.0"


class ErrorDataT(TypedDict):
    """Error data in response."""

    code: int
    message: str


class AudioT(TypedDict):
    """Audio representation."""

    id: int
    sensitivityConfigurable: bool
    sensitivity: NotRequired[float]


class ApiVersionsT(TypedDict):
    """List of supported API versions."""

    apiVersions: list[str]


general_error_codes = {
    1100: "Internal error",
    2100: "API version not supported",
    2101: "Invalid JSON",
    2102: "Method not supported",
    2103: "Required parameter missing",
    2104: "Invalid parameter value specified",
}

sensor_specific_error_codes = general_error_codes | {
    2200: "Invalid sensor ID",
    2201: "Sensor does not have configurable sensitivity",
}


@dataclass(frozen=True)
class Audio(ApiItem):
    """Audio representation."""

    configurable: bool
    sensitivity: float | None = None

    @classmethod
    def decode(cls, data: AudioT) -> Self:
        """Decode dict to class object."""
        return cls(
            id=str(data["id"]),
            configurable=data["sensitivityConfigurable"],
            sensitivity=data.get("sensitivity"),
        )
