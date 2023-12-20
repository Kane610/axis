"""Axis Vapix parameter management.

https://www.axis.com/vapix-library/#/subjects/t10037719/section/t10036014

Lists Brand, Image, Ports, Properties, PTZ, Stream profiles.
"""

from typing import TYPE_CHECKING, Any

from ...models.parameters.brand import BrandParam
from ...models.parameters.image import ImageParam
from ...models.parameters.param_cgi import ParamRequest, params_to_dict
from ...models.parameters.properties import PropertyParam
from ...models.parameters.stream_profile import StreamProfileParam
from ...models.stream_profile import StreamProfile
from ..api_handler import ApiHandler
from .brand import BrandParameterHandler
from .image import ImageParameterHandler
from .io_port import IOPortParameterHandler
from .properties import PropertyParameterHandler
from .ptz import PtzParameterHandler
from .stream_profile import StreamProfileParameterHandler

if TYPE_CHECKING:
    from ...vapix import Vapix

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

    def __init__(self, vapix: "Vapix") -> None:
        """Initialize API items."""
        super().__init__(vapix)

        self.brand_handler = BrandParameterHandler(self)
        self.image_handler = ImageParameterHandler(self)
        self.io_port_handler = IOPortParameterHandler(self)
        self.property_handler = PropertyParameterHandler(self)
        self.ptz_handler = PtzParameterHandler(self)
        self.stream_profile_handler = StreamProfileParameterHandler(self)

    async def _api_request(self) -> dict[str, Any]:
        """Refresh data."""
        await self.update()
        return self._items
        # data = await self.update_group()
        # params = params_to_dict(data)
        # self._items.update(data)

    async def update(self, group: str = "") -> None:
        """Refresh data."""
        group = "" if group == "" or group.startswith("root.") else f"root.{group}"
        bytes_data = await self.vapix.new_request(ParamRequest(group))
        data = params_to_dict(bytes_data.decode())
        root = self._items.setdefault("root", {})
        if objects := data.get("root"):
            root.update(objects)
            for obj_id in objects.keys():
                self.signal_subscribers(obj_id)

    def get_param(self, group: str) -> dict[str, Any]:
        """Get parameter group."""
        return self._items.get("root", {}).get(group, {})

    # Brand

    async def update_brand(self) -> None:
        """Update brand group of parameters."""
        await self.brand_handler.update()

    @property
    def brand(self) -> BrandParam | None:
        """Provide brand parameters."""
        return self.brand_handler.get_params().get("0")

    # Image

    async def update_image(self) -> None:
        """Update image group of parameters."""
        await self.image_handler.update()

    @property
    def image_params(self) -> ImageParam:
        """Provide image parameters."""
        return self.image_handler.get_params().get("0")
        return ImageParam.decode(self.get_param("Image"))

    @property
    def image_sources(self) -> dict[str, Any]:
        """Image source information."""
        data = {}
        if params := self.image_handler.get_params().get("0"):
            data = params.data
        return data

    # Properties

    async def update_properties(self) -> None:
        """Update properties group of parameters."""
        await self.property_handler.update()
        # await self.update("Properties")

    @property
    def properties(self) -> PropertyParam:
        """Provide property parameters."""
        return self.property_handler.get_params().get("0")
        # data = {}
        # if params := self.property_handler.get_params().get("0"):
        #     data = params
        # return data
        # return PropertyParam.decode(self.get_param("Properties"))

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
        await self.stream_profile_handler.update()

    @property
    def stream_profiles_params(self) -> StreamProfileParam:
        """Provide stream profiles parameters."""
        return self.stream_profile_handler.get_params().get("0")

    @property
    def stream_profiles_max_groups(self) -> int:
        """Maximum number of supported stream profiles."""
        return self.stream_profile_handler.get_params().get("0").max_groups

    @property
    def stream_profiles(self) -> list[StreamProfile]:
        """Return a list of stream profiles."""
        return self.stream_profile_handler.get_params().get("0").stream_profiles
