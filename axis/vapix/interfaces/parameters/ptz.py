"""PTZ parameters."""

from ...models.parameters.ptz import PtzItem
from .param_handler import ParamHandler


class PtzParameterHandler(ParamHandler[PtzItem]):
    """Handler for PTZ parameters."""

    parameter_group = "PTZ"

    def get_params(self) -> dict[str, PtzItem]:
        """Retrieve brand properties."""
        if data := self.vapix.params.get_param(self.parameter_group):
            return PtzItem.from_dict(data)
        return {}
