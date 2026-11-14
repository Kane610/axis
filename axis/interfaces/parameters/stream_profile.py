"""Read saved video-stream settings through the VAPIX parameter API."""

from ...models.parameters.param_cgi import ParameterGroup
from ...models.parameters.stream_profile import StreamProfileParam
from .param_handler import ParamHandler


class StreamProfileParameterHandler(ParamHandler[StreamProfileParam]):
    """Keep parameter-based stream profiles available when the newer API is not loaded."""

    parameter_group = ParameterGroup.STREAMPROFILE
    parameter_item = StreamProfileParam
