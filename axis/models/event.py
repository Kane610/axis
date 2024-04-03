"""Python library to enable Axis devices to integrate with Home Assistant."""

from dataclasses import dataclass
import enum
import logging
from typing import Any, Self

import xmltodict

LOGGER = logging.getLogger(__name__)


class EventOperation(enum.StrEnum):
    """Possible operations of an event."""

    INITIALIZED = "Initialized"
    CHANGED = "Changed"
    DELETED = "Deleted"
    UNKNOWN = "Unknown"

    @classmethod
    def _missing_(cls, value: object) -> EventOperation:
        """Set default enum member if an unknown value is provided."""
        if LOGGER.isEnabledFor(logging.DEBUG):
            LOGGER.warning("Unsupported operation %s", value)
        return EventOperation.UNKNOWN


class EventTopic(enum.StrEnum):
    """Supported event topics."""

    DAY_NIGHT_VISION = "onvif:VideoSource/axis:DayNightVision"
    FENCE_GUARD = "axis:CameraApplicationPlatform/FenceGuard"
    LIGHT_STATUS = "onvif:Device/axis:Light/Status"
    LOITERING_GUARD = "axis:CameraApplicationPlatform/LoiteringGuard"
    MOTION_DETECTION = "onvif:VideoAnalytics/axis:MotionDetection"
    MOTION_DETECTION_3 = "onvif:RuleEngine/axis:VMD3/vmd3_video_1"
    MOTION_DETECTION_4 = "axis:CameraApplicationPlatform/VMD"
    MOTION_GUARD = "axis:CameraApplicationPlatform/MotionGuard"
    OBJECT_ANALYTICS = "axis:CameraApplicationPlatform/ObjectAnalytics"
    PIR = "onvif:Device/axis:Sensor/PIR"
    PORT_INPUT = "onvif:Device/axis:IO/Port"
    PORT_SUPERVISED_INPUT = "onvif:Device/axis:IO/SupervisedPort"
    PTZ_IS_MOVING = "onvif:PTZController/axis:Move"
    PTZ_ON_PRESET = "onvif:PTZController/axis:PTZPresets"
    RELAY = "onvif:Device/Trigger/Relay"
    SOUND_TRIGGER_LEVEL = "onvif:AudioSource/axis:TriggerLevel"
    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls, value: object) -> EventTopic:
        """Set default enum member if an unknown value is provided."""
        if LOGGER.isEnabledFor(logging.DEBUG):
            LOGGER.warning("Unsupported topic %s", value)
        return EventTopic.UNKNOWN


TOPIC_TO_STATE = {
    EventTopic.LIGHT_STATUS: "ON",
    EventTopic.RELAY: "active",
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


@dataclass
class Event:
    """Event data from Axis device."""

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

        if (topic_base := EventTopic(topic)) is EventTopic.UNKNOWN:
            _topic_base, _, _source_idx = topic.rpartition("/")
            topic_base = EventTopic(_topic_base)
            if source_idx == "":
                source_idx = _source_idx

        if source_idx == "-1":
            source_idx = "ANY"

        return cls(
            id=source_idx,
            is_tripped=value == TOPIC_TO_STATE.get(topic_base, "1"),
            operation=operation,
            source=source,
            state=value,
            topic=topic,
            topic_base=topic_base,
            data=data,
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

        topic = (
            str(traverse(raw, TOPIC))
            .replace("tns1", "onvif")
            .replace("tnsaxis", "axis")
        )
        # timestamp = traverse(raw, TIMESTAMP)
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
