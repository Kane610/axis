"""Axis Vapix parameter management.

https://www.axis.com/vapix-library/#/subjects/t10037719/section/t10036014

Lists Brand, Image, Ports, Properties, PTZ, Stream profiles.
"""

import asyncio
from typing import Any, cast

from ..models.param_cgi import (
    BrandParam,
    BrandT,
    GetParamsRequest,
    ImageParam,
    PropertyParam,
    StreamProfileParam,
    params_to_dict,
)
from ..models.port_cgi import GetPortsRequest, ListInputRequest, ListOutputRequest
from ..models.stream_profile import StreamProfile
from .api_handler import ApiHandler

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


class Params(ApiHandler[Any]):
    """Represents all parameters of param.cgi."""

    async def _api_request(self) -> dict[str, Any]:
        """Refresh data."""
        await self.update()
        return self._items
        # data = await self.update_group()
        # params = params_to_dict(data)
        # self._items.update(data)

    async def update(self, group: str = "") -> None:
        """Refresh data."""
        if group != "":
            group = f"root.{group}"
        bytes_data = await self.vapix.new_request(GetParamsRequest(group))
        data = params_to_dict(bytes_data.decode())
        self._items.update(data)

    def get_param(self, group: str) -> dict[str, Any]:
        """Get parameter group."""
        return self._items.get("root", {}).get(group, {})

    # Brand

    async def update_brand(self) -> None:
        """Update brand group of parameters."""
        await self.update("Brand")

    @property
    def brand(self) -> BrandParam:
        """Provide brand parameters."""
        return BrandParam.decode(cast(BrandT, self.get_param("Brand")))

    # Image

    async def update_image(self) -> None:
        """Update image group of parameters."""
        await self.update("Image")

    @property
    def image_params(self) -> ImageParam:
        """Provide image parameters."""
        return ImageParam.decode(self.get_param("Image"))

    @property
    def image_sources(self) -> dict[str, Any]:
        """Image source information."""
        return self.get_param("Image")

    # Ports

    async def update_ports(self) -> None:
        """Update port groups of parameters."""
        bytes_list = await asyncio.gather(
            self.vapix.new_request(ListInputRequest()),
            self.vapix.new_request(GetPortsRequest()),
            self.vapix.new_request(ListOutputRequest()),
        )
        data = params_to_dict(b"\n".join(bytes_list).decode())
        self._items.update(data)

    @property
    def nbrofinput(self) -> int:
        """Match the number of configured inputs."""
        return self.get_param("Input").get("NbrOfInputs", 0)

    @property
    def nbrofoutput(self) -> int:
        """Match the number of configured outputs."""
        return self.get_param("Output").get("NbrOfOutputs", 0)

    @property
    def ports(self) -> dict[str, Any]:
        """Create a smaller dictionary containing all ports."""
        return self.get_param("IOPort")

    # Properties

    async def update_properties(self) -> None:
        """Update properties group of parameters."""
        await self.update("Properties")

    @property
    def properties(self) -> PropertyParam:
        """Provide property parameters."""
        return PropertyParam.decode(self.get_param("Properties"))

    # PTZ

    async def update_ptz(self) -> None:
        """Update PTZ group of parameters."""
        await self.update("PTZ")

    @property
    def ptz_data(self) -> dict[str, Any]:
        """Create a smaller dictionary containing all PTZ information."""
        return self.get_param("PTZ")

    # Stream profiles

    async def update_stream_profiles(self) -> None:
        """Update stream profiles group of parameters."""
        await self.update("StreamProfile")

    @property
    def stream_profiles_params(self) -> StreamProfileParam:
        """Provide stream profiles parameters."""
        return StreamProfileParam.decode(self.get_param("StreamProfile"))

    @property
    def stream_profiles_max_groups(self) -> int:
        """Maximum number of supported stream profiles."""
        return self.get_param("StreamProfile").get("MaxGroups", 0)

    @property
    def stream_profiles(self) -> list[StreamProfile]:
        """Return a list of stream profiles."""
        if not (data := self.get_param("StreamProfile")):
            return []

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
