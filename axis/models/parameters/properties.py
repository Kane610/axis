"""Property parameters from param.cgi."""

from dataclasses import dataclass
from typing import NotRequired, Self

from typing_extensions import TypedDict

from .param_cgi import ParamItem


class PropertyApiHttpParamT(TypedDict):
    """Represent an API HTTP object."""

    AdminPath: str
    Version: int


class PropertyApiMetadataParamT(TypedDict):
    """Represent an API Metadata object."""

    Metadata: str
    Version: str


class PropertyApiPtzPresetsParamT(TypedDict):
    """Represent a PTZ preset object."""

    Version: NotRequired[str]


class PropertyApiPtzParamT(TypedDict):
    """Represent an API PTZ object."""

    Presets: PropertyApiPtzPresetsParamT


class PropertyApiParamT(TypedDict):
    """Represent an API object."""

    HTTP: PropertyApiHttpParamT
    Metadata: PropertyApiMetadataParamT
    PTZ: NotRequired[PropertyApiPtzParamT]


class PropertyEmbeddedDevelopmentRuleEngineParamT(TypedDict):
    """Represent an embedded development rule engine object."""

    MultiConfiguration: bool


class PropertyEmbeddedDevelopmentParamT(TypedDict):
    """Represent an embedded development object."""

    CacheSize: int
    DefaultCacheSize: int
    EmbeddedDevelopment: bool
    Version: str
    RuleEngine: PropertyEmbeddedDevelopmentRuleEngineParamT


class PropertyFirmwareParamT(TypedDict):
    """Represent a firmware object."""

    BuildDate: str
    BuildNumber: str
    Version: str


class PropertyImageParamT(TypedDict):
    """Represent an image object."""

    Format: NotRequired[str]
    NbrOfViews: int
    Resolution: str
    Rotation: str
    ShowSuboptimalResolutions: bool


class PropertyLightControlParamT(TypedDict):
    """Represent a light control object."""

    LightControl2: NotRequired[bool]
    LightControlAvailable: bool


class PropertyPtzParamT(TypedDict):
    """Represent a PTZ object."""

    DigitalPTZ: bool
    DriverManagement: bool
    DriverModeList: str
    PTZ: bool
    PTZOnQuadView: bool
    SelectableDriverMode: bool


class PropertySystemParamT(TypedDict):
    """Represent a system object."""

    Architecture: str
    HardwareID: str
    Language: str
    LanguageType: str
    SerialNumber: str
    Soc: str


class PropertyParamT(TypedDict):
    """Represent a property object."""

    API: PropertyApiParamT
    EmbeddedDevelopment: NotRequired[PropertyEmbeddedDevelopmentParamT]
    Firmware: PropertyFirmwareParamT
    Image: NotRequired[PropertyImageParamT]
    LightControl: NotRequired[PropertyLightControlParamT]
    PTZ: NotRequired[PropertyPtzParamT]
    System: PropertySystemParamT


@dataclass(frozen=True)
class PropertyParam(ParamItem):
    """Property parameters."""

    api_http_version: int
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

    firmware_build_date: str
    """Firmware build date."""

    firmware_build_number: str
    """Firmware build number."""

    firmware_version: str
    """Firmware version."""

    image_format: str
    """Supported image formats."""

    image_number_of_views: int
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

    system_serial_number: str
    """Device serial number."""

    @classmethod
    def decode(cls, data: PropertyParamT) -> Self:
        """Decode dictionary to class object."""
        return cls(
            id="properties",
            api_http_version=data["API"]["HTTP"]["Version"],
            api_metadata=data["API"].get("Metadata", {}).get("Metadata", "no"),
            api_metadata_version=data["API"].get("Metadata", {}).get("Version", "0.0"),
            api_ptz_presets_version=data["API"]
            .get("PTZ", {})
            .get("Presets", {})
            .get("Version", False),
            embedded_development=data.get("EmbeddedDevelopment", {}).get(
                "Version", "0.0"
            ),
            firmware_build_date=data["Firmware"]["BuildDate"],
            firmware_build_number=data["Firmware"]["BuildNumber"],
            firmware_version=data["Firmware"]["Version"],
            image_format=data.get("Image", {}).get("Format", ""),
            image_number_of_views=int(data.get("Image", {}).get("NbrOfViews", 0)),
            image_resolution=data.get("Image", {}).get("Resolution", ""),
            image_rotation=data.get("Image", {}).get("Rotation", ""),
            light_control=data.get("LightControl", {}).get("LightControl2", False),
            ptz=data.get("PTZ", {}).get("PTZ", False),
            digital_ptz=data.get("PTZ", {}).get("DigitalPTZ", False),
            system_serial_number=data["System"]["SerialNumber"],
        )
