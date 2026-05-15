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
    """Transport-agnostic desired event subscription request."""

    topic: str
    source: str | None = None
    source_ids: tuple[str, ...] | None = None
