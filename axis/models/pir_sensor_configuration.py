"""PIR sensor configuration api.

The PIR sensor configuration API helps you list and configure
the sensitivity of the PIR (passive infrared) sensors on your Axis device.
"""

from dataclasses import dataclass
from typing import NotRequired, Self

import orjson
from typing_extensions import TypedDict

from .api import CONTEXT, ApiItem, ApiRequest, ApiResponse

API_VERSION = "1.0"


class ErrorDataT(TypedDict):
    """Error data in response."""

    code: int
    message: str


class PirSensorConfigurationT(TypedDict):
    """Pir sensor configuration representation."""

    id: int
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


@dataclass(frozen=True)
class PirSensorConfiguration(ApiItem):
    """Pir sensor configuration representation."""

    configurable: bool
    sensitivity: float | None = None

    @classmethod
    def decode(cls, data: PirSensorConfigurationT) -> Self:
        """Decode dict to class object."""
        return cls(
            id=str(data["id"]),
            configurable=data["sensitivityConfigurable"],
            sensitivity=data.get("sensitivity"),
        )


@dataclass
class ListSensorsResponse(ApiResponse[dict[str, PirSensorConfiguration]]):
    """Response object for list sensors response."""

    api_version: str
    context: str
    method: str
    data: dict[str, PirSensorConfiguration]
    # error: ErrorDataT | None = None

    @classmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Prepare response data."""
        data: ListSensorsResponseT = orjson.loads(bytes_data)
        return cls(
            api_version=data["apiVersion"],
            context=data["context"],
            method=data["method"],
            data=PirSensorConfiguration.decode_to_dict(data["data"]["sensors"]),
        )


@dataclass
class ListSensorsRequest(ApiRequest):
    """Request object for listing PIR sensors."""

    method = "post"
    path = "/axis-cgi/pirsensor.cgi"
    content_type = "application/json"
    error_codes = general_error_codes

    api_version: str = API_VERSION
    context: str = CONTEXT

    @property
    def content(self) -> bytes:
        """Initialize request data."""
        return orjson.dumps(
            {
                "apiVersion": self.api_version,
                "context": self.context,
                "method": "listSensors",
            }
        )


@dataclass
class GetSensitivityResponse(ApiResponse[float | None]):
    """Response object for get sensitivity response."""

    api_version: str
    context: str
    method: str
    data: float | None
    # error: ErrorDataT | None = None

    @classmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Prepare response data."""
        data: GetSensitivityResponseT = orjson.loads(bytes_data)
        return cls(
            api_version=data["apiVersion"],
            context=data["context"],
            method=data["method"],
            data=data["data"]["sensitivity"],
        )


@dataclass
class GetSensitivityRequest(ApiRequest):
    """Request object for getting PIR sensor sensitivity."""

    method = "post"
    path = "/axis-cgi/pirsensor.cgi"
    content_type = "application/json"
    error_codes = sensor_specific_error_codes

    id: int

    api_version: str = API_VERSION
    context: str = CONTEXT

    @property
    def content(self) -> bytes:
        """Initialize request data."""
        return orjson.dumps(
            {
                "apiVersion": self.api_version,
                "context": self.context,
                "method": "getSensitivity",
                "params": {
                    "id": self.id,
                },
            }
        )


@dataclass
class SetSensitivityRequest(ApiRequest):
    """Request object for setting PIR sensor sensitivity."""

    method = "post"
    path = "/axis-cgi/pirsensor.cgi"
    content_type = "application/json"
    error_codes = sensor_specific_error_codes

    id: int
    sensitivity: float

    api_version: str = API_VERSION
    context: str = CONTEXT

    @property
    def content(self) -> bytes:
        """Initialize request data."""
        return orjson.dumps(
            {
                "apiVersion": self.api_version,
                "context": self.context,
                "method": "setSensitivity",
                "params": {
                    "id": self.id,
                    "sensitivity": self.sensitivity,
                },
            }
        )


@dataclass
class GetSupportedVersionsRequest(ApiRequest):
    """Request object for listing supported API versions."""

    method = "post"
    path = "/axis-cgi/pirsensor.cgi"
    content_type = "application/json"
    error_codes = general_error_codes

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
        """Prepare response data."""
        data: GetSupportedVersionsResponseT = orjson.loads(bytes_data)
        return cls(
            api_version=data["apiVersion"],
            context=data["context"],
            method=data["method"],
            data=data.get("data", {}).get("apiVersions", []),
        )
