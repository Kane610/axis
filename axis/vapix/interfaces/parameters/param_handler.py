"""Parameter handler sub class of API handler.

Generalises parameter specific handling like
- Subscribing to new data
- Defining parameter group
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .param_cgi import Params

from ...models.api_discovery import ApiId
from ...models.parameters.param_cgi import ParameterGroup, ParamItemT
from ..api_handler import ApiHandler


class ParamHandler(ApiHandler[ParamItemT]):
    """Base class for a map of API Items."""

    parameter_group: ParameterGroup
    parameter_item: type[ParamItemT]
    api_id = ApiId.PARAM_CGI

    def __init__(self, param_handler: "Params") -> None:
        """Initialize API items."""
        super().__init__(param_handler.vapix)
        param_handler.subscribe(self.update_params, self.parameter_group.value)

    def supported(self) -> bool:
        """Is parameter group supported."""
        return self.vapix.params.get_param(self.parameter_group) != {}

    def get_params(self) -> dict[str, ParamItemT]:
        """Retrieve parameters from param_cgi class."""
        if data := self.vapix.params.get_param(self.parameter_group):
            return self.parameter_item.from_dict(data)
        return {}

    def update_params(self, obj_id: str) -> None:
        """Update parameter data.

        Callback from parameter handler subscription.
        """
        self._items = self.get_params()
        self.initialized = True

    async def update(self) -> None:
        """Refresh data."""
        await self.vapix.params.update_group(self.parameter_group)

    async def _api_request(self) -> dict[str, ParamItemT]:
        """Unusedd in this subclass."""
        raise NotImplementedError
