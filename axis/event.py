"""Python library to enable Axis devices to integrate with Home Assistant."""

import logging
import re

from copy import deepcopy

from .utils import session_request

_LOGGER = logging.getLogger(__name__)

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

    def translate(self, item, key, to_key=None):
        """Translate between Axis and HASS syntax.

        If to_key is omitted full entry will be returned.
        Type: configuration value for event manager.
        Class: what class should event belong to in HASS.
        Platform: which HASS platform this event belongs to.
        Topic: event topic to look for when receiving events.
        Subscribe: subscription form of event topic.
        """
        for entry in self.event_map:
            if entry[key] == item:
                if to_key:
                    return entry[to_key]
                return entry
        return None

    def new_map_entry(self, item):
        """Create new map entry based on item.

        Returns a copy of the entry.
        """
        for entry in METAMAP:
            if entry[EVENT_TOPIC] in item:
                entry_copy = deepcopy(entry)
                entry_copy[EVENT_TOPIC] = item
                self.event_map.append(entry_copy)
                return entry_copy
        return

    def create_event_query(self, event_types):
        """Take a list of event types and return a query string."""
        if not event_types:
            return 'off'
        topics = [event['subscribe']
                  for event in self.event_map + METAMAP
                  if event['type'] in event_types]
        return 'on&eventtopic={}'.format('|'.join(topics))

    def _parse_event(self, event_data):
        """Parse metadata xml."""
        output = {}

        data = event_data.decode()

        message = MESSAGE.search(data)
        if not message:
            return {}
        output[EVENT_OPERATION] = message.group(EVENT_OPERATION)

        topic = TOPIC.search(data)
        if topic:
            output[EVENT_TOPIC] = topic.group(EVENT_TOPIC)

        source = SOURCE.search(data)
        if source:
            output[EVENT_SOURCE] = source.group(EVENT_SOURCE)
            output[EVENT_SOURCE_IDX] = source.group(EVENT_SOURCE_IDX)

        data = DATA.search(data)
        if data:
            output[EVENT_TYPE] = data.group(EVENT_TYPE)
            output[EVENT_VALUE] = data.group(EVENT_VALUE)

        _LOGGER.debug(output)

        return output

    def manage_event(self, event_data):
        """Received new metadata.

        Operation missing means this is the first message in stream.
        Operation initialized means new event, also happens if reconnecting.
        Operation changed updates existing events state.
        """
        data = self._parse_event(event_data)
        operation = data.get(EVENT_OPERATION)

        if operation:
            event_name = EVENT_NAME.format(
                topic=data[EVENT_TOPIC], source=data.get(EVENT_SOURCE_IDX))

        if operation == 'Initialized':
            description = self.translate(data[EVENT_TOPIC], EVENT_TOPIC)

            if not description:
                description = self.new_map_entry(data[EVENT_TOPIC])

            new_event = AxisEvent(data, description)

            if event_name not in self.events:
                self.events[event_name] = new_event
                self.signal('add', new_event)

        elif operation == 'Changed':
            self.events[event_name].state = data[EVENT_VALUE]

        elif operation == 'Deleted':
            _LOGGER.debug("Deleted event from stream")


class AxisEvent(object):  # pylint: disable=R0904
    """Class to represent each Axis device event."""

    def __init__(self, data, description):
        """Set up Axis event."""
        _LOGGER.info("New AxisEvent %s", data)
        self.topic = data[EVENT_TOPIC]
        self.source = data.get(EVENT_SOURCE)
        self.id = data.get(EVENT_SOURCE_IDX)

        self.event_class = description[MAP_CLASS]
        self.event_type = description[MAP_TYPE]
        self.event_platform = description[MAP_PLATFORM]

        self._state = None
        self.callback = None

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


def device_events(config):
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


def create_topics(event_map):
    """"""
    topics = []
    for entry in event_map:
        topic = []
        for namespace, item_list in entry[MAP_BASE].items():
            topic.append('{}:{}'.format(namespace, '/'.join(item_list)))
        topics.append('/'.join(topic))
    return topics


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
