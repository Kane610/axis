"""Axis Vapix parameter management.

https://www.axis.com/vapix-library/#/subjects/t10037719/section/t10036014

Lists Brand, Ports, Properties, Stream profiles.
"""

import asyncio

from .api import APIItem, APIItems
from .stream_profiles import StreamProfile

PROPERTY = "Properties.API.HTTP.Version=3"

URL = "/axis-cgi/param.cgi"
URL_GET = URL + "?action=list"
GROUP = "&group={group}"

BRAND = "root.Brand"
INPUT = "root.Input"
IOPORT = "root.IOPort"
OUTPUT = "root.Output"
PROPERTIES = "root.Properties"
PTZ = "root.PTZ"
STREAM_PROFILES = "root.StreamProfile"


class Params(APIItems):
    """Represents all parameters of param.cgi."""

    def __init__(self, request: object) -> None:
        super().__init__("", request, URL_GET, APIItem)

    def process_raw(self, raw: str) -> None:
        """Pre-process raw string.

        Prepare parameters to work with APIItems.
        """
        raw_params = dict(group.split("=", 1) for group in raw.splitlines())

        super().process_raw(raw_params)

    def process_dynamic_group(self, group_id, attributes):
        """Convert raw params to detailed """
        group = {}
        for camera in list(range(1, self.ptz_number_of_cameras + 1)):
            group[camera] = {}
            for attribute in attributes:
                parameter = f"{group_id}{camera}.{attribute}"
                if parameter in self:
                    if self[parameter].raw in ("true", "false"):
                        group[camera][attribute] = self[parameter].raw == "true"
                    elif (
                        self[parameter].raw.isdigit()
                        or self[parameter].raw[1:].isdigit()  # Negative values
                    ):
                        group[camera][attribute] = int(self[parameter].raw)
                    else:
                        group[camera][attribute] = self[parameter].raw
        return group

    # Brand

    async def update_brand(self) -> None:
        """Update brand group of parameters."""
        await self.update(path=URL_GET + GROUP.format(group=BRAND))

    @property
    def brand(self) -> str:
        return self[f"{BRAND}.Brand"].raw

    @property
    def prodfullname(self) -> str:
        return self[f"{BRAND}.ProdFullName"].raw

    @property
    def prodnbr(self) -> str:
        return self[f"{BRAND}.ProdNbr"].raw

    @property
    def prodshortname(self) -> str:
        return self[f"{BRAND}.ProdShortName"].raw

    @property
    def prodtype(self) -> str:
        return self[f"{BRAND}.ProdType"].raw

    @property
    def prodvariant(self) -> str:
        return self[f"{BRAND}.ProdVariant"].raw

    @property
    def weburl(self) -> str:
        return self[f"{BRAND}.WebURL"].raw

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
        return self[f"{INPUT}.NbrOfInputs"].raw

    @property
    def nbrofoutput(self) -> int:
        """Match the number of configured outputs."""
        return self[f"{OUTPUT}.NbrOfOutputs"].raw

    @property
    def ports(self) -> dict:
        """Create a smaller dictionary containing all ports."""
        return {param: self[param].raw for param in self if param.startswith(IOPORT)}

    # Properties

    async def update_properties(self) -> None:
        """Update properties group of parameters."""
        await self.update(path=URL_GET + GROUP.format(group=PROPERTIES))

    @property
    def api_http_version(self) -> str:
        return self[f"{PROPERTIES}.API.HTTP.Version"].raw

    @property
    def api_metadata(self) -> str:
        return self[f"{PROPERTIES}.API.Metadata.Metadata"].raw

    @property
    def api_metadata_version(self) -> str:
        return self[f"{PROPERTIES}.API.Metadata.Version"].raw

    @property
    def api_ptz_presets_version(self) -> bool:
        """The index for the preset that is the device's home position at start-up.

        As of version 2.00 of the PTZ preset API Properties.API.PTZ.Presets.Version=2.00
        adding, updating and removing presets using param.cgi is no longer supported.
        """
        presets_version = f"{PROPERTIES}.API.PTZ.Presets.Version"
        if presets_version not in self:
            return False
        return self[presets_version].raw

    @property
    def embedded_development(self) -> str:
        """VAPIX® Application API is supported.

        Application list.cgi supported if => 1.20.
        """
        return self[f"{PROPERTIES}.EmbeddedDevelopment.Version"].raw

    @property
    def firmware_builddate(self) -> str:
        return self[f"{PROPERTIES}.Firmware.BuildDate"].raw

    @property
    def firmware_buildnumber(self) -> str:
        return self[f"{PROPERTIES}.Firmware.BuildNumber"].raw

    @property
    def firmware_version(self) -> str:
        return self[f"{PROPERTIES}.Firmware.Version"].raw

    @property
    def image_format(self) -> str:
        image_format = f"{PROPERTIES}.Image.Format"
        if image_format not in self:
            return None
        return self[image_format].raw

    @property
    def image_nbrofviews(self) -> str:
        return self[f"{PROPERTIES}.Image.NbrOfViews"].raw

    @property
    def image_resolution(self) -> str:
        return self[f"{PROPERTIES}.Image.Resolution"].raw

    @property
    def image_rotation(self) -> str:
        return self[f"{PROPERTIES}.Image.Rotation"].raw

    @property
    def light_control(self) -> bool:
        light_control = f"{PROPERTIES}.LightControl.LightControl2"
        if light_control not in self:
            return False
        return self[light_control].raw == "yes"

    @property
    def ptz(self) -> bool:
        ptz_support = f"{PROPERTIES}.PTZ.PTZ"
        if ptz_support not in self:
            return False
        return self[ptz_support].raw == "yes"

    @property
    def digital_ptz(self) -> bool:
        digital_ptz_support = f"{PROPERTIES}.PTZ.DigitalPTZ"
        if digital_ptz_support not in self:
            return False
        return self[digital_ptz_support].raw == "yes"

    @property
    def system_serialnumber(self) -> str:
        return self[f"{PROPERTIES}.System.SerialNumber"].raw

    # PTZ

    async def update_ptz(self) -> None:
        """Update PTZ group of parameters."""
        await self.update(path=URL_GET + GROUP.format(group=PTZ))

    @property
    def ptz_camera_default(self) -> int:
        """The video channel used if the camera parameter is omitted in HTTP requests."""
        return int(self[f"{PTZ}.CameraDefault"].raw)

    @property
    def ptz_number_of_cameras(self) -> int:
        """Number of video channels."""
        return int(self[f"{PTZ}.NbrOfCameras"].raw)

    @property
    def ptz_number_of_serial_ports(self) -> int:
        """Number of serial ports."""
        return int(self[f"{PTZ}.NbrOfSerPorts"].raw)

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
        return self.process_dynamic_group(f"{PTZ}.Limit.L", attributes)

    @property
    def ptz_support(self):
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
        return self.process_dynamic_group(f"{PTZ}.Support.S", attributes)

    @property
    def ptz_various(self):
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
        return self.process_dynamic_group(f"{PTZ}.Various.V", attributes)

    # Stream profiles

    async def update_stream_profiles(self) -> None:
        """Update stream profiles group of parameters."""
        await self.update(path=URL_GET + GROUP.format(group=STREAM_PROFILES))

    @property
    def stream_profiles_max_groups(self) -> int:
        """Maximum number of supported stream profiles."""
        if f"{STREAM_PROFILES}.MaxGroups" in self:
            return int(self[f"{STREAM_PROFILES}.MaxGroups"].raw)
        return 0

    def stream_profiles(self) -> list:
        """Return a list of stream profiles."""
        profiles = []

        try:
            for nbr in range(self.stream_profiles_max_groups):
                raw = {
                    "name": self[f"{STREAM_PROFILES}.S{nbr}.Name"].raw,
                    "description": self[f"{STREAM_PROFILES}.S{nbr}.Description"].raw,
                    "parameters": self[f"{STREAM_PROFILES}.S{nbr}.Parameters"].raw,
                }
                profiles.append(StreamProfile(raw["name"], raw, self._request))
        except KeyError:
            pass

        return profiles
