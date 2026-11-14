"""Read camera image settings through the VAPIX parameter API."""

from ...models.parameters.image import ImageParam
from ...models.parameters.param_cgi import ParameterGroup
from .param_handler import ParamHandler


class ImageParameterHandler(ParamHandler[ImageParam]):
    """Keep decoded image settings available as cached parameter data."""

    parameter_group = ParameterGroup.IMAGE
    parameter_item = ImageParam
