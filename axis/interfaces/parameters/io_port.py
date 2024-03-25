"""I/O port parameters."""

from ...models.parameters.io_port import IOPortParam
from ...models.parameters.param_cgi import ParameterGroup
from .param_handler import ParamHandler


class IOPortParameterHandler(ParamHandler[IOPortParam]):
    """Handler for I/O port parameters."""

    parameter_group = ParameterGroup.IOPORT
    parameter_item = IOPortParam
