"""Axis Vapix parameter management.

https://www.axis.com/vapix-library/#/subjects/t10037719/section/t10036014

Lists Brand, Image, Ports, Properties, PTZ, Stream profiles.
"""

import asyncio
from typing import Any, Optional, Union

from .api import APIItem, APIItems
from .stream_profiles import StreamProfile

PROPERTY = "Properties.API.HTTP.Version=3"

URL = "/axis-cgi/param.cgi"
URL_GET = URL + "?action=list"
GROUP = "&group={group}"

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

    def __init__(self, request: object) -> None:
        super().__init__({}, request, URL_GET, Param)

    async def update(self, path: Optional[str] = None) -> None:
        if not path:
            path = self._path
        raw_string = await self._request("get", path)

        raw = {}
        for raw_line in raw_string.splitlines():  # root.group.parameter..=value
            split_line = raw_line.split(".", 2)  # root, group, parameter..=value
            group = ".".join(split_line[:2])  # root.group

            if group not in SUPPORTED_GROUPS:
                continue

            raw.setdefault(group, {})

            param = split_line[2].split("=", 1)  # parameter.., value
            raw[group][param[0]] = param[1]  # {root.group: {parameter..: value}}

        self.process_raw(raw)

    def process_dynamic_group(
        self, group_name: str, group_id: str, attributes: tuple
    ) -> dict:
        """Convert raw params to detailed."""
        group = {}
        for camera in list(range(1, self.ptz_number_of_cameras + 1)):
            group[camera] = {}
            for attribute in attributes:
                parameter = f"{group_id}{camera}.{attribute}"
                if parameter in self[group_name]:
                    if self[group_name][parameter] in ("true", "false"):
                        group[camera][attribute] = self[group_name][parameter] == "true"
                    elif (
                        self[group_name][parameter].isdigit()
                        or self[group_name][parameter][1:].isdigit()  # Negative values
                    ):
                        group[camera][attribute] = int(self[group_name][parameter])
                    else:
                        group[camera][attribute] = self[group_name][parameter]
        return group

    # Brand

    async def update_brand(self) -> None:
        """Update brand group of parameters."""
        await self.update(path=URL_GET + GROUP.format(group=BRAND))

    @property
    def brand(self) -> str:
        return self[BRAND]["Brand"]

    @property
    def prodfullname(self) -> str:
        return self[BRAND]["ProdFullName"]

    @property
    def prodnbr(self) -> str:
        return self[BRAND]["ProdNbr"]

    @property
    def prodshortname(self) -> str:
        return self[BRAND]["ProdShortName"]

    @property
    def prodtype(self) -> str:
        return self[BRAND]["ProdType"]

    @property
    def prodvariant(self) -> str:
        return self[BRAND]["ProdVariant"]

    @property
    def weburl(self) -> str:
        return self[BRAND]["WebURL"]

    # Image

    async def update_image(self) -> None:
        """Update image group of parameters."""
        await self.update(path=f"{URL_GET}&group={IMAGE}")

    @property
    def image_sources(self) -> list:
        """Basic image source information."""
        sources = []

        for nbr in range(self.image_nbrofviews):
            sources.append(
                {
                    "name": self[IMAGE][f"I{nbr}.Name"],
                    "source": int(self[IMAGE][f"I{nbr}.Source"]),
                }
            )

        return sources

    # Ports

    async def update_ports(self) -> None:
        """Update port groups of parameters."""
        await asyncio.gather(
            self.update(path=URL_GET + GROUP.format(group=INPUT)),
            self.update(path=URL_GET + GROUP.format(group=IOPORT)),
            self.update(path=URL_GET + GROUP.format(group=OUTPUT)),
        )

    @property
    def nbrofinput(self) -> int:
        """Match the number of configured inputs."""
        return self[INPUT]["NbrOfInputs"]

    @property
    def nbrofoutput(self) -> int:
        """Match the number of configured outputs."""
        return self[OUTPUT]["NbrOfOutputs"]

    @property
    def ports(self) -> dict:
        """Create a smaller dictionary containing all ports."""
        if IOPORT in self:
            return self[IOPORT].raw
        return {}

    # Properties

    async def update_properties(self) -> None:
        """Update properties group of parameters."""
        await self.update(path=URL_GET + GROUP.format(group=PROPERTIES))

    @property
    def api_http_version(self) -> str:
        return self[PROPERTIES]["API.HTTP.Version"]

    @property
    def api_metadata(self) -> str:
        return self[PROPERTIES]["API.Metadata.Metadata"]

    @property
    def api_metadata_version(self) -> str:
        return self[PROPERTIES]["API.Metadata.Version"]

    @property
    def api_ptz_presets_version(self) -> Union[str, bool]:
        """The index for the preset that is the device's home position at start-up.

        As of version 2.00 of the PTZ preset API Properties.API.PTZ.Presets.Version=2.00
        adding, updating and removing presets using param.cgi is no longer supported.
        """
        return self[PROPERTIES].get("API.PTZ.Presets.Version", False)

    @property
    def embedded_development(self) -> str:
        """VAPIX® Application API is supported.

        Application list.cgi supported if => 1.20.
        """
        return self.get(PROPERTIES, {}).get("EmbeddedDevelopment.Version", "0.0")

    @property
    def firmware_builddate(self) -> str:
        return self[PROPERTIES]["Firmware.BuildDate"]

    @property
    def firmware_buildnumber(self) -> str:
        return self[PROPERTIES]["Firmware.BuildNumber"]

    @property
    def firmware_version(self) -> str:
        return self[PROPERTIES]["Firmware.Version"]

    @property
    def image_format(self) -> str:
        return self[PROPERTIES].get("Image.Format")

    @property
    def image_nbrofviews(self) -> int:
        """Number of supported view areas."""
        return int(self[PROPERTIES]["Image.NbrOfViews"])

    @property
    def image_resolution(self) -> str:
        return self[PROPERTIES]["Image.Resolution"]

    @property
    def image_rotation(self) -> str:
        return self[PROPERTIES]["Image.Rotation"]

    @property
    def light_control(self) -> bool:
        return self.get(PROPERTIES, {}).get("LightControl.LightControl2") == "yes"

    @property
    def ptz(self) -> bool:
        return self.get(PROPERTIES, {}).get("PTZ.PTZ") == "yes"

    @property
    def digital_ptz(self) -> bool:
        return self[PROPERTIES].get("PTZ.DigitalPTZ") == "yes"

    @property
    def system_serialnumber(self) -> str:
        return self[PROPERTIES]["System.SerialNumber"]

    # PTZ

    async def update_ptz(self) -> None:
        """Update PTZ group of parameters."""
        await self.update(path=URL_GET + GROUP.format(group=PTZ))

    @property
    def ptz_camera_default(self) -> int:
        """The video channel used if the camera parameter is omitted in HTTP requests."""
        return int(self[PTZ]["CameraDefault"])

    @property
    def ptz_number_of_cameras(self) -> int:
        """Number of video channels."""
        return int(self[PTZ]["NbrOfCameras"])

    @property
    def ptz_number_of_serial_ports(self) -> int:
        """Number of serial ports."""
        return int(self[PTZ]["NbrOfSerPorts"])

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
        return self.process_dynamic_group(PTZ, "Limit.L", attributes)

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
        return self.process_dynamic_group(PTZ, "Support.S", attributes)

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
        return self.process_dynamic_group(PTZ, "Various.V", attributes)

    # Stream profiles

    async def update_stream_profiles(self) -> None:
        """Update stream profiles group of parameters."""
        await self.update(path=URL_GET + GROUP.format(group=STREAM_PROFILES))

    @property
    def stream_profiles_max_groups(self) -> int:
        """Maximum number of supported stream profiles."""
        return int(self.get(STREAM_PROFILES, {}).get("MaxGroups", 0))

    def stream_profiles(self) -> list:
        """Return a list of stream profiles."""
        profiles = []

        try:
            for nbr in range(self.stream_profiles_max_groups):
                raw = {
                    "name": self[STREAM_PROFILES][f"S{nbr}.Name"],
                    "description": self[STREAM_PROFILES][f"S{nbr}.Description"],
                    "parameters": self[STREAM_PROFILES][f"S{nbr}.Parameters"],
                }
                profiles.append(StreamProfile(raw["name"], raw, self._request))
        except KeyError:
            pass

        return profiles


class Param(APIItem):
    """Parameter group."""

    def __contains__(self, obj_id: str) -> bool:
        """Evaluate object membership to parameter group."""
        return obj_id in self.raw

    def get(self, obj_id: str, default: Optional[Any] = None) -> Any:
        """Get object if stored in raw else return default."""
        return self.raw.get(obj_id, default)

    def __getitem__(self, obj_id: str) -> Any:
        """Return Param[obj_id]."""
        return self.raw[obj_id]
