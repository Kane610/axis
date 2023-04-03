"""PIR sensor configuration api.

The PIR sensor configuration API helps you list and configure
the sensitivity of the PIR (passive infrared) sensors on your Axis device.
"""
from dataclasses import dataclass
from http import HTTPStatus

import orjson
from typing_extensions import NotRequired, TypedDict

from .api import CONTEXT, ApiItem, ApiRequest

API_VERSION = "1.0"


class PirSensorConfigurationT(TypedDict):
    """Pir sensor configuration representation."""

    id: str
    sensitivityConfigurable: bool
    sensitivity: NotRequired[float]


class ListSensorsDataT(TypedDict):
    """List of Pir sensor configuration data."""

    sensors: list[PirSensorConfigurationT]


class TypedListSensorsResponse(TypedDict):
    """ListSensors response."""

    apiVersion: str
    context: str
    method: str
    data: ListSensorsDataT


class GetSensitivityDataT(TypedDict):
    """Sensitivity data."""

    sensitivity: float


class GetSensitivityResponseT(TypedDict):
    """GetSensitivity response."""

    apiVersion: str
    context: str
    method: str
    data: GetSensitivityDataT


class SetSensitivityResponseT(TypedDict):
    """SetSensitivity response."""

    apiVersion: str
    context: str
    method: str


@dataclass
class PirSensorConfiguration(ApiItem):
    """Pir sensor configuration representation."""

    configurable: bool
    sensitivity: float | None = None


class ApiVersionsT(TypedDict):
    """List of supported API versions."""

    apiVersions: list[str]


class GetSupportedVersionsT(TypedDict):
    """ListSensors response."""

    apiVersion: str
    context: str
    method: str
    data: ApiVersionsT


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
class ListSensorsRequest(ApiRequest[dict[str, PirSensorConfiguration]]):
    """Request object for listing PIR sensors."""

    @classmethod
    def create(
        cls,
        *,
        context: str = CONTEXT,
        version: str = API_VERSION,
    ) -> "ListSensorsRequest":
        """Create list sensors request."""
        return cls(
            method="post",
            path="/axis-cgi/pirsensor.cgi",
            data={
                "apiVersion": version,
                "context": context,
                "method": "listSensors",
            },
            http_code=HTTPStatus.OK,
            content_type="application/json",
            error_codes=general_error_codes,
        )

    def process_raw(self, raw: str) -> dict[str, PirSensorConfiguration]:
        """Prepare Pir sensor configuration dictionary."""
        data: TypedListSensorsResponse = orjson.loads(raw)
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

    @classmethod
    def create(
        cls,
        id: int,
        *,
        context: str = CONTEXT,
        version: str = API_VERSION,
    ) -> "GetSensitivityRequest":
        """Create get sensitivity request."""
        return cls(
            method="post",
            path="/axis-cgi/pirsensor.cgi",
            data={
                "apiVersion": version,
                "context": context,
                "method": "getSensitivity",
                "params": {
                    "id": id,
                },
            },
            http_code=HTTPStatus.OK,
            content_type="application/json",
            error_codes=sensor_specific_error_codes,
        )

    def process_raw(self, raw: str) -> float | None:
        """Prepare sensitivity value."""
        data: GetSensitivityResponseT = orjson.loads(raw)
        return data.get("data", {}).get("sensitivity")


@dataclass
class SetSensitivityRequest(ApiRequest[None]):
    """Request object for setting PIR sensor sensitivity."""

    @classmethod
    def create(
        cls,
        id: int,
        sensitivity: float,
        *,
        context: str = CONTEXT,
        version: str = API_VERSION,
    ) -> "SetSensitivityRequest":
        """Create set sensitivity request."""
        return cls(
            method="post",
            path="/axis-cgi/pirsensor.cgi",
            data={
                "apiVersion": version,
                "context": context,
                "method": "setSensitivity",
                "params": {
                    "id": id,
                    "sensitivity": sensitivity,
                },
            },
            http_code=HTTPStatus.OK,
            content_type="application/json",
            error_codes=sensor_specific_error_codes,
        )

    def process_raw(self, raw: str) -> None:
        """No expected data in response."""
        return None


@dataclass
class GetSupportedVersionsRequest(ApiRequest[list[str]]):
    """Request object for listing supported API versions."""

    @classmethod
    def create(
        cls,
        *,
        context: str = CONTEXT,
    ) -> "GetSupportedVersionsRequest":
        """Create supported API versions request."""
        return cls(
            method="post",
            path="/axis-cgi/pirsensor.cgi",
            data={
                "context": context,
                "method": "getSupportedVersions",
            },
            http_code=HTTPStatus.OK,
            content_type="application/json",
            error_codes=general_error_codes,
        )

    def process_raw(self, raw: str) -> list[str]:
        """Process supported versions."""
        data: GetSupportedVersionsT = orjson.loads(raw)
        return data.get("data", {}).get("apiVersions", [])
