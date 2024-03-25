"""Brand parameters."""

from ...models.parameters.brand import BrandParam
from ...models.parameters.param_cgi import ParameterGroup
from .param_handler import ParamHandler


class BrandParameterHandler(ParamHandler[BrandParam]):
    """Handler for brand parameters."""

    parameter_group = ParameterGroup.BRAND
    parameter_item = BrandParam
