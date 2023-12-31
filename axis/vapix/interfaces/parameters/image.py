"""Image parameters."""

from ...models.parameters.image import ImageParam
from ...models.parameters.param_cgi import ParameterGroup
from .param_handler import ParamHandler


class ImageParameterHandler(ParamHandler[ImageParam]):
    """Handler for image parameters."""

    parameter_group = ParameterGroup.IMAGE

    def get_params(self) -> dict[str, ImageParam]:
        """Retrieve brand properties."""
        if data := self.vapix.params.get_param(self.parameter_group):
            return ImageParam.from_dict(data)
        return {}
