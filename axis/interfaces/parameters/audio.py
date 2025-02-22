"""Audio parameters."""

from ...models.parameters.audio import AudioParam
from ...models.parameters.param_cgi import ParameterGroup
from .param_handler import ParamHandler


class AudioParameterHandler(ParamHandler[AudioParam]):
    """Handler for audio parameters."""

    parameter_group = ParameterGroup.AUDIO
    parameter_item = AudioParam
