"""Stream profile parameters."""

from ...models.parameters.param_cgi import ParameterGroup
from ...models.parameters.stream_profile import StreamProfileParam
from .param_handler import ParamHandler


class StreamProfileParameterHandler(ParamHandler[StreamProfileParam]):
    """Handler for stream profile parameters."""

    parameter_group = ParameterGroup.STREAMPROFILE
    parameter_item = StreamProfileParam
