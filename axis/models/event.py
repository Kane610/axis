"""Python library to enable Axis devices to integrate with Home Assistant."""

from dataclasses import dataclass
import enum
from typing import Any, Self

import xmltodict


class EventOperation(enum.StrEnum):
    """Possible operations of an event."""

    INITIALIZED = "Initialized"
    CHANGED = "Changed"
    DELETED = "Deleted"
    UNKNOWN = "Unknown"

    @classmethod
    def _missing_(cls, value: object) -> EventOperation:
        """Set default enum member if an unknown value is provided."""
        return EventOperation.UNKNOWN


class EventTopic(enum.StrEnum):
    """Supported event topics."""

    DAY_NIGHT_VISION = "tns1:VideoSource/tnsaxis:DayNightVision"
    FENCE_GUARD = "tnsaxis:CameraApplicationPlatform/FenceGuard"
    LIGHT_STATUS = "tns1:Device/tnsaxis:Light/Status"
    LOITERING_GUARD = "tnsaxis:CameraApplicationPlatform/LoiteringGuard"
    MOTION_DETECTION = "tns1:VideoAnalytics/tnsaxis:MotionDetection"
    MOTION_DETECTION_3 = "tns1:RuleEngine/tnsaxis:VMD3/vmd3_video_1"
    MOTION_DETECTION_4 = "tnsaxis:CameraApplicationPlatform/VMD"
    MOTION_GUARD = "tnsaxis:CameraApplicationPlatform/MotionGuard"
    OBJECT_ANALYTICS = "tnsaxis:CameraApplicationPlatform/ObjectAnalytics"
    PIR = "tns1:Device/tnsaxis:Sensor/PIR"
    PORT_INPUT = "tns1:Device/tnsaxis:IO/Port"
    PORT_SUPERVISED_INPUT = "tns1:Device/tnsaxis:IO/SupervisedPort"
    PTZ_IS_MOVING = "tns1:PTZController/tnsaxis:Move"
    PTZ_ON_PRESET = "tns1:PTZController/tnsaxis:PTZPresets"
    RELAY = "tns1:Device/Trigger/Relay"
    SOUND_TRIGGER_LEVEL = "tns1:AudioSource/tnsaxis:TriggerLevel"
    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls, value: object) -> EventTopic:
        """Set default enum member if an unknown value is provided."""
        return EventTopic.UNKNOWN


def event_group(topic: EventTopic) -> str:
    """Return logical group for the event topic."""
    group = "none"
    if topic in (EventTopic.PORT_INPUT, EventTopic.PORT_SUPERVISED_INPUT):
        group = "input"
    elif topic in (EventTopic.DAY_NIGHT_VISION, EventTopic.LIGHT_STATUS):
        group = "light"
    elif topic in (
        EventTopic.FENCE_GUARD,
        EventTopic.LOITERING_GUARD,
        EventTopic.MOTION_DETECTION,
        EventTopic.MOTION_DETECTION_3,
        EventTopic.MOTION_DETECTION_4,
        EventTopic.MOTION_GUARD,
        EventTopic.OBJECT_ANALYTICS,
        EventTopic.PIR,
    ):
        group = "motion"
    elif topic == EventTopic.RELAY:
        group = "output"
    elif topic in (EventTopic.PTZ_IS_MOVING, EventTopic.PTZ_ON_PRESET):
        group = "ptz"
    elif topic == EventTopic.SOUND_TRIGGER_LEVEL:
        group = "sound"
    return group


TOPIC_TO_STATE = {
    EventTopic.LIGHT_STATUS: "ON",
    EventTopic.RELAY: "active",
}

KNOWN_FALSE_STATES = {"", "0", "false", "inactive", "low", "off"}
KNOWN_TRUE_STATES = {"1", "active", "high", "on", "true"}

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
    """Traverse dictionary using keys to retrieve last item."""
    if not isinstance(data, dict):
        return {}

    head, *tail = keys
    item = data.get(head, {})
    return traverse(item, tail) if tail else item


def extract_name_value(
    data: dict[str, list[dict[str, str]] | dict[str, str]], prefer: str | None = None
) -> tuple[str, str]:
    """Extract name and value from a simple item, take first dictionary if it is a list."""
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
    """Return whether an event value should be considered active/tripped."""
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
    """Event data from Axis device."""

    data: dict[str, Any]
    group: str
    id: str
    is_tripped: bool
    operation: EventOperation
    source: str
    state: str
    topic: str
    topic_base: EventTopic

    @classmethod
    def decode(cls, data: bytes | dict[str, Any]) -> Self:
        """Decode data to an event object."""
        if isinstance(data, dict):
            return cls._decode_from_dict(data)
        return cls._decode_from_bytes(data)

    @classmethod
    def _decode_from_dict(cls, data: dict[str, Any]) -> Self:
        """Create event instance from dict."""
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
            data=data,
            group=event_group(topic_base),
            id=source_idx,
            is_tripped=is_tripped(value, topic_base, event_type),
            operation=operation,
            source=source,
            state=value,
            topic=topic,
            topic_base=topic_base,
        )

    @classmethod
    def _decode_from_bytes(cls, data: bytes) -> Self:
        """Parse metadata xml."""
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
