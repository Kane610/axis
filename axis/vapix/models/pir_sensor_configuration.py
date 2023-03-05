"""PIR sensor configuration api.

The PIR sensor configuration API helps you list and configure
the sensitivity of the PIR (passive infrared) sensors on your Axis device.
"""
from dataclasses import dataclass
from http import HTTPStatus

from .api import CONTEXT, ApiItem, ApiRequest

API_VERSION = "1.0"


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
class ListSensorsRequest(ApiRequest):
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


@dataclass
class GetSensitivityRequest(ApiRequest):
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


@dataclass
class SetSensitivityRequest(ApiRequest):
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


@dataclass
class SupportedVersionsRequest(ApiRequest):
    """Request object for listing supported API versions."""

    @classmethod
    def create(
        cls,
        *,
        context: str = CONTEXT,
    ) -> "SupportedVersionsRequest":
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


@dataclass
class PirSensorConfiguration(ApiItem):
    """"""

    configurable: bool
    sensitivity: float | None = None
