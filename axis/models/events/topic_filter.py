"""Topic-domain primitives for event filtering.

This module owns two related concerns:
1) Topic namespace conversion helpers between canonical (tns1/tnsaxis)
    and transport-facing MQTT/websocket format (onvif/axis).
2) The EventTopicFilter value object used by callers to describe a
    wildcard subscription or a normalized set of explicit topics.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from collections.abc import Sequence

    from .event import EventTopic

# ---------------------------------------------------------------------------
# Topic namespace conversion
# ---------------------------------------------------------------------------

_CANONICAL_PREFIXES = ("tns1", "tnsaxis")
_MQTT_PREFIXES = ("onvif", "axis")

SegmentFormat = Literal["canonical", "mqtt", "unknown"]


def _convert_segment(segment: str, mapping: dict[str, str]) -> str:
    for source, target in mapping.items():
        prefix = f"{source}:"
        if segment.startswith(prefix):
            return f"{target}:{segment[len(prefix) :]}"
    return segment


def _convert_topic(topic: str, mapping: dict[str, str]) -> str:
    return "/".join(_convert_segment(segment, mapping) for segment in topic.split("/"))


def to_canonical(topic: str) -> str:
    """Convert topic namespaces to canonical (tns1/tnsaxis) representation.

    This is the internal normalization format used across filtering and
    local allow-list comparisons.
    """
    return _convert_topic(topic, {"onvif": "tns1", "axis": "tnsaxis"})


def to_mqtt(topic: str) -> str:
    """Convert topic namespaces to MQTT (onvif/axis) representation.

    Used for outbound transport configuration where the device API expects
    onvif/axis prefixes.
    """
    return _convert_topic(topic, {"tns1": "onvif", "tnsaxis": "axis"})


def to_topic_filter(topic: str) -> str:
    """Convert canonical topic to transport topic-filter representation.

    Today this is equivalent to MQTT representation and is kept as a named
    helper to make intent explicit at call sites.
    """
    return to_mqtt(topic)


def detect_format(topic: str) -> SegmentFormat:
    """Detect topic namespace format from segment prefixes.

    Returns canonical, mqtt, or unknown. Unknown means no known namespace
    prefixes were found in any topic segment.
    """
    segments = topic.split("/")

    if any(
        segment.startswith(f"{prefix}:")
        for prefix in _CANONICAL_PREFIXES
        for segment in segments
    ):
        return "canonical"

    if any(
        segment.startswith(f"{prefix}:")
        for prefix in _MQTT_PREFIXES
        for segment in segments
    ):
        return "mqtt"

    return "unknown"


# ---------------------------------------------------------------------------
# EventTopicFilter value object
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class EventTopicFilter:
    """Immutable, transport-agnostic event topic filter.

    Normalizes topic inputs to canonical form and exposes per-transport
    output properties. Wire-format construction (e.g. WebSocket dict shape)
    is the responsibility of the transport layer.

    Do not construct directly; prefer for_all_events() and from_topics().
    This keeps wildcard and normalization behavior centralized.
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

        Duplicate logical topics are collapsed after normalization.
        Raises ValueError if topics is empty; use for_all_events() for wildcard.
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
