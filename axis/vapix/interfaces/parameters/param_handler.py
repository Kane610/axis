"""Parameter handler sub class of API handler.

Generalises parameter specific handling like
- Subscribing to new data
- Defining parameter group
"""

from abc import abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .param_cgi import Params

from ...models.api import ApiItemT
from ...models.api_discovery import ApiId
from ..api_handler import ApiHandler


class ParamHandler(ApiHandler[ApiItemT]):
    """Base class for a map of API Items."""

    parameter_group: str
    api_id = ApiId.PARAM_CGI

    def __init__(self, param_handler: "Params") -> None:
        """Initialize API items."""
        super().__init__(param_handler.vapix)
        param_handler.subscribe(self.update_params, self.parameter_group)

    @abstractmethod
    def get_params(self) -> dict[str, ApiItemT]:
        """Retrieve parameters from param_cgi class."""

    def update_params(self, obj_id: str) -> None:
        """Update parameter data.

        Callback from parameter handler subscription.
        """
        self._items = self.get_params()

    async def _api_request(self) -> dict[str, ApiItemT]:
        """Get API data method defined by subclass."""
        await self.vapix.params.update(self.parameter_group)
        return self.get_params()
