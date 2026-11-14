"""Brand parameters from param.cgi."""

from dataclasses import dataclass
from typing import NotRequired, Self, TypedDict

from .param_cgi import ParamItem


class BrandT(TypedDict):
    """Brand and product identity fields under the param.cgi Brand group."""

    Brand: str
    ProdFullName: str
    ProdNbr: str
    ProdShortName: str
    ProdType: str
    ProdVariant: NotRequired[str]
    WebURL: str


@dataclass(frozen=True)
class BrandParam(ParamItem):
    """Normalized manufacturer, model, and product URL from the Brand group."""

    brand: str
    """Device branding."""

    product_full_name: str
    """Device product full name."""

    product_number: str
    """Device product number."""

    product_short_name: str
    """Device product short name."""

    product_type: str
    """Device product type."""

    product_variant: str
    """Device product variant."""

    web_url: str
    """Device home page URL."""

    @classmethod
    def decode(cls, data: BrandT) -> Self:
        """Convert the Brand group payload to normalized product fields."""
        return cls(
            id="brand",
            brand=data["Brand"],
            product_full_name=data["ProdFullName"],
            product_number=data["ProdNbr"],
            product_short_name=data["ProdShortName"],
            product_type=data["ProdType"],
            product_variant=data.get("ProdVariant", ""),
            web_url=data["WebURL"],
        )
