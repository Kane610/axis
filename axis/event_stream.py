"""Python library to enable Axis devices to integrate with Home Assistant."""

import logging
import re

from .utils import session_request

_LOGGER = logging.getLogger(__name__)

CLASS_INPUT = 'input'
CLASS_LIGHT = 'light'
CLASS_MOTION = 'motion'
CLASS_OUTPUT = 'output'
CLASS_SOUND = 'sound'

EVENT_NAME = '{topic}_{source}'

EVENT_OPERATION = 'operation'
EVENT_SOURCE = 'source'
EVENT_SOURCE_IDX = 'source_idx'
EVENT_TOPIC = 'topic'
EVENT_TYPE = 'type'
EVENT_VALUE = 'value'

MESSAGE = re.compile(r'(?<=PropertyOperation)="(?P<operation>\w+)"')
TOPIC = re.compile(r'(?<=<wsnt:Topic).*>(?P<topic>.*)(?=<\/wsnt:Topic>)')
SOURCE = re.compile(r'(?<=<tt:Source>).*Name="(?P<source>\w+)"' +
                    r'.*Value="(?P<source_idx>\w+)".*(?=<\/tt:Source>)')
DATA = re.compile(r'(?<=<tt:Data>).*Name="(?P<type>\w*)"' +
                  r'.*Value="(?P<value>\w*)".*(?=<\/tt:Data>)')


class EventManager:
    """Initialize new events and update states of existing events."""

    def __init__(self, signal) -> None:
        """Ready information about events."""
        self.signal = signal
        self.events = {}

    def new_event(self, event_data: str) -> None:
        """New event to process."""
        event = self.parse_event_xml(event_data)

        if EVENT_OPERATION in event:
            self.manage_event(event)

    def parse_event_xml(self, event_data) -> dict:
        """Parse metadata xml."""
        event = {}

        event_xml = event_data.decode()

        message = MESSAGE.search(event_xml)
        if not message:
            return {}
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

        _LOGGER.debug(event)

        return event

    def manage_event(self, event) -> None:
        """Received new metadata.

        Operation initialized means new event, also happens if reconnecting.
        Operation changed updates existing events state.
        """
        name = EVENT_NAME.format(
            topic=event[EVENT_TOPIC], source=event.get(EVENT_SOURCE_IDX))

        if event[EVENT_OPERATION] == 'Initialized' and name not in self.events:

            for event_class in EVENT_CLASSES:
                if event_class.TOPIC in event[EVENT_TOPIC]:
                    self.events[name] = event_class(event)
                    self.signal('add', name)
                    return

            _LOGGER.debug('Unsupported event %s', event[EVENT_TOPIC])

        elif event[EVENT_OPERATION] == 'Changed' and name in self.events:
            self.events[name].state = event[EVENT_VALUE]

            # elif operation == 'Deleted':
            #     _LOGGER.debug("Deleted event from stream")


class AxisBinaryEvent:
    """"""
    BINARY = True
    TOPIC = None
    CLASS = None
    TYPE = None

    def __init__(self, event: dict) -> None:
        self.topic = event[EVENT_TOPIC]
        self.source = event.get(EVENT_SOURCE)
        self.id = event.get(EVENT_SOURCE_IDX)
        self._state = event[EVENT_VALUE]

        self._callbacks = []

    @property
    def state(self) -> str:
        """State of the event."""
        return self._state

    @state.setter
    def state(self, state: str) -> None:
        """Update state of event."""
        self._state = state
        for callback in self._callbacks:
            callback()

    @property
    def is_tripped(self) -> bool:
        """Event is tripped now."""
        return self.state == '1'

    def register_callback(self, callback) -> None:
        """Register callback for state updates."""
        self._callbacks.append(callback)

    def remove_callback(self, callback) -> None:
        """Remove callback."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)


# {
#     'operation': 'Initialized',
#     'topic': 'tns1:LightControl/tnsaxis:LightStatusChanged/Status',
#     'type': 'state',
#     'value': 'OFF'
# }


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
    TOPIC = 'tns1:AudioSource/tnsaxis:TriggerLevel'
    CLASS = CLASS_SOUND
    TYPE = 'Sound'

    def __init__(self, event: dict) -> None:
        super().__init__(event)


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
    TOPIC = 'tns1:VideoSource/tnsaxis:DayNightVision'
    CLASS = CLASS_LIGHT
    TYPE = 'DayNight'

    def __init__(self, event: dict) -> None:
        super().__init__(event)


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
    TOPIC = 'tns1:Device/tnsaxis:IO/Port'
    CLASS = CLASS_INPUT
    TYPE = 'Input'

    def __init__(self, event: dict) -> None:
        super().__init__(event)


class Motion(AxisBinaryEvent):
    """Motion detection event."""
    TOPIC = 'tns1:VideoAnalytics/tnsaxis:MotionDetection'
    CLASS = CLASS_MOTION
    TYPE = 'Motion'

    def __init__(self, event: dict) -> None:
        super().__init__(event)


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
    TOPIC = 'tns1:Device/tnsaxis:Sensor/PIR'
    CLASS = CLASS_MOTION
    TYPE = 'PIR'

    def __init__(self, event: dict) -> None:
        super().__init__(event)


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
    TOPIC = 'tns1:Device/Trigger/Relay'
    CLASS = CLASS_OUTPUT
    TYPE = 'Relay'

    def __init__(self, event: dict) -> None:
        super().__init__(event)

    @property
    def is_tripped(self) -> bool:
        """Event is tripped now."""
        return self.state == 'active'


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
    TOPIC = 'tns1:Device/tnsaxis:IO/SupervisedPort'
    CLASS = CLASS_INPUT
    TYPE = 'Supervised Input'

    def __init__(self, event: dict) -> None:
        super().__init__(event)


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
    TOPIC = 'tns1:RuleEngine/tnsaxis:VMD3/vmd3_video_1'
    CLASS = CLASS_MOTION
    TYPE = 'VMD3'

    def __init__(self, event: dict) -> None:
        super().__init__(event)


class Vmd4(AxisBinaryEvent):
    """Visual Motion Detection 4.

    {
        'operation': 'Initialized',
        'topic': 'tnsaxis:CameraApplicationPlatform/VMD/Camera1Profile#',
        'type': 'active',
        'value': '1'
    }
    """
    TOPIC = 'tnsaxis:CameraApplicationPlatform/VMD'
    CLASS = CLASS_MOTION
    TYPE = 'VMD4'

    def __init__(self, event: dict) -> None:
        super().__init__(event)
        self.id = event[EVENT_TOPIC].split('/')[-1]


EVENT_CLASSES = (
    Audio, DayNight, Input, Motion, Pir, Relay, SupervisedInput, Vmd3, Vmd4)


# Future events
# {
#   'operation': 'Initialized',
#   'topic': 'tnsaxis:Storage/Recording',
#   'type': 'recording',
#   'value': '0'
# }
# {
#   'operation': 'Initialized',
#   'topic': 'tnsaxis:Storage/Disruption',
#   'source': 'disk_id',
#   'source_idx': 'NetworkShare',
#   'type': 'disruption',
#   'value': '1'
# }
# {
#   'operation': 'Initialized',
#   'topic': 'tns1:Device/tnsaxis:HardwareFailure/StorageFailure',
#   'source': 'disk_id',
#   'source_idx': 'SD_DISK',
#   'type': 'disruption',
#   'value': '1'
# }
# {
#   'operation': 'Initialized',
#   'topic': 'tns1:VideoSource/tnsaxis:LiveStreamAccessed',
#   'type': 'accessed',
#   'value': '1'
# }
# {
#   'operation': 'Initialized',
#   'topic': 'tns1:Device/Trigger/DigitalInput',
#   'source': 'InputToken',
#   'source_idx': '0',
#   'type': 'LogicalState',
#   'value': 'false'
# }
# {
#   'operation': 'Initialized',
#   'topic': 'tns1:RuleEngine/MotionRegionDetector/Motion',
#   'source': 'VideoSource',
#   'source_idx': '0',
#   'type': 'State',
#   'value': '0'
# }
