"""Property parameters."""

from ...models.parameters.param_cgi import ParameterGroup
from ...models.parameters.properties import PropertyParam
from .param_handler import ParamHandler


class PropertyParameterHandler(ParamHandler[PropertyParam]):
    """Handler for property parameters."""

    parameter_group = ParameterGroup.PROPERTIES
    parameter_item = PropertyParam
