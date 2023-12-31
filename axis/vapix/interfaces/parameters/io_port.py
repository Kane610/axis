"""I/O port parameters."""

from ...models.parameters.io_port import Port
from ...models.parameters.param_cgi import ParameterGroup
from .param_handler import ParamHandler


class IOPortParameterHandler(ParamHandler[Port]):
    """Handler for I/O port parameters."""

    parameter_group = ParameterGroup.IOPORT

    def get_params(self) -> dict[str, Port]:
        """Retrieve I/O port parameters."""
        if data := self.vapix.params.get_param(self.parameter_group):
            return Port.from_dict(data)
        return {}
