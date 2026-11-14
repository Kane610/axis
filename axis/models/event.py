"""Decode Axis event-stream payloads and normalize event states and topics."""

from dataclasses import dataclass
import enum
from typing import Any, Self

import xmltodict


class EventOperation(enum.StrEnum):
    """Change reported for an event topic."""

    INITIALIZED = "Initialized"
    CHANGED = "Changed"
    DELETED = "Deleted"
    UNKNOWN = "Unknown"

    @classmethod
    def _missing_(cls, value: object) -> EventOperation:
        """Return UNKNOWN when the device reports an unrecognized operation."""
        return EventOperation.UNKNOWN


class EventTopic(enum.StrEnum):
    """Known Axis and ONVIF event topics normalized by this package."""

    AUDIO_CLASSIFICATION = "tnsaxis:AudioClassification"
    DAY_NIGHT_VISION = "tns1:VideoSource/tnsaxis:DayNightVision"
    FENCE_GUARD = "tnsaxis:CameraApplicationPlatform/FenceGuard"
    INTERCOM_DOOR_STATE = "tns1:Device/tnsaxis:Intercom/DoorState"
    LIGHT_STATUS = "tns1:Device/tnsaxis:Light/Status"
    LOITERING_GUARD = "tnsaxis:CameraApplicationPlatform/LoiteringGuard"
    MOTION_DETECTION = "tns1:VideoAnalytics/tnsaxis:MotionDetection"
    MOTION_DETECTION_2 = "tns1:RuleEngine/tnsaxis:VideoMotionDetection"
    MOTION_DETECTION_3 = "tns1:RuleEngine/tnsaxis:VMD3"
    MOTION_DETECTION_4 = "tnsaxis:CameraApplicationPlatform/VMD"
    MOTION_GUARD = "tnsaxis:CameraApplicationPlatform/MotionGuard"
    OBJECT_ANALYTICS = "tnsaxis:CameraApplicationPlatform/ObjectAnalytics"
    PIR = "tns1:Device/tnsaxis:Sensor/PIR"
    PORT_INPUT = "tns1:Device/tnsaxis:IO/Port"
    PORT_OUTPUT = "tns1:Device/tnsaxis:IO/OutputPort"
    PORT_SUPERVISED_INPUT = "tns1:Device/tnsaxis:IO/SupervisedPort"
    PTZ_IS_MOVING = "tns1:PTZController/tnsaxis:Move"
    PTZ_ON_PRESET = "tns1:PTZController/tnsaxis:PTZPresets"
    RELAY = "tns1:Device/Trigger/Relay"
    SOUND_TRIGGER_LEVEL = "tns1:AudioSource/tnsaxis:TriggerLevel"
    VIRTUAL_INPUT = "tns1:Device/tnsaxis:IO/VirtualInput"
    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls, value: object) -> EventTopic:
        """Return UNKNOWN when the event topic is not in the known topic list."""
        return EventTopic.UNKNOWN


TOPIC_TO_STATE = {
    EventTopic.LIGHT_STATUS: "ON",
    EventTopic.RELAY: "active",
}

KNOWN_FALSE_STATES = {"", "0", "false", "inactive", "low", "off"}
KNOWN_TRUE_STATES = {"1", "active", "high", "on", "true"}

TOPIC_TO_INACTIVE_STATE = {
    EventTopic.LIGHT_STATUS: "OFF",
    EventTopic.RELAY: "inactive",
}

EVENT_OPERATION = "operation"
EVENT_SOURCE = "source"
EVENT_SOURCE_IDX = "source_idx"
EVENT_TOPIC = "topic"
EVENT_TYPE = "type"
EVENT_VALUE = "value"

NOTIFICATION_MESSAGE = ("MetadataStream", "Event", "NotificationMessage")
MESSAGE = (*NOTIFICATION_MESSAGE, "Message", "Message")
TOPIC = (*NOTIFICATION_MESSAGE, "Topic", "#text")
OPERATION = (*MESSAGE, "PropertyOperation")
SOURCE = (*MESSAGE, "Source")
DATA = (*MESSAGE, "Data")

XML_NAMESPACES = {
    "http://www.onvif.org/ver10/schema": None,
    "http://docs.oasis-open.org/wsn/b-2": None,
}


def traverse(data: Any, keys: tuple[str, ...] | list[str]) -> Any:
    """Follow a sequence of dictionary keys and return the final value."""
    if not isinstance(data, dict):
        return {}

    head, *tail = keys
    item = data.get(head, {})
    return traverse(item, tail) if tail else item


def extract_name_value(
    data: dict[str, list[dict[str, str]] | dict[str, str]], prefer: str | None = None
) -> tuple[str, str]:
    """Read a SimpleItem's name and value, selecting a preferred or first list entry."""
    item = data.get("SimpleItem", {})
    if isinstance(item, list):
        if not item:
            return "", ""
        if prefer is None:
            item = item[0]
        else:
            item = next(
                (item for item in item if item.get("Name", "") == prefer), item[0]
            )
    return item.get("Name", ""), item.get("Value", "")


def is_tripped(value: object, topic_base: EventTopic, event_type: object) -> bool:
    """Return True for active states or non-empty stateless values, else False."""
    if (expected_state := TOPIC_TO_STATE.get(topic_base)) is not None:
        return str(value) == expected_state

    value_text = str(value).strip()
    state = value_text.casefold()

    if state in KNOWN_FALSE_STATES:
        return False

    if state in KNOWN_TRUE_STATES:
        return True

    if str(event_type).casefold() == "active":
        return False

    # Non-empty semantic values (for example classification values like "human")
    # are treated as stateless event triggers.
    return bool(value_text)


@dataclass
class Event:
    """Normalized event topic, source, operation, value, and active state."""

    id: str
    is_tripped: bool
    operation: EventOperation
    source: str
    state: str
    topic: str
    topic_base: EventTopic
    data: dict[str, Any]

    @classmethod
    def decode(cls, data: bytes | dict[str, Any]) -> Self:
        """Decode either a normalized event dictionary or an XML metadata message."""
        if isinstance(data, dict):
            return cls._decode_from_dict(data)
        return cls._decode_from_bytes(data)

    @classmethod
    def _decode_from_dict(cls, data: dict[str, Any]) -> Self:
        """Normalize event fields and derive the topic base and active state."""
        operation = EventOperation(data.get(EVENT_OPERATION, ""))
        topic = data.get(EVENT_TOPIC, "")
        source = data.get(EVENT_SOURCE, "")
        source_idx = data.get(EVENT_SOURCE_IDX, "")
        event_type = data.get(EVENT_TYPE, "")
        value = data.get(EVENT_VALUE, "")

        if (topic_base := EventTopic(topic)) is EventTopic.UNKNOWN:
            _topic_base, _, _source_idx = topic.rpartition("/")
            topic_base = EventTopic(_topic_base)
            if source_idx == "":
                source_idx = _source_idx

        if source_idx == "-1":
            source_idx = "ANY" if source != "port" else ""

        return cls(
            id=source_idx,
            is_tripped=is_tripped(value, topic_base, event_type),
            operation=operation,
            source=source,
            state=value,
            topic=topic,
            topic_base=topic_base,
            data=data,
        )

    @classmethod
    def _decode_from_bytes(cls, data: bytes) -> Self:
        """Extract topic, source, operation, and value from an ONVIF XML message."""
        raw = xmltodict.parse(
            data,
            attr_prefix="",  # Remove "@" prefix from XML attributes for easier access
            process_namespaces=True,
            namespaces=XML_NAMESPACES,
        )

        # Normalize the ONVIF metadata root: always use a dict, drop any stray
        # XML namespace attribute ("xmlns") added by xmltodict, and bail out
        # early if the payload is empty.
        stream = raw.get("MetadataStream") or {}
        if not stream or not any(key != "xmlns" for key in stream):
            return cls._decode_from_dict({})

        topic = traverse(raw, TOPIC)
        operation = traverse(raw, OPERATION)

        source = source_idx = ""
        if match := traverse(raw, SOURCE):
            source, source_idx = extract_name_value(match)

        data_type = data_value = ""
        if match := traverse(raw, DATA):
            data_type, data_value = extract_name_value(match, "active")

        return cls._decode_from_dict(
            {
                EVENT_OPERATION: operation,
                EVENT_TOPIC: topic,
                EVENT_SOURCE: source,
                EVENT_SOURCE_IDX: source_idx,
                EVENT_TYPE: data_type,
                EVENT_VALUE: data_value,
            }
        )
