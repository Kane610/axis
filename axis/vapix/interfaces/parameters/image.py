"""Image parameters."""

from ...models.parameters.image import ImageParam
from ...models.parameters.param_cgi import ParameterGroup
from .param_handler import ParamHandler


class ImageParameterHandler(ParamHandler[ImageParam]):
    """Handler for image parameters."""

    parameter_group = ParameterGroup.IMAGE
    parameter_item = ImageParam
