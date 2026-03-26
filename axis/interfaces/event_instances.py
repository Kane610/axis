"""Event service and action service APIs available in Axis network device."""

from typing import Any

from ..models.event_instance import (
    ListEventInstancesRequest,
    ListEventInstancesResponse,
)
from .api_handler import ApiHandler


class EventInstanceHandler(ApiHandler[Any]):
    """Event instances for Axis devices."""

    async def _api_request(self) -> dict[str, Any]:
        """Get default data of API discovery."""
        return await self.get_event_instances()

    async def get_event_instances(self) -> dict[str, Any]:
        """List all event instances."""
        bytes_data = await self.vapix.api_request(ListEventInstancesRequest())
        response = ListEventInstancesResponse.decode(bytes_data)
        return response.data
