import asyncio
import logging
import re
import socket

import requests
from requests.auth import HTTPDigestAuth  # , HTTPBasicAuth

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


# def print_response(response_string):
#     """ Human readable RTSP response
#     """
#     for response in response_string.splitlines():
#         print(response)
#         _LOGGER.debug(response)


class RTSPMethods(object):
    """Generate RTSP messages based on session data.
    """

    def __init__(self, session):
        """Define message methods
        """
        self.session = session
        self.message_methods = {'OPTIONS': self.OPTIONS,
                                'DESCRIBE': self.DESCRIBE,
                                'SETUP': self.SETUP,
                                'PLAY': self.PLAY,
                                'KEEP-ALIVE': self.KEEP_ALIVE,
                                'TEARDOWN': self.TEARDOWN}

    @property
    def message(self):
        """Returns RTSP method based on sequence number from session.
        """
        message = self.message_methods[self.session.method]()
        _LOGGER.debug(message)
        return message

    def KEEP_ALIVE(self):
        """Keep-Alive messages doesn't need authentication
        """
        return self.OPTIONS(False)

    def OPTIONS(self, authenticate=True):
        """Request options device supports
        """
        message = "OPTIONS " + self.session.url + " RTSP/1.0\r\n"
        message += self.sequence
        message += self.authentication if authenticate else ''
        message += self.user_agent
        message += self.session_id
        message += '\r\n'
        return message

    def DESCRIBE(self):
        """Request description of what services RTSP server make available
        """
        message = "DESCRIBE " + self.session.url + " RTSP/1.0\r\n"
        message += self.sequence
        message += self.authentication
        message += self.user_agent
        message += "Accept: application/sdp\r\n"
        message += '\r\n'
        return message

    def SETUP(self):
        """Set up stream transport
        """
        message = "SETUP " + self.session.control_url + " RTSP/1.0\r\n"
        message += self.sequence
        message += self.authentication
        message += self.user_agent
        message += self.transport
        message += '\r\n'
        return message

    def PLAY(self):
        """RTSP session is ready to send data.
        """
        message = "PLAY " + self.session.url + " RTSP/1.0\r\n"
        message += self.sequence
        message += self.authentication
        message += self.user_agent
        message += self.session_id
        message += '\r\n'
        return message

    def TEARDOWN(self):
        """Tell device to tear down session.
        """
        message = "TEARDOWN " + self.session.url + " RTSP/1.0\r\n"
        message += self.sequence
        message += self.authentication
        message += self.user_agent
        message += self.session_id
        message += '\r\n'
        return message

    @property
    def sequence(self):
        """Generate sequence string.
        """
        return "CSeq: " + str(self.session.sequence) + '\r\n'

    @property
    def authentication(self):
        """Generate authentication string.
        """
        if self.session.digest:
            authentication = self.session.generate_digest()
        elif self.session.basic:
            authentication = self.session.generate_basic()
        else:
            return ''
        return "Authorization: " + authentication + '\r\n'

    @property
    def user_agent(self):
        """Generate user-agent string.
        """
        return "User-Agent: " + self.session.user_agent + '\r\n'

    @property
    def session_id(self):
        """Generate session string.
        """
        if self.session.session_id:
            return "Session: " + self.session.session_id + '\r\n'
        else:
            return ''

    @property
    def transport(self):
        """Generate transport string.
        """
        transport = "Transport: RTP/AVP;unicast;client_port={}-{}\r\n"
        return transport.format(str(self.session.rtp_port),
                                str(self.session.rtcp_port))


class RTSPSession(object):
    """All RTSP session data.
    Stores device stream configuration and session data.
    """

    def __init__(self, url, host, username, password):
        """Session parameters.
        """
        self.url = url
        self.host = host
        self.port = 554
        self.username = username
        self.password = password
        self.sequence = 0
        self.user_agent = "HASS Axis"
        self.rtp_port = None
        self.rtcp_port = None
        self.basic_auth = None
        self.methods = ['OPTIONS',
                        'DESCRIBE',
                        'SETUP',
                        'PLAY',
                        'KEEP-ALIVE',
                        'TEARDOWN']
        # Information as part of ack from device
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

    @property
    def method(self):
        """Which method the sequence number corresponds to.
        0 - OPTIONS
        1 - DESCRIBE
        2 - SETUP
        3 - PLAY
        4 - KEEP-ALIVE (OPTIONS)
        5 - TEARDOWN
        """
        return self.methods[self.sequence]

    @property
    def state(self):
        """Which state the session is in
        Starting - all messages needed to get stream started
        Playing - keep-alive messages every self.session_timeout
        """
        if self.method in ['OPTIONS', 'DESCRIBE', 'SETUP', 'PLAY']:
            state = STATE_STARTING
        elif self.method in ['KEEP-ALIVE']:
            state = STATE_PLAYING
        else:
            state = STATE_STOPPED
        _LOGGER.debug('RTSP session state %s', state)
        return state

    def update(self, response):
        """Update session information from device response.
        Increment sequence number when starting stream, not when playing.
        If device requires authentication resend previous message with auth.
        """
        data = response.splitlines()
        _LOGGER.debug('Received data %s', data)
        while data:
            line = data.pop(0)
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
        elif self.status_code == 401:
            # Device requires authorization, do not increment to next method
            pass
        else:
            # If device configuration is correct we should never get here
            print(self.status_code, self.status_text)

    def generate_digest(self):
        """RFC 2617
        """
        from hashlib import md5
        ha1 = self.username + ':' + self.realm + ':' + self.password
        HA1 = md5(ha1.encode('UTF-8')).hexdigest()
        ha2 = self.method + ':' + self.url
        HA2 = md5(ha2.encode('UTF-8')).hexdigest()
        encrypt_response = HA1 + ':' + self.nonce + ':' + HA2
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
        """RFC 2617
        """
        from base64 import b64encode
        if not self.basic_auth:
            creds = self.username + ':' + self.password
            self.basic_auth = 'Basic '
            self.basic_auth += b64encode(creds.encode('UTF-8')).decode('UTF-8')
        return self.basic_auth


class RTSPClient(asyncio.Protocol):
    """RTSP transport, session handling, message generation.
    """

    def __init__(self, loop, url, host, username, password, callback):
        """RTSP
        """
        self.loop = loop
        self.rtp = RTPClient(loop, callback)
        self.session = RTSPSession(url, host, username, password)
        self.session.rtp_port = self.rtp.port
        self.session.rtcp_port = self.rtp.rtcp_port
        self.method = RTSPMethods(self.session)
        self.transport = None
        conn = loop.create_connection(lambda: self,
                                      self.session.host,
                                      self.session.port)
        task = loop.create_task(conn)
        task.add_done_callback(self.init_done)

    def init_done(self, fut):
        """Server ready.
        If we get OSError during init the device is not available.
        """
        try:
            if fut.exception():
                fut.result()
        except OSError as err:
            print('Got exception', err)
            self.stop()

    def stop(self, retry=False):
        """Stop session.
        """
        if self.transport:
            self.transport.write(self.method.TEARDOWN().encode())
            self.transport.close()
        self.rtp.stop(retry)

    def connection_made(self, transport):
        """Connection to device is successful.
        Start configuring RTSP session.
        Schedule time out handle in case device doesn't respond.
        """
        self.transport = transport
        self.transport.write(self.method.message.encode())
        self.time_out_handle = self.loop.call_later(5, self.time_out)
        # print('Data sent: {!r}'.format(self.request('OPTIONS')))

    def data_received(self, data):
        """Got response on RTSP session.
        Manage time out handle since response came in a reasonable time.
        Update session parameters with latest response.
        If state is playing schedule keep-alive.
        """
        # print('Data received: {!r}'.format(data.decode()))
        self.time_out_handle.cancel()
        self.session.update(data.decode())
        if self.session.state == STATE_STARTING:
            self.transport.write(self.method.message.encode())
            self.time_out_handle = self.loop.call_later(5, self.time_out)
            #print('Data sent: {!r}'.format(self.request(method)))
        elif self.session.state == STATE_PLAYING:
            interval = self.session.session_timeout - 5
            self.loop.call_later(interval, self.keep_alive)
        else:
            self.stop()

    def keep_alive(self):
        """Keep RTSP session alive per negotiated time interval
        """
        self.transport.write(self.method.message.encode())
        self.time_out_handle = self.loop.call_later(5, self.time_out)
        # print('Data sent: {!r}'.format(self.request('OPTIONS')))

    def time_out(self):
        """If we don't get a response within time the RTSP request time out.
        This usually happens if device isn't available on specified IP.
        """
        _LOGGER.warning('Response timed out %s', self.config.host)
        retry = True
        self.stop(retry)

    def connection_lost(self, exc):
        """Happens when device closes connection or stop() has been called.
        """
        print("RTSP Session connection lost", exc)


class RTPClient(object):
    """Data connection to device.
    When data is received send a signal on callback to whoever is interested.
    """

    def __init__(self, loop, callback=None):
        """Configure and bind socket
        Store port for RTSP session setup
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('', 0))
        self.port = sock.getsockname()[1]
        self.client = self.UDPClient(callback)
        # conn = loop.create_datagram_endpoint(lambda: self.client, sock=sock)
        # conn = loop.create_datagram_endpoint(lambda: self.client, local_addr=('0.0.0.0', 0))
        conn = loop.create_datagram_endpoint(lambda: self.client,
                                             local_addr=('0.0.0.0', self.port))
        loop.create_task(conn)
        # self.port = self.client.transport.get_extra_info('sockname')[1]
        self.rtcp_port = self.port + 1

    def stop(self, retry=False):
        """Close transport from receiving any more packages.
        """
        self.client.retry = retry
        if self.client.transport:
            self.client.transport.close()

    @property
    def data(self):
        """Reference to most recently received data.
        """
        return self.client.data

    class UDPClient:
        """Datagram recepient for device data.
        """

        def __init__(self, callback):
            """Callback is used to signal events to subscriber.
            """
            self.callback = callback
            self.data = None
            self.retry = False
            self.transport = None

        def connection_made(self, transport):
            """Executes when port is up and listening.
            Save reference to transport for future control.
            """
            _LOGGER.debug('Stream listener online')
            self.transport = transport

        def connection_lost(self, exc):
            """Signal retry if RTSP session fails to get a response.
            """
            _LOGGER.debug('Stream recepient offline')
            if self.retry and self.callback:
                self.callback('retry')

        def datagram_received(self, data, addr):
            """Signals when new data is available
            """
            # print('Received %r from %s' % (data, addr))
            if self.callback:
                self.data = data[12:]
                self.callback('data')


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
            print('Changed', event_name, data['Data_value'])

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

        # print(self.version)
        # print(self.model)
        # print(self.serial_number)
        # print(self.meta_data_support)


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
