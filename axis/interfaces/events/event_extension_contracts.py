"""Extension contracts for transport filter planning."""

from __future__ import annotations

from dataclasses import dataclass
import enum


class EventTransport(enum.StrEnum):
    """Event transport types used for capability planning."""

    RTSP = "rtsp"
    WEBSOCKET = "websocket"
    MQTT = "mqtt"


@dataclass(frozen=True)
class TransportFilterCapability:
    """Describes upstream filter capabilities for a transport."""

    transport: EventTransport
    supports_upstream_topic_filter: bool
    notes: str


TRANSPORT_FILTER_CAPABILITIES: dict[EventTransport, TransportFilterCapability] = {
    EventTransport.RTSP: TransportFilterCapability(
        transport=EventTransport.RTSP,
        supports_upstream_topic_filter=False,
        notes="RTSP supports event stream on/off only",
    ),
    EventTransport.WEBSOCKET: TransportFilterCapability(
        transport=EventTransport.WEBSOCKET,
        supports_upstream_topic_filter=True,
        notes="WebSocket supports events:configure eventFilterList",
    ),
    EventTransport.MQTT: TransportFilterCapability(
        transport=EventTransport.MQTT,
        supports_upstream_topic_filter=True,
        notes="MQTT event publication supports topicFilter list",
    ),
}


@dataclass(frozen=True)
class DesiredEventSubscription:
    """Transport-agnostic desired event subscription request."""

    topic: str
    source: str | None = None
    source_ids: tuple[str, ...] | None = None
