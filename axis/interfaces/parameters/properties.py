"""Read firmware information and feature-support flags through VAPIX param.cgi."""

from ...models.parameters.param_cgi import ParameterGroup
from ...models.parameters.properties import PropertyParam
from .param_handler import ParamHandler


class PropertyParameterHandler(ParamHandler[PropertyParam]):
    """Keep device properties available for firmware and API support checks."""

    parameter_group = ParameterGroup.PROPERTIES
    parameter_item = PropertyParam
