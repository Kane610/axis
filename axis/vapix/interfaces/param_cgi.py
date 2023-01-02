"""Axis Vapix parameter management.

https://www.axis.com/vapix-library/#/subjects/t10037719/section/t10036014

Lists Brand, Image, Ports, Properties, PTZ, Stream profiles.
"""

import asyncio
from typing import Dict, Union

from ..models.param_cgi import Param
from ..models.stream_profile import StreamProfile
from .api import APIItems

PROPERTY = "Properties.API.HTTP.Version=3"

URL = "/axis-cgi/param.cgi"
URL_GET = URL + "?action=list"

BRAND = "root.Brand"
IMAGE = "root.Image"
INPUT = "root.Input"
IOPORT = "root.IOPort"
OUTPUT = "root.Output"
PROPERTIES = "root.Properties"
PTZ = "root.PTZ"
STREAM_PROFILES = "root.StreamProfile"

SUPPORTED_GROUPS = [
    BRAND,
    IMAGE,
    INPUT,
    IOPORT,
    OUTPUT,
    PROPERTIES,
    PTZ,
    STREAM_PROFILES,
]


class Params(APIItems):
    """Represents all parameters of param.cgi."""

    item_cls = Param
    path = URL_GET

    async def update(self, group: str = "") -> None:
        """Refresh data."""
        path = URL_GET + (f"&group={group}" if group else "")
        raw = await self.vapix.request("get", path)
        self.process_raw(raw)

    @staticmethod
    def pre_process_raw(raw: str) -> dict:  # type: ignore[override]
        """Return a dictionary of parameter groups."""
        params: Dict[str, Dict[str, str]] = {}
        for raw_line in raw.splitlines():  # root.group.parameter..=value
            split_line = raw_line.split(".", 2)  # root, group, parameter..=value
            group = ".".join(split_line[:2])  # root.group

            if group not in SUPPORTED_GROUPS:
                continue

            params.setdefault(group, {})

            param = split_line[2].split("=", 1)  # parameter.., value
            params[group][param[0]] = param[1]  # {root.group: {parameter..: value}}

        return params

    @staticmethod
    def process_dynamic_group(
        raw_group: dict, prefix: str, attributes: tuple, group_range: range
    ) -> dict:
        """Convert raw dynamic groups to a proper dictionary.

        raw_group: self[group]
        prefix: "Support.S"
        attributes: ("AbsoluteZoom", "DigitalZoom")
        group_range: range(5)
        """
        dynamic_group = {}
        for index in group_range:
            item = {}

            for attribute in attributes:
                parameter = f"{prefix}{index}.{attribute}"  # Support.S0.AbsoluteZoom

                if parameter not in raw_group:
                    continue

                parameter_value = raw_group[parameter]

                if parameter_value in ("true", "false"):  # Boolean values
                    item[attribute] = parameter_value == "true"

                elif parameter_value in ("yes", "no"):  # Boolean values
                    item[attribute] = parameter_value == "yes"

                elif parameter_value.lstrip("-").isdigit():  # Positive/negative values
                    item[attribute] = int(parameter_value)

                else:
                    item[attribute] = parameter_value

            if item:
                dynamic_group[index] = item

        return dynamic_group

    # Brand

    async def update_brand(self) -> None:
        """Update brand group of parameters."""
        await self.update(BRAND)

    @property
    def brand(self) -> str:
        """Device branding."""
        return self[BRAND]["Brand"]  # type: ignore

    @property
    def prodfullname(self) -> str:
        """Device product full name."""
        return self[BRAND]["ProdFullName"]  # type: ignore

    @property
    def prodnbr(self) -> str:
        """Device product number."""
        return self[BRAND]["ProdNbr"]  # type: ignore

    @property
    def prodshortname(self) -> str:
        """Device product short name."""
        return self[BRAND]["ProdShortName"]  # type: ignore

    @property
    def prodtype(self) -> str:
        """Device product type."""
        return self[BRAND]["ProdType"]  # type: ignore

    @property
    def prodvariant(self) -> str:
        """Device product variant."""
        return self[BRAND]["ProdVariant"]  # type: ignore

    @property
    def weburl(self) -> str:
        """Device home page URL."""
        return self[BRAND]["WebURL"]  # type: ignore

    # Image

    async def update_image(self) -> None:
        """Update image group of parameters."""
        await self.update(IMAGE)

    @property
    def image_sources(self) -> dict:
        """Image source information."""
        if IMAGE not in self:
            return {}

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

        sources = self.process_dynamic_group(
            self[IMAGE],  # type: ignore[arg-type]
            "I",
            attributes,
            range(self.image_nbrofviews),
        )

        return sources

    # Ports

    async def update_ports(self) -> None:
        """Update port groups of parameters."""
        await asyncio.gather(
            self.update(INPUT),
            self.update(IOPORT),
            self.update(OUTPUT),
        )

    @property
    def nbrofinput(self) -> int:
        """Match the number of configured inputs."""
        return int(self[INPUT]["NbrOfInputs"])  # type: ignore

    @property
    def nbrofoutput(self) -> int:
        """Match the number of configured outputs."""
        return int(self[OUTPUT]["NbrOfOutputs"])  # type: ignore

    @property
    def ports(self) -> dict:
        """Create a smaller dictionary containing all ports."""
        if IOPORT not in self:
            return {}

        attributes = (
            "Usage",
            "Configurable",
            "Direction",
            "Input.Name",
            "Input.Trig",
            "Output.Active",
            "Output.Button",
            "Output.DelayTime",
            "Output.Mode",
            "Output.Name",
            "Output.PulseTime",
        )

        ports = self.process_dynamic_group(
            self[IOPORT],  # type: ignore[arg-type]
            "I",
            attributes,
            range(self.nbrofinput + self.nbrofoutput),
        )

        return ports

    # Properties

    async def update_properties(self) -> None:
        """Update properties group of parameters."""
        await self.update(PROPERTIES)

    @property
    def api_http_version(self) -> str:
        """HTTP API version."""
        return self[PROPERTIES]["API.HTTP.Version"]  # type: ignore

    @property
    def api_metadata(self) -> str:
        """Support metadata API."""
        return self[PROPERTIES]["API.Metadata.Metadata"]  # type: ignore

    @property
    def api_metadata_version(self) -> str:
        """Metadata API version."""
        return self[PROPERTIES]["API.Metadata.Version"]  # type: ignore

    @property
    def api_ptz_presets_version(self) -> Union[str, bool]:
        """Preset index for device home position at start-up.

        As of version 2.00 of the PTZ preset API Properties.API.PTZ.Presets.Version=2.00
        adding, updating and removing presets using param.cgi is no longer supported.
        """
        return self[PROPERTIES].get("API.PTZ.Presets.Version", False)  # type: ignore[attr-defined]

    @property
    def embedded_development(self) -> str:
        """VAPIX® Application API is supported.

        Application list.cgi supported if => 1.20.
        """
        return self.get(PROPERTIES, {}).get("EmbeddedDevelopment.Version", "0.0")

    @property
    def firmware_builddate(self) -> str:
        """Firmware build date."""
        return self[PROPERTIES]["Firmware.BuildDate"]  # type: ignore

    @property
    def firmware_buildnumber(self) -> str:
        """Firmware build number."""
        return self[PROPERTIES]["Firmware.BuildNumber"]  # type: ignore

    @property
    def firmware_version(self) -> str:
        """Firmware version."""
        return self[PROPERTIES]["Firmware.Version"]  # type: ignore

    @property
    def image_format(self) -> str:
        """Supported image formats."""
        return self[PROPERTIES].get("Image.Format", "")  # type: ignore[attr-defined]

    @property
    def image_nbrofviews(self) -> int:
        """Amount of supported view areas."""
        return int(self[PROPERTIES]["Image.NbrOfViews"])  # type: ignore

    @property
    def image_resolution(self) -> str:
        """Supported image resolutions."""
        return self[PROPERTIES]["Image.Resolution"]  # type: ignore

    @property
    def image_rotation(self) -> str:
        """Supported image rotations."""
        return self[PROPERTIES]["Image.Rotation"]  # type: ignore

    @property
    def light_control(self) -> bool:
        """Support light control."""
        return self.get(PROPERTIES, {}).get("LightControl.LightControl2") == "yes"

    @property
    def ptz(self) -> bool:
        """Support PTZ control."""
        return self.get(PROPERTIES, {}).get("PTZ.PTZ") == "yes"

    @property
    def digital_ptz(self) -> bool:
        """Support digital PTZ control."""
        return self[PROPERTIES].get("PTZ.DigitalPTZ") == "yes"  # type: ignore[attr-defined]

    @property
    def system_serialnumber(self) -> str:
        """Device serial number."""
        return self[PROPERTIES]["System.SerialNumber"]  # type: ignore

    # PTZ

    async def update_ptz(self) -> None:
        """Update PTZ group of parameters."""
        await self.update(PTZ)

    @property
    def ptz_camera_default(self) -> int:
        """PTZ default video channel.

        When camera parameter is omitted in HTTP requests.
        """
        return int(self[PTZ]["CameraDefault"])  # type: ignore

    @property
    def ptz_number_of_cameras(self) -> int:
        """Amount of video channels."""
        return int(self[PTZ]["NbrOfCameras"])  # type: ignore

    @property
    def ptz_number_of_serial_ports(self) -> int:
        """Amount of serial ports."""
        return int(self[PTZ]["NbrOfSerPorts"])  # type: ignore

    @property
    def ptz_limits(self) -> dict:
        """PTZ.Limit.L# are populated when a driver is installed on a video channel.

        Index # is the video channel number, starting on 1.
        When it is possible to obtain the current position from the driver,
        for example the current pan position, it is possible to apply limit restrictions
        to the requested operation. For instance, if an absolute pan to position 150
        is requested, but the upper limit is set to 140, the new pan position will be 140.
        This is the purpose of all but MinFieldAngle and MaxFieldAngle in this group.
        The purpose of those two parameters is to calibrate image centering.
        """
        attributes = (
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
        return self.process_dynamic_group(
            self[PTZ],  # type: ignore[arg-type]
            "Limit.L",
            attributes,
            range(1, self.ptz_number_of_cameras + 1),
        )

    @property
    def ptz_support(self) -> dict:
        """PTZ.Support.S# are populated when a driver is installed on a video channel.

        A parameter in the group has the value true if the corresponding capability
        is supported by the driver. The index # is the video channel number which starts from 1.
        An absolute operation means moving to a certain position,
        a relative operation means moving relative to the current position.
        Arguments referred to apply to PTZ control.
        """
        attributes = (
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
        return self.process_dynamic_group(
            self[PTZ],  # type: ignore[arg-type]
            "Support.S",
            attributes,
            range(1, self.ptz_number_of_cameras + 1),
        )

    @property
    def ptz_various(self) -> dict:
        """PTZ.Various.V# are populated when a driver is installed on a video channel.

        The index # is the video channel number which starts from 1.
        The group consists of several different types of parameters for the video channel.
        To distinguish the parameter types, the group is presented as
        three different categories below. The Enabled parameters determine
        if a specific feature can be controlled using ptz.cgi (see section PTZ control).
        """
        attributes = (
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
        return self.process_dynamic_group(
            self[PTZ],  # type: ignore[arg-type]
            "Various.V",
            attributes,
            range(1, self.ptz_number_of_cameras + 1),
        )

    # Stream profiles

    async def update_stream_profiles(self) -> None:
        """Update stream profiles group of parameters."""
        await self.update(STREAM_PROFILES)

    @property
    def stream_profiles_max_groups(self) -> int:
        """Maximum number of supported stream profiles."""
        return int(self.get(STREAM_PROFILES, {}).get("MaxGroups", 0))

    @property
    def stream_profiles(self) -> list:
        """Return a list of stream profiles."""
        if STREAM_PROFILES not in self:
            return []

        raw_profiles = self.process_dynamic_group(
            self[STREAM_PROFILES],  # type: ignore[arg-type]
            "S",
            ("Name", "Description", "Parameters"),
            range(self.stream_profiles_max_groups),
        )

        profiles = []

        for raw_profile in raw_profiles.values():  # Convert profile keys to lower case
            profile = dict((k.lower(), v) for k, v in raw_profile.items())
            profiles.append(StreamProfile(profile["name"], profile, self.vapix.request))

        return profiles
