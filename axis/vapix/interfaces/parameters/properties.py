"""Property parameters."""

from ...models.parameters.properties import PropertyParam
from .param_handler import ParamHandler


class PropertyParameterHandler(ParamHandler[PropertyParam]):
    """Handler for property parameters."""

    parameter_group = "Properties"

    def get_params(self) -> dict[str, PropertyParam]:
        """Retrieve brand properties."""
        params = {}
        if data := self.vapix.params.get_param(self.parameter_group):
            params["0"] = PropertyParam.decode(data)
        return params
