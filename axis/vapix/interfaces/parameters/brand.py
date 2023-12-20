"""Brand parameters."""

from typing import cast

from ...models.parameters.brand import BrandParam, BrandT
from .param_handler import ParamHandler


class BrandParameterHandler(ParamHandler[BrandParam]):
    """Handler for brand parameters."""

    parameter_group = "Brand"

    def get_params(self) -> dict[str, BrandParam]:
        """Retrieve brand properties."""
        params = {}
        if data := self.vapix.params.get_param(self.parameter_group):
            params["0"] = BrandParam.decode(cast(BrandT, data))
        return params
