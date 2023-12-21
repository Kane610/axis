"""Axis Vapix parameter management.

https://www.axis.com/vapix-library/#/subjects/t10037719/section/t10036014

Lists Brand, Image, Ports, Properties, PTZ, Stream profiles.
"""

from typing import TYPE_CHECKING, Any

from ...models.parameters.param_cgi import ParamRequest, params_to_dict
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
