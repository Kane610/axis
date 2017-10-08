import asyncio
import logging
import re

import requests
from requests.auth import HTTPDigestAuth  # , HTTPBasicAuth

try:
    from .rtsp import RTSPClient
except SystemError:
    from rtsp import RTSPClient


# import aiohttp
# PYTHON RTSP INSPIRATION
# https://github.com/timohoeting/python-mjpeg-over-rtsp-client/blob/master/rtsp_client.py
# http://codegist.net/snippet/python/rtsp_authenticationpy_crayfishapps_python
# https://github.com/perexg/satip-axe/blob/master/tools/multicast-rtp


_LOGGER = logging.getLogger(__name__)

STATE_STARTING = 'starting'
STATE_PLAYING = 'playing'
STATE_STOPPED = 'stopped'
STATE_PAUSED = 'paused'

MESSAGE = re.compile('(?<=PropertyOperation)="(?P<operation>\w+)"')
TOPIC = re.compile('(?<=<wsnt:Topic).*>(?P<topic>.*)(?=<\/wsnt:Topic>)')
SOURCE = re.compile('(?<=<tt:Source>).*Name="(?P<name>\w+)"' +
                    '.*Value="(?P<value>\w+)".*(?=<\/tt:Source>)')
DATA = re.compile('(?<=<tt:Data>).*Name="(?P<name>\w*)"' +
                  '.*Value="(?P<value>\w*)".*(?=<\/tt:Data>)')


class AxisEvent(object):  # pylint: disable=R0904
    """Class to represent each Axis device event.
    """

    def __init__(self, data):
        """Setup an Axis event.
        """
        _LOGGER.info("New AxisEvent {}".format(data))
        self.topic = data['Topic']
        self.id = data['Source_value']
        self.type = data['Data_name']
        self.source = data['Source_name']
        self.name = '{}_{}'.format(self.topic, self.id)

        self._state = None
        self.callback = None

    @property
    def event_class(self):
        """
        """
        return convert(self.topic, 'topic', 'class')

    @property
    def event_type(self):
        """
        """
        return convert(self.topic, 'topic', 'type')

    @property
    def event_platform(self):
        """
        """
        return convert(self.topic, 'topic', 'platform')

    @property
    def state(self):
        """The State of the event.
        """
        return self._state

    @state.setter
    def state(self, state):
        """Update state of event.
        """
        print(state)
        self._state = state
        if self.callback:
            self.callback()

    @property
    def is_tripped(self):
        """Event is tripped now.
        """
        return self._state == '1'

    def as_dict(self):
        """Callback for __dict__.
        """
        cdict = self.__dict__.copy()
        if 'callback' in cdict:
            del cdict['callback']
        return cdict


class EventManager(object):
    """Initialize new events and update states of existing events
    """

    def __init__(self, event_types, signal):
        """Ready information about events
        """
        self.signal = signal
        self.events = {}
        self.query = self.create_event_query(event_types)

    def create_event_query(self, event_types):
        """Takes a list of event types and returns a query string
        """
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
        else:
            return 'off'

    def parse_event(self, event_data):
        """Parse metadata xml.
        """
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
        Operation missing means this is the first message in stream
        Operation initialized means new event, will also happen if reconnecting
        Operation changed updates existing events state
        """
        data = self.parse_event(event_data)
        if 'Operation' not in data:
            return False

        elif data['Operation'] == 'Initialized':
            new_event = AxisEvent(data)
            if new_event.name not in self.events:
                self.events[new_event.name] = new_event
                if self.signal:
                    self.signal('add', new_event)

        elif data['Operation'] == 'Changed':
            event_name = '{}_{}'.format(data['Topic'], data['Source_value'])
            self.events[event_name].state = data['Data_value']

        elif data['Operation'] == 'Deleted':
            _LOGGER.debug("Deleted event from stream")
            # ToDo:
            # keep a list of deleted events and a follow up timer of X,
            # then clean up. This should also take care of rebooting a camera

        else:
            _LOGGER.warning("Unexpected response: %s", data)


class StreamManager(object):
    """Setup, start, stop and retry stream
    """

    @asyncio.coroutine
    def __init__(self):
        """Start stream if any event type is specified
        """
        # self.config
        self.video = None  # Unsupported
        self.audio = None  # Unsupported
        self.event = EventManager(self.config.event_types, self.config.signal)
        self.stream = None
        if self.event != 'off':
            self.start()

    @property
    def stream_url(self):
        """Build url for stream
        """
        rtsp = 'rtsp://{}/axis-media/media.amp'.format(self.config.host)
        source = '?video={0}&audio={1}&event={2}'.format(self.video_query,
                                                         self.audio_query,
                                                         self.event.query)
        _LOGGER.debug(rtsp + source)
        return rtsp + source

    @property
    def video_query(self):
        """Generate video query, not supported
        """
        return 0

    @property
    def audio_query(self):
        """Generate audio query, not supported
        """
        return 0

    def session_callback(self, signal):
        """Signalling from stream session.
           Data - new data available for processing
           Retry - if there is no connection to device.
        """
        if signal == 'data':
            self.event.manage_event(self.data)
        elif signal == 'retry':
            self.retry()

    @property
    def data(self):
        """Get stream data.
        """
        return self.stream.rtp.data

    def start(self):
        """Start stream.
        """
        if not self.stream or self.stream.session.state == STATE_STOPPED:
            self.stream = RTSPClient(self.config.loop,
                                     self.stream_url,
                                     self.config.host,
                                     self.config.username,
                                     self.config.password,
                                     self.session_callback)

    def stop(self):
        """Stop stream.
        """
        if self.stream and self.stream.session.state != STATE_STOPPED:
            self.stream.stop()

    def retry(self):
        """No connection to device, retry connection after 15 seconds.
        """
        self.stream = None
        self.config.loop.call_later(15, self.start)
        _LOGGER.debug('Reconnecting to %s', self.config.host)


PARAM_URL = 'http://{}:{}/axis-cgi/{}?action={}&{}'


class Vapix(object):
    """Vapix parameter request
    """

    def __init__(self, config):
        """Store local reference to device config
        """
        self.config = config

    def get_param(self, param):
        """Get parameter and remove descriptive part of response.
        """
        cgi = 'param.cgi'
        action = 'list'
        try:
            r = self.do_request(cgi, action, 'group=' + param)
        except requests.ConnectionError:
            return None
        except requests.exceptions.HTTPError:
            return None
        v = {}
        for s in filter(None, r.split('\n')):
            key, value = s.split('=')
            v[key] = value
        if len(v.items()) == 1:
            return v[param]
        else:
            return v

    def do_request(self, cgi, action, param):
        """Do HTTP request and return response as dictionary.
        """
        url = PARAM_URL.format(self.config.host, self.config.port, cgi, action, param)
        auth = HTTPDigestAuth(self.config.username, self.config.password)
        try:
            r = requests.get(url, auth=auth)
            r.raise_for_status()
        except requests.ConnectionError as err:
            _LOGGER.error("Connection error: %s", err)
            raise
        except requests.exceptions.HTTPError as err:
            _LOGGER.error("HTTP error: %s", err)
            raise
        _LOGGER.debug('Request response: %s from %s', r.text, self.config.host)
        return r.text


class Parameters(object):
    """Device parameters resolved upon request
    """

    @property
    def version(self):
        """Firmware version
        """
        if '_version' not in self.__dict__:
            self._version = self.vapix.get_param('Properties.Firmware.Version')
        return self._version

    @property
    def model(self):
        """Product model
        """
        if '_model' not in self.__dict__:
            self._model = self.vapix.get_param('Brand.ProdNbr')
        return self._model

    @property
    def serial_number(self):
        """Device MAC address
        """
        if '_serial_number' not in self.__dict__:
            self._serial_number = self.vapix.get_param('Properties.System.SerialNumber')
        return self._serial_number

    @property
    def meta_data_support(self):
        """Yes if meta data stream is supported
        """
        if '_meta_data_support' not in self.__dict__:
            self._meta_data_support = self.vapix.get_param('Properties.API.Metadata.Metadata')
        return self._meta_data_support


class Configuration(object):
    """Device configuration
    """

    def __init__(self, loop, host, username, password, **kwargs):
        """All config params available to the device
        """
        self.loop = loop
        self.host = host
        self.port = kwargs.get('port', 80)
        self.username = username
        self.password = password
        self.event_types = kwargs.get('events', None)
        self.signal = kwargs.get('signal', None)
        self.kwargs = kwargs


class AxisDevice(Parameters, StreamManager):
    """Creates a new Axis device.self.
    """

    def __init__(self, loop, **kwargs):
        """Initialize device functionality.
        """
        self.config = Configuration(loop, **kwargs)
        self.vapix = Vapix(self.config)
        loop.create_task(StreamManager.__init__(self))


def convert(item, from_key, to_key):
    """Translate between Axis and HASS syntax.
    Type: configuration value for event manager
    Class: what class should event belong to in HASS
    Platform: which HASS platform this event belongs to
    Topic: event topic to look for when receiving events
    Subscribe: subscription form of event topic
    """
    for entry in REMAP:
        if entry[from_key] == item:
            return entry[to_key]


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


if __name__ == '__main__':
    from functools import partial
    loop = asyncio.get_event_loop()
    port = 8080
    #port = 443
    event_list = ['motion']
    kw = {'host': '10.0.1.51',
          'username': 'root',
          'password': 'pass',
          'port': port,
          'events': event_list}
    loop.call_soon(partial(AxisDevice, loop, **kw))
    loop.run_forever()
    loop.close()



## observe som hanterar device status tillgånglig/otillgänglig och sköter retry
