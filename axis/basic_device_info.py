"""API Discovery api."""

import attr

from .api import APIItem, APIItems

URL = "/axis-cgi/basicdeviceinfo.cgi"

API_DISCOVERY_ID = "basic-device-info"

API_VERSION = "1.1"
CONTEXT = "Axis library"


@attr.s
class body:
    """Create basic device info request body."""

    method: str = attr.ib()
    apiVersion: str = attr.ib(default=API_VERSION)


class BasicDeviceInfo(APIItems):
    """Basic device information for Axis devices."""

    def __init__(self, raw: dict, request: object) -> None:
        super().__init__(raw, request, URL, APIItem)

    def update(self, path=None) -> None:
        raw = self.get_all_properties()
        self.process_raw(raw["data"]["propertyList"])

    def get_all_properties(self) -> dict:
        """List all properties of basic device info."""
        return self._request("post", URL, json=attr.asdict(body("getAllProperties")))

    def get_supported_versions(self) -> dict:
        """Supported versions of basic device info."""
        return self._request(
            "post",
            URL,
            json=attr.asdict(
                body("getSupportedVersions"),
                filter=attr.filters.include(attr.fields(body).method),
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
