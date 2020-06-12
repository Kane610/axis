"""Basic Device Info api.

AXIS Basic device information API can be used to retrieve simple information about the product.
This information is used to identify basic properties of the product.
"""

import attr

from .api import APIItem, APIItems, Body

URL = "/axis-cgi/basicdeviceinfo.cgi"

API_DISCOVERY_ID = "basic-device-info"
API_VERSION = "1.1"


class BasicDeviceInfo(APIItems):
    """Basic device information for Axis devices."""

    def __init__(self, request: object) -> None:
        super().__init__({}, request, URL, APIItem)

    def update(self, path=None) -> None:
        raw = self.get_all_properties()
        self.process_raw(raw["data"]["propertyList"])

    def get_all_properties(self) -> dict:
        """List all properties of basic device info."""
        return self._request(
            "post",
            URL,
            json=attr.asdict(
                Body("getAllProperties", API_VERSION),
                filter=attr.filters.exclude(attr.fields(Body).params),
            ),
        )

    def get_supported_versions(self) -> dict:
        """Supported versions of basic device info."""
        return self._request(
            "post",
            URL,
            json=attr.asdict(
                Body("getSupportedVersions", API_VERSION),
                filter=attr.filters.include(attr.fields(Body).method),
            ),
        )

    @property
    def architecture(self):
        """ApiVersion 1.1"""
        return self["Architecture"].raw

    @property
    def brand(self):
        """ApiVersion 1.1"""
        return self["Brand"].raw

    @property
    def builddate(self):
        """ApiVersion 1.1"""
        return self["BuildDate"].raw

    @property
    def hardwareid(self):
        """ApiVersion 1.1"""
        return self["HardwareID"].raw

    @property
    def prodfullname(self):
        """ApiVersion 1.1"""
        return self["ProdFullName"].raw

    @property
    def prodnbr(self):
        """ApiVersion 1.1"""
        return self["ProdNbr"].raw

    @property
    def prodshortname(self):
        """ApiVersion 1.1"""
        return self["ProdShortName"].raw

    @property
    def prodtype(self):
        """ApiVersion 1.1"""
        return self["ProdType"].raw

    @property
    def prodvariant(self):
        """ApiVersion 1.1"""
        return self["ProdVariant"].raw

    @property
    def serialnumber(self):
        """ApiVersion 1.1"""
        return self["SerialNumber"].raw

    @property
    def soc(self):
        """ApiVersion 1.1"""
        return self["Soc"].raw

    @property
    def socserialnumber(self):
        """ApiVersion 1.1"""
        return self["SocSerialNumber"].raw

    @property
    def version(self):
        """ApiVersion 1.1"""
        return self["Version"].raw

    @property
    def weburl(self):
        """ApiVersion 1.1"""
        return self["WebURL"].raw
