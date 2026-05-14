"""Event service and action service APIs available in Axis network device."""

from typing import TYPE_CHECKING

from ..models.event_instance import (
    EventInstance,
    ListEventInstancesRequest,
    ListEventInstancesResponse,
)
from .api_handler import ApiHandler
from .event_manager import BLACK_LISTED_TOPICS

if TYPE_CHECKING:
    from ..models.event import Event


class EventInstanceHandler(ApiHandler[EventInstance]):
    """Event instances for Axis devices."""

    async def _api_request(self) -> dict[str, EventInstance]:
        """Get default data of API discovery."""
        return await self.get_event_instances()

    async def get_event_instances(self) -> dict[str, EventInstance]:
        """List all event instances."""
        bytes_data = await self.vapix.api_request(ListEventInstancesRequest())
        response = ListEventInstancesResponse.decode(bytes_data)
        return response.data

    def get_expected_events_per_topic(
        self,
        include_internal_topics: bool = False,
    ) -> dict[str, list[Event]]:
        """Return expected startup events grouped by topic.

        Event instances are the protocol-agnostic bootstrap source for startup
        predeclaration. Returned events are synthesized from schema data and represent
        expected event identity/state (operation=Initialized), not live stream updates.
        """
        grouped: dict[str, list[Event]] = {}
        for item in self.values():
            if not include_internal_topics and item.topic in BLACK_LISTED_TOPICS:
                continue
            grouped[item.topic] = item.to_events()
        return grouped
