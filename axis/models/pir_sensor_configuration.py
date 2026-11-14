"""Models for the VAPIX PIR Sensor Configuration API.

The PIR sensor configuration API helps you list and configure
the sensitivity of the PIR (passive infrared) sensors on your Axis device.
"""

from dataclasses import dataclass
from typing import NotRequired, Self, TypedDict

import orjson

from .api import CONTEXT, ApiItem, ApiRequest, ApiResponse, BytesResponse

API_VERSION = "1.0"


class ErrorDataT(TypedDict):
    """Error code and message returned by the PIR Sensor Configuration API."""

    code: int
    message: str


class PirSensorConfigurationT(TypedDict):
    """Sensor ID, sensitivity editability, and optional current sensitivity."""

    id: int
    sensitivityConfigurable: bool
    sensitivity: NotRequired[float]


class ListSensorsDataT(TypedDict):
    """Sensors returned by the listSensors method."""

    sensors: list[PirSensorConfigurationT]


class ListSensorsResponseT(TypedDict):
    """JSON envelope returned by listSensors."""

    apiVersion: str
    context: str
    method: str
    data: ListSensorsDataT
    error: NotRequired[ErrorDataT]


class GetSensitivityDataT(TypedDict):
    """Sensitivity value returned for one sensor."""

    sensitivity: float


class GetSensitivityResponseT(TypedDict):
    """JSON envelope returned by getSensitivity."""

    apiVersion: str
    context: str
    method: str
    data: GetSensitivityDataT
    error: NotRequired[ErrorDataT]


class SetSensitivityResponseT(TypedDict):
    """JSON envelope returned by setSensitivity."""

    apiVersion: str
    context: str
    method: str
    error: NotRequired[ErrorDataT]


class ApiVersionsT(TypedDict):
    """PIR Sensor Configuration API versions supported by the device."""

    apiVersions: list[str]


class GetSupportedVersionsResponseT(TypedDict):
    """JSON envelope returned by getSupportedVersions."""

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
    """One PIR sensor's ID, ability to change sensitivity, and current value."""

    configurable: bool
    sensitivity: float | None = None

    @classmethod
    def decode(cls, data: PirSensorConfigurationT) -> Self:
        """Convert one API sensor entry into a configuration model."""
        return cls(
            id=str(data["id"]),
            configurable=data["sensitivityConfigurable"],
            sensitivity=data.get("sensitivity"),
        )


@dataclass
class ListSensorsResponse(ApiResponse[dict[str, PirSensorConfiguration]]):
    """PIR sensors indexed by their IDs."""

    api_version: str
    context: str
    method: str
    data: dict[str, PirSensorConfiguration]
    # error: ErrorDataT | None = None

    @classmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Parse and index the sensor configurations returned by listSensors."""
        data: ListSensorsResponseT = orjson.loads(bytes_data)
        return cls(
            api_version=data["apiVersion"],
            context=data["context"],
            method=data["method"],
            data=PirSensorConfiguration.decode_to_dict(data["data"]["sensors"]),
        )


@dataclass
class ListSensorsRequest(ApiRequest[ListSensorsResponse]):
    """Request the PIR sensors present on the device."""

    method = "post"
    path = "/axis-cgi/pirsensor.cgi"
    content_type = "application/json"
    response_type = ListSensorsResponse
    error_codes = general_error_codes

    api_version: str = API_VERSION
    context: str = CONTEXT

    @property
    def content(self) -> bytes:
        """Encode a listSensors request as JSON."""
        return orjson.dumps(
            {
                "apiVersion": self.api_version,
                "context": self.context,
                "method": "listSensors",
            }
        )


@dataclass
class GetSensitivityResponse(ApiResponse[float | None]):
    """Sensitivity value returned for one PIR sensor."""

    api_version: str
    context: str
    method: str
    data: float | None
    # error: ErrorDataT | None = None

    @classmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Extract the sensitivity value from the response envelope."""
        data: GetSensitivityResponseT = orjson.loads(bytes_data)
        return cls(
            api_version=data["apiVersion"],
            context=data["context"],
            method=data["method"],
            data=data["data"]["sensitivity"],
        )


@dataclass
class GetSensitivityRequest(ApiRequest[GetSensitivityResponse]):
    """Request the current sensitivity of one PIR sensor."""

    method = "post"
    path = "/axis-cgi/pirsensor.cgi"
    content_type = "application/json"
    response_type = GetSensitivityResponse
    error_codes = sensor_specific_error_codes

    id: int

    api_version: str = API_VERSION
    context: str = CONTEXT

    @property
    def content(self) -> bytes:
        """Encode the sensor ID in a getSensitivity request."""
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
class SetSensitivityRequest(ApiRequest[ApiResponse[bytes]]):
    """Set the sensitivity of one PIR sensor."""

    method = "post"
    path = "/axis-cgi/pirsensor.cgi"
    content_type = "application/json"
    response_type = BytesResponse
    error_codes = sensor_specific_error_codes

    id: int
    sensitivity: float

    api_version: str = API_VERSION
    context: str = CONTEXT

    @property
    def content(self) -> bytes:
        """Encode the sensor ID and new sensitivity in a setSensitivity request."""
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
class GetSupportedVersionsResponse(ApiResponse[list[str]]):
    """PIR Sensor Configuration API versions supported by the device."""

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
    """Request the PIR Sensor Configuration API versions supported by the device."""

    method = "post"
    path = "/axis-cgi/pirsensor.cgi"
    content_type = "application/json"
    response_type = GetSupportedVersionsResponse
    error_codes = general_error_codes

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
