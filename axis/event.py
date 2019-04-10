"""Python library to enable Axis devices to integrate with Home Assistant."""

import logging
import re

from copy import deepcopy

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

MAP_BASE = 'base'
MAP_CLASS = 'class'
MAP_PLATFORM = 'platform'
MAP_SUBSCRIBE = 'subscribe'
MAP_TOPIC = 'topic'
MAP_TYPE = 'type'

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
        self.event_map = MAP
        self.query = self.create_event_query(event_types)

    def create_event_query(self, events) -> str:
        """Take a list of event types and return a query string."""
        if events is False or events == 'off':
            return 'off'

        if events is True or events == 'on':
            return 'on'

        topics = [event['subscribe']
                  for event in self.event_map + METAMAP
                  if event['type'] in events]

        return 'on&eventtopic={}'.format('|'.join(topics))

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

    def __init__(self, event):
        """"""
        super().__init__(event)

        self.event_class = 'sound'
        self.event_type = 'Sound'


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

    def __init__(self, event):
        """"""
        super().__init__(event)

        self.event_class = 'light'
        self.event_type = 'DayNight'


class MotionEvent(AxisBinaryEvent):
    """Motion detection event."""

    def __init__(self, event):
        """"""
        super().__init__(event)

        self.event_class = 'motion'
        self.event_type = 'Motion'


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

    def __init__(self, event):
        """"""
        super().__init__(event)

        self.event_class = 'motion'
        self.event_type = 'PIR'


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

    def __init__(self, event):
        """"""
        super().__init__(event)

        self.event_class = 'motion'
        self.event_type = 'VMD3'



class Vmd4Event(AxisBinaryEvent):
    """Visual Motion Detection 4.

    {
        'operation': 'Initialized',
        'topic': 'tnsaxis:CameraApplicationPlatform/VMD/Camera1Profile#',
        'type': 'active',
        'value': '1'
    }
    """

    def __init__(self, event):
        """"""
        super().__init__(event)
        self.id = event[EVENT_TOPIC].split('/')[-1]

        self.event_class = 'motion'
        self.event_type = 'VMD4'


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

MAP = [
    {
        MAP_TYPE: 'motion',
        MAP_CLASS: 'motion',
        MAP_PLATFORM: 'binary_sensor',
        MAP_BASE: {'onvif': ['VideoAnalytics'], 'axis': ['MotionDetection']},
        MAP_TOPIC: 'tns1:VideoAnalytics/tnsaxis:MotionDetection',
        MAP_SUBSCRIBE: 'onvif:VideoAnalytics/axis:MotionDetection'},
    {
        MAP_TYPE: 'vmd3',
        MAP_CLASS: 'motion',
        MAP_PLATFORM: 'binary_sensor',
        MAP_BASE: {'onvif': ['RuleEngine'], 'axis': ['VMD3', 'vmd3_video_1']},
        MAP_TOPIC: 'tns1:RuleEngine/tnsaxis:VMD3/vmd3_video_1',
        MAP_SUBSCRIBE: 'onvif:RuleEngine/axis:VMD3/vmd3_video_1'},
    {
        MAP_TYPE: 'pir',
        MAP_CLASS: 'motion',
        MAP_PLATFORM: 'binary_sensor',
        MAP_BASE: {'onvif': ['Device'], 'axis': ['Sensor', 'PIR']},
        MAP_TOPIC: 'tns1:Device/tnsaxis:Sensor/PIR',
        MAP_SUBSCRIBE: 'onvif:Device/axis:Sensor/PIR'},
    {
        MAP_TYPE: 'sound',
        MAP_CLASS: 'sound',
        MAP_PLATFORM: 'binary_sensor',
        MAP_BASE: {'onvif': ['AudioSource'], 'axis': ['TriggerLevel']},
        MAP_TOPIC: 'tns1:AudioSource/tnsaxis:TriggerLevel',
        MAP_SUBSCRIBE: 'onvif:AudioSource/axis:TriggerLevel'},
    {
        MAP_TYPE: 'daynight',
        MAP_CLASS: 'light',
        MAP_PLATFORM: 'binary_sensor',
        MAP_BASE: {'onvif': ['VideoSource'], 'axis': ['DayNightVision']},
        MAP_TOPIC: 'tns1:VideoSource/tnsaxis:DayNightVision',
        MAP_SUBSCRIBE: 'onvif:VideoSource/axis:DayNightVision'},
    {
        MAP_TYPE: 'tampering',
        MAP_CLASS: 'safety',
        MAP_PLATFORM: 'binary_sensor',
        MAP_BASE: {'onvif': ['VideoSource'], 'axis': ['Tampering']},
        MAP_TOPIC: 'tns1:VideoSource/tnsaxis:Tampering',
        MAP_SUBSCRIBE: 'onvif:VideoSource/axis:Tampering'},
    {
        MAP_TYPE: 'input',
        MAP_CLASS: 'input',
        MAP_PLATFORM: 'binary_sensor',
        MAP_BASE: {'onvif': ['Device'], 'axis':['IO', 'Port']},
        MAP_TOPIC: 'tns1:Device/tnsaxis:IO/Port',
        MAP_SUBSCRIBE: 'onvif:Device/axis:IO/Port'
    }
]

METAMAP = [
    {
        MAP_TYPE: 'vmd4',
        MAP_CLASS: 'motion',
        MAP_PLATFORM: 'binary_sensor',
        MAP_BASE: {'axis': ['CameraApplicationPlatform', 'VMD']},
        MAP_TOPIC: 'tnsaxis:CameraApplicationPlatform/VMD',
        MAP_SUBSCRIBE: 'axis:CameraApplicationPlatform/VMD//.'
    }
]


device_event_url = '{proto}://{host}:{port}/vapix/services'
headers = {'Content-Type': 'application/soap+xml',
            'SOAPAction': 'http://www.axis.com/vapix/ws/event1/GetEventInstances'}
request_xml = ("<s:Envelope xmlns:s=\"http://www.w3.org/2003/05/soap-envelope\">"
                "<s:Body xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" "
                "xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\">"
                "<GetEventInstances xmlns=\"http://www.axis.com/vapix/ws/event1\"/>"
                "</s:Body>"
                "</s:Envelope>")


def get_event_list(config):
    """Get a dict of supported events from device."""
    eventinstances = session_request(
        config.session.post, device_event_url.format(
            proto=config.web_proto, host=config.host, port=config.port),
        auth=config.session.auth, headers=headers, data=request_xml)

    raw_event_list = _prepare_event(eventinstances)

    event_list = {}
    for entry in MAP + METAMAP:
        instance = raw_event_list
        try:
            for item in sum(entry[MAP_BASE].values(), []):
                instance = instance[item]
        except KeyError:
            continue
        event_list[entry[MAP_TYPE]] = instance

    return event_list


# def device_map(event_list):
#     """Create a map of device supported events.

#     event_list is output from device_events.
#     Event_map can be used to replace event_map in event_manager.
#     """
#     event_map = []
#     for entry in MAP + METAMAP:
#         if entry[MAP_TYPE] in event_list and entry[MAP_TYPE] == 'vmd4':
#             for profile, instance in event_list['vmd4'].items():
#                 if re.search(r'^Camera[0-9]Profile[0-9]$', profile):
#                     from copy import deepcopy
#                     entry_copy = deepcopy(entry)
#                     entry_copy[MAP_BASE]['axis'].append(profile)
#                     entry_copy['name'] = instance['NiceName']
#                     entry_copy[MAP_SUBSCRIBE] = entry_copy[MAP_SUBSCRIBE].format(
#                         profile)
#                     entry_copy[MAP_TOPIC] = entry_copy[MAP_TOPIC].format(profile)
#                     event_map.append(entry_copy)
#         elif entry[MAP_TYPE] in event_list:
#             event_map.append(entry)
#     return event_map


# def create_topics(event_map):
#     """"""
#     topics = []
#     for entry in event_map:
#         topic = []
#         for namespace, item_list in entry[MAP_BASE].items():
#             topic.append('{}:{}'.format(namespace, '/'.join(item_list)))
#         topics.append('/'.join(topic))
#     return topics


def _prepare_event(eventinstances):
    """Converts event instances to a relevant dictionary."""
    import xml.etree.ElementTree as ET

    def parse_event(events):
        """Find all events inside of an topicset list.

        MessageInstance signals that subsequent children will
        contain source and data descriptions.
        """

        def clean_attrib(attrib={}):
            """Clean up child attributes by removing XML namespace."""
            attributes = {}
            for key, value in attrib.items():
                attributes[key.split('}')[-1]] = value
            return attributes

        description = {}
        for child in events:
            child_tag = child.tag.split('}')[-1]
            child_attrib = clean_attrib(child.attrib)
            if child_tag != 'MessageInstance':
                description[child_tag] = {
                    **child_attrib, **parse_event(child)}
            elif child_tag == 'MessageInstance':
                description = {}
                for item in child:
                    tag = item.tag.split('}')[-1]
                    description[tag] = clean_attrib(item[0].attrib)
        return description

    root = ET.fromstring(eventinstances)
    return parse_event(root[0][0][0])
