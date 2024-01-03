"""Axis Vapix parameter management."""

from typing import TYPE_CHECKING, Any

from ...models.parameters.param_cgi import ParameterGroup, ParamRequest, params_to_dict
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

    def get_param(self, group: ParameterGroup) -> dict[str, Any]:
        """Get parameter group."""
        return self._items.get("root", {}).get(group.value, {})

    async def update_group(self, group: ParameterGroup | None = None) -> None:
        """Refresh data."""
        bytes_data = await self.vapix.new_request(ParamRequest(group))
        data = params_to_dict(bytes_data.decode())

        root = self._items.setdefault("root", {})
        if objects := data.get("root"):
            root.update(objects)
            self.initialized = True

            for obj_id in objects.keys():
                self.signal_subscribers(obj_id)

    async def update(self) -> None:
        """Refresh data."""
        await self.update_group()

    async def _api_request(self) -> dict[str, Any]:
        """Unusedd in this subclass."""
        raise NotImplementedError
