"""Axis Vapix parameter management."""

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

from ...models.api_discovery import ApiId
from ...models.parameters.param_cgi import ParameterGroup, ParamRequest, params_to_dict
from ..api_handler import ApiHandler
from .brand import BrandParameterHandler
from .image import ImageParameterHandler
from .io_port import IOPortParameterHandler
from .properties import PropertyParameterHandler
from .ptz import PtzParameterHandler
from .stream_profile import StreamProfileParameterHandler

if TYPE_CHECKING:
    from ..vapix import Vapix


class Params(ApiHandler[Any]):
    """Represents all parameters of param.cgi."""

    api_id = ApiId.PARAM_CGI

    def __init__(self, vapix: "Vapix") -> None:
        """Initialize parameter classes."""
        super().__init__(vapix)

        self.brand_handler = BrandParameterHandler(self)
        self.image_handler = ImageParameterHandler(self)
        self.io_port_handler = IOPortParameterHandler(self)
        self.property_handler = PropertyParameterHandler(self)
        self.ptz_handler = PtzParameterHandler(self)
        self.stream_profile_handler = StreamProfileParameterHandler(self)

    async def _api_request(self, group: ParameterGroup | None = None) -> dict[str, Any]:
        """Fetch parameter data and convert it into a dictionary."""
        bytes_data = await self.vapix.api_request(ParamRequest(group))
        return params_to_dict(bytes_data.decode()).get("root") or {}

    async def _update(self, group: ParameterGroup | None = None) -> Sequence[str]:
        """Request parameter data and update items."""
        objects = await self._api_request(group)
        self._items.update(objects)
        self.initialized = True
        return list(self.keys())

    async def request_group(self, group: ParameterGroup | None = None) -> Sequence[str]:
        """Request parameter data and signal subscribers."""
        if obj_ids := await self._update(group):
            for obj_id in obj_ids:
                self.signal_subscribers(obj_id)
        return obj_ids
