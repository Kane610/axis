"""Read device product identity from the Brand parameter group in VAPIX param.cgi."""

from ...models.parameters.brand import BrandParam
from ...models.parameters.param_cgi import ParameterGroup
from .param_handler import ParamHandler


class BrandParameterHandler(ParamHandler[BrandParam]):
    """Keep decoded product identity available as cached parameter data."""

    parameter_group = ParameterGroup.BRAND
    parameter_item = BrandParam
