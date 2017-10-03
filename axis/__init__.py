import asyncio
import logging
import re
import socket

import requests
from requests.auth import HTTPDigestAuth  # , HTTPBasicAuth

# import aiohttp

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

LINE_SPLIT_STR = '\r\n'

RTSP_URL = '{}'
RTSP_VERSION = 'RTSP/1.0' + LINE_SPLIT_STR
USERAGENT = "User-Agent: {}" + LINE_SPLIT_STR
SEQUENCE = "CSeq: {}" + LINE_SPLIT_STR
TRANSPORT = "Transport: RTP/AVP;unicast;client_port={}-{}" + LINE_SPLIT_STR
SESSION = 'Session: {}' + LINE_SPLIT_STR
AUTHENTICATION = 'Authorization: {} {}' + LINE_SPLIT_STR


# def print_response(response_string):
#     """ Human readable RTSP response
#     """
#     for response in response_string.splitlines():
#         print(response)
#         _LOGGER.debug(response)

class handlestream(object):
    def __init__(self, loop, url, host, username, password, callback):
        self.parser = RTSPSession(url, host, username, password)
        self.rtsp_session = RTSPMethods(self.parser)
        self.rtsp_connection = RTSPClient(loop, self.rtsp_session, callback)


class RTSPMethods(object):
    def __init__(self, parser):
        self.parser = parser
        self.messages = {'OPTIONS': self.OPTIONS,
                         'DESCRIBE': self.DESCRIBE,
                         'SETUP': self.SETUP,
                         'PLAY': self.PLAY,
                         'KEEP-ALIVE': self.KEEP_ALIVE,
                         'TEARDOWN': self.TEARDOWN}

    @property
    def message(self):
        message = self.messages[self.parser.method]()
        # print(message)
        return message

    def response(self, response):
        return self.parser.parse_response(response)

    def KEEP_ALIVE(self):
        return self.OPTIONS(True)

    def OPTIONS(self, noAuth=False):
        message = "OPTIONS " + self.parser.url + " RTSP/1.0\r\n"
        message += self.sequence
        message += self.authentication if not noAuth else ''
        message += self.user_agent
        message += self.session_id
        message += "\r\n"
        return message

    def DESCRIBE(self):
        message = "DESCRIBE " + self.parser.url + " RTSP/1.0\r\n"
        message += self.sequence
        message += self.authentication
        message += self.user_agent
        message += "Accept: application/sdp\r\n"
        message += "\r\n"
        return message

    def SETUP(self):
        message = "SETUP " + self.parser.control_url + " RTSP/1.0\r\n"
        message += self.sequence
        message += self.authentication
        message += self.user_agent
        message += self.transport
        message += "\r\n"
        return message

    def PLAY(self):
        message = "PLAY " + self.parser.url + " RTSP/1.0\r\n"
        message += self.sequence
        message += self.authentication
        message += self.user_agent
        message += self.session_id
        message += "\r\n"
        return message

    def TEARDOWN(self):
        message = "TEARDOWN " + self.parser.url + " RTSP/1.0\r\n"
        message += self.sequence
        message += self.authentication
        message += self.user_agent
        message += self.session_id
        message += "\r\n"
        return message

    @property
    def sequence(self):
        return "CSeq: " + str(self.parser.sequence) + "\r\n"

    @property
    def authentication(self):
        if self.parser.digest:
            authentication = self.parser.generate_digest()
        elif self.parser.basic:
            authentication = self.parser.generate_basic()
        else:
            return ''
        return "Authorization: " + authentication + "\r\n"

    @property
    def user_agent(self):
        return "User-Agent: " + self.parser.user_agent + "\r\n"

    @property
    def session_id(self):
        if self.parser.session_id:
            return "Session: " + self.parser.session_id + "\r\n"
        else:
            return ''

    @property
    def transport(self):
        transport = "Transport: RTP/AVP;unicast;client_port={}-{}\r\n"
        return transport.format(str(self.parser.rtp_port),
                                str(self.parser.rtcp_port))


class RTSPSession(object):

    def __init__(self, url, host, username, password):
        self.url = url
        self.host = host
        self.port = 554
        self.username = username
        self.password = password
        self.sequence = 0
        self.user_agent = 'HASS Axis'
        self.rtp_port = None
        self.rtcp_port = None
        self.basic_auth = None
        self.rtsp_version = None
        self.status_code = None
        self.status_text = None
        self.sequence_ack = None
        self.date = None
        self.methods_ack = None
        self.basic = False
        self.digest = False
        self.realm = None
        self.nonce = None
        self.stale = None
        self.content_type = None
        self.content_base = None
        self.content_length = None
        self.session_id = None
        self.session_timeout = None
        self.transport_ack = None
        self.range = None
        self.rtp_info = None
        self.sdp = None
        self.control_url = None
        self.methods = ['OPTIONS',
                        'DESCRIBE',
                        'SETUP',
                        'PLAY',
                        'KEEP-ALIVE',
                        'TEARDOWN']

    def parse_response(self, response):
        data = response.splitlines()
        # print(data)
        while data:
            line = data.pop(0)
            # print(line)
            if 'RTSP/1.0' in line:
                self.rtsp_version = int(line.split(' ')[0][5])
                self.status_code = int(line.split(' ')[1])
                self.status_text = line.split(' ')[2]
            elif 'CSeq' in line:
                self.sequence_ack = int(line.split(': ')[1])
            elif 'Date' in line:
                self.date = line.split(': ')[1]
            elif 'Public' in line:
                self.methods_ack = line.split(': ')[1].split(', ')
            elif "WWW-Authenticate: Basic" in line:
                self.basic = True
                self.realm = line.split('"')[1]
            elif "WWW-Authenticate: Digest" in line:
                self.digest = True
                self.realm = line.split('"')[1]
                self.nonce = line.split('"')[3]
                self.stale = (line.split('stale=')[1] == 'TRUE')
            elif 'Content-Type' in line:
                self.content_type = line.split(': ')[1]
            elif 'Content-Base' in line:
                self.content_base = line.split(': ')[1]
            elif 'Content-Length' in line:
                self.content_length = int(line.split(': ')[1])
            elif 'Session' in line:
                self.session_id = line.split(': ')[1].split(";")[0]
                if '=' in line:
                    self.session_timeout = int(line.split(': ')[1].split('=')[1])
            elif 'Transport' in line:
                self.transport_ack = line.split(': ')[1]
            elif 'Range' in line:
                self.range = line.split(': ')[1]
            elif 'RTP-Info' in line:
                self.rtp_info = line.split(': ')[1]
            elif not line:
                if data:
                    self.sdp = data
                    break
        if self.sdp:
            stream_found = False
            for param in self.sdp:
                if not stream_found and 'm=application' in param:
                    stream_found = True
                elif stream_found and 'a=control:rtsp' in param:
                    self.control_url = param.split(':', 1)[1]
                    break

        if self.status_code == 200:
            if self.state == STATE_STARTING:
                self.sequence += 1
            return True
        elif self.status_code == 404:
            print(rtsp.status_text)
        else:
            return False

    def generate_digest(self):
        from hashlib import md5
        ha1 = self.username + ":" + self.realm + ":" + self.password
        HA1 = md5(ha1.encode('UTF-8')).hexdigest()
        ha2 = self.method + ":" + self.url
        HA2 = md5(ha2.encode('UTF-8')).hexdigest()
        encrypt_response = HA1 + ":" + self.nonce + ":" + HA2
        response = md5(encrypt_response.encode('UTF-8')).hexdigest()

        digest_auth = 'Digest '
        digest_auth += 'username=\"' + self.username + "\", "
        digest_auth += 'realm=\"' + self.realm + "\", "
        digest_auth += "algorithm=\"MD5\", "
        digest_auth += 'nonce=\"' + self.nonce + "\", "
        digest_auth += 'uri=\"' + self.url + "\", "
        digest_auth += 'response=\"' + response + '\"'
        return digest_auth

    def generate_basic(self):
        from base64 import b64encode
        if not self.basic_auth:
            creds = self.username + ':' + self.password
            self.basic_auth = 'Basic '
            self.basic_auth += b64encode(creds.encode('UTF-8')).decode('UTF-8')
        return self.basic_auth

    @property
    def method(self):
        return self.methods[self.sequence]

    @property
    def state(self):
        if self.method in ['OPTIONS', 'DESCRIBE', 'SETUP', 'PLAY']:
            state = STATE_STARTING
        elif self.method in ['KEEP-ALIVE']:
            state = STATE_PLAYING
        else:
            state = STATE_STOPPED
        # print('STATE: ', state)
        return state


class RTSPClient(asyncio.Protocol):

    def __init__(self, loop, session, callback):
        self.loop = loop
        self.session = session
        self.rtp = RTPClient(loop, callback)
        self.session.parser.rtp_port = self.rtp.port
        self.session.parser.rtcp_port = self.rtp.rtcp_port
        conn = loop.create_connection(lambda: self, self.session.parser.host, self.session.parser.port)
        loop.create_task(conn)

    def stop(self):
        self.session.TEARDOWN()
        self.transport.close()
        self.rtp.stop()

    def connection_made(self, transport):
        self.transport = transport
        self.transport.write(self.session.message.encode())
        # print('Data sent: {!r}'.format(self.request('OPTIONS')))

    def data_received(self, data):
        # print('Data received: {!r}'.format(data.decode()))
        result = self.session.response(data.decode())
        if self.session.parser.state == STATE_STARTING:
            self.transport.write(self.session.message.encode())
            #print('Data sent: {!r}'.format(self.request(method)))
        elif self.session.parser.state == STATE_PLAYING:
            interval = self.session.parser.session_timeout - 15
            self.loop.call_later(interval, self.keep_alive)
        else:
            self.stop()

    def keep_alive(self):
        print('KEEP ALIVE')
        self.transport.write(self.session.message.encode())
        # print('Data sent: {!r}'.format(self.request('OPTIONS')))

    def connection_lost(self, exc):
        print('RTSP Session connection lost', exc)


class RTPClient(object):
    def __init__(self, loop, callback=None):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('', 0))
        self.port = sock.getsockname()[1]
        self.client = self.UDPClient(callback)
        # conn = loop.create_datagram_endpoint(lambda: self.client, sock=sock)
        # conn = loop.create_datagram_endpoint(lambda: self.client, local_addr=('0.0.0.0', 0))
        conn = loop.create_datagram_endpoint(lambda: self.client,
                                             local_addr=('0.0.0.0', self.port))
        loop.create_task(conn)
        #self.port = self.client.transport.get_extra_info('sockname')[1]
        self.rtcp_port = self.port + 1

    def stop(self):
        if self.client.transport:
            self.client.transport.close()

    @property
    def data(self):
        return self.client.data

    class UDPClient:
        def __init__(self, callback=None):
            self.callback = callback
            self.data = None
            self.transport = None

        def connection_made(self, transport):
            print('UDP connection made')
            self.transport = transport

        def connection_lost(self, exc):
            print('UDP connection lost')

        def datagram_received(self, data, addr):
            # print('Received %r from %s' % (data, addr))
            if self.callback:
                self.data = data[12:]
                self.callback()


class Configuration(object):
    #@asyncio.coroutine
    def __init__(self, host, username, password, port=80, kwargs=None):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.kwargs = kwargs

    @property
    def version(self):
        if '_version' not in self.__dict__:
            self._version = self.get_param('Properties.Firmware.Version')
        return self._version

    @property
    def model(self):
        if '_model' not in self.__dict__:
            self._model = self.get_param('Brand.ProdNbr')
        return self._model

    @property
    def serial_number(self):
        if '_serial_number' not in self.__dict__:
            self._serial_number = self.get_param('Properties.System.SerialNumber')
        return self._serial_number


PARAM_URL = 'http://{}:{}/axis-cgi/{}?action={}&{}'


class Vapix(object):
    def up(self):
        print('Vapix')

    def get_param(self, param):
        """Get parameter and remove descriptive part of response"""
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
        """Do HTTP request and return response as dictionary"""
        url = PARAM_URL.format(self.host, self.port, cgi, action, param)
        auth = HTTPDigestAuth(self.username, self.password)
        try:
            r = requests.get(url, auth=auth)
            r.raise_for_status()
        except requests.ConnectionError as err:
            _LOGGER.error("Connection error: %s", err)
            raise
        except requests.exceptions.HTTPError as err:
            _LOGGER.error("HTTP error: %s", err)
            raise
        _LOGGER.debug('Request response: %s', r.text)
        return r.text


class EventManager(object):
    @asyncio.coroutine
    def __init__(self):
        self.events = {}
        event_types = self.kwargs.get('events', None)
        self.event_query = yield from self.create_event_query(event_types)
        print('event manager')

    @asyncio.coroutine
    def create_event_query(self, event_types):
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
        """Received new metadata."""
        data = self.parse_event(event_data)
        if 'Operation' not in data:
            return False

        elif data['Operation'] == 'Initialized':
            new_event = AxisEvent(data)
            if new_event.name not in self.events:
                self.events[new_event.name] = new_event
                if self.signal:
                    self.signal('add', new_event)
                    pass

        elif data['Operation'] == 'Changed':
            event_name = '{}_{}'.format(data['Topic'], data['Source_value'])
            self.events[event_name].state = data['Data_value']
            print('Changed', event_name, data['Data_value'])

        elif data['Operation'] == 'Deleted':
            _LOGGER.debug("Deleted event from stream")
            # ToDo:
            # keep a list of deleted events and a follow up timer of X,
            # then clean up. This should also take care of rebooting a camera

        else:
            _LOGGER.warning("Unexpected response: %s", data)


class AxisEvent(object):  # pylint: disable=R0904
    """Class to represent each Axis device event."""

    def __init__(self, data):
        """Setup an Axis event."""
        _LOGGER.info("New AxisEvent {}".format(data))
        self._topic = data['Topic']
        self._id = data['Source_value']
        self._type = data['Data_name']
        self._source = data['Source_name']
        self._name = '{}_{}'.format(self._topic, self._id)

        self._state = None
        self.callback = None

    @property
    def topic(self):
        """The Topic which the event belongs to."""
        return self._topic

    @property
    def id(self):
        """Source ID for the event."""
        return self._id

    @property
    def type(self):
        """The Type of event."""
        return self._type

    @property
    def source(self):
        """The Source of the event."""
        return self._source

    @property
    def name(self):
        """Uniquely identifying name for the event within the device."""
        return self._name
        # return '{}_{}'.format(self._topic, self._id)

    @property
    def event_class(self):
        return convert(self.topic, 'topic', 'class')

    @property
    def event_type(self):
        return convert(self.topic, 'topic', 'type')

    @property
    def event_platform(self):
        return convert(self.topic, 'topic', 'platform')

    @property
    def state(self):
        """The State of the event."""
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
        if '_device' in cdict:
            del cdict['_device']
        return cdict


class StreamManager(EventManager):
    @asyncio.coroutine
    def __init__(self):
        self.video = 0  # Unsupported self.kwargs.get('video', 0)
        self.audio = 0  # Unsupported self.kwargs.get('audio', 0)
        yield from EventManager.__init__(self)
        self.stream_state = None
        self.start()

    def up(self):
        print('StreamManager')

    @property
    def stream_url(self):
        rtsp = 'rtsp://{}/axis-media/media.amp'.format(self.host)
        source = '?video={0}&audio={1}&event={2}'.format(self.video_query,
                                                         self.audio_query,
                                                         self.event_query)
        return rtsp + source

    @property
    def video_query(self):
        return self.video

    @property
    def audio_query(self):
        return self.audio

    def packet_dispatcher(self):
        print('Vart ska data paketet?')

    def on_data(self):
        self.manage_event(self.data)

    @property
    def data(self):
        """Get data."""
        return self.stream.rtsp_connection.rtp.data
        # return self.stream.rtp.data

    def start(self):
        """Change state to playing."""
        if self.stream_state in [None, STATE_STOPPED]:
            self.stream_state = STATE_STARTING
            self.stream = handlestream(self.loop,
                                       self.stream_url,
                                       self.host,
                                       self.username,
                                       self.password,
                                       self.on_data)

    def stop(self):
        """Change state to stop."""
        if self.stream_state in [STATE_STARTING, STATE_PLAYING, STATE_PAUSED]:
            self.stream_state = STATE_STOPPED
            self.stream.stop()


class AxisDevice(Configuration, Vapix, StreamManager):
    """Creates a new Axis device."""

    def __init__(self, loop, host, username, password, port=80, **kwargs):
        """Initialize device."""
        self.loop = loop
        self.signal = None
        print('kwargs ', kwargs)
        Configuration.__init__(self, host, username, password, port, kwargs)
        loop.create_task(StreamManager.__init__(self))
        print('after')
        #self.up()

    def up(self):
        # updat
        print('Axisdevice')
        super().up()

        #print(self.version)
        #print(self.model)
        #print(self.serial_number)


def convert(item, from_key, to_key):
    """Translate between Axis and HASS syntax."""
    for entry in REMAP:
        if entry[from_key] == item:
            return entry[to_key]


REMAP = [{'type': 'motion',
          'class': 'motion',
          'topic': 'tns1:VideoAnalytics/tnsaxis:MotionDetection',
          'subscribe': 'onvif:VideoAnalytics/axis:MotionDetection',
          'platform': 'binary_sensor'},
         {'type': 'vmd3',
          'class': 'motion',
          'topic': 'tns1:RuleEngine/tnsaxis:VMD3/vmd3_video_1',
          'subscribe': 'onvif:RuleEngine/axis:VMD3/vmd3_video_1',
          'platform': 'binary_sensor'},
         {'type': 'pir',
          'class': 'motion',
          'topic': 'tns1:Device/tnsaxis:Sensor/PIR',
          'subscribe': 'onvif:Device/axis:Sensor/axis:PIR',
          'platform': 'binary_sensor'},
         {'type': 'sound',
          'class': 'sound',
          'topic': 'tns1:AudioSource/tnsaxis:TriggerLevel',
          'subscribe': 'onvif:AudioSource/axis:TriggerLevel',
          'platform': 'binary_sensor'},
         {'type': 'daynight',
          'class': 'light',
          'topic': 'tns1:VideoSource/tnsaxis:DayNightVision',
          'subscribe': 'onvif:VideoSource/axis:DayNightVision',
          'platform': 'binary_sensor'},
         {'type': 'tampering',
          'class': 'safety',
          'topic': 'tns1:VideoSource/tnsaxis:Tampering',
          'subscribe': 'onvif:VideoSource/axis:Tampering',
          'platform': 'binary_sensor'},
         {'type': 'input',
          'class': 'input',
          'topic': 'tns1:Device/tnsaxis:IO/Port',
          'subscribe': 'onvif:Device/axis:IO/Port',
          'platform': 'binary_sensor'}, ]


if __name__ == '__main__':
    from functools import partial
    loop = asyncio.get_event_loop()
    port = 8080
    #port = 443
    event_list = ['motion']
    loop.call_soon(partial(AxisDevice,
                           loop,
                           '10.0.1.51',
                           'root',
                           'pass',
                           port,
                           events=event_list))
    loop.run_forever()
    loop.close()
