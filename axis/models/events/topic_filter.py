"""Transport-agnostic event topic filter value object."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .topic_normalizer import detect_format, to_canonical, to_topic_filter

if TYPE_CHECKING:
    from collections.abc import Sequence

    from .event import EventTopic
    from .subscription_contracts import DesiredEventSubscription


@dataclass(frozen=True)
class EventTopicFilter:
    """Immutable, transport-agnostic event topic filter.

    Normalizes topic inputs to canonical form and exposes per-transport
    output properties. Wire-format construction (e.g. WebSocket dict shape)
    is the responsibility of the transport layer.

    Do not construct directly — use the provided classmethods.
    """

    # None means wildcard (subscribe to all); never empty frozenset.
    _topics: frozenset[str] | None = field(default=None, repr=True)

    @classmethod
    def for_all_events(cls) -> EventTopicFilter:
        """Return a wildcard filter — subscribe to all events.

        On WebSocket, equivalent to eventFilterList [{"topicFilter": "//."}].
        On MQTT, no topic filter is applied.
        EventManager allows all topics through.
        """
        return cls(_topics=None)

    @classmethod
    def from_topics(
        cls,
        topics: Sequence[str | EventTopic],
    ) -> EventTopicFilter:
        """Build from a sequence of topic strings and/or EventTopic enum values.

        Accepts topics in any format: canonical (tns1/tnsaxis), MQTT (onvif/axis),
        or EventTopic enum. All inputs are normalized to canonical form.

        Raises ValueError if topics is empty — use for_all_events() for wildcard.
        """
        if not topics:
            msg = "topics must not be empty; use EventTopicFilter.for_all_events() to subscribe to all events"
            raise ValueError(msg)

        canonical: set[str] = set()
        for topic in topics:
            raw: str = topic.value if hasattr(topic, "value") else topic
            canonical.add(to_canonical(raw) if detect_format(raw) == "mqtt" else raw)
        return cls(_topics=frozenset(canonical))

    @property
    def is_wildcard(self) -> bool:
        """True when this filter represents 'subscribe to all events'."""
        return self._topics is None

    @property
    def canonical_topics(self) -> list[str]:
        """Sorted canonical (tns1/tnsaxis) topic strings.

        Consumed by EventManager.set_allowed_topics().
        Returns an empty list for wildcard filters — callers interpret
        empty as 'allow all'.
        """
        if self._topics is None:
            return []
        return sorted(self._topics)

    @property
    def mqtt_topic_filters(self) -> list[str]:
        """Sorted MQTT (onvif/axis) topic filter strings.

        Consumed by MqttClientHandler.configure_event_publication().
        Returns an empty list for wildcard filters — callers should skip
        setting an MQTT filter when this is empty.
        """
        if self._topics is None:
            return []
        return sorted(to_topic_filter(t) for t in self._topics)


def from_desired_subscriptions(
    subscriptions: Sequence[DesiredEventSubscription],
) -> EventTopicFilter:
    """Build an EventTopicFilter from legacy DesiredEventSubscription objects.

    Compatibility helper for callers that construct DesiredEventSubscription.
    Prefer EventTopicFilter.from_topics() for new code.
    """
    return EventTopicFilter.from_topics([s.topic for s in subscriptions])
