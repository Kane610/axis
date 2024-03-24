"""Parameter handler sub class of API handler.

Generalises parameter specific handling like
- Subscribing to new data
- Defining parameter group
"""

from collections.abc import Sequence
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .param_cgi import Params

from ...models.parameters.param_cgi import ParameterGroup, ParamItemT
from ..api_handler import ApiHandler


class ParamHandler(ApiHandler[ParamItemT]):
    """Base class for a map of API Items."""

    parameter_group: ParameterGroup
    parameter_item: type[ParamItemT]

    def __init__(self, param_handler: "Params") -> None:
        """Initialize API items."""
        super().__init__(param_handler.vapix)
        param_handler.subscribe(self._update_params_callback, self.parameter_group)

    @property
    def listed_in_parameters(self) -> bool:
        """Is parameter group supported."""
        return self.vapix.params.get(self.parameter_group) is not None

    async def _update(self) -> Sequence[str]:
        """Request parameter group data from parameter handler.

        This method returns after _update_params_callback has updated items.
        """
        return await self.vapix.params.request_group(self.parameter_group)

    def _update_params_callback(self, obj_id: str) -> None:
        """Update parameter data from parameter handler subscription."""
        if data := self.vapix.params.get(self.parameter_group):
            self._items.update(self.parameter_item.decode_to_dict([data]))
            self.initialized = True
