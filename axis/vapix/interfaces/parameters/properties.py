"""Property parameters."""

from ...models.parameters.properties import PropertyParam
from .param_handler import ParamHandler


class PropertyParameterHandler(ParamHandler[PropertyParam]):
    """Handler for property parameters."""

    parameter_group = "Properties"

    def get_params(self) -> dict[str, PropertyParam]:
        """Retrieve brand properties."""
        if data := self.vapix.params.get_param(self.parameter_group):
            return PropertyParam.from_dict(data)
        return {}
