"""Transport capability metadata for event filter planning.

This module defines the transport contract used by extension-facing planning
APIs: supported event transports and whether each transport can apply topic
filters upstream.
"""

from __future__ import annotations

from dataclasses import dataclass
import enum


class EventTransport(enum.StrEnum):
    """Event transport types used by capability matrix and public contracts."""

    RTSP = "rtsp"
    WEBSOCKET = "websocket"
    MQTT = "mqtt"


@dataclass(frozen=True)
class TransportFilterCapability:
    """Describes upstream filter capabilities for a transport.

    supports_upstream_topic_filter indicates whether the transport API can
    accept topic filters at source, reducing downstream event volume.
    """

    transport: EventTransport
    supports_upstream_topic_filter: bool
    notes: str


TRANSPORT_FILTER_CAPABILITIES: dict[EventTransport, TransportFilterCapability] = {
    EventTransport.RTSP: TransportFilterCapability(
        transport=EventTransport.RTSP,
        supports_upstream_topic_filter=False,
        notes="RTSP can only toggle event stream on/off; no topic-level filter endpoint.",
    ),
    EventTransport.WEBSOCKET: TransportFilterCapability(
        transport=EventTransport.WEBSOCKET,
        supports_upstream_topic_filter=True,
        notes="WebSocket supports events:configure with eventFilterList topic filters.",
    ),
    EventTransport.MQTT: TransportFilterCapability(
        transport=EventTransport.MQTT,
        supports_upstream_topic_filter=True,
        notes="MQTT publication setup supports a topicFilter list for upstream filtering.",
    ),
}
