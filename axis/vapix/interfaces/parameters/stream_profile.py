"""Stream profile parameters."""

from ...models.parameters.stream_profile import StreamProfileParam
from .param_handler import ParamHandler


class StreamProfileParameterHandler(ParamHandler[StreamProfileParam]):
    """Handler for stream profile parameters."""

    parameter_group = "StreamProfile"

    def get_params(self) -> dict[str, StreamProfileParam]:
        """Retrieve brand properties."""
        if data := self.vapix.params.get_param(self.parameter_group):
            return StreamProfileParam.from_dict(data)
        return {}
