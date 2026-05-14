"""Tests for event topic normalization extension contract."""

from axis.interfaces.events.topic_normalizer import (
    detect_format,
    to_canonical,
    to_mqtt,
    to_topic_filter,
)


def test_round_trip_topic_conversion() -> None:
    """Canonical and MQTT representations should round-trip."""
    canonical = "tns1:Device/tnsaxis:Sensor/PIR"

    mqtt = to_mqtt(canonical)
    assert mqtt == "onvif:Device/axis:Sensor/PIR"
    assert to_canonical(mqtt) == canonical


def test_detect_topic_format() -> None:
    """Format detection should classify known topic namespace variants."""
    assert detect_format("tns1:Device/tnsaxis:Sensor/PIR") == "canonical"
    assert detect_format("onvif:Device/axis:Sensor/PIR") == "mqtt"
    assert detect_format("Device/Sensor/PIR") == "unknown"


def test_to_topic_filter_uses_mqtt_form() -> None:
    """Topic filter representation should use MQTT namespaces."""
    assert (
        to_topic_filter("tns1:Device/tnsaxis:Light/Status")
        == "onvif:Device/axis:Light/Status"
    )
