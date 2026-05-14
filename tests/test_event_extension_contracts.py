"""Tests for extension contract capability matrix."""

from axis.interfaces.events.event_extension_contracts import (
    TRANSPORT_FILTER_CAPABILITIES,
    EventTransport,
)


def test_transport_filter_capabilities() -> None:
    """Capability matrix should reflect expected transport support."""
    assert not TRANSPORT_FILTER_CAPABILITIES[
        EventTransport.RTSP
    ].supports_upstream_topic_filter
    assert TRANSPORT_FILTER_CAPABILITIES[
        EventTransport.WEBSOCKET
    ].supports_upstream_topic_filter
    assert TRANSPORT_FILTER_CAPABILITIES[
        EventTransport.MQTT
    ].supports_upstream_topic_filter
