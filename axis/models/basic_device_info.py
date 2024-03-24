"""Basic device information description."""

from dataclasses import dataclass
from typing import NotRequired, Self

import orjson
from typing_extensions import TypedDict

from .api import CONTEXT, ApiItem, ApiRequest, ApiResponse

API_VERSION = "1.1"


class ErrorDataT(TypedDict):
    """Error data in response."""

    code: int
    message: str


class DeviceInformationDescriptionT(TypedDict):
    """API description representation."""

    Architecture: str
    Brand: str
    BuildDate: str
    HardwareID: str
    ProdFullName: str
    ProdNbr: str
    ProdShortName: str
    ProdType: str
    ProdVariant: str
    SerialNumber: str
    Soc: str
    SocSerialNumber: str
    Version: str
    WebURL: str


class PropertiesDataT(TypedDict):
    """List of API description data."""

    propertyList: DeviceInformationDescriptionT


class GetAllPropertiesResponseT(TypedDict):
    """ListApis response."""

    apiVersion: str
    context: str
    method: str
    data: PropertiesDataT
    error: NotRequired[ErrorDataT]


class ApiVersionsT(TypedDict):
    """List of supported API versions."""

    apiVersions: list[str]


class GetSupportedVersionsResponseT(TypedDict):
    """ListApis response."""

    apiVersion: str
    context: str
    method: str
    data: ApiVersionsT
    error: NotRequired[ErrorDataT]


error_codes = {
    1000: "Invalid parameter value specified",
    2001: "Access forbidden",
    2002: "HTTP request type not supported. Only POST is supported",
    2003: "Requested API version is not supported",
    2004: "Method not supported",
    4000: "Invalid JSON",
    4002: "Required parameter missing or invalid",
    8000: "Internal error",
}


@dataclass(frozen=True)
class DeviceInformation(ApiItem):
    """API Discovery item."""

    architecture: str
    brand: str
    build_date: str
    firmware_version: str
    hardware_id: str
    product_full_name: str
    product_number: str
    product_short_name: str
    product_type: str
    product_variant: str
    serial_number: str
    soc: str
    soc_serial_number: str
    web_url: str

    @classmethod
    def decode(cls, data: DeviceInformationDescriptionT) -> Self:
        """Decode dict to class object."""
        return cls(
            id="0",
            architecture=data["Architecture"],
            brand=data["Brand"],
            build_date=data["BuildDate"],
            firmware_version=data["Version"],
            hardware_id=data["HardwareID"],
            product_full_name=data["ProdFullName"],
            product_number=data["ProdNbr"],
            product_short_name=data["ProdShortName"],
            product_type=data["ProdType"],
            product_variant=data["ProdVariant"],
            serial_number=data["SerialNumber"],
            soc=data["Soc"],
            soc_serial_number=data["SocSerialNumber"],
            web_url=data["WebURL"],
        )


@dataclass
class GetAllPropertiesResponse(ApiResponse[DeviceInformation]):
    """Response object for basic device info."""

    api_version: str
    context: str
    method: str
    data: DeviceInformation
    # error: ErrorDataT | None = None

    @classmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Prepare API description dictionary."""
        data: GetAllPropertiesResponseT = orjson.loads(bytes_data)
        return cls(
            api_version=data["apiVersion"],
            context=data["context"],
            method=data.get("method", ""),
            data=DeviceInformation.decode(data["data"]["propertyList"]),
        )


@dataclass
class GetAllPropertiesRequest(ApiRequest):
    """Request object for basic device info."""

    method = "post"
    path = "/axis-cgi/basicdeviceinfo.cgi"
    content_type = "application/json"
    error_codes = error_codes

    api_version: str = API_VERSION
    context: str = CONTEXT

    @property
    def content(self) -> bytes:
        """Initialize request data."""
        return orjson.dumps(
            {
                "apiVersion": self.api_version,
                "context": self.context,
                "method": "getAllProperties",
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
        """Prepare API description dictionary."""
        data: GetSupportedVersionsResponseT = orjson.loads(bytes_data)
        return cls(
            api_version=data["apiVersion"],
            context=data["context"],
            method=data["method"],
            data=data.get("data", {}).get("apiVersions", []),
        )


@dataclass
class GetSupportedVersionsRequest(ApiRequest):
    """Request object for listing supported API versions."""

    method = "post"
    path = "/axis-cgi/basicdeviceinfo.cgi"
    content_type = "application/json"
    error_codes = error_codes

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
