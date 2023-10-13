"""Axis Vapix parameter management.

https://www.axis.com/vapix-library/#/subjects/t10037719/section/t10036014

Lists Brand, Image, Ports, Properties, PTZ, Stream profiles.
"""
from dataclasses import dataclass
from typing import Any

from typing_extensions import NotRequired, Self, TypedDict

from .api import APIItem, ApiItem


class BrandT(TypedDict):
    """Represent a brand object."""

    Brand: str
    ProdFullName: str
    ProdNbr: str
    ProdShortName: str
    ProdType: str
    ProdVariant: str
    WebURL: str


class Param(APIItem):
    """Parameter group."""

    def __contains__(self, obj_id: str) -> bool:
        """Evaluate object membership to parameter group."""
        return obj_id in self.raw

    def get(self, obj_id: str, default: Any | None = None) -> Any:
        """Get object if stored in raw else return default."""
        return self.raw.get(obj_id, default)

    def __getitem__(self, obj_id: str) -> Any:
        """Return Param[obj_id]."""
        return self.raw[obj_id]


@dataclass
class BrandParam(ApiItem):
    """Brand parameters."""

    brand: str
    prodfullname: str
    prodnbr: str
    prodshortname: str
    prodtype: str
    prodvariant: str
    weburl: str

    @classmethod
    def decode(cls, data: BrandT) -> Self:
        """Decode dictionary to class object."""
        return cls(
            id="brand",
            brand=data["Brand"],
            prodfullname=data["ProdFullName"],
            prodnbr=data["ProdNbr"],
            prodshortname=data["ProdShortName"],
            prodtype=data["ProdType"],
            prodvariant=data["ProdVariant"],
            weburl=data["WebURL"],
        )
