"""Image parameters."""

from ...models.parameters.image import ImageParam
from .param_handler import ParamHandler


class ImageParameterHandler(ParamHandler[ImageParam]):
    """Handler for image parameters."""

    parameter_group = "Image"

    def get_params(self) -> dict[str, ImageParam]:
        """Retrieve brand properties."""
        params = {}
        if data := self.vapix.params.get_param(self.parameter_group):
            params["0"] = ImageParam.decode(data)
        return params
