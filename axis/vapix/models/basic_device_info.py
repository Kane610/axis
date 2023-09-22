"""Basic device information description."""

from dataclasses import dataclass

import orjson
from typing_extensions import NotRequired, TypedDict

from .api import CONTEXT, ApiItem, ApiRequest

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


@dataclass
class DeviceInformation(ApiItem):
    """API Discovery item."""

    architecture: str
    brand: str
    build_date: str
    hardware_id: str
    product_full_name: str
    product_number: str
    product_short_name: str
    product_type: str
    product_variant: str
    serial_number: str
    soc: str
    soc_serial_number: str
    version: str
    web_url: str


GetAllPropertiesT = dict[str, DeviceInformation]


@dataclass
class GetAllPropertiesRequest(ApiRequest[GetAllPropertiesT]):
    """Request object for listing API descriptions."""

    method = "post"
    path = "/axis-cgi/basicdeviceinfo.cgi"
    content_type = "application/json"
    error_codes = error_codes

    api_version: str = API_VERSION
    context: str = CONTEXT

    def __post_init__(self) -> None:
        """Initialize request data."""
        self.data = {
            "apiVersion": self.api_version,
            "context": self.context,
            "method": "getAllProperties",
        }

    def process_raw(self, raw: bytes) -> GetAllPropertiesT:
        """Prepare API description dictionary."""
        data: GetAllPropertiesResponseT = orjson.loads(raw)
        device_information = data.get("data", {}).get("propertyList", {})
        return {
            "0": DeviceInformation(
                id="0",
                architecture=device_information["Architecture"],
                brand=device_information["Brand"],
                build_date=device_information["BuildDate"],
                hardware_id=device_information["HardwareID"],
                product_full_name=device_information["ProdFullName"],
                product_number=device_information["ProdNbr"],
                product_short_name=device_information["ProdShortName"],
                product_type=device_information["ProdType"],
                product_variant=device_information["ProdVariant"],
                serial_number=device_information["SerialNumber"],
                soc=device_information["Soc"],
                soc_serial_number=device_information["SocSerialNumber"],
                version=device_information["Version"],
                web_url=device_information["WebURL"],
            )
        }


@dataclass
class GetSupportedVersionsRequest(ApiRequest[list[str]]):
    """Request object for listing supported API versions."""

    method = "post"
    path = "/axis-cgi/basicdeviceinfo.cgi"
    content_type = "application/json"
    error_codes = error_codes

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
