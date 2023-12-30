"""Axis Vapix parameter management."""

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
        """Refresh data.

        Not used.
        """
        return {}

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
