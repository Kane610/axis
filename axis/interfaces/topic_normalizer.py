"""Topic normalization helpers for cross-transport event handling."""

from __future__ import annotations

from typing import Literal

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
    """Convert topic namespaces to canonical (tns1/tnsaxis) representation."""
    return _convert_topic(topic, {"onvif": "tns1", "axis": "tnsaxis"})


def to_mqtt(topic: str) -> str:
    """Convert topic namespaces to MQTT (onvif/axis) representation."""
    return _convert_topic(topic, {"tns1": "onvif", "tnsaxis": "axis"})


def to_topic_filter(topic: str) -> str:
    """Convert canonical topic to topic-filter namespace representation."""
    return to_mqtt(topic)


def detect_format(topic: str) -> SegmentFormat:
    """Detect topic namespace format from segment prefixes."""
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
