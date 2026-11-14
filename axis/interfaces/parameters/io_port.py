"""Read digital input and output port settings through the VAPIX parameter API."""

from ...models.parameters.io_port import IOPortParam
from ...models.parameters.param_cgi import ParameterGroup
from .param_handler import ParamHandler


class IOPortParameterHandler(ParamHandler[IOPortParam]):
    """Keep decoded I/O port settings available as cached parameter data."""

    parameter_group = ParameterGroup.IOPORT
    parameter_item = IOPortParam
