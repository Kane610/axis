"""Property parameters from param.cgi."""

from dataclasses import dataclass
from typing import NotRequired, Self, TypedDict

from .param_cgi import ParamItem


class PropertyApiHttpParamT(TypedDict):
    """HTTP API administrative path and version from the Properties group."""

    AdminPath: str
    Version: int


class PropertyApiMetadataParamT(TypedDict):
    """Metadata API availability and version from the Properties group."""

    Metadata: str
    Version: str


class PropertyApiPtzPresetsParamT(TypedDict):
    """PTZ preset API version reported by the Properties group."""

    Version: NotRequired[str]


class PropertyApiPtzParamT(TypedDict):
    """PTZ-related API versions reported by the Properties group."""

    Presets: PropertyApiPtzPresetsParamT


class PropertyApiParamT(TypedDict):
    """HTTP, metadata, and optional PTZ API properties."""

    HTTP: PropertyApiHttpParamT
    Metadata: PropertyApiMetadataParamT
    PTZ: NotRequired[PropertyApiPtzParamT]


class PropertyEmbeddedDevelopmentRuleEngineParamT(TypedDict):
    """Rule-engine capabilities reported under EmbeddedDevelopment."""

    MultiConfiguration: bool


class PropertyEmbeddedDevelopmentParamT(TypedDict):
    """Embedded-development API version, cache sizes, and rule-engine settings."""

    CacheSize: int
    DefaultCacheSize: int
    EmbeddedDevelopment: bool
    Version: str
    RuleEngine: PropertyEmbeddedDevelopmentRuleEngineParamT


class PropertyFirmwareParamT(TypedDict):
    """Firmware build date, build number, and version from the Properties group."""

    BuildDate: str
    BuildNumber: str
    Version: str


class PropertyImageParamT(TypedDict):
    """Image format, views, resolution, rotation, and display capabilities."""

    Format: NotRequired[str]
    NbrOfViews: int
    Resolution: str
    Rotation: str
    ShowSuboptimalResolutions: bool


class PropertyLightControlParamT(TypedDict):
    """Light-control availability and API capability flags."""

    LightControl2: NotRequired[bool]
    LightControlAvailable: bool


class PropertyPtzParamT(TypedDict):
    """PTZ control and driver-management capability flags."""

    DigitalPTZ: bool
    DriverManagement: bool
    DriverModeList: str
    PTZ: bool
    PTZOnQuadView: bool
    SelectableDriverMode: bool


class PropertySystemParamT(TypedDict):
    """Hardware and system identity fields from the Properties group."""

    Architecture: str
    HardwareID: str
    Language: str
    LanguageType: str
    SerialNumber: str
    Soc: str


class PropertyVirtualInputParamT(TypedDict):
    """Whether the device supports virtual input ports."""

    VirtualInput: bool


class PropertyParamT(TypedDict):
    """The API, firmware, system, and optional device features in Properties."""

    API: PropertyApiParamT
    EmbeddedDevelopment: NotRequired[PropertyEmbeddedDevelopmentParamT]
    Firmware: PropertyFirmwareParamT
    Image: NotRequired[PropertyImageParamT]
    LightControl: NotRequired[PropertyLightControlParamT]
    PTZ: NotRequired[PropertyPtzParamT]
    System: PropertySystemParamT
    VirtualInput: NotRequired[PropertyVirtualInputParamT]


@dataclass(frozen=True)
class PropertyParam(ParamItem):
    """Normalized API versions and device capabilities from param.cgi Properties."""

    api_http_version: int
    """HTTP API version."""

    api_metadata: str
    """Whether the device advertises metadata API support."""

    api_metadata_version: str
    """Metadata API version."""

    api_ptz_presets_version: bool | str
    """PTZ preset API version, or False when no version is reported.

    From version 2.00, presets can no longer be added, updated, or removed with
    param.cgi.
    """

    embedded_development: str
    """Version of the embedded-development API, or "0.0" when unavailable.

    Application list.cgi is supported from version 1.20.
    """

    firmware_build_date: str
    """Firmware build date."""

    firmware_build_number: str
    """Firmware build number."""

    firmware_version: str
    """Firmware version."""

    image_format: str
    """Image formats supported by the device."""

    image_number_of_views: int
    """Number of image views the device supports."""

    image_resolution: str
    """Supported image resolutions."""

    image_rotation: str
    """Supported image rotations."""

    light_control: bool
    """Whether the device advertises Light Control API support."""

    ptz: bool
    """Whether the device supports PTZ control."""

    digital_ptz: bool
    """Whether the device supports digital PTZ."""

    system_serial_number: str
    """Device serial number."""

    virtual_input: bool
    """Whether the device supports virtual input ports."""

    @classmethod
    def decode(cls, data: PropertyParamT) -> Self:
        """Convert the Properties group into normalized version and capability fields."""
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
            virtual_input=data.get("VirtualInput", {}).get("VirtualInput", False),
        )
