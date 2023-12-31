"""Property parameters."""

from ...models.parameters.param_cgi import ParameterGroup
from ...models.parameters.properties import PropertyParam
from .param_handler import ParamHandler


class PropertyParameterHandler(ParamHandler[PropertyParam]):
    """Handler for property parameters."""

    parameter_group = ParameterGroup.PROPERTIES

    def get_params(self) -> dict[str, PropertyParam]:
        """Retrieve brand properties."""
        if data := self.vapix.params.get_param(self.parameter_group):
            return PropertyParam.from_dict(data)
        return {}
