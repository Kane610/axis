"""Python library to enable Axis devices to integrate with Home Assistant."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Callable, Union

import xmltodict  # type: ignore[import]

from .vapix.interfaces.api import APIItems
from .vapix.models.api import APIItem

if TYPE_CHECKING:
    from .device import AxisDevice

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


def traverse(data: dict, keys: Union[tuple, list]) -> dict:
    """Traverse dictionary using keys to retrieve last item."""
    head, *tail = keys
    return traverse(data.get(head, {}), tail) if tail else data.get(head, {})


def extract_name_value(data: dict) -> tuple:
    """Extract name and value from a simple item, take first dictionary if it is a list."""
    item = data.get("SimpleItem", {})
    if isinstance(item, list):
        item = item[0]
    return (item.get("@Name", ""), item.get("@Value", ""))


class EventManager(APIItems):
    """Initialize new events and update states of existing events."""

    path = ""
    signal: Callable | None = None

    def __init__(self, device: "AxisDevice") -> None:
        """Ready information about events."""
        self.device = device
        self.item_cls = create_event
        super().__init__(device.vapix)

    def update(self, raw: Union[bytes, list]) -> None:  # type: ignore[override]
        """Prepare event."""
        if self.signal is None:
            return

        new_events = self.process_raw(raw)

        for new_event in new_events:
            # Don't signal on unsupported events
            if self[new_event].topic_base:  # type: ignore[attr-defined]
                self.signal(OPERATION_INITIALIZED, new_event)

    @staticmethod
    def pre_process_raw(raw: Union[bytes, list]) -> dict:  # type: ignore[override]
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
            event[EVENT_SOURCE], event[EVENT_SOURCE_IDX] = extract_name_value(source)  # type: ignore[arg-type]

        data = traverse(raw, DATA)
        if data:
            event[EVENT_TYPE], event[EVENT_VALUE] = extract_name_value(data)  # type: ignore[arg-type]

        LOGGER.debug(event)

        return event


class AxisEvent(APIItem):
    """Axis base event.

    Topic - some events disregards the initial way topics where used (a common string),
      this brings back the commonality to the topic.
    Group - create a kinship between similar events.
    Type - a more human readable string of event.
    """

    binary = False
    topic_base = ""
    group = ""
    type = ""

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
        """ID of the event.

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

    binary = True

    @property
    def is_tripped(self) -> bool:
        """Event is tripped now."""
        return self.state == "1"


class Audio(AxisBinaryEvent):
    """Audio trigger event."""

    topic_base = "tns1:AudioSource/tnsaxis:TriggerLevel"
    group = CLASS_SOUND
    type = "Sound"


class DayNight(AxisBinaryEvent):
    """Day/Night vision trigger event."""

    topic_base = "tns1:VideoSource/tnsaxis:DayNightVision"
    group = CLASS_LIGHT
    type = "DayNight"


class FenceGuard(AxisBinaryEvent):
    """Fence Guard trigger event."""

    topic_base = "tnsaxis:CameraApplicationPlatform/FenceGuard"
    group = CLASS_MOTION
    type = "Fence Guard"

    @property
    def id(self) -> str:
        """ID of the event."""
        return self.topic.split("/")[-1]


class Input(AxisBinaryEvent):
    """Digital input event."""

    topic_base = "tns1:Device/tnsaxis:IO/Port"
    group = CLASS_INPUT
    type = "Input"


class Light(AxisBinaryEvent):
    """Light status event."""

    topic_base = "tns1:Device/tnsaxis:Light/Status"
    group = CLASS_LIGHT
    type = "Light"

    @property
    def is_tripped(self) -> bool:
        """Event is tripped now."""
        return self.state == "ON"


class LoiteringGuard(AxisBinaryEvent):
    """Loitering Guard trigger event."""

    topic_base = "tnsaxis:CameraApplicationPlatform/LoiteringGuard"
    group = CLASS_MOTION
    type = "Loitering Guard"

    @property
    def id(self) -> str:
        """ID of the event."""
        return self.topic.split("/")[-1]


class Motion(AxisBinaryEvent):
    """Motion detection event."""

    topic_base = "tns1:VideoAnalytics/tnsaxis:MotionDetection"
    group = CLASS_MOTION
    type = "Motion"


class MotionGuard(AxisBinaryEvent):
    """Motion Guard trigger event."""

    topic_base = "tnsaxis:CameraApplicationPlatform/MotionGuard"
    group = CLASS_MOTION
    type = "Motion Guard"

    @property
    def id(self) -> str:
        """ID of the event."""
        return self.topic.split("/")[-1]


class ObjectAnalytics(AxisBinaryEvent):
    """Object Analytics trigger event."""

    topic_base = "tnsaxis:CameraApplicationPlatform/ObjectAnalytics/"
    group = CLASS_MOTION
    type = "Object Analytics"

    @property
    def id(self) -> str:
        """ID of the event."""
        return self.topic.split("/")[-1]


class Pir(AxisBinaryEvent):
    """Passive IR event."""

    topic_base = "tns1:Device/tnsaxis:Sensor/PIR"
    group = CLASS_MOTION
    type = "PIR"


class PtzMove(AxisBinaryEvent):
    """PTZ Move event."""

    topic_base = "tns1:PTZController/tnsaxis:Move"
    group = CLASS_PTZ
    type = "is_moving"


class PtzPreset(AxisBinaryEvent):
    """PTZ Move event."""

    topic_base = "tns1:PTZController/tnsaxis:PTZPresets"
    group = CLASS_PTZ
    type = "on_preset"


class Relay(AxisBinaryEvent):
    """Relay event."""

    topic_base = "tns1:Device/Trigger/Relay"
    group = CLASS_OUTPUT
    type = "Relay"

    @property
    def is_tripped(self) -> bool:
        """Event is tripped now."""
        return self.state == "active"


class SupervisedInput(AxisBinaryEvent):
    """Supervised input event."""

    topic_base = "tns1:Device/tnsaxis:IO/SupervisedPort"
    group = CLASS_INPUT
    type = "Supervised Input"


class Vmd3(AxisBinaryEvent):
    """Visual Motion Detection 3."""

    topic_base = "tns1:RuleEngine/tnsaxis:VMD3/vmd3_video_1"
    group = CLASS_MOTION
    type = "VMD3"


class Vmd4(AxisBinaryEvent):
    """Visual Motion Detection 4."""

    topic_base = "tnsaxis:CameraApplicationPlatform/VMD"
    group = CLASS_MOTION
    type = "VMD4"

    @property
    def id(self) -> str:
        """ID of the event."""
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


def create_event(event_id: str, event: dict, request: Callable[..., Any]) -> AxisEvent:
    """Simplify creating event by not needing to know type."""
    for event_class in EVENT_CLASSES:
        if event[EVENT_TOPIC] in BLACK_LISTED_TOPICS:
            break
        if event_class.topic_base in event[EVENT_TOPIC]:
            return event_class(event_id, event, request)

    LOGGER.debug("Unsupported event %s", event[EVENT_TOPIC])
    return AxisEvent(event_id, event, request)
