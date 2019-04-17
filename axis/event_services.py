"""Event service and action service APIs available in Axis network products."""

import logging
from copy import deepcopy

from .utils import session_request

_LOGGER = logging.getLogger(__name__)

MAP_BASE = 'base'
MAP_CLASS = 'class'
MAP_PLATFORM = 'platform'
MAP_SUBSCRIBE = 'subscribe'
MAP_TOPIC = 'topic'
MAP_TYPE = 'type'

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
