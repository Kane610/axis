"""Python library to enable Axis devices to integrate with Home Assistant."""

from __future__ import annotations

from dataclasses import dataclass
import enum
import logging
from typing import TYPE_CHECKING, Any, Callable, Optional, Union

import xmltodict  # type: ignore[import]

from .vapix.interfaces.api import APIItems
from .vapix.models.api import APIItem

if TYPE_CHECKING:
    from .device import AxisDevice


SubscriptionCallback = Callable[["Event"], None]
SubscriptionType = tuple[SubscriptionCallback, Optional[tuple["EventTopic", ...]]]
UnsubscribeType = Callable[[], None]

ID_FILTER_ALL = "*"
TOPIC_FILTER_ALL = "*"

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


@dataclass
class Event:
    """Event data from deCONZ websocket."""

    data: dict[str, Any]
    group: EventGroup
    id: str
    is_tripped: bool
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

        state = data[EVENT_VALUE]
        topic = topic_base = data[EVENT_TOPIC]

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
            is_tripped=state == TOPIC_TO_STATE.get(topic_base, "1"),
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


class EventManager(APIItems):
    """Initialize new events and update states of existing events."""

    path = ""
    signal: Callable | None = None

    def __init__(self, device: "AxisDevice") -> None:
        """Ready information about events."""
        self.device = device
        self._subscribers: dict[str, list[SubscriptionType]] = {ID_FILTER_ALL: []}

        # Legacy
        self.item_cls = create_event
        super().__init__(device.vapix)

    def handler(self, data: bytes | dict[str, Any]) -> None:
        """Create event and pass it along to subscribers."""
        try:
            if isinstance(data, dict):
                event = Event.from_dict(data)
            else:
                event = Event.from_bytes(data)
        except AssertionError:
            return

        subscribers: list[SubscriptionType] = (
            self._subscribers.get(event.id, []) + self._subscribers[ID_FILTER_ALL]
        )
        for callback, topic_filter in subscribers:
            if topic_filter is not None and event.topic not in topic_filter:
                continue
            callback(event)

    def subscribe(
        self,
        callback: SubscriptionCallback,
        topic_filter: tuple[EventTopic, ...] | EventTopic | None = None,
        id_filter: tuple[str] | str | None = None,
    ) -> UnsubscribeType:
        """Subscribe to events.

        "callback" - callback function to call when on event.
        Return function to unsubscribe.
        """
        if isinstance(topic_filter, EventTopic):
            topic_filter = (topic_filter,)
        subscription = (callback, topic_filter)

        _id_filter: tuple[str]
        if id_filter is None:
            _id_filter = (ID_FILTER_ALL,)
        elif isinstance(id_filter, str):
            _id_filter = (id_filter,)

        for obj_id in _id_filter:
            if obj_id not in self._subscribers:
                self._subscribers[obj_id] = []
            self._subscribers[obj_id].append(subscription)

        def unsubscribe() -> None:
            for obj_id in _id_filter:
                if obj_id not in self._subscribers:
                    continue
                if subscription not in self._subscribers[obj_id]:
                    continue
                self._subscribers[obj_id].remove(subscription)

        return unsubscribe

    def __len__(self) -> int:
        """List number of subscribers."""
        return sum(len(s) for s in self._subscribers.values())

    # Legacy

    def update(self, raw: Union[bytes, list]) -> None:  # type: ignore[override]
        """Prepare event."""
        if self.signal is None:
            return

        new_events = self.process_raw(raw)

        for new_event in new_events:
            # Don't signal on unsupported events
            if self[new_event].topic_base != EventTopic.UNKNOWN:  # type: ignore[attr-defined]
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
    """

    binary = False
    topic_base = EventTopic.UNKNOWN
    group = EventGroup.NONE

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

    topic_base = EventTopic.SOUND_TRIGGER_LEVEL
    group = EventGroup.SOUND


class DayNight(AxisBinaryEvent):
    """Day/Night vision trigger event."""

    topic_base = EventTopic.DAY_NIGHT_VISION
    group = EventGroup.LIGHT


class FenceGuard(AxisBinaryEvent):
    """Fence Guard trigger event."""

    topic_base = EventTopic.FENCE_GUARD
    group = EventGroup.MOTION

    @property
    def id(self) -> str:
        """ID of the event."""
        return self.topic.split("/")[-1]


class Input(AxisBinaryEvent):
    """Digital input event."""

    topic_base = EventTopic.PORT_INPUT
    group = EventGroup.INPUT


class Light(AxisBinaryEvent):
    """Light status event."""

    topic_base = EventTopic.LIGHT_STATUS
    group = EventGroup.LIGHT

    @property
    def is_tripped(self) -> bool:
        """Event is tripped now."""
        return self.state == "ON"


class LoiteringGuard(AxisBinaryEvent):
    """Loitering Guard trigger event."""

    topic_base = EventTopic.LOITERING_GUARD
    group = EventGroup.MOTION

    @property
    def id(self) -> str:
        """ID of the event."""
        return self.topic.split("/")[-1]


class Motion(AxisBinaryEvent):
    """Motion detection event."""

    topic_base = EventTopic.MOTION_DETECTION
    group = EventGroup.MOTION


class MotionGuard(AxisBinaryEvent):
    """Motion Guard trigger event."""

    topic_base = EventTopic.MOTION_GUARD
    group = EventGroup.MOTION

    @property
    def id(self) -> str:
        """ID of the event."""
        return self.topic.split("/")[-1]


class ObjectAnalytics(AxisBinaryEvent):
    """Object Analytics trigger event."""

    topic_base = EventTopic.OBJECT_ANALYTICS
    group = EventGroup.MOTION

    @property
    def id(self) -> str:
        """ID of the event."""
        return self.topic.split("/")[-1]


class Pir(AxisBinaryEvent):
    """Passive IR event."""

    topic_base = EventTopic.PIR
    group = EventGroup.MOTION


class PtzMove(AxisBinaryEvent):
    """PTZ Move event."""

    topic_base = EventTopic.PTZ_IS_MOVING
    group = EventGroup.PTZ


class PtzPreset(AxisBinaryEvent):
    """PTZ Move event."""

    topic_base = EventTopic.PTZ_ON_PRESET
    group = EventGroup.PTZ


class Relay(AxisBinaryEvent):
    """Relay event."""

    topic_base = EventTopic.RELAY
    group = EventGroup.OUTPUT

    @property
    def is_tripped(self) -> bool:
        """Event is tripped now."""
        return self.state == "active"


class SupervisedInput(AxisBinaryEvent):
    """Supervised input event."""

    topic_base = EventTopic.PORT_SUPERVISED_INPUT
    group = EventGroup.INPUT


class Vmd3(AxisBinaryEvent):
    """Visual Motion Detection 3."""

    topic_base = EventTopic.MOTION_DETECTION_3
    group = EventGroup.MOTION


class Vmd4(AxisBinaryEvent):
    """Visual Motion Detection 4."""

    topic_base = EventTopic.MOTION_DETECTION_4
    group = EventGroup.MOTION

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
        if event_class.topic_base.value in event[EVENT_TOPIC]:
            return event_class(event_id, event, request)

    LOGGER.debug("Unsupported event %s", event[EVENT_TOPIC])
    return AxisEvent(event_id, event, request)
