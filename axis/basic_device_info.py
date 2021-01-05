"""Basic Device Info api.

AXIS Basic device information API can be used to retrieve simple information about the product.
This information is used to identify basic properties of the product.
"""

from typing import Any, Optional

import attr

from .api import APIItem, APIItems, Body

URL = "/axis-cgi/basicdeviceinfo.cgi"

API_DISCOVERY_ID = "basic-device-info"
API_VERSION = "1.1"


class BasicDeviceInfo(APIItems):
    """Basic device information for Axis devices."""

    def __init__(self, request: object) -> None:
        super().__init__({}, request, URL, APIItem)

    def __getitem__(self, obj_id: str) -> Optional[Any]:
        """self["string"] will return self._item["string"].raw."""
        return self._items[obj_id].raw

    async def update(self) -> None:
        raw = await self.get_all_properties()
        self.process_raw(raw)

    @staticmethod
    def pre_process_raw(raw: dict) -> dict:
        """Return a dictionary of device information."""
        return raw.get("data", {}).get("propertyList", {})

    async def get_all_properties(self) -> dict:
        """List all properties of basic device info."""
        return await self._request(
            "post",
            URL,
            json=attr.asdict(
                Body("getAllProperties", API_VERSION),
                filter=attr.filters.exclude(attr.fields(Body).params),
            ),
        )

    async def get_supported_versions(self) -> dict:
        """Supported versions of basic device info."""
        return await self._request(
            "post",
            URL,
            json=attr.asdict(
                Body("getSupportedVersions", API_VERSION),
                filter=attr.filters.include(attr.fields(Body).method),
            ),
        )

    @property
    def architecture(self) -> str:
        """ApiVersion 1.1"""
        return self["Architecture"]

    @property
    def brand(self) -> str:
        """ApiVersion 1.1"""
        return self["Brand"]

    @property
    def builddate(self) -> str:
        """ApiVersion 1.1"""
        return self["BuildDate"]

    @property
    def hardwareid(self) -> str:
        """ApiVersion 1.1"""
        return self["HardwareID"]

    @property
    def prodfullname(self) -> str:
        """ApiVersion 1.1"""
        return self["ProdFullName"]

    @property
    def prodnbr(self) -> str:
        """ApiVersion 1.1"""
        return self["ProdNbr"]

    @property
    def prodshortname(self) -> str:
        """ApiVersion 1.1"""
        return self["ProdShortName"]

    @property
    def prodtype(self) -> str:
        """ApiVersion 1.1"""
        return self["ProdType"]

    @property
    def prodvariant(self) -> str:
        """ApiVersion 1.1"""
        return self["ProdVariant"]

    @property
    def serialnumber(self) -> str:
        """ApiVersion 1.1"""
        return self["SerialNumber"]

    @property
    def soc(self) -> str:
        """ApiVersion 1.1"""
        return self["Soc"]

    @property
    def socserialnumber(self) -> str:
        """ApiVersion 1.1"""
        return self["SocSerialNumber"]

    @property
    def version(self) -> str:
        """ApiVersion 1.1"""
        return self["Version"]

    @property
    def weburl(self) -> str:
        """ApiVersion 1.1"""
        return self["WebURL"]
