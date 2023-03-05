"""PIR sensor configuration api.

The PIR sensor configuration API helps you list and configure
the sensitivity of the PIR (passive infrared) sensors on your Axis device.
"""
from typing import Any

from ..models.api_discovery import ApiId
from ..models.pir_sensor_configuration import (
    ListSensorsRequest,
    PirSensorConfiguration,
    SupportedVersionsRequest,
)
from .api_handler import ApiHandler


class PirSensorConfigurationHandler(ApiHandler[PirSensorConfiguration]):
    """PIR sensor configuration for Axis devices."""

    api_id = ApiId.PIR_SENSOR_CONFIGURATION
    item_cls = PirSensorConfiguration

    async def update(self) -> None:
        """Refresh data."""
        raw = await self.list_sensors()
        self.process_raw(raw)
        # raw = await self.list_sensors()
        # api_data = raw.get("data", {}).get("sensors", [])
        # self.process_raw({api["id"]: api for api in api_data})

    async def list_sensors(self) -> dict[str, Any]:
        """List all APIs registered on API Discovery service."""
        raw = await self.vapix.request2(ListSensorsRequest.create())
        api_data = raw.get("data", {}).get("sensors", [])
        return {api["id"]: api for api in api_data}
        # return await self.vapix.request2(ListSensorsRequest.create())

    async def get_supported_versions(self) -> dict:
        """Supported versions of API Discovery API."""
        return await self.vapix.request2(SupportedVersionsRequest.create())
