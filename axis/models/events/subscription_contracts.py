"""Domain contracts for event-subscription planning."""

from __future__ import annotations

from dataclasses import dataclass
import enum


class EventTransport(enum.StrEnum):
    """Event transport types used for capability planning."""

    RTSP = "rtsp"
    WEBSOCKET = "websocket"
    MQTT = "mqtt"


@dataclass(frozen=True)
class DesiredEventSubscription:
    """Transport-agnostic desired event subscription request.

    Deprecated: Use EventTopicFilter.from_topics() instead.
    Accepted by apply_event_transport_filters() for backward compatibility.
    """

    topic: str
