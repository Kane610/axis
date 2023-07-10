"""Basic Device Info api.

AXIS Basic device information API can be used to retrieve
 simple information about the product.
This information is used to identify basic properties of the product.
"""

from ..models.api_discovery import ApiId
from ..models.basic_device_info import (
    DeviceInformation,
    GetAllPropertiesRequest,
    GetAllPropertiesT,
    GetSupportedVersionsRequest,
)
from .api_handler import ApiHandler2


class BasicDeviceInfoHandler(ApiHandler2[DeviceInformation]):
    """Basic device information for Axis devices."""

    api_id = ApiId.BASIC_DEVICE_INFO

    async def _api_request(self) -> dict[str, DeviceInformation]:
        """Get default data of basic device information."""
        return await self.get_all_properties()

    async def get_all_properties(self) -> GetAllPropertiesT:
        """List all properties of basic device info."""
        discovery_item = self.vapix.api_discovery[self.api_id.value]
        response = await self.vapix.request3(
            GetAllPropertiesRequest(discovery_item.version)
        )
        return {"0": response.data}

    async def get_supported_versions(self) -> list[str]:
        """List supported API versions."""
        response = await self.vapix.request3(GetSupportedVersionsRequest())
        return response.data

    @property
    def architecture(self) -> str:
        """SOC architecture."""
        return self["0"].architecture

    @property
    def brand(self) -> str:
        """Device branding."""
        return self["0"].brand

    @property
    def builddate(self) -> str:
        """Firmware build date."""
        return self["0"].build_date

    @property
    def hardwareid(self) -> str:
        """Device hardware ID."""
        return self["0"].hardware_id

    @property
    def prodfullname(self) -> str:
        """Device product full name."""
        return self["0"].product_full_name

    @property
    def prodnbr(self) -> str:
        """Device product number."""
        return self["0"].product_number

    @property
    def prodshortname(self) -> str:
        """Device product short name."""
        return self["0"].product_short_name

    @property
    def prodtype(self) -> str:
        """Device product type."""
        return self["0"].product_type

    @property
    def prodvariant(self) -> str:
        """Device product variant."""
        return self["0"].product_variant

    @property
    def serialnumber(self) -> str:
        """Device serial number."""
        return self["0"].serial_number

    @property
    def soc(self) -> str:
        """System on chip variant."""
        return self["0"].soc

    @property
    def socserialnumber(self) -> str:
        """SOC serial number."""
        return self["0"].soc_serial_number

    @property
    def version(self) -> str:
        """Firmware version."""
        return self["0"].version

    @property
    def weburl(self) -> str:
        """Device home page URL."""
        return self["0"].web_url
