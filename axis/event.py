"""Python library to enable Axis devices to integrate with Home Assistant."""

import logging
import re

from .utils import session_request

_LOGGER = logging.getLogger(__name__)

MESSAGE = re.compile(r'(?<=PropertyOperation)="(?P<operation>\w+)"')
TOPIC = re.compile(r'(?<=<wsnt:Topic).*>(?P<topic>.*)(?=<\/wsnt:Topic>)')
SOURCE = re.compile(r'(?<=<tt:Source>).*Name="(?P<name>\w+)"' +
                    r'.*Value="(?P<value>\w+)".*(?=<\/tt:Source>)')
DATA = re.compile(r'(?<=<tt:Data>).*Name="(?P<name>\w*)"' +
                  r'.*Value="(?P<value>\w*)".*(?=<\/tt:Data>)')

EVENT_NAME = '{topic}_{source}'


class EventManager(object):
    """Initialize new events and update states of existing events."""

    def __init__(self, event_types, signal):
        """Ready information about events."""
        self.signal = signal
        self.events = {}
        self.event_map = REMAP
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
        if re.search(r'^tnsaxis:CameraApplicationPlatform/VMD', item):
            topic, profile = item.rsplit('/', 1)
            index = re.findall(r'\d+|ANY$', profile)
            from copy import deepcopy
            for entry in MAPPING:
                if topic == entry['topic']:
                    entry_copy = deepcopy(entry)
                    entry_copy['topic'] = item
                    entry_copy['source'] = '{}_{}'.format(index[0], index[1])
                    self.event_map.append(entry_copy)
                    return entry_copy
                return None


    def create_event_query(self, event_types):
        """Take a list of event types and return a query string."""
        if not event_types:
            return 'off'
        topics = [event['subscribe']
                  for event in self.event_map + MAPPING
                  if event['type'] in event_types]
        return 'on&eventtopic={}'.format('|'.join(topics))

    def _parse_event(self, event_data):
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
        else:
            output['Source_name'] = 'VMD4'
            output['Source_value'] = 0

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
        data = self._parse_event(event_data)
        operation = data.get('Operation')

        if operation == 'Initialized':
            description = self.translate(data['Topic'], 'topic')
            if not description:
                description = self.new_map_entry(data['Topic'])
                data['Source_value'] = description['source']
            new_event = AxisEvent(data, description)
            if new_event.name not in self.events:
                self.events[new_event.name] = new_event
                self.signal('add', new_event)

        elif operation == 'Changed':
            event_name = EVENT_NAME.format(
                topic=data['Topic'], source=data['Source_value'])
            self.events[event_name].state = data['Data_value']

        elif operation == 'Deleted':
            _LOGGER.debug("Deleted event from stream")
            # ToDo:
            # keep a list of deleted events and a follow up timer of X,
            # then clean up. This should also take care of rebooting a camera


class AxisEvent(object):  # pylint: disable=R0904
    """Class to represent each Axis device event."""

    def __init__(self, data, description):
        """Set up Axis event."""
        _LOGGER.info("New AxisEvent %s", data)
        self.topic = data['Topic']
        self.id = data['Source_value']
        self.type = data['Data_name']
        self.source = data['Source_name']
        self.event_class = description['class']
        self.event_type = description['type']
        self.event_platform = description['platform']
        self.event_name = description.get('name')  # Only VMD4
        self.name = EVENT_NAME.format(topic=self.topic, source=self.id)

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


REMAP = [{'type': 'motion',
          'class': 'motion',
          'platform': 'binary_sensor',
          'base': {'onvif': ['VideoAnalytics'], 'axis': ['MotionDetection']},
          'topic': 'tns1:VideoAnalytics/tnsaxis:MotionDetection',
          'subscribe': 'onvif:VideoAnalytics/axis:MotionDetection'},
         {'type': 'vmd3',
          'class': 'motion',
          'platform': 'binary_sensor',
          'base': {'onvif': ['RuleEngine'], 'axis': ['VMD3', 'vmd3_video_1']},
          'topic': 'tns1:RuleEngine/tnsaxis:VMD3/vmd3_video_1',
          'subscribe': 'onvif:RuleEngine/axis:VMD3/vmd3_video_1'},
         {'type': 'pir',
          'class': 'motion',
          'platform': 'binary_sensor',
          'base': {'onvif': ['Device'], 'axis': ['Sensor', 'PIR']},
          'topic': 'tns1:Device/tnsaxis:Sensor/PIR',
          'subscribe': 'onvif:Device/axis:Sensor/PIR'},
         {'type': 'sound',
          'class': 'sound',
          'platform': 'binary_sensor',
          'base': {'onvif': ['AudioSource'], 'axis': ['TriggerLevel']},
          'topic': 'tns1:AudioSource/tnsaxis:TriggerLevel',
          'subscribe': 'onvif:AudioSource/axis:TriggerLevel'},
         {'type': 'daynight',
          'class': 'light',
          'platform': 'binary_sensor',
          'base': {'onvif': ['VideoSource'], 'axis': ['DayNightVision']},
          'topic': 'tns1:VideoSource/tnsaxis:DayNightVision',
          'subscribe': 'onvif:VideoSource/axis:DayNightVision'},
         {'type': 'tampering',
          'class': 'safety',
          'platform': 'binary_sensor',
          'base': {'onvif': ['VideoSource'], 'axis': ['Tampering']},
          'topic': 'tns1:VideoSource/tnsaxis:Tampering',
          'subscribe': 'onvif:VideoSource/axis:Tampering'},
         {'type': 'input',
          'class': 'input',
          'platform': 'binary_sensor',
          'base': {'onvif': ['Device'], 'axis':['IO', 'Port']},
          'topic': 'tns1:Device/tnsaxis:IO/Port',
          'subscribe': 'onvif:Device/axis:IO/Port'}
        ]

MAPPING = [{'type': 'vmd4',
            'class': 'motion',
            'platform': 'binary_sensor',
            'base': {'axis': ['CameraApplicationPlatform', 'VMD']},
            'topic': 'tnsaxis:CameraApplicationPlatform/VMD',
            'subscribe': 'axis:CameraApplicationPlatform/VMD//.'}]


device_event_url = '{}://{}:{}/vapix/services'
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
            config.web_proto, config.host, config.port),
        auth=config.session.auth, headers=headers, data=request_xml)

    raw_event_list = _prepare_event(eventinstances)

    event_list = {}
    for entry in REMAP + MAPPING:
        instance = raw_event_list
        try:
            for item in sum(entry['base'].values(), []):
                instance = instance[item]
        except KeyError:
            continue
        event_list[entry['type']] = instance
    return event_list


def device_map(event_list):
    """Create a map of device supported events.

    event_list is output from device_events.
    Event_map can be used to replace event_map in event_manager.
    """
    event_map = []
    for entry in REMAP + MAPPING:
        if entry['type'] in event_list and entry['type'] == 'vmd4':
            for profile, instance in event_list['vmd4'].items():
                if re.search(r'^Camera[0-9]Profile[0-9]$', profile):
                    from copy import deepcopy
                    entry_copy = deepcopy(entry)
                    entry_copy['base']['axis'].append(profile)
                    entry_copy['name'] = instance['NiceName']
                    entry_copy['subscribe'] = entry_copy['subscribe'].format(
                        profile)
                    entry_copy['topic'] = entry_copy['topic'].format(profile)
                    event_map.append(entry_copy)
        elif entry['type'] in event_list:
            event_map.append(entry)
    return event_map


def create_topics(event_map):
    """"""
    topics = []
    for entry in event_map:
        topic = []
        for namespace, item_list in entry['base'].items():
            topic.append('{}:{}'.format(namespace, '/'.join(item_list)))
        topics.append('/'.join(topic))
    return topics


def _prepare_event(eventinstances):
    """"""
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
