"""Event service and action service APIs available in Axis network device."""

from typing import TYPE_CHECKING, Any

from ..models.event_instance import (
    EventInstance,
    ListEventInstancesRequest,
    ListEventInstancesResponse,
)
from .api_handler import ApiHandler

if TYPE_CHECKING:
    from ..models.event import Event


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

    def get_events_per_topic(self) -> dict[str, list[Event]]:
        """Return synthesized initialized events grouped by event-instance topic."""
        grouped: dict[str, list[Event]] = {}
        for item in self.values():
            if not isinstance(item, EventInstance):
                continue
            grouped[item.topic] = item.to_events()
        return grouped
