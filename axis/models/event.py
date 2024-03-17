"""Python library to enable Axis devices to integrate with Home Assistant."""

from dataclasses import dataclass
import enum
import logging
from typing import Any, Self

import xmltodict

LOGGER = logging.getLogger(__name__)


class EventGroup(enum.StrEnum):
    """Logical grouping of events."""

    INPUT = "input"
    LIGHT = "light"
    MOTION = "motion"
    OUTPUT = "output"
    PTZ = "ptz"
    SOUND = "sound"
    NONE = "none"


class EventOperation(enum.StrEnum):
    """Possible operations of an event."""

    INITIALIZED = "Initialized"
    CHANGED = "Changed"
    DELETED = "Deleted"
    UNKNOWN = "Unknown"

    @classmethod
    def _missing_(cls, value: object) -> "EventOperation":
        """Set default enum member if an unknown value is provided."""
        if LOGGER.isEnabledFor(logging.DEBUG):
            LOGGER.warning("Unsupported operation %s", value)
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
    def _missing_(cls, value: object) -> "EventTopic":
        """Set default enum member if an unknown value is provided."""
        if LOGGER.isEnabledFor(logging.DEBUG):
            LOGGER.warning("Unsupported topic %s", value)
        return EventTopic.UNKNOWN


TOPIC_TO_GROUP = {
    EventTopic.DAY_NIGHT_VISION: EventGroup.LIGHT,
    EventTopic.FENCE_GUARD: EventGroup.MOTION,
    EventTopic.LIGHT_STATUS: EventGroup.LIGHT,
    EventTopic.LOITERING_GUARD: EventGroup.MOTION,
    EventTopic.MOTION_DETECTION: EventGroup.MOTION,
    EventTopic.MOTION_DETECTION_3: EventGroup.MOTION,
    EventTopic.MOTION_DETECTION_4: EventGroup.MOTION,
    EventTopic.MOTION_GUARD: EventGroup.MOTION,
    EventTopic.OBJECT_ANALYTICS: EventGroup.MOTION,
    EventTopic.PIR: EventGroup.MOTION,
    EventTopic.PORT_INPUT: EventGroup.INPUT,
    EventTopic.PORT_SUPERVISED_INPUT: EventGroup.INPUT,
    EventTopic.PTZ_IS_MOVING: EventGroup.PTZ,
    EventTopic.PTZ_ON_PRESET: EventGroup.PTZ,
    EventTopic.RELAY: EventGroup.OUTPUT,
    EventTopic.SOUND_TRIGGER_LEVEL: EventGroup.SOUND,
}

TOPIC_TO_STATE = {
    EventTopic.LIGHT_STATUS: "ON",
    EventTopic.RELAY: "active",
}

EVENT_OPERATION = "operation"
EVENT_SOURCE = "source"
EVENT_SOURCE_IDX = "source_idx"
EVENT_TIMESTAMP = "timestamp"
EVENT_TOPIC = "topic"
EVENT_TYPE = "type"
EVENT_VALUE = "value"

NOTIFICATION_MESSAGE = ("MetadataStream", "Event", "NotificationMessage")
MESSAGE = (*NOTIFICATION_MESSAGE, "Message", "Message")
TOPIC = (*NOTIFICATION_MESSAGE, "Topic", "#text")
TIMESTAMP = (*MESSAGE, "@UtcTime")
OPERATION = (*MESSAGE, "@PropertyOperation")
SOURCE = (*MESSAGE, "Source")
DATA = (*MESSAGE, "Data")

XML_NAMESPACES = {
    "http://www.onvif.org/ver10/schema": None,
    "http://docs.oasis-open.org/wsn/b-2": None,
}


def traverse(
    data: dict[str, dict[str, Any]], keys: tuple[str, ...] | list[str]
) -> dict[str, Any]:
    """Traverse dictionary using keys to retrieve last item."""
    head, *tail = keys
    return traverse(data.get(head, {}), tail) if tail else data.get(head, {})


def extract_name_value(
    data: dict[str, list[dict[str, str]] | dict[str, str]],
) -> tuple[str, str]:
    """Extract name and value from a simple item, take first dictionary if it is a list."""
    item = data.get("SimpleItem", {})
    if isinstance(item, list):
        item = item[0]
    return item.get("@Name", ""), item.get("@Value", "")
    # return item.get("Name", ""), item.get("Value", "")


@dataclass
class Event:
    """Event data from Axis device."""

    data: dict[str, Any]
    group: EventGroup
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
        value = data.get(EVENT_VALUE, "")

        if (topic_base := EventTopic(topic)) == EventTopic.UNKNOWN:
            _topic_base, _, _source_idx = topic.rpartition("/")
            topic_base = EventTopic(_topic_base)
            if source_idx == "":
                source_idx = _source_idx

        if source_idx == "-1":
            source_idx = "ANY" if source != "port" else ""

        return cls(
            data=data,
            group=TOPIC_TO_GROUP.get(topic_base, EventGroup.NONE),
            id=source_idx,
            is_tripped=value == TOPIC_TO_STATE.get(topic_base, "1"),
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
            # attr_prefix="",
            process_namespaces=True,
            namespaces=XML_NAMESPACES,
        )

        if raw.get("MetadataStream") is None:
            return cls._decode_from_dict({})

        topic = traverse(raw, TOPIC)
        # timestamp = traverse(raw, TIMESTAMP)
        operation = traverse(raw, OPERATION)

        source = source_idx = ""
        if match := traverse(raw, SOURCE):
            source, source_idx = extract_name_value(match)

        data_type = data_value = ""
        if match := traverse(raw, DATA):
            data_type, data_value = extract_name_value(match)

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
