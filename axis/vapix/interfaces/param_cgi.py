"""Axis Vapix parameter management.

https://www.axis.com/vapix-library/#/subjects/t10037719/section/t10036014

Lists Brand, Image, Ports, Properties, PTZ, Stream profiles.
"""

import asyncio
from typing import Any, Dict, cast

from ..models.param_cgi import (
    BrandParam,
    BrandT,
    ImageParam,
    Param,
    PropertyParam,
    StreamProfileParam,
    params_to_dict,
)
from ..models.port_cgi import GetPortsRequest, ListInputRequest, ListOutputRequest
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

    # Brand

    async def update_brand(self) -> None:
        """Update brand group of parameters."""
        await self.update(BRAND)

    @property
    def brand(self) -> BrandParam:
        """Provide brand parameters."""
        brand = ""
        for k, v in self[BRAND].raw.items():
            brand += f"root.Brand.{k}={v}\n"
        brand_params: BrandT = (
            params_to_dict(brand, "root.Brand").get("root", {}).get("Brand", {})
        )
        return BrandParam.decode(brand_params)

    # Image

    async def update_image(self) -> None:
        """Update image group of parameters."""
        await self.update(IMAGE)

    @property
    def image_params(self) -> ImageParam:
        """Provide image parameters."""
        return ImageParam.decode(self[IMAGE].raw)

    @property
    def image_sources(self) -> dict[str, Any]:
        """Image source information."""
        if IMAGE not in self:
            return {}

        image = ""
        for k, v in self[IMAGE].raw.items():
            image += f"root.Image.{k}={v}\n"
        return params_to_dict(image, "root.Image").get("root", {}).get("Image", {})

    # Ports

    async def update_ports(self) -> None:
        """Update port groups of parameters."""
        bytes_list = await asyncio.gather(
            self.vapix.new_request(ListInputRequest()),
            self.vapix.new_request(GetPortsRequest()),
            self.vapix.new_request(ListOutputRequest()),
        )
        for bytes_data in bytes_list:
            self.process_raw(bytes_data.decode())

    @property
    def nbrofinput(self) -> int:
        """Match the number of configured inputs."""
        return int(self[INPUT]["NbrOfInputs"])  # type: ignore

    @property
    def nbrofoutput(self) -> int:
        """Match the number of configured outputs."""
        return int(self[OUTPUT]["NbrOfOutputs"])  # type: ignore

    @property
    def ports(self) -> bytes:
        """Create a smaller dictionary containing all ports."""
        if IOPORT not in self:
            return b""

        io_port = ""
        for k, v in self[IOPORT].raw.items():
            io_port += f"root.IOPort.{k}={v}\n"
        return io_port.encode()

    # Properties

    async def update_properties(self) -> None:
        """Update properties group of parameters."""
        await self.update(PROPERTIES)

    @property
    def property_params(self) -> PropertyParam:
        """Provide property parameters."""
        return PropertyParam.decode(self[PROPERTIES].raw)

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
    def api_ptz_presets_version(self) -> bool | str:
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
    def ptz_data(self) -> bytes:
        """Create a smaller dictionary containing all PTZ information."""
        if PTZ not in self:
            return b""

        ptz = ""
        for k, v in self[PTZ].raw.items():
            ptz += f"root.PTZ.{k}={v}\n"
        return ptz.encode()

    # Stream profiles

    async def update_stream_profiles(self) -> None:
        """Update stream profiles group of parameters."""
        await self.update(STREAM_PROFILES)

    @property
    def stream_profiles_params(self) -> StreamProfileParam:
        """Provide stream profiles parameters."""
        return StreamProfileParam.decode(
            cast(dict[str, str], self[STREAM_PROFILES].raw)
        )

    @property
    def stream_profiles_max_groups(self) -> int:
        """Maximum number of supported stream profiles."""
        return int(self.get(STREAM_PROFILES, {}).get("MaxGroups", 0))

    @property
    def stream_profiles(self) -> list[StreamProfile]:
        """Return a list of stream profiles."""
        if STREAM_PROFILES not in self:
            return []

        stream_profiles = ""
        for k, v in self[STREAM_PROFILES].raw.items():
            stream_profiles += f"root.StreamProfile.{k}={v}\n"
        data = (
            params_to_dict(stream_profiles, "root.StreamProfile")
            .get("root", {})
            .get("StreamProfile", {})
        )
        profiles = dict(data)
        del profiles["MaxGroups"]

        return [
            StreamProfile(
                id=str(profile["Name"]),
                description=str(profile["Description"]),
                parameters=str(profile["Parameters"]),
            )
            for profile in profiles.values()
        ]
