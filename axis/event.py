"""Python library to enable Axis devices to integrate with Home Assistant."""

import logging
import re

MESSAGE = re.compile(r'(?<=PropertyOperation)="(?P<operation>\w+)"')
TOPIC = re.compile(r'(?<=<wsnt:Topic).*>(?P<topic>.*)(?=<\/wsnt:Topic>)')
SOURCE = re.compile(r'(?<=<tt:Source>).*Name="(?P<name>\w+)"' +
                    r'.*Value="(?P<value>\w+)".*(?=<\/tt:Source>)')
DATA = re.compile(r'(?<=<tt:Data>).*Name="(?P<name>\w*)"' +
                  r'.*Value="(?P<value>\w*)".*(?=<\/tt:Data>)')

_LOGGER = logging.getLogger(__name__)


class EventManager(object):
    """Initialize new events and update states of existing events."""

    def __init__(self, event_types, signal):
        """Ready information about events."""
        self.signal = signal
        self.events = {}
        self.query = self.create_event_query(event_types)

    def create_event_query(self, event_types):
        """Take a list of event types and return a query string."""
        if event_types:
            topics = None
            for event in event_types:
                topic = convert(event, 'type', 'subscribe')
                if topics is None:
                    topics = topic
                else:
                    topics = '{}|{}'.format(topics, topic)
            topic_query = '&eventtopic={}'.format(topics)
            return 'on' + topic_query
        return 'off'

    def parse_event(self, event_data):
        """Parse metadata xml."""
        output = {}

        data = event_data.decode()

        message = MESSAGE.search(data)
        if message:
            output['Operation'] = message.group('operation')

        topic = TOPIC.search(data)
        if topic:
            output['Topic'] = topic.group('topic')

        source = SOURCE.search(data)
        if source:
            output['Source_name'] = source.group('name')
            output['Source_value'] = source.group('value')

        data = DATA.search(data)
        if data:
            output['Data_name'] = data.group('name')
            output['Data_value'] = data.group('value')

        _LOGGER.debug(output)

        return output

    def manage_event(self, event_data):
        """Received new metadata.

        Operation missing means this is the first message in stream.
        Operation initialized means new event, also happens if reconnecting.
        Operation changed updates existing events state.
        """
        data = self.parse_event(event_data)
        operation = data.get('Operation')

        if operation == 'Initialized':
            new_event = AxisEvent(data)
            if new_event.name not in self.events:
                self.events[new_event.name] = new_event
                if self.signal:
                    self.signal('add', new_event)

        elif operation == 'Changed':
            event_name = '{}_{}'.format(data['Topic'], data['Source_value'])
            self.events[event_name].state = data['Data_value']

        elif operation == 'Deleted':
            _LOGGER.debug("Deleted event from stream")
            # ToDo:
            # keep a list of deleted events and a follow up timer of X,
            # then clean up. This should also take care of rebooting a camera


class AxisEvent(object):  # pylint: disable=R0904
    """Class to represent each Axis device event."""

    def __init__(self, data):
        """Set up Axis event."""
        _LOGGER.info("New AxisEvent %s", data)
        self.topic = data['Topic']
        self.id = data['Source_value']
        self.type = data['Data_name']
        self.source = data['Source_name']
        self.name = '{}_{}'.format(self.topic, self.id)

        self._state = None
        self.callback = None

    @property
    def event_class(self):
        """Class event should belong to in HASS."""
        return convert(self.topic, 'topic', 'class')

    @property
    def event_type(self):
        """Use to configure what events to subscribe to in event manager."""
        return convert(self.topic, 'topic', 'type')

    @property
    def event_platform(self):
        """Which HASS platform this event belongs to."""
        return convert(self.topic, 'topic', 'platform')

    @property
    def state(self):
        """State of the event."""
        return self._state

    @state.setter
    def state(self, state):
        """Update state of event."""
        self._state = state
        if self.callback:
            self.callback()

    @property
    def is_tripped(self):
        """Event is tripped now."""
        return self._state == '1'

    def as_dict(self):
        """Callback for __dict__."""
        cdict = self.__dict__.copy()
        if 'callback' in cdict:
            del cdict['callback']
        return cdict


def convert(item, from_key, to_key):
    """Translate between Axis and HASS syntax.

    Type: configuration value for event manager.
    Class: what class should event belong to in HASS.
    Platform: which HASS platform this event belongs to.
    Topic: event topic to look for when receiving events.
    Subscribe: subscription form of event topic.
    """
    result = None
    for entry in REMAP:
        if entry[from_key] == item:
            result = entry[to_key]
            break
    return result


#tnsaxis: CameraApplicationPlatform/VMD//
#tns1:VideoSource/MotionAlarm//.
REMAP = [{'type': 'motion',
          'class': 'motion',
          'platform': 'binary_sensor',
          'topic': 'tns1:VideoAnalytics/tnsaxis:MotionDetection',
          'subscribe': 'onvif:VideoAnalytics/axis:MotionDetection'},
         {'type': 'vmd3',
          'class': 'motion',
          'platform': 'binary_sensor',
          'topic': 'tns1:RuleEngine/tnsaxis:VMD3/vmd3_video_1',
          'subscribe': 'onvif:RuleEngine/axis:VMD3/vmd3_video_1'},
         {'type': 'pir',
          'class': 'motion',
          'platform': 'binary_sensor',
          'topic': 'tns1:Device/tnsaxis:Sensor/PIR',
          'subscribe': 'onvif:Device/axis:Sensor/axis:PIR'},
         {'type': 'sound',
          'class': 'sound',
          'platform': 'binary_sensor',
          'topic': 'tns1:AudioSource/tnsaxis:TriggerLevel',
          'subscribe': 'onvif:AudioSource/axis:TriggerLevel'},
         {'type': 'daynight',
          'class': 'light',
          'platform': 'binary_sensor',
          'topic': 'tns1:VideoSource/tnsaxis:DayNightVision',
          'subscribe': 'onvif:VideoSource/axis:DayNightVision'},
         {'type': 'tampering',
          'class': 'safety',
          'platform': 'binary_sensor',
          'topic': 'tns1:VideoSource/tnsaxis:Tampering',
          'subscribe': 'onvif:VideoSource/axis:Tampering'},
         {'type': 'input',
          'class': 'input',
          'platform': 'binary_sensor',
          'topic': 'tns1:Device/tnsaxis:IO/Port',
          'subscribe': 'onvif:Device/axis:IO/Port'}
        ]
