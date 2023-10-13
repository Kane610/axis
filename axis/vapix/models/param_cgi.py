"""Axis Vapix parameter management.

https://www.axis.com/vapix-library/#/subjects/t10037719/section/t10036014

Lists Brand, Image, Ports, Properties, PTZ, Stream profiles.
"""
from dataclasses import dataclass
from typing import Any, cast

from typing_extensions import NotRequired, Self, TypedDict

from .api import APIItem, ApiItem


class BrandT(TypedDict):
    """Represent a brand object."""

    Brand: str
    ProdFullName: str
    ProdNbr: str
    ProdShortName: str
    ProdType: str
    ProdVariant: str
    WebURL: str


class PropertyT(TypedDict):
    """Represent a property object."""

    API_HTTP_Version: str
    API_Metadata_Metadata: str
    API_Metadata_Version: str
    API_PTZ_Presets_Version: NotRequired[str]
    EmbeddedDevelopment_Version: NotRequired[str]
    Firmware_BuildDate: str
    Firmware_BuildNumber: str
    Firmware_Version: str
    Image_Format: NotRequired[str]
    Image_NbrOfViews: str
    Image_Resolution: str
    Image_Rotation: str
    LightControl_LightControl2: NotRequired[str]
    PTZ_PTZ: NotRequired[str]
    PTZ_DigitalPTZ: NotRequired[str]
    System_SerialNumber: str


class Param(APIItem):
    """Parameter group."""

    def __contains__(self, obj_id: str) -> bool:
        """Evaluate object membership to parameter group."""
        return obj_id in self.raw

    def get(self, obj_id: str, default: Any | None = None) -> Any:
        """Get object if stored in raw else return default."""
        return self.raw.get(obj_id, default)

    def __getitem__(self, obj_id: str) -> Any:
        """Return Param[obj_id]."""
        return self.raw[obj_id]


@dataclass
class BrandParam(ApiItem):
    """Brand parameters."""

    brand: str
    """Device branding."""

    prodfullname: str
    """Device product full name."""

    prodnbr: str
    """Device product number."""

    prodshortname: str
    """Device product short name."""

    prodtype: str
    """Device product type."""

    prodvariant: str
    """Device product variant."""

    weburl: str
    """Device home page URL."""

    @classmethod
    def decode(cls, data: BrandT) -> Self:
        """Decode dictionary to class object."""
        return cls(
            id="brand",
            brand=data["Brand"],
            prodfullname=data["ProdFullName"],
            prodnbr=data["ProdNbr"],
            prodshortname=data["ProdShortName"],
            prodtype=data["ProdType"],
            prodvariant=data["ProdVariant"],
            weburl=data["WebURL"],
        )


@dataclass
class PropertyParam(ApiItem):
    """Property parameters."""

    api_http_version: str
    """HTTP API version."""

    api_metadata: str
    """Support metadata API."""

    api_metadata_version: str
    """Metadata API version."""

    api_ptz_presets_version: bool | str
    """Preset index for device home position at start-up.

    As of version 2.00 of the PTZ preset API Properties.API.PTZ.Presets.Version=2.00
    adding, updating and removing presets using param.cgi is no longer supported.
    """

    embedded_development: str
    """VAPIX® Application API is supported.

    Application list.cgi supported if => 1.20.
    """

    firmware_builddate: str
    """Firmware build date."""

    firmware_buildnumber: str
    """Firmware build number."""

    firmware_version: str
    """Firmware version."""

    image_format: str
    """Supported image formats."""

    image_nbrofviews: int
    """Amount of supported view areas."""

    image_resolution: str
    """Supported image resolutions."""

    image_rotation: str
    """Supported image rotations."""

    light_control: bool
    """Support light control."""

    ptz: bool
    """Support PTZ control."""

    digital_ptz: bool
    """Support digital PTZ control."""

    system_serialnumber: str
    """Device serial number."""

    @classmethod
    def decode(cls, data: dict[str, str]) -> Self:
        """Decode dictionary to class object."""
        data2 = cast(PropertyT, {k.replace(".", "_"): v for k, v in data.items()})
        return cls(
            id="properties",
            api_http_version=data2["API_HTTP_Version"],
            api_metadata=data2["API_Metadata_Metadata"],
            api_metadata_version=data2["API_Metadata_Version"],
            api_ptz_presets_version=data2.get("API_PTZ_Presets_Version", False),
            embedded_development=data2.get("EmbeddedDevelopment_Version", "0.0"),
            firmware_builddate=data2["Firmware_BuildDate"],
            firmware_buildnumber=data2["Firmware_BuildNumber"],
            firmware_version=data2["Firmware_Version"],
            image_format=data2.get("Image_Format", ""),
            image_nbrofviews=int(data2["Image_NbrOfViews"]),
            image_resolution=data2["Image_Resolution"],
            image_rotation=data2["Image_Rotation"],
            light_control=data2.get("LightControl_LightControl2") == "yes",
            ptz=data2.get("PTZ_PTZ") == "yes",
            digital_ptz=data2.get("PTZ_DigitalPTZ") == "yes",
            system_serialnumber=data2["System_SerialNumber"],
        )
