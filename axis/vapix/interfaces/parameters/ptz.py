"""PTZ parameters."""

from ...models.parameters.ptz import GetPtzResponse, PtzItem
from .param_handler import ParamHandler


class PtzParameterHandler(ParamHandler[PtzItem]):
    """Handler for PTZ parameters."""

    parameter_group = "PTZ"

    def get_params(self) -> dict[str, PtzItem]:
        """Retrieve brand properties."""
        params = {}
        if data := self.vapix.params.get_param(self.parameter_group):
            params.update(GetPtzResponse.from_dict(data).data)
        return params
