"""List the event types and sources an Axis device supports through its event service."""

from typing import TYPE_CHECKING

from ..models.event_instance import (
    EventInstance,
    ListEventInstancesRequest,
)
from .api_handler import ApiHandler
from .event_manager import BLACK_LISTED_TOPICS

if TYPE_CHECKING:
    from ..models.event import Event


class EventInstanceHandler(ApiHandler[EventInstance]):
    """Read event definitions and derive the events expected when a stream starts."""

    async def _api_request(self) -> dict[str, EventInstance]:
        """Read device event definitions for this handler's cached data."""
        return await self.get_event_instances()

    async def get_event_instances(self) -> dict[str, EventInstance]:
        """List all event instances."""
        response = await self.vapix.api_request(ListEventInstancesRequest())
        return response.data

    def get_expected_events_per_topic(
        self,
        include_internal_topics: bool = False,
    ) -> dict[str, list[Event]]:
        """Return expected startup events grouped by topic.

        Build these events from the device's event definitions, not from live
        stream updates. They describe expected sources and initial states
        (operation=Initialized), regardless of the streaming transport.
        """
        grouped: dict[str, list[Event]] = {}
        for item in self.values():
            if not include_internal_topics and item.topic in BLACK_LISTED_TOPICS:
                continue
            grouped[item.topic] = item.to_events()
        return grouped
