"""Python library to enable Axis devices to integrate with Home Assistant."""

import logging
import re

from .api import APIItem, APIItems

LOGGER = logging.getLogger(__name__)

CLASS_INPUT = "input"
CLASS_LIGHT = "light"
CLASS_MOTION = "motion"
CLASS_OUTPUT = "output"
CLASS_SOUND = "sound"

EVENT_OPERATION = "operation"
EVENT_SOURCE = "source"
EVENT_SOURCE_IDX = "source_idx"
EVENT_TOPIC = "topic"
EVENT_TYPE = "type"
EVENT_VALUE = "value"

OPERATION_INITIALIZED = "Initialized"
OPERATION_CHANGED = "Changed"
OPERATION_DELETED = "Deleted"

MESSAGE = re.compile(r'(?<=PropertyOperation)="(?P<operation>\w+)"')
TOPIC = re.compile(r"(?<=<wsnt:Topic).*>(?P<topic>.*)(?=<\/wsnt:Topic>)")
SOURCE = re.compile(
    r'(?<=<tt:Source>).*Name="(?P<source>\w+)"'
    + r'.*Value="(?P<source_idx>\w+)".*(?=<\/tt:Source>)'
)
DATA = re.compile(
    r'(?<=<tt:Data>).*Name="(?P<type>\w*)"'
    + r'.*Value="(?P<value>\w*)".*(?=<\/tt:Data>)'
)


class EventManager(APIItems):
    """Initialize new events and update states of existing events."""

    def __init__(self, signal: object) -> None:
        """Ready information about events."""
        super().__init__(raw={}, request=None, path="", item_cls=create_event)
        self.signal = signal

    def update(self, event_data: str) -> None:
        """Prepare event."""
        event = self.parse_event_xml(event_data)

        if not event:
            return

        self.process_event(event)

    def process_event(self, event: dict) -> None:
        """New event to process."""
        if event[EVENT_OPERATION] in (OPERATION_INITIALIZED, OPERATION_CHANGED):
            id = f'{event[EVENT_TOPIC]}_{event.get(EVENT_SOURCE_IDX, "")}'

            new_events = self.process_raw({id: event})
            for new_event in new_events:
                if self[new_event].TOPIC:
                    self.signal(OPERATION_INITIALIZED, new_event)

        elif event[EVENT_OPERATION] == OPERATION_DELETED:
            LOGGER.debug("Deleted event from stream")

    def parse_event_xml(self, event_data) -> dict:
        """Parse metadata xml."""
        event = {}

        event_xml = event_data.decode()
        message = MESSAGE.search(event_xml)

        if not message:
            return event

        event[EVENT_OPERATION] = message.group(EVENT_OPERATION)

        topic = TOPIC.search(event_xml)
        if topic:
            event[EVENT_TOPIC] = topic.group(EVENT_TOPIC)

        source = SOURCE.search(event_xml)
        if source:
            event[EVENT_SOURCE] = source.group(EVENT_SOURCE)
            event[EVENT_SOURCE_IDX] = source.group(EVENT_SOURCE_IDX)

        data = DATA.search(event_xml)
        if data:
            event[EVENT_TYPE] = data.group(EVENT_TYPE)
            event[EVENT_VALUE] = data.group(EVENT_VALUE)

        LOGGER.debug(event)

        return event


class AxisEvent(APIItem):
    """Axis base event."""

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
        """Id of the event."""
        return self.raw.get(EVENT_SOURCE_IDX, "")

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
    """Audio trigger event.

    {
        'operation': 'Initialized',
        'topic': 'tns1:AudioSource/tnsaxis:TriggerLevel',
        'source': 'channel',
        'source_idx': '1',
        'type': 'triggered',
        'value': '0'
    }
    """

    TOPIC = "tns1:AudioSource/tnsaxis:TriggerLevel"
    CLASS = CLASS_SOUND
    TYPE = "Sound"


class DayNight(AxisBinaryEvent):
    """Day/Night vision trigger event.

    {
        'operation': 'Initialized',
        'topic': 'tns1:VideoSource/tnsaxis:DayNightVision',
        'source': 'VideoSourceConfigurationToken',
        'source_idx': '1',
        'type': 'day',
        'value': '1'
    }
    """

    TOPIC = "tns1:VideoSource/tnsaxis:DayNightVision"
    CLASS = CLASS_LIGHT
    TYPE = "DayNight"


class FenceGuard(AxisBinaryEvent):
    """Fence Guard trigger event.

    {
        'operation': 'Initialized',
        'topic': 'tnsaxis:CameraApplicationPlatform/FenceGuard/Camera1Profile#',
        'type': 'active',
        'value': '1'
    }
    """

    TOPIC = "tnsaxis:CameraApplicationPlatform/FenceGuard"
    CLASS = CLASS_MOTION
    TYPE = "Fence Guard"

    @property
    def id(self) -> str:
        """Id of the event."""
        return self.topic.split("/")[-1]


class Input(AxisBinaryEvent):
    """Digital input event.

    {
        'operation': 'Initialized',
        'topic': 'tns1:Device/tnsaxis:IO/Port',
        'source': 'port',
        'source_idx': '0',
        'type': 'state',
        'value': '0'
    }
    """

    TOPIC = "tns1:Device/tnsaxis:IO/Port"
    CLASS = CLASS_INPUT
    TYPE = "Input"


class Light(AxisBinaryEvent):
    """Light status event.

    {
        'operation': 'Initialized',
        'topic': 'tns1:Device/tnsaxis:Light/Status',
        'source': 'id',
        'source_idx': '0',
        'type': 'state',
        'value': 'OFF'
    }
    """

    TOPIC = "tns1:Device/tnsaxis:Light/Status"
    CLASS = CLASS_LIGHT
    TYPE = "Light"

    @property
    def is_tripped(self) -> bool:
        """Event is tripped now."""
        return self.state == "ON"


class LoiteringGuard(AxisBinaryEvent):
    """Loitering Guard trigger event.

    {
        'operation': 'Initialized',
        'topic': 'tnsaxis:CameraApplicationPlatform/LoiteringGuard/Camera#Profile#',
        'type': 'active',
        'value': '0'
    }
    """

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
    """Motion Guard trigger event.

    {
        'operation': 'Initialized',
        'topic': 'tnsaxis:CameraApplicationPlatform/MotionGuard/Camera#Profile#',
        'type': 'active',
        'value': '0'
    }
    """

    TOPIC = "tnsaxis:CameraApplicationPlatform/MotionGuard"
    CLASS = CLASS_MOTION
    TYPE = "Motion Guard"

    @property
    def id(self) -> str:
        """Id of the event."""
        return self.topic.split("/")[-1]


class ObjectAnalytics(AxisBinaryEvent):
    """Object Analytics trigger event.

    {
        'operation': 'Initialized',
        'topic': 'tnsaxis:CameraApplicationPlatform/ObjectAnalytics/Device1Scenario1',
        'type': 'active',
        'value': '0'
    }
    """

    TOPIC = "tnsaxis:CameraApplicationPlatform/ObjectAnalytics/"
    CLASS = CLASS_MOTION
    TYPE = "Object Analytics"

    @property
    def id(self) -> str:
        """Id of the event."""
        return self.topic.split("/")[-1]


class Pir(AxisBinaryEvent):
    """Passive IR event.

    {
        'operation': 'Initialized',
        'topic': 'tns1:Device/tnsaxis:Sensor/PIR',
        'source': 'sensor',
        'source_idx': '0',
        'type': 'state',
        'value': '0'
    }
    """

    TOPIC = "tns1:Device/tnsaxis:Sensor/PIR"
    CLASS = CLASS_MOTION
    TYPE = "PIR"


class Relay(AxisBinaryEvent):
    """Relay event.

    {
        'operation': 'Initialized',
        'topic': 'tns1:Device/Trigger/Relay',
        'source': 'RelayToken',
        'source_idx': '0',
        'type': 'LogicalState',
        'value': 'inactive'
    }
    """

    TOPIC = "tns1:Device/Trigger/Relay"
    CLASS = CLASS_OUTPUT
    TYPE = "Relay"

    @property
    def is_tripped(self) -> bool:
        """Event is tripped now."""
        return self.state == "active"


class SupervisedInput(AxisBinaryEvent):
    """Supervised input event.

    {
        'operation': 'Initialized',
        'topic': 'tns1:Device/tnsaxis:IO/SupervisedPort',
        'source': 'port',
        'source_idx': '0',
        'type': 'state',
        'value': '0'
    }
    """

    TOPIC = "tns1:Device/tnsaxis:IO/SupervisedPort"
    CLASS = CLASS_INPUT
    TYPE = "Supervised Input"


class Vmd3(AxisBinaryEvent):
    """Visual Motion Detection 3.

    {
        'operation': 'Initialized',
        'topic': 'tns1:RuleEngine/tnsaxis:VMD3/vmd3_video_1',
        'source': 'areaid',
        'source_idx': '0',
        'type': 'active',
        'value': '1'
    }
    """

    TOPIC = "tns1:RuleEngine/tnsaxis:VMD3/vmd3_video_1"
    CLASS = CLASS_MOTION
    TYPE = "VMD3"


class Vmd4(AxisBinaryEvent):
    """Visual Motion Detection 4.

    {
        'operation': 'Initialized',
        'topic': 'tnsaxis:CameraApplicationPlatform/VMD/Camera1Profile#',
        'type': 'active',
        'value': '1'
    }
    """

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
    Relay,
    SupervisedInput,
    Vmd3,
    Vmd4,
)

BLACK_LISTED_TOPICS = "tnsaxis:CameraApplicationPlatform/VMD/xinternal_data"


def create_event(event_id: str, event: dict, request) -> AxisEvent:
    """Simplify creating event by not needing to know type."""
    for event_class in EVENT_CLASSES:
        if event[EVENT_TOPIC] in BLACK_LISTED_TOPICS:
            break
        if event_class.TOPIC in event[EVENT_TOPIC]:
            return event_class(event_id, event, request)

    LOGGER.debug("Unsupported event %s", event[EVENT_TOPIC])
    return AxisEvent(event_id, event, request)
