"""Property parameters from param.cgi."""

from dataclasses import dataclass
from typing import Any

from typing_extensions import NotRequired, Self, TypedDict

from ..api import ApiItem


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
    def decode(cls, data: dict[str, Any]) -> Self:
        """Decode dictionary to class object."""
        return cls(
            id="properties",
            api_http_version=data["API"]["HTTP"]["Version"],
            api_metadata=data["API"]["Metadata"]["Metadata"],
            api_metadata_version=data["API"]["Metadata"]["Version"],
            api_ptz_presets_version=data["API"]["PTZ"]["Presets"]["Version"],
            # api_ptz_presets_version=data.get("API"]["PTZ"]["Presets"]["Version", False),
            embedded_development=data["EmbeddedDevelopment"]["Version"],
            # embedded_development=data.get("EmbeddedDevelopment_Version", "0.0"),
            firmware_builddate=data["Firmware"]["BuildDate"],
            firmware_buildnumber=data["Firmware"]["BuildNumber"],
            firmware_version=data["Firmware"]["Version"],
            image_format=data["Image"]["Format"],
            # image_format=data.get("Image_Format", ""),
            image_nbrofviews=int(data["Image"]["NbrOfViews"]),
            image_resolution=data["Image"]["Resolution"],
            image_rotation=data["Image"]["Rotation"],
            light_control=data["LightControl"]["LightControl2"],
            # light_control=data.get("LightControl_LightControl2") == "yes",
            ptz=data["PTZ"]["PTZ"],
            # ptz=data.get("PTZ_PTZ") == "yes",
            digital_ptz=data["PTZ"]["DigitalPTZ"],
            # digital_ptz=data.get("PTZ_DigitalPTZ") == "yes",
            system_serialnumber=data["System"]["SerialNumber"],
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> dict[str, Self]:
        """Create objects from dict."""
        return {"0": cls.decode(data)}
