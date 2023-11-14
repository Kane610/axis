"""Axis Vapix parameter management.

https://www.axis.com/vapix-library/#/subjects/t10037719/section/t10036014

Lists Brand, Image, Ports, Properties, PTZ, Stream profiles.
"""
from dataclasses import dataclass
from typing import Any

from typing_extensions import NotRequired, Self, TypedDict

from ..models.stream_profile import StreamProfile
from .api import APIItem, ApiItem, ApiRequest


class BrandT(TypedDict):
    """Represent a brand object."""

    Brand: str
    ProdFullName: str
    ProdNbr: str
    ProdShortName: str
    ProdType: str
    ProdVariant: str
    WebURL: str


class ImageParamT(TypedDict):
    """Represent an image object."""

    Enabled: str
    Name: str
    Source: str
    Appearance_ColorEnabled: str
    Appearance_Compression: str
    Appearance_MirrorEnabled: str
    Appearance_Resolution: str
    Appearance_Rotation: str
    MPEG_Complexity: str
    MPEG_ConfigHeaderInterval: str
    MPEG_FrameSkipMode: str
    MPEG_ICount: str
    MPEG_PCount: str
    MPEG_UserDataEnabled: str
    MPEG_UserDataInterval: str
    MPEG_ZChromaQPMode: str
    MPEG_ZFpsMode: str
    MPEG_ZGopMode: str
    MPEG_ZMaxGopLength: str
    MPEG_ZMinFps: str
    MPEG_ZStrength: str
    MPEG_H264_Profile: str
    MPEG_H264_PSEnabled: str
    Overlay_Enabled: str
    Overlay_XPos: str
    Overlay_YPos: str
    Overlay_MaskWindows_Color: str
    RateControl_MaxBitrate: str
    RateControl_Mode: str
    RateControl_Priority: str
    RateControl_TargetBitrate: str
    SizeControl_MaxFrameSize: str
    Stream_Duration: str
    Stream_FPS: str
    Stream_NbrOfFrames: str
    Text_BGColor: str
    Text_ClockEnabled: str
    Text_Color: str
    Text_DateEnabled: str
    Text_Position: str
    Text_String: str
    Text_TextEnabled: str
    Text_TextSize: str


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


class StreamProfileT(TypedDict):
    """Represent a property object."""

    MaxGroups: int
    API_Metadata_Metadata: str


def params_to_dict(params: str, starts_with: str | None = None) -> dict[str, Any]:
    """Convert params to dictionary."""

    def convert(value: str) -> bool | int | str:
        """Convert value to Python type."""
        if value in ("true", "false", "yes", "no"):  # Boolean values
            return value in ("true", "yes")
        if value.lstrip("-").isnumeric():  # Positive/negative values
            return int(value)
        return value

    def populate(store: dict[str, Any], keys: str, v: bool | int | str) -> None:
        """Populate store with new keys and value.

        populate({}, "root.IOPort.I1.Output.Active", "closed")
        {'root': {'IOPort': {'I1': {'Output': {'Active': 'closed'}}}}}
        """
        k, _, keys = keys.partition(".")  # "root", ".", "IOPort.I1.Output.Active"
        populate(store.setdefault(k, {}), keys, v) if keys else store.update({k: v})

    param_dict: dict[str, Any] = {}
    for line in params.splitlines():
        if starts_with is not None and not line.startswith(starts_with):
            continue
        keys, _, value = line.partition("=")
        populate(param_dict, keys, convert(value))
    return param_dict


@dataclass
class GetParamsRequest(ApiRequest):
    """Request object for listing parameters."""

    method = "get"
    path = "/axis-cgi/param.cgi"
    content_type = "text/plain"

    group: str

    @property
    def params(self) -> dict[str, str]:
        """Request query parameters."""
        group = f"&group={self.group}" if self.group else ""
        return {"action": f"list{group}"}


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
class ImageParam(ApiItem):
    """Image parameters."""

    data: dict[int, ImageParamT]

    @classmethod
    def decode(cls, data: dict[str, Any]) -> Self:
        """Decode dictionary to class object."""
        return cls(id="image", data=data)


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
            # api_ptz_presets_version=data2.get("API"]["PTZ"]["Presets"]["Version", False),
            embedded_development=data["EmbeddedDevelopment"]["Version"],
            # embedded_development=data.get("EmbeddedDevelopment_Version", "0.0"),
            firmware_builddate=data["Firmware"]["BuildDate"],
            firmware_buildnumber=data["Firmware"]["BuildNumber"],
            firmware_version=data["Firmware"]["Version"],
            image_format=data["Image"]["Format"],
            # image_format=data2.get("Image_Format", ""),
            image_nbrofviews=int(data["Image"]["NbrOfViews"]),
            image_resolution=data["Image"]["Resolution"],
            image_rotation=data["Image"]["Rotation"],
            light_control=data["LightControl"]["LightControl2"],
            # light_control=data2.get("LightControl_LightControl2") == "yes",
            ptz=data["PTZ"]["PTZ"],
            # ptz=data2.get("PTZ_PTZ") == "yes",
            digital_ptz=data["PTZ"]["DigitalPTZ"],
            # digital_ptz=data2.get("PTZ_DigitalPTZ") == "yes",
            system_serialnumber=data["System"]["SerialNumber"],
        )


@dataclass
class StreamProfileParam(ApiItem):
    """Stream profile parameters."""

    max_groups: int
    """Maximum number of supported stream profiles."""

    stream_profiles: list[StreamProfile]
    """List of stream profiles."""

    @classmethod
    def decode(cls, data: dict[str, Any]) -> Self:
        """Decode dictionary to class object."""
        max_groups = int(data.get("MaxGroups", 0))

        raw_profiles = dict(data)
        del raw_profiles["MaxGroups"]

        profiles = [
            StreamProfile(
                id=str(profile["Name"]),
                description=str(profile["Description"]),
                parameters=str(profile["Parameters"]),
            )
            for profile in raw_profiles.values()
        ]

        return cls(
            id="stream profiles",
            max_groups=max_groups,
            stream_profiles=profiles,
        )
