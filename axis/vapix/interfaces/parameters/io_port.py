"""I/O port parameters."""

from ...models.parameters.io_port import Port
from .param_handler import ParamHandler


class IOPortParameterHandler(ParamHandler[Port]):
    """Handler for I/O port parameters."""

    parameter_group = "IOPort"

    def get_params(self) -> dict[str, Port]:
        """Retrieve I/O port parameters."""
        if data := self.vapix.params.get_param(self.parameter_group):
            return Port.from_dict(data)
        return {}
