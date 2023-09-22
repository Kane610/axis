"""PIR sensor configuration api.

The PIR sensor configuration API helps you list and configure
the sensitivity of the PIR (passive infrared) sensors on your Axis device.
"""
from dataclasses import dataclass

import orjson
from typing_extensions import NotRequired, TypedDict

from .api import CONTEXT, ApiItem, ApiRequest

API_VERSION = "1.0"


class ErrorDataT(TypedDict):
    """Error data in response."""

    code: int
    message: str


class PirSensorConfigurationT(TypedDict):
    """Pir sensor configuration representation."""

    id: str
    sensitivityConfigurable: bool
    sensitivity: NotRequired[float]


class ListSensorsDataT(TypedDict):
    """List of Pir sensor configuration data."""

    sensors: list[PirSensorConfigurationT]


class ListSensorsResponseT(TypedDict):
    """ListSensors response."""

    apiVersion: str
    context: str
    method: str
    data: ListSensorsDataT
    error: NotRequired[ErrorDataT]


class GetSensitivityDataT(TypedDict):
    """Sensitivity data."""

    sensitivity: float


class GetSensitivityResponseT(TypedDict):
    """GetSensitivity response."""

    apiVersion: str
    context: str
    method: str
    data: GetSensitivityDataT
    error: NotRequired[ErrorDataT]


class SetSensitivityResponseT(TypedDict):
    """SetSensitivity response."""

    apiVersion: str
    context: str
    method: str
    error: NotRequired[ErrorDataT]


class ApiVersionsT(TypedDict):
    """List of supported API versions."""

    apiVersions: list[str]


class GetSupportedVersionsResponseT(TypedDict):
    """ListSensors response."""

    apiVersion: str
    context: str
    method: str
    data: ApiVersionsT
    error: NotRequired[ErrorDataT]


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


@dataclass
class PirSensorConfiguration(ApiItem):
    """Pir sensor configuration representation."""

    configurable: bool
    sensitivity: float | None = None


ListSensorsT = dict[str, PirSensorConfiguration]


@dataclass
class ListSensorsRequest(ApiRequest[ListSensorsT]):
    """Request object for listing PIR sensors."""

    method = "post"
    path = "/axis-cgi/pirsensor.cgi"
    content_type = "application/json"
    error_codes = general_error_codes

    api_version: str = API_VERSION
    context: str = CONTEXT

    def __post_init__(self) -> None:
        """Initialize request data."""
        self.data = {
            "apiVersion": self.api_version,
            "context": self.context,
            "method": "listSensors",
        }

    def process_raw(self, raw: bytes) -> ListSensorsT:
        """Prepare Pir sensor configuration dictionary."""
        data: ListSensorsResponseT = orjson.loads(raw)
        sensors = data.get("data", {}).get("sensors", [])
        return {
            sensor["id"]: PirSensorConfiguration(
                id=sensor["id"],
                configurable=sensor["sensitivityConfigurable"],
                sensitivity=sensor.get("sensitivity"),
            )
            for sensor in sensors
        }


@dataclass
class GetSensitivityRequest(ApiRequest[float | None]):
    """Request object for getting PIR sensor sensitivity."""

    method = "post"
    path = "/axis-cgi/pirsensor.cgi"
    content_type = "application/json"
    error_codes = sensor_specific_error_codes

    id: int
    api_version: str = API_VERSION
    context: str = CONTEXT

    def __post_init__(self) -> None:
        """Initialize request data."""
        self.data = {
            "apiVersion": self.api_version,
            "context": self.context,
            "method": "getSensitivity",
            "params": {
                "id": self.id,
            },
        }

    def process_raw(self, raw: bytes) -> float | None:
        """Prepare sensitivity value."""
        data: GetSensitivityResponseT = orjson.loads(raw)
        return data.get("data", {}).get("sensitivity")


@dataclass
class SetSensitivityRequest(ApiRequest[None]):
    """Request object for setting PIR sensor sensitivity."""

    method = "post"
    path = "/axis-cgi/pirsensor.cgi"
    content_type = "application/json"
    error_codes = sensor_specific_error_codes

    id: int
    sensitivity: float
    api_version: str = API_VERSION
    context: str = CONTEXT

    def __post_init__(self) -> None:
        """Initialize request data."""
        self.data = {
            "apiVersion": self.api_version,
            "context": self.context,
            "method": "setSensitivity",
            "params": {
                "id": self.id,
                "sensitivity": self.sensitivity,
            },
        }

    def process_raw(self, raw: bytes) -> None:
        """No expected data in response."""
        return None


@dataclass
class GetSupportedVersionsRequest(ApiRequest[list[str]]):
    """Request object for listing supported API versions."""

    method = "post"
    path = "/axis-cgi/pirsensor.cgi"
    content_type = "application/json"
    error_codes = general_error_codes

    context: str = CONTEXT

    def __post_init__(self) -> None:
        """Initialize request data."""
        self.data = {
            "context": self.context,
            "method": "getSupportedVersions",
        }

    def process_raw(self, raw: bytes) -> list[str]:
        """Process supported versions."""
        data: GetSupportedVersionsResponseT = orjson.loads(raw)
        return data.get("data", {}).get("apiVersions", [])
