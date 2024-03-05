"""Brand parameters from param.cgi."""

from dataclasses import dataclass
from typing import NotRequired, Self

from typing_extensions import TypedDict

from .param_cgi import ParamItem


class BrandT(TypedDict):
    """Represent a brand object."""

    Brand: str
    ProdFullName: str
    ProdNbr: str
    ProdShortName: str
    ProdType: str
    ProdVariant: NotRequired[str]
    WebURL: str


@dataclass(frozen=True)
class BrandParam(ParamItem):
    """Brand parameters."""

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
        """Decode dictionary to class object."""
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
