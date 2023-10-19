"""Axis Vapix parameter management.

https://www.axis.com/vapix-library/#/subjects/t10037719/section/t10036014

Lists Brand, Image, Ports, Properties, PTZ, Stream profiles.
"""
from dataclasses import dataclass
from typing import Any, cast

from typing_extensions import NotRequired, Self, TypedDict

from ..models.stream_profile import StreamProfile
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


def process_dynamic_group(
    raw_group: dict[str, str],
    prefix: str,
    attributes: tuple[str, ...],
    group_range: range,
) -> dict[int, dict[str, bool | int | str]]:
    """Convert raw dynamic groups to a proper dictionary.

    raw_group: self[group]
    prefix: "Support.S"
    attributes: ("AbsoluteZoom", "DigitalZoom")
    group_range: range(5)
    """
    dynamic_group = {}
    for index in group_range:
        item: dict[str, bool | int | str] = {}

        for attribute in attributes:
            parameter = f"{prefix}{index}.{attribute}"  # Support.S0.AbsoluteZoom

            if parameter not in raw_group:
                continue

            parameter_value = raw_group[parameter]

            if parameter_value in ("true", "false", "yes", "no"):  # Boolean values
                item[attribute] = parameter_value in ("true", "yes")

            elif parameter_value.lstrip("-").isdigit():  # Positive/negative values
                item[attribute] = int(parameter_value)

            else:
                item[attribute] = parameter_value

            # item[attribute] = raw_group[parameter]

        if item:
            dynamic_group[index] = item

    return dynamic_group


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
    def decode(cls, data: dict[str, str]) -> Self:
        """Decode dictionary to class object."""
        attributes = (
            "Enabled",
            "Name",
            "Source",
            "Appearance.ColorEnabled",
            "Appearance.Compression",
            "Appearance.MirrorEnabled",
            "Appearance.Resolution",
            "Appearance.Rotation",
            "MPEG.Complexity",
            "MPEG.ConfigHeaderInterval",
            "MPEG.FrameSkipMode",
            "MPEG.ICount",
            "MPEG.PCount",
            "MPEG.UserDataEnabled",
            "MPEG.UserDataInterval",
            "MPEG.ZChromaQPMode",
            "MPEG.ZFpsMode",
            "MPEG.ZGopMode",
            "MPEG.ZMaxGopLength",
            "MPEG.ZMinFps",
            "MPEG.ZStrength",
            "MPEG.H264.Profile",
            "MPEG.H264.PSEnabled",
            "Overlay.Enabled",
            "Overlay.XPos",
            "Overlay.YPos",
            "Overlay.MaskWindows.Color",
            "RateControl.MaxBitrate",
            "RateControl.Mode",
            "RateControl.Priority",
            "RateControl.TargetBitrate",
            "SizeControl.MaxFrameSize",
            "Stream.Duration",
            "Stream.FPS",
            "Stream.NbrOfFrames",
            "Text.BGColor",
            "Text.ClockEnabled",
            "Text.Color",
            "Text.DateEnabled",
            "Text.Position",
            "Text.String",
            "Text.TextEnabled",
            "Text.TextSize",
        )
        return cls(
            id="image",
            data=cast(
                dict[int, ImageParamT],
                process_dynamic_group(data, "I", attributes, range(20)),
            ),
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


@dataclass
class PTZParam(ApiItem):
    """Stream profile parameters."""

    camera_default: int
    """PTZ default video channel.

    When camera parameter is omitted in HTTP requests.
    """

    number_of_cameras: int
    """Amount of video channels."""

    number_of_serial_ports: int
    """Amount of serial ports."""

    limits: dict
    """PTZ.Limit.L# are populated when a driver is installed on a video channel.

    Index # is the video channel number, starting on 1.
    When it is possible to obtain the current position from the driver,
    for example the current pan position, it is possible to apply limit restrictions
    to the requested operation. For instance, if an absolute pan to position 150
    is requested, but the upper limit is set to 140, the new pan position will be 140.
    This is the purpose of all but MinFieldAngle and MaxFieldAngle in this group.
    The purpose of those two parameters is to calibrate image centering.
    """

    support: dict
    """PTZ.Support.S# are populated when a driver is installed on a video channel.

    A parameter in the group has the value true if the corresponding capability
    is supported by the driver. The index # is the video channel number which starts from 1.
    An absolute operation means moving to a certain position,
    a relative operation means moving relative to the current position.
    Arguments referred to apply to PTZ control.
    """

    various: dict
    """PTZ.Various.V# are populated when a driver is installed on a video channel.

    The index # is the video channel number which starts from 1.
    The group consists of several different types of parameters for the video channel.
    To distinguish the parameter types, the group is presented as
    three different categories below. The Enabled parameters determine
    if a specific feature can be controlled using ptz.cgi (see section PTZ control).
    """

    @classmethod
    def decode(cls, data: dict[str, str]) -> Self:
        """Decode dictionary to class object."""
        number_of_cameras = int(data["NbrOfCameras"])
        limit_attributes = (
            "MaxBrightness",
            "MaxFieldAngle",
            "MaxFocus",
            "MaxIris",
            "MaxPan",
            "MaxTilt",
            "MaxZoom",
            "MinBrightness",
            "MinFieldAngle",
            "MinFocus",
            "MinIris",
            "MinPan",
            "MinTilt",
            "MinZoom",
        )
        support_attributes = (
            "AbsoluteBrightness",
            "AbsoluteFocus",
            "AbsoluteIris",
            "AbsolutePan",
            "AbsoluteTilt",
            "AbsoluteZoom",
            "ActionNotification",
            "AreaZoom",
            "AutoFocus",
            "AutoIrCutFilter",
            "AutoIris",
            "Auxiliary",
            "BackLight",
            "ContinuousBrightness",
            "ContinuousFocus",
            "ContinuousIris",
            "ContinuousPan",
            "ContinuousTilt",
            "ContinuousZoom",
            "DevicePreset",
            "DigitalZoom",
            "GenericHTTP",
            "IrCutFilter",
            "JoyStickEmulation",
            "LensOffset",
            "OSDMenu",
            "ProportionalSpeed",
            "RelativeBrightness",
            "RelativeFocus",
            "RelativeIris",
            "RelativePan",
            "RelativeTilt",
            "RelativeZoom",
            "ServerPreset",
            "SpeedCtl",
        )
        various_attributes = (
            "AutoFocus",
            "AutoIris",
            "BackLight",
            "BackLightEnabled",
            "BrightnessEnabled",
            "CtlQueueing",
            "CtlQueueLimit",
            "CtlQueuePollTime",
            "FocusEnabled",
            "HomePresetSet",
            "IrCutFilter",
            "IrCutFilterEnabled",
            "IrisEnabled",
            "MaxProportionalSpeed",
            "PanEnabled",
            "ProportionalSpeedEnabled",
            "PTZCounter",
            "ReturnToOverview",
            "SpeedCtlEnabled",
            "TiltEnabled",
            "ZoomEnabled",
        )
        return cls(
            id="ptz",
            camera_default=int(data["CameraDefault"]),
            number_of_cameras=int(data["NbrOfCameras"]),
            number_of_serial_ports=int(data["NbrOfSerPorts"]),
            limits=process_dynamic_group(
                data, "Limit.L", limit_attributes, range(1, number_of_cameras + 1)
            ),
            support=process_dynamic_group(
                data, "Support.S", support_attributes, range(1, number_of_cameras + 1)
            ),
            various=process_dynamic_group(
                data, "Various.V", various_attributes, range(1, number_of_cameras + 1)
            ),
        )


@dataclass
class StreamProfileParam(ApiItem):
    """Stream profile parameters."""

    max_groups: int
    """Maximum number of supported stream profiles."""

    stream_profiles: list[StreamProfile]
    """List of stream profiles."""

    @classmethod
    def decode(cls, data: dict[str, str]) -> Self:
        """Decode dictionary to class object."""
        max_groups = int(data.get("MaxGroups", 0))

        raw_profiles = process_dynamic_group(
            data, "S", ("Name", "Description", "Parameters"), range(max_groups)
        )

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
