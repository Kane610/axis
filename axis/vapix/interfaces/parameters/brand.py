"""Brand parameters."""

from ...models.parameters.brand import BrandParam
from ...models.parameters.param_cgi import ParameterGroup
from .param_handler import ParamHandler


class BrandParameterHandler(ParamHandler[BrandParam]):
    """Handler for brand parameters."""

    parameter_group = ParameterGroup.BRAND

    def get_params(self) -> dict[str, BrandParam]:
        """Retrieve brand properties."""
        if data := self.vapix.params.get_param(self.parameter_group):
            return BrandParam.from_dict(data)
        return {}
