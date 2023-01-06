"""Python library to enable Axis devices to integrate with Home Assistant."""

from __future__ import annotations

from dataclasses import dataclass
import enum
import logging
from typing import Any

import xmltodict

LOGGER = logging.getLogger(__name__)


class EventGroup(enum.Enum):
    """Logical grouping of events."""

    INPUT = "input"
    LIGHT = "light"
    MOTION = "motion"
    OUTPUT = "output"
    PTZ = "ptz"
    SOUND = "sound"
    NONE = "none"


class EventOperation(str, enum.Enum):
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


class EventTopic(enum.Enum):
    """Supported event topics."""

    DAY_NIGHT_VISION = "tns1:VideoSource/tnsaxis:DayNightVision"
    FENCE_GUARD = "tnsaxis:CameraApplicationPlatform/FenceGuard"
    LIGHT_STATUS = "tns1:Device/tnsaxis:Light/Status"
    LOITERING_GUARD = "tnsaxis:CameraApplicationPlatform/LoiteringGuard"
    MOTION_DETECTION = "tns1:VideoAnalytics/tnsaxis:MotionDetection"
    MOTION_DETECTION_3 = "tns1:RuleEngine/tnsaxis:VMD3/vmd3_video_1"
    MOTION_DETECTION_4 = "tnsaxis:CameraApplicationPlatform/VMD"
    MOTION_GUARD = "tnsaxis:CameraApplicationPlatform/MotionGuard"
    OBJECT_ANALYTICS = "tnsaxis:CameraApplicationPlatform/ObjectAnalytics/"
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

BLACK_LISTED_TOPICS = ["tnsaxis:CameraApplicationPlatform/VMD/xinternal_data"]

EVENT_OPERATION = "operation"
EVENT_SOURCE = "source"
EVENT_SOURCE_IDX = "source_idx"
EVENT_TIMESTAMP = "timestamp"
EVENT_TOPIC = "topic"
EVENT_TYPE = "type"
EVENT_VALUE = "value"


OPERATION_INITIALIZED = EventOperation.INITIALIZED
OPERATION_CHANGED = EventOperation.CHANGED
OPERATION_DELETED = EventOperation.DELETED

NOTIFICATION_MESSAGE = ("MetadataStream", "Event", "NotificationMessage")
MESSAGE = NOTIFICATION_MESSAGE + ("Message", "Message")
TOPIC = NOTIFICATION_MESSAGE + ("Topic", "#text")
TIMESTAMP = MESSAGE + ("@UtcTime",)
OPERATION = MESSAGE + ("@PropertyOperation",)
SOURCE = MESSAGE + ("Source",)
DATA = MESSAGE + ("Data",)

NAMESPACES = {
    "http://www.onvif.org/ver10/schema": None,
    "http://docs.oasis-open.org/wsn/b-2": None,
}


def traverse(data: dict, keys: tuple | list) -> dict:
    """Traverse dictionary using keys to retrieve last item."""
    head, *tail = keys
    return traverse(data.get(head, {}), tail) if tail else data.get(head, {})


def extract_name_value(data: dict) -> tuple:
    """Extract name and value from a simple item, take first dictionary if it is a list."""
    item = data.get("SimpleItem", {})
    if isinstance(item, list):
        item = item[0]
    return (item.get("@Name", ""), item.get("@Value", ""))


@dataclass
class Event:
    """Event data from deCONZ websocket."""

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
    def from_dict(cls, data: dict[str, Any]) -> "Event":
        """Create event instance from dict."""
        assert data[EVENT_TOPIC] not in BLACK_LISTED_TOPICS

        if LOGGER.isEnabledFor(logging.DEBUG):
            LOGGER.debug(data)

        operation = EventOperation(data[EVENT_OPERATION])
        state = data[EVENT_VALUE]
        topic = topic_base = data[EVENT_TOPIC]

        source: str
        index: str
        if not (source := data.get(EVENT_SOURCE, "")):
            # Topics from VMD4 et. al provide source and index at the end of the topic
            topic_base, _, index = topic.rpartition("/")

        elif index := data.get(EVENT_SOURCE_IDX, ""):
            # Regex returned empty string
            index = index if index != "-1" else ""

        _topic_base = EventTopic(topic_base)
        return cls(
            data=data,
            group=TOPIC_TO_GROUP.get(_topic_base, EventGroup.NONE),
            id=index,
            is_tripped=state == TOPIC_TO_STATE.get(_topic_base, "1"),
            operation=operation,
            source=source,
            state=state,
            topic=topic,
            topic_base=_topic_base,
        )

    @classmethod
    def from_bytes(cls, data: bytes) -> "Event":
        """Parse metadata xml."""
        raw = xmltodict.parse(data, process_namespaces=True, namespaces=NAMESPACES)
        assert raw.get("MetadataStream") is not None  # Empty data

        event = {}
        event[EVENT_TOPIC] = traverse(raw, TOPIC)
        # event[EVENT_TIMESTAMP] = traverse(raw, TIMESTAMP)
        event[EVENT_OPERATION] = traverse(raw, OPERATION)

        if match := traverse(raw, SOURCE):
            event[EVENT_SOURCE], event[EVENT_SOURCE_IDX] = extract_name_value(match)  # type: ignore[arg-type]

        if match := traverse(raw, DATA):
            event[EVENT_TYPE], event[EVENT_VALUE] = extract_name_value(match)  # type: ignore[arg-type]

        return Event.from_dict(event)
