"""Transport capability metadata for event filter planning."""

from __future__ import annotations

from dataclasses import dataclass

from ...models.events.subscription_contracts import EventTransport


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
