"""Models for product identity and supported versions from Basic Device Information."""

from dataclasses import dataclass
from typing import NotRequired, Self, TypedDict

import orjson

from .api import CONTEXT, ApiItem, ApiRequest, ApiResponse

API_VERSION = "1.1"


class ErrorDataT(TypedDict):
    """Error code and message returned by the Basic Device Information API."""

    code: int
    message: str


class DeviceInformationDescriptionT(TypedDict):
    """Product, firmware, hardware, and system fields returned by the API."""

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
    """Device property list in a getAllProperties response."""

    propertyList: DeviceInformationDescriptionT


class GetAllPropertiesResponseT(TypedDict):
    """JSON envelope returned by getAllProperties."""

    apiVersion: str
    context: str
    method: str
    data: PropertiesDataT
    error: NotRequired[ErrorDataT]


class ApiVersionsT(TypedDict):
    """Versions of the Basic Device Information API supported by the device."""

    apiVersions: list[str]


class GetSupportedVersionsResponseT(TypedDict):
    """JSON envelope returned by getSupportedVersions."""

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
    """Normalized product, firmware, hardware, and system identity."""

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
        """Convert the API's property names to the device information model."""
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
    """Device identity fields returned by getAllProperties."""

    api_version: str
    context: str
    method: str
    data: DeviceInformation
    # error: ErrorDataT | None = None

    @classmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Parse the JSON envelope and decode its device property list."""
        data: GetAllPropertiesResponseT = orjson.loads(bytes_data)
        return cls(
            api_version=data["apiVersion"],
            context=data["context"],
            method=data.get("method", ""),
            data=DeviceInformation.decode(data["data"]["propertyList"]),
        )


@dataclass
class GetAllPropertiesRequest(ApiRequest[GetAllPropertiesResponse]):
    """Request product and firmware properties from the device."""

    method = "post"
    path = "/axis-cgi/basicdeviceinfo.cgi"
    content_type = "application/json"
    response_type = GetAllPropertiesResponse
    supports_companion_param = False
    error_codes = error_codes

    api_version: str = API_VERSION
    context: str = CONTEXT

    @property
    def content(self) -> bytes:
        """Encode a getAllProperties request as JSON."""
        return orjson.dumps(
            {
                "apiVersion": self.api_version,
                "context": self.context,
                "method": "getAllProperties",
            }
        )


@dataclass
class GetSupportedVersionsResponse(ApiResponse[list[str]]):
    """Basic Device Information API versions supported by the device."""

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
    """Request the Basic Device Information API versions supported by the device."""

    method = "post"
    path = "/axis-cgi/basicdeviceinfo.cgi"
    content_type = "application/json"
    response_type = GetSupportedVersionsResponse
    supports_companion_param = False
    error_codes = error_codes

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
