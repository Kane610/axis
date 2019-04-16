"""Python library to enable Axis devices to integrate with Home Assistant."""

import logging
import re

from .utils import session_request

_LOGGER = logging.getLogger(__name__)

# Topics
AUDIO = 'tns1:AudioSource/tnsaxis:TriggerLevel'
DAYNIGHT = 'tns1:VideoSource/tnsaxis:DayNightVision'
MOTION = 'tns1:VideoAnalytics/tnsaxis:MotionDetection'
PIR = 'tns1:Device/tnsaxis:Sensor/PIR'
VMD3 = 'tns1:RuleEngine/tnsaxis:VMD3/vmd3_video_1'
VMD4 = 'tnsaxis:CameraApplicationPlatform/VMD'

BINARY_EVENT = [AUDIO, DAYNIGHT, MOTION, PIR, VMD3, VMD4]

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

EVENT_NAME = '{topic}_{source}'


class EventManager(object):
    """Initialize new events and update states of existing events."""

    def __init__(self, event_types, signal):
        """Ready information about events."""
        self.signal = signal
        self.events = {}
        self.query = self.create_event_query(event_types)

    def create_event_query(self, events) -> str:
        """Take a list of event types and return a query string."""
        if events is False or events == 'off':
            return 'off'

        if events is True or events == 'on':
            return 'on'

    def new_event(self, event_data) -> None:
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

        if event[EVENT_OPERATION] == 'Initialized' and supported_event(event):
            new_event = create_event(event)

            if name not in self.events:
                self.events[name] = new_event
                self.signal('add', new_event)

        elif event[EVENT_OPERATION] == 'Changed' and name in self.events:
            self.events[name].state = event[EVENT_VALUE]

            # elif operation == 'Deleted':
            #     _LOGGER.debug("Deleted event from stream")


class AxisBinaryEvent:
    """"""
    event_class = None
    event_type = None
    binary = True

    def __init__(self, event):
        self.topic = event[EVENT_TOPIC]
        self.source = event.get(EVENT_SOURCE)
        self.id = event.get(EVENT_SOURCE_IDX)
        self._state = event[EVENT_VALUE]

        self._callbacks = []

    @property
    def state(self):
        """State of the event."""
        return self._state

    @state.setter
    def state(self, state):
        """Update state of event."""
        self._state = state
        for callback in self._callbacks:
            callback()

    @property
    def is_tripped(self):
        """Event is tripped now."""
        return self._state == '1'

    def register_callback(self, callback):
        """Register callback for state updates."""
        self._callbacks.append(callback)

    def remove_callback(self, callback):
        """Remove callback."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    def as_dict(self):
        """Callback for __dict__."""
        cdict = self.__dict__.copy()
        if '_callbacks' in cdict:
            del cdict['_callbacks']
        return cdict


# {'operation': 'Initialized', 'topic': 'tns1:LightControl/tnsaxis:LightStatusChanged/Status', 'type': 'state', 'value': 'OFF'}


class AudioEvent(AxisBinaryEvent):
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
    event_class = 'sound'
    event_type = 'Sound'

    def __init__(self, event):
        super().__init__(event)


class DayNightEvent(AxisBinaryEvent):
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
    event_class = 'light'
    event_type = 'DayNight'

    def __init__(self, event):
        super().__init__(event)


class MotionEvent(AxisBinaryEvent):
    """Motion detection event."""
    event_class = 'motion'
    event_type = 'Motion'

    def __init__(self, event):
        super().__init__(event)


class PirEvent(AxisBinaryEvent):
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
    event_class = 'motion'
    event_type = 'PIR'

    def __init__(self, event):
        super().__init__(event)


class Vmd3Event(AxisBinaryEvent):
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
    event_class = 'motion'
    event_type = 'VMD3'

    def __init__(self, event):
        super().__init__(event)



class Vmd4Event(AxisBinaryEvent):
    """Visual Motion Detection 4.

    {
        'operation': 'Initialized',
        'topic': 'tnsaxis:CameraApplicationPlatform/VMD/Camera1Profile#',
        'type': 'active',
        'value': '1'
    }
    """
    event_class = 'motion'
    event_type = 'VMD4'

    def __init__(self, event):
        super().__init__(event)
        self.id = event[EVENT_TOPIC].split('/')[-1]


def create_event(event):
    """Create event based on its topic."""
    if event[EVENT_TOPIC] in AUDIO:
        return AudioEvent(event)
    if event[EVENT_TOPIC] in DAYNIGHT:
        return DayNightEvent(event)
    if event[EVENT_TOPIC] in MOTION:
        return MotionEvent(event)
    if event[EVENT_TOPIC] in PIR:
        return PirEvent(event)
    if event[EVENT_TOPIC] in VMD3:
        return Vmd3Event(event)
    if VMD4 in event[EVENT_TOPIC]:
        return Vmd4Event(event)


def supported_event(event):
    """Check if event is supported by Axis."""
    for topic in BINARY_EVENT:
        if topic in event[EVENT_TOPIC]:
            return True
    _LOGGER.debug('Unsupported event %s', event[EVENT_TOPIC])
    return False
