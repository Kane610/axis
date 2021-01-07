"""Python library to enable Axis devices to integrate with Home Assistant."""

import logging
from typing import Union

import xmltodict

from .api import APIItem, APIItems

LOGGER = logging.getLogger(__name__)

CLASS_INPUT = "input"
CLASS_LIGHT = "light"
CLASS_MOTION = "motion"
CLASS_OUTPUT = "output"
CLASS_PTZ = "ptz"
CLASS_SOUND = "sound"

EVENT_OPERATION = "operation"
EVENT_SOURCE = "source"
EVENT_SOURCE_IDX = "source_idx"
EVENT_TIMESTAMP = "timestamp"
EVENT_TOPIC = "topic"
EVENT_TYPE = "type"
EVENT_VALUE = "value"

OPERATION_INITIALIZED = "Initialized"
OPERATION_CHANGED = "Changed"
OPERATION_DELETED = "Deleted"

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


def traverse(data: dict, keys: tuple) -> Union[dict, str]:
    """Traverse dictionary using keys to retrieve last item."""
    head, *tail = keys
    return traverse(data.get(head, {}), tail) if tail else data.get(head, "")


def extract_name_value(data: dict) -> tuple:
    """Extract name and value from a simple item, take first dictionary if it is a list."""
    item = data.get("SimpleItem", {})
    if isinstance(item, list):
        item = item[0]
    return (item.get("@Name", ""), item.get("@Value", ""))


class EventManager(APIItems):
    """Initialize new events and update states of existing events."""

    def __init__(self, signal: object) -> None:
        """Ready information about events."""
        super().__init__({}, None, "", create_event)
        self.signal = signal

    def update(self, raw: Union[bytes, list]) -> None:
        """Prepare event."""
        new_events = self.process_raw(raw)

        for new_event in new_events:
            if self[new_event].TOPIC:  # Don't signal on unsupported events
                self.signal(OPERATION_INITIALIZED, new_event)

    @staticmethod
    def pre_process_raw(raw: Union[bytes, list]) -> dict:
        """Return a dictionary of initialized or changed events."""
        if not raw:
            return {}

        if isinstance(raw, bytes):
            raw = [EventManager.parse_event_xml(raw)]

        events = {}
        for event in raw:
            if not event:
                continue

            if event[EVENT_OPERATION] not in (OPERATION_INITIALIZED, OPERATION_CHANGED):
                LOGGER.debug("Unsupported event operation %s", event[EVENT_OPERATION])
                continue

            id = f'{event[EVENT_TOPIC]}_{event.get(EVENT_SOURCE_IDX, "")}'
            events[id] = event

        return events

    @staticmethod
    def parse_event_xml(raw_bytes: bytes) -> dict:
        """Parse metadata xml."""
        raw = xmltodict.parse(raw_bytes, process_namespaces=True, namespaces=NAMESPACES)

        if not raw.get("MetadataStream"):
            return {}

        event = {}

        event[EVENT_TOPIC] = traverse(raw, TOPIC)
        # event[EVENT_TIMESTAMP] = traverse(raw, TIMESTAMP)
        event[EVENT_OPERATION] = traverse(raw, OPERATION)

        source = traverse(raw, SOURCE)
        if source:
            event[EVENT_SOURCE], event[EVENT_SOURCE_IDX] = extract_name_value(source)

        data = traverse(raw, DATA)
        if data:
            event[EVENT_TYPE], event[EVENT_VALUE] = extract_name_value(data)

        LOGGER.debug(event)

        return event


class AxisEvent(APIItem):
    """Axis base event.

    TOPIC - some events disregards the initial way topics where used (a common string), this brings back the commonality to the topic.
    CLASS - create a kinship between similar events.
    TYPE - a more human readable string of event.
    """

    BINARY = False
    TOPIC = None
    CLASS = None
    TYPE = None

    @property
    def topic(self) -> str:
        """Topic of the event."""
        return self.raw[EVENT_TOPIC]

    @property
    def source(self) -> str:
        """Source of the event."""
        return self.raw.get(EVENT_SOURCE, "")

    @property
    def id(self) -> str:
        """Id of the event.

        -1 means ANY source.
        """
        index = self.raw.get(EVENT_SOURCE_IDX, "")
        return index if index != "-1" else ""  # Regex returned empty string

    @property
    def state(self) -> str:
        """State of the event."""
        return self.raw[EVENT_VALUE]


class AxisBinaryEvent(AxisEvent):
    """Axis binary event."""

    BINARY = True

    @property
    def is_tripped(self) -> bool:
        """Event is tripped now."""
        return self.state == "1"


class Audio(AxisBinaryEvent):
    """Audio trigger event."""

    TOPIC = "tns1:AudioSource/tnsaxis:TriggerLevel"
    CLASS = CLASS_SOUND
    TYPE = "Sound"


class DayNight(AxisBinaryEvent):
    """Day/Night vision trigger event."""

    TOPIC = "tns1:VideoSource/tnsaxis:DayNightVision"
    CLASS = CLASS_LIGHT
    TYPE = "DayNight"


class FenceGuard(AxisBinaryEvent):
    """Fence Guard trigger event."""

    TOPIC = "tnsaxis:CameraApplicationPlatform/FenceGuard"
    CLASS = CLASS_MOTION
    TYPE = "Fence Guard"

    @property
    def id(self) -> str:
        """Id of the event."""
        return self.topic.split("/")[-1]


class Input(AxisBinaryEvent):
    """Digital input event."""

    TOPIC = "tns1:Device/tnsaxis:IO/Port"
    CLASS = CLASS_INPUT
    TYPE = "Input"


class Light(AxisBinaryEvent):
    """Light status event."""

    TOPIC = "tns1:Device/tnsaxis:Light/Status"
    CLASS = CLASS_LIGHT
    TYPE = "Light"

    @property
    def is_tripped(self) -> bool:
        """Event is tripped now."""
        return self.state == "ON"


class LoiteringGuard(AxisBinaryEvent):
    """Loitering Guard trigger event."""

    TOPIC = "tnsaxis:CameraApplicationPlatform/LoiteringGuard"
    CLASS = CLASS_MOTION
    TYPE = "Loitering Guard"

    @property
    def id(self) -> str:
        """Id of the event."""
        return self.topic.split("/")[-1]


class Motion(AxisBinaryEvent):
    """Motion detection event."""

    TOPIC = "tns1:VideoAnalytics/tnsaxis:MotionDetection"
    CLASS = CLASS_MOTION
    TYPE = "Motion"


class MotionGuard(AxisBinaryEvent):
    """Motion Guard trigger event."""

    TOPIC = "tnsaxis:CameraApplicationPlatform/MotionGuard"
    CLASS = CLASS_MOTION
    TYPE = "Motion Guard"

    @property
    def id(self) -> str:
        """Id of the event."""
        return self.topic.split("/")[-1]


class ObjectAnalytics(AxisBinaryEvent):
    """Object Analytics trigger event."""

    TOPIC = "tnsaxis:CameraApplicationPlatform/ObjectAnalytics/"
    CLASS = CLASS_MOTION
    TYPE = "Object Analytics"

    @property
    def id(self) -> str:
        """Id of the event."""
        return self.topic.split("/")[-1]


class Pir(AxisBinaryEvent):
    """Passive IR event."""

    TOPIC = "tns1:Device/tnsaxis:Sensor/PIR"
    CLASS = CLASS_MOTION
    TYPE = "PIR"


class PtzMove(AxisBinaryEvent):
    """PTZ Move event."""

    TOPIC = "tns1:PTZController/tnsaxis:Move"
    CLASS = CLASS_PTZ
    TYPE = "is_moving"


class PtzPreset(AxisBinaryEvent):
    """PTZ Move event."""

    TOPIC = "tns1:PTZController/tnsaxis:PTZPresets"
    CLASS = CLASS_PTZ
    TYPE = "on_preset"


class Relay(AxisBinaryEvent):
    """Relay event."""

    TOPIC = "tns1:Device/Trigger/Relay"
    CLASS = CLASS_OUTPUT
    TYPE = "Relay"

    @property
    def is_tripped(self) -> bool:
        """Event is tripped now."""
        return self.state == "active"


class SupervisedInput(AxisBinaryEvent):
    """Supervised input event."""

    TOPIC = "tns1:Device/tnsaxis:IO/SupervisedPort"
    CLASS = CLASS_INPUT
    TYPE = "Supervised Input"


class Vmd3(AxisBinaryEvent):
    """Visual Motion Detection 3."""

    TOPIC = "tns1:RuleEngine/tnsaxis:VMD3/vmd3_video_1"
    CLASS = CLASS_MOTION
    TYPE = "VMD3"


class Vmd4(AxisBinaryEvent):
    """Visual Motion Detection 4."""

    TOPIC = "tnsaxis:CameraApplicationPlatform/VMD"
    CLASS = CLASS_MOTION
    TYPE = "VMD4"

    @property
    def id(self) -> str:
        """Id of the event."""
        return self.topic.split("/")[-1]


EVENT_CLASSES = (
    Audio,
    DayNight,
    FenceGuard,
    Input,
    Light,
    LoiteringGuard,
    Motion,
    MotionGuard,
    ObjectAnalytics,
    Pir,
    PtzMove,
    PtzPreset,
    Relay,
    SupervisedInput,
    Vmd3,
    Vmd4,
)

BLACK_LISTED_TOPICS = ["tnsaxis:CameraApplicationPlatform/VMD/xinternal_data"]


def create_event(event_id: str, event: dict, request: object) -> AxisEvent:
    """Simplify creating event by not needing to know type."""
    for event_class in EVENT_CLASSES:
        if event[EVENT_TOPIC] in BLACK_LISTED_TOPICS:
            break
        if event_class.TOPIC in event[EVENT_TOPIC]:
            return event_class(event_id, event, request)

    LOGGER.debug("Unsupported event %s", event[EVENT_TOPIC])
    return AxisEvent(event_id, event, request)
