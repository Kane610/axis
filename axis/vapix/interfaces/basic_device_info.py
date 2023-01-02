"""Basic Device Info api.

AXIS Basic device information API can be used to retrieve simple information about the product.
This information is used to identify basic properties of the product.
"""

import attr

from ..models.api import APIItem
from .api import APIItems, Body

URL = "/axis-cgi/basicdeviceinfo.cgi"

API_DISCOVERY_ID = "basic-device-info"
API_VERSION = "1.1"


class BasicDeviceInfo(APIItems):
    """Basic device information for Axis devices."""

    item_cls = APIItem
    path = URL

    def __getitem__(self, obj_id: str) -> str:  # type: ignore[override]
        """self["string"] will return self._item["string"].raw."""
        return self._items[obj_id].raw

    async def update(self) -> None:
        """Refresh data."""
        raw = await self.get_all_properties()
        self.process_raw(raw)

    @staticmethod
    def pre_process_raw(raw: dict) -> dict:
        """Return a dictionary of device information."""
        return raw.get("data", {}).get("propertyList", {})

    async def get_all_properties(self) -> dict:
        """List all properties of basic device info."""
        return await self.vapix.request(
            "post",
            URL,
            json=attr.asdict(
                Body("getAllProperties", API_VERSION),
                filter=attr.filters.exclude(attr.fields(Body).params),
            ),
        )

    async def get_supported_versions(self) -> dict:
        """Supported versions of basic device info."""
        return await self.vapix.request(
            "post",
            URL,
            json=attr.asdict(
                Body("getSupportedVersions", API_VERSION),
                filter=attr.filters.include(attr.fields(Body).method),
            ),
        )

    @property
    def architecture(self) -> str:
        """SOC architecture.

        ApiVersion 1.1.
        """
        return self["Architecture"]

    @property
    def brand(self) -> str:
        """Device branding.

        ApiVersion 1.1.
        """
        return self["Brand"]

    @property
    def builddate(self) -> str:
        """Firmware build date.

        ApiVersion 1.1.
        """
        return self["BuildDate"]

    @property
    def hardwareid(self) -> str:
        """Device hardware ID.

        ApiVersion 1.1.
        """
        return self["HardwareID"]

    @property
    def prodfullname(self) -> str:
        """Device product full name.

        ApiVersion 1.1.
        """
        return self["ProdFullName"]

    @property
    def prodnbr(self) -> str:
        """Device product number.

        ApiVersion 1.1.
        """
        return self["ProdNbr"]

    @property
    def prodshortname(self) -> str:
        """Device product short name.

        ApiVersion 1.1.
        """
        return self["ProdShortName"]

    @property
    def prodtype(self) -> str:
        """Device product type.

        ApiVersion 1.1.
        """
        return self["ProdType"]

    @property
    def prodvariant(self) -> str:
        """Device product variant.

        ApiVersion 1.1.
        """
        return self["ProdVariant"]

    @property
    def serialnumber(self) -> str:
        """Device serial number.

        ApiVersion 1.1.
        """
        return self["SerialNumber"]

    @property
    def soc(self) -> str:
        """System on chip variant.

        ApiVersion 1.1.
        """
        return self["Soc"]

    @property
    def socserialnumber(self) -> str:
        """SOC serial number.

        ApiVersion 1.1.
        """
        return self["SocSerialNumber"]

    @property
    def version(self) -> str:
        """Firmware version.

        ApiVersion 1.1.
        """
        return self["Version"]

    @property
    def weburl(self) -> str:
        """Device home page URL.

        ApiVersion 1.1.
        """
        return self["WebURL"]
