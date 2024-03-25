"""PTZ parameters."""

from ...models.parameters.param_cgi import ParameterGroup
from ...models.parameters.ptz import PtzParam
from .param_handler import ParamHandler


class PtzParameterHandler(ParamHandler[PtzParam]):
    """Handler for PTZ parameters."""

    parameter_group = ParameterGroup.PTZ
    parameter_item = PtzParam
