"""Event transport orchestration manager."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from ...models.events.topic_filter import EventTopicFilter
from ...models.events.transport_capabilities import (
    TRANSPORT_FILTER_CAPABILITIES,
    EventTransport,
    TransportFilterCapability,
)

if TYPE_CHECKING:
    from ...stream_manager import StreamManager
    from ..mqtt import MqttClientHandler
    from .event_instances import EventInstanceHandler
    from .event_manager import EventManager

LOGGER = logging.getLogger(__name__)


class EventTransportManager:
    """Owns event transport filter orchestration across subsystems."""

    def __init__(
        self,
        event_instances: EventInstanceHandler,
        stream: StreamManager,
        event: EventManager,
        mqtt: MqttClientHandler,
    ) -> None:
        """Store subsystem dependencies used for transport filter application."""
        self._event_instances = event_instances
        self._stream = stream
        self._event = event
        self._mqtt = mqtt

    def get_event_transport_capabilities(
        self,
    ) -> dict[EventTransport, TransportFilterCapability]:
        """Return extension capability matrix for event transports."""
        return dict(TRANSPORT_FILTER_CAPABILITIES)

    def get_supported_event_descriptors(
        self,
        include_internal_topics: bool = False,
    ) -> dict[str, dict[str, Any]]:
        """Return normalized supported-event descriptors from event instances.

        This method is extension-oriented and has no side effects.
        """
        return self._event_instances.get_supported_event_descriptors(
            include_internal_topics=include_internal_topics
        )

    async def apply_event_transport_filters(
        self,
        event_filter: EventTopicFilter | None = None,
        include_internal_topics: bool = False,
    ) -> None:
        """Apply validated transport filters to websocket, MQTT, and local fallback.

        This method performs no implicit event-instance initialization. Callers must
        invoke ``initialize_event_instances`` before applying filters.
        """
        if not self._event_instances.initialized:
            msg = (
                "Event instances are not initialized. "
                "Call initialize_event_instances() first."
            )
            raise RuntimeError(msg)

        if event_filter is None:
            supported = self._event_instances.get_supported_topics(
                include_internal_topics=include_internal_topics
            )
            event_filter = (
                EventTopicFilter.from_topics(list(supported))
                if supported
                else EventTopicFilter.for_all_events()
            )

        if not event_filter.is_wildcard:
            supported_topics = set(
                self._event_instances.get_supported_topics(
                    include_internal_topics=include_internal_topics
                )
            )
            unknown_topics = sorted(
                set(event_filter.canonical_topics) - supported_topics
            )
            if unknown_topics:
                message = f"Requested unsupported topics: {', '.join(unknown_topics)}"
                raise ValueError(message)

        self._stream.set_event_subscription(event_filter)

        if self._mqtt.supported:
            await self._mqtt.configure_event_publication(
                event_filter.mqtt_topic_filters
            )

        self._event.set_allowed_topics(event_filter.canonical_topics or None)

        LOGGER.debug(
            "Applied event transport filters: websocket=%s mqtt=%s local=%s topics=%s",
            True,
            self._mqtt.supported,
            True,
            len(event_filter.canonical_topics)
            if not event_filter.is_wildcard
            else "all",
        )
