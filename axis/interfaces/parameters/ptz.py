"""Read pan, tilt, and zoom settings through the VAPIX parameter API."""

from ...models.parameters.param_cgi import ParameterGroup
from ...models.parameters.ptz import PtzParam
from .param_handler import ParamHandler


class PtzParameterHandler(ParamHandler[PtzParam]):
    """Keep decoded PTZ settings available as cached parameter data."""

    parameter_group = ParameterGroup.PTZ
    parameter_item = PtzParam
