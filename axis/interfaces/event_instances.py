"""Event service and action service APIs available in Axis network device."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..models.event_instance import (
    EventInstance,
    ListEventInstancesRequest,
    ListEventInstancesResponse,
)
from .api_handler import ApiHandler
from .event_manager import BLACK_LISTED_TOPICS
from .events.topic_normalizer import to_canonical, to_topic_filter

if TYPE_CHECKING:
    from ..models.event import Event
    from .events.event_extension_contracts import DesiredEventSubscription


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

    def get_supported_topics(
        self, include_internal_topics: bool = False
    ) -> tuple[str, ...]:
        """Return canonical supported event topics from event instances."""
        expected = self.get_expected_events_per_topic(
            include_internal_topics=include_internal_topics
        )
        return tuple(sorted(to_canonical(topic) for topic in expected))

    def get_supported_event_descriptors(
        self, include_internal_topics: bool = False
    ) -> dict[str, dict[str, Any]]:
        """Return normalized supported-event descriptors for extension consumers."""
        descriptors: dict[str, dict[str, Any]] = {}
        for topic, events in self.get_expected_events_per_topic(
            include_internal_topics=include_internal_topics
        ).items():
            canonical_topic = to_canonical(topic)
            topic_filter = to_topic_filter(canonical_topic)
            descriptors[canonical_topic] = {
                "topic": canonical_topic,
                "topic_filter": topic_filter,
                "count": len(events),
                "sources": tuple(
                    sorted({event.source for event in events if event.source})
                ),
            }
        return descriptors

    def build_transport_filter_payloads(
        self,
        subscriptions: list[DesiredEventSubscription] | None = None,
        include_internal_topics: bool = False,
    ) -> dict[str, list[str]]:
        """Build no-op extension payloads for MQTT and WebSocket topic filters."""
        if subscriptions:
            topics = sorted(
                {to_canonical(subscription.topic) for subscription in subscriptions}
            )
        else:
            topics = list(self.get_supported_topics(include_internal_topics))

        topic_filters = [to_topic_filter(topic) for topic in topics]

        return {
            "canonical_topics": topics,
            "mqtt_topics": topic_filters,
            "websocket_topic_filters": topic_filters,
        }
