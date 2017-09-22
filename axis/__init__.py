import asyncio
import logging
import re
import socket

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


class RTSP_Response(object):

    def __init__(self, response):
        self.rtsp_version = None
        self.status_code = None
        self.status_text = None
        self.sequence = None
        self.date = None
        self.methods = None
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
        self.transport = None
        self.range = None
        self.rtp_info = None
        self.sdp = None

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
                self.sequence = int(line.split(': ')[1])
            elif 'Date' in line:
                self.date = line.split(': ')[1]
            elif 'Public' in line:
                self.methods = line.split(': ')[1].split(', ')
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
                self.transport = line.split(': ')[1]
            elif 'Range' in line:
                self.range = line.split(': ')[1]
            elif 'RTP-Info' in line:
                self.rtp_info = line.split(': ')[1]
            elif not line:
                if data:
                    self.sdp = data
                    data = []
            else:
                # print('BREAK')
                break


class RTSPSession(asyncio.Protocol):

    def __init__(self, loop, metadata_url, callback):
        self.loop = loop
        from urllib.parse import urlsplit
        self.metadata_url = metadata_url
        self.host = urlsplit(self.metadata_url).hostname
        self.username = urlsplit(self.metadata_url).username
        self.password = urlsplit(self.metadata_url).password
        self.auth_method = None
        self.authentication = None
        self.session_id = None
        self.session_timeout = 0
        self.sequence = 0
        self.rtp = RTPClient(loop, callback)
        conn = loop.create_connection(lambda: self, self.host, 554)
        loop.create_task(conn)

    def ready(self):
        conn = loop.create_connection(lambda: self, self.host, 554)
        loop.create_task(conn)

    def stop(self):
        self.transport.close()
        self.rtp.stop()

    def connection_made(self, transport):
        self.transport = transport
        self.transport.write(self.request('OPTIONS').encode())
        #print('Data sent: {!r}'.format(self.request('OPTIONS')))

    def data_received(self, data):
        #print('Data received: {!r}'.format(data.decode()))
        self.parse_response(data.decode())
        if self.sequence < 4:
            method = self.method()
            self.transport.write(self.request(method).encode())
            #print('Data sent: {!r}'.format(self.request(method)))
            print(method)
        else:
            interval = self.session_timeout - 15
            self.loop.call_later(interval, self.keep_alive)

    def keep_alive(self):
        print('KEEP ALIVE')
        self.transport.write(self.request('OPTIONS').encode())
        #print('Data sent: {!r}'.format(self.request('OPTIONS')))

    def connection_lost(self, exc):
        print('RTSP Session connection lost')

    def method(self):
        methods = ['OPTIONS', 'DESCRIBE', 'SETUP', 'PLAY']
        if self.sequence < len(methods):
            method = methods[self.sequence]
        else:
            method = 'OPTIONS'
        return method

    def request(self, method):
        request = method + ' ' + self.metadata_url + ' ' + RTSP_VERSION
        request += USERAGENT.format("Python RTSP Client 1.0")
        request += SEQUENCE.format(self.sequence)
        if self.auth_method:
            self.generate_authentication(method)
            request += self.authentication
        if self.session_id:
            request += SESSION.format(self.session_id)
        if method == 'SETUP':
            request += TRANSPORT.format(self.rtp.port, self.rtp.rtcp_port)
        request += LINE_SPLIT_STR
        return request

    def parse_response(self, response):
        rtsp = RTSP_Response(response)

        method = self.method()

        if rtsp.status_text == 'Unauthorized':
            if rtsp.digest:
                self.auth_method = 'digest'
                self.realm = rtsp.realm
                self.nonce = rtsp.nonce
            elif rtsp.basic:
                self.auth_method = 'basic'
            return True

        if method == 'SETUP':
            self.session_id = rtsp.session_id
            self.session_timeout = rtsp.session_timeout

        if rtsp.status_code == 200:
            self.sequence += 1
            return True
        else:
            return False

    def generate_authentication(self, method):
        if self.auth_method == 'digest':
            from hashlib import md5
            ha1 = self.username + ":" + self.realm + ":" + self.password
            HA1 = md5(ha1.encode('UTF-8')).hexdigest()
            ha2 = method + ":" + self.metadata_url
            HA2 = md5(ha2.encode('UTF-8')).hexdigest()
            encrypt_response = HA1 + ":" + self.nonce + ":" + HA2
            response = md5(encrypt_response.encode('UTF-8')).hexdigest()

            digest_auth = 'username=\"' + self.username + "\", "
            digest_auth += 'realm=\"' + self.realm + "\", "
            digest_auth += "algorithm=\"MD5\", "
            digest_auth += 'nonce=\"' + self.nonce + "\", "
            digest_auth += 'uri=\"' + self.metadata_url + "\", "
            digest_auth += 'response=\"' + response + '\"'
            self.authentication = AUTHENTICATION.format('Digest', digest_auth)
        elif self.auth_method == 'basic':
            from base64 import b64encode
            if not self.authentication:
                creds = self.username + ':' + self.password
                basic_auth = b64encode(creds.encode('UTF-8')).decode('UTF-8')
                self.authentication = AUTHENTICATION.format('Basic',
                                                            basic_auth)


class RTPClient(object):
    def __init__(self, loop, callback=None):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('', 0))
        self.port = sock.getsockname()[1]
        #self.rtcp_port = self.port + 1
        self.client = self.UDPClient(callback)
        #conn = loop.create_datagram_endpoint(lambda: self.client, sock=sock)
        #conn = loop.create_datagram_endpoint(lambda: self.client, local_addr=('0.0.0.0', 0))
        conn = loop.create_datagram_endpoint(lambda: self.client, local_addr=('0.0.0.0', self.port))
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
            print('connection made')
            self.transport = transport
            pass

        def connection_lost(self, exc):
            print('UDP connection lost')

        def datagram_received(self, data, addr):
            # print('Received %r from %s' % (data, addr))
            if self.callback:
                self.data = data[12:]
                self.callback()


import requests
from requests.auth import HTTPDigestAuth  # , HTTPBasicAuth


class Configuration(object):
    def __init__(self, host, username, password, port=80):
        self.host = host
        self.port = port
        self.username = username
        self.password = password

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
                # self.initialize_new_event(new_event)

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
        return '{}_{}'.format(self._topic, self._id)

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
    def __init__(self):
        print('init stream manager')
        self.events = {}
        self.video = 0  # Unsupported
        self.audio = 0  # Unsupported
        self.topics = 'onvif:VideoAnalytics/axis:MotionDetection'
        rtsp_str = 'rtsp://{0}:{1}@{2}/axis-media/media.amp'
        source_str = '?video={0}&audio={1}&event=on&eventtopic={2}'
        rtsp = rtsp_str.format(self.username, self.password, self.host)
        source = source_str.format(self.video, self.audio, self.topics)
        self.stream_url = rtsp + source
        self.stream_state = None
        self.start()

    def packet_dispatcher(self):
        print('Vart ska data paketet?')

    def on_data(self):
        self.manage_event(self.data)

    def start(self):
        """Change state to playing."""
        if self.stream_state in [None, STATE_STOPPED]:
            self.stream_state = STATE_STARTING
            self.stream = RTSPSession(self.loop, self.stream_url, self.on_data)

    def stop(self):
        """Change state to stop."""
        if self.stream_state in [STATE_STARTING, STATE_PLAYING, STATE_PAUSED]:
            self.stream_state = STATE_STOPPED
            self.stream.stop()

    @property
    def data(self):
        """Get metadata."""
        return self.stream.rtp.data


class AxisDevice(Configuration, Vapix, StreamManager):
    """Creates a new Axis device."""

    def __init__(self, loop, host, username, password, port=8080):
        """Initialize device."""
        self.loop = loop
        self.signal = None
        Configuration.__init__(self, host, username, password, port)
        StreamManager.__init__(self)

        print(self.version)
        print(self.model)
        print(self.serial_number)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    device = AxisDevice(loop, '10.0.1.51', 'root', 'pass')
    print(device.__dict__)
    loop.run_forever()
    loop.close()


# RTSP/1.0 401 Unauthorized
# CSeq: 1
# WWW-Authenticate: Digest realm="AXIS_00408CFE6F45",
#    nonce="006a9bc1Y550601855bbd97cae8063796a4fb833637097", stale=FALSE
# WWW-Authenticate: Basic realm="AXIS_00408CFE6F45"
# Date: Thu, 10 Aug 2017 19:28:44 GMT











# import logging
# import requests
# import re
# from requests.auth import HTTPDigestAuth  # , HTTPBasicAuth
# from threading import Timer

# _LOGGER = logging.getLogger(__name__)

# MESSAGE = re.compile('(?<=PropertyOperation)="(?P<operation>\w+)"')
# TOPIC = re.compile('(?<=<wsnt:Topic).*>(?P<topic>.*)(?=<\/wsnt:Topic>)')
# SOURCE = re.compile('(?<=<tt:Source>).*Name="(?P<name>\w+)"' +
#                     '.*Value="(?P<value>\w+)".*(?=<\/tt:Source>)')
# DATA = re.compile('(?<=<tt:Data>).*Name="(?P<name>\w*)"' +
#                   '.*Value="(?P<value>\w*)".*(?=<\/tt:Data>)')

# PARAM_URL = 'http://{}:{}/axis-cgi/{}?action={}&{}'


# class AxisDevice(object):
#     """Creates a new Axis device."""

#     def __init__(self, config):
#         """Initialize device."""

#         _LOGGER.debug("Initializing new Axis device at: %s", config['host'])

#         # Device configuration
#         self._name = config['name']
#         self._url = config['host']
#         self._username = config['username']
#         self._password = config['password']
#         self._port = config.get('port', 80)
#         self._config = config

#         # Metadatastream
#         self._metadatastream = None  # Instance of metadatastream
#         self._event_topics = None  # Topics to subscribe on metadatastream
#         self.initialize_new_event = None  # Metadata initialize callback
#         self.events = {}  # Active device events

#         # Device data needs to be aqcuired manually
#         self._version = self.get_param('Properties.Firmware.Version')
#         self._model = self.get_param('Brand.ProdNbr')
#         self._serial_number = self.get_param('Properties.System.SerialNumber')

#         # Unsupported configuration
#         self._video = 0  # No support for this yet
#         self._audio = 0  # No support for this yet

#     def get_param(self, param):
#         """Get parameter and remove descriptive part of response"""
#         cgi = 'param.cgi'
#         action = 'list'
#         try:
#             r = self.do_request(cgi, action, 'group=' + param)
#         except requests.ConnectionError:
#             return None
#         except requests.exceptions.HTTPError:
#             return None
#         v = {}
#         for s in filter(None, r.split('\n')):
#             key, value = s.split('=')
#             v[key] = value
#         if len(v.items()) == 1:
#             return v[param]
#         else:
#             return v

#     def do_request(self, cgi, action, param):
#         """Do HTTP request and return response as dictionary"""
#         url = PARAM_URL.format(self._url, self._port, cgi, action, param)
#         auth = HTTPDigestAuth(self._username, self._password)
#         try:
#             r = requests.get(url, auth=auth)
#             r.raise_for_status()
#         except requests.ConnectionError as err:
#             _LOGGER.error("Connection error: %s", err)
#             raise
#         except requests.exceptions.HTTPError as err:
#             _LOGGER.error("HTTP error: %s", err)
#             raise
#         _LOGGER.debug('Request response: %s', r.text)
#         return r.text

#     @property
#     def metadata_url(self):
#         """Set up url for metadatastream"""
#         rtsp = "rtsp://{0}:{1}@{2}/axis-media/media.amp?".format(
#             self._username, self._password, self._url)
#         source = 'video={0}&audio={1}&event=on&eventtopic={2}'.format(
#             self._video, self._audio, self._event_topics)
#         return rtsp + source

#     @property
#     def name(self):
#         """Device name"""
#         return self._name

#     @property
#     def serial_number(self):
#         """Device MAC address"""
#         return self._serial_number

#     @property
#     def url(self):
#         return self._url

#     @url.setter
#     def url(self, url):
#         """Update url of device."""
#         self._url = url
#         if self._metadatastream:
#             self._metadatastream.set_up_pipeline(self.metadata_url)
#         _LOGGER.info("New IP (%s) set for device %s", self.url, self.name)

#     def add_event_topic(self, event_topic):
#         """Add new event topic to subscribe to on metadatastream"""
#         if self._event_topics is None:
#             self._event_topics = event_topic
#         else:
#             self._event_topics = '{}|{}'.format(self._event_topics,
#                                                 event_topic)

#     def minimum_firmware(self, constraint):
#         """Checks that firmwware isn't older than constraint."""
#         from packaging import version
#         return version.parse(self._version) >= version.parse(constraint)

#     def initiate_metadatastream(self):
#         """Set up gstreamer pipeline and data callback for metadatastream"""
#         if not self.minimum_firmware('5.50'):
#             _LOGGER.info("Too old firmware for metadatastream")
#             #return False
#         try:
#             from .stream import MetaDataStream
#             #from .rtsp import MetaDataStream
#         except ImportError as err:
#             _LOGGER.error("Missing dependency: %s, check documentation", err)
#             return False
#         self._metadatastream = MetaDataStream(self.metadata_url)
#         self._metadatastream.signal_parent = self.stream_signal
#         self._metadatastream.start()
#         self._retry_timer = None
#         return True

#     def start_metadatastream(self):
#         """Start metadatastream."""
#         if self._metadatastream:
#             self._metadatastream.start()

#     def stop_metadatastream(self):
#         """Stop metadatastream."""
#         if self._metadatastream:
#             self._metadatastream.stop()
#             if self._retry_timer is not None:
#                 self._retry_timer.cancel()

#     def reconnect_metadatastream(self):
#         """Reconnect metadatastream"""
#         if self._retry_timer is not None:
#             self._retry_timer.cancel()
#         self._retry_timer = Timer(15, self.start_metadatastream)
#         self._retry_timer.start()

#     def stream_signal(self):
#         """Manage signals from stream"""
#         if self._metadatastream.stream_state == 'playing':
#             self.new_metadata()
#         elif self._metadatastream.stream_state == 'stopped':
#             _LOGGER.info('Data stream stopped, trying to reconnect to %s',
#                          self._url)
#             self.reconnect_metadatastream()

#     def parse_metadata(self, metadata):
#         """Parse metadata xml."""
#         output = {}

#         message = MESSAGE.search(metadata)
#         if message:
#             output['Operation'] = message.group('operation')

#         topic = TOPIC.search(metadata)
#         if topic:
#             output['Topic'] = topic.group('topic')

#         source = SOURCE.search(metadata)
#         if source:
#             output['Source_name'] = source.group('name')
#             output['Source_value'] = source.group('value')

#         data = DATA.search(metadata)
#         if data:
#             output['Data_name'] = data.group('name')
#             output['Data_value'] = data.group('value')

#         _LOGGER.debug(output)

#         return output

#     def new_metadata(self):
#         """Received new metadata."""
#         metadata = self._metadatastream.data
#         data = self.parse_metadata(metadata)
#         if 'Operation' not in data:
#             return False

#         elif data['Operation'] == 'Initialized':
#             new_event = AxisEvent(data, self)
#             if new_event.name not in self.events:
#                 self.events[new_event.name] = new_event
#                 self.initialize_new_event(new_event)

#         elif data['Operation'] == 'Changed':
#             event_name = '{}_{}'.format(data['Topic'], data['Source_value'])
#             self.events[event_name].state = data['Data_value']

#         elif data['Operation'] == 'Deleted':
#             _LOGGER.debug("Deleted event from stream")
#             # ToDo:
#             # keep a list of deleted events and a follow up timer of X,
#             # then clean up. This should also take care of rebooting a camera

#         else:
#             _LOGGER.warning("Unexpected response: %s", data)


# class AxisEvent(object):  # pylint: disable=R0904
#     """Class to represent each Axis device event."""

#     def __init__(self, data, device):
#         """Setup an Axis event."""
#         _LOGGER.info("New AxisEvent {}".format(data))
#         self._device = device
#         self._topic = data['Topic']
#         self._id = data['Source_value']
#         self._type = data['Data_name']
#         self._source = data['Source_name']

#         self._state = None
#         self.callback = None

#     @property
#     def device_name(self):
#         """Return device name that the event belongs to."""
#         return self._device.name

#     def device_config(self, key):
#         """Return config value"""
#         return self._device._config[key]

#     @property
#     def topic(self):
#         """The Topic which the event belongs to."""
#         return self._topic

#     @property
#     def id(self):
#         """Source ID for the event."""
#         return self._id

#     @property
#     def type(self):
#         """The Type of event."""
#         return self._type

#     @property
#     def source(self):
#         """The Source of the event."""
#         return self._source

#     @property
#     def name(self):
#         """Uniquely identifying name for the event within the device."""
#         return '{}_{}'.format(self._topic, self._id)

#     @property
#     def state(self):
#         """The State of the event."""
#         return self._state

#     @state.setter
#     def state(self, state):
#         """Update state of event and trigger callback for notification."""
#         self._state = state
#         if self.callback:
#             self.callback()
#         else:
#             _LOGGER.info("state.setter has no callback")

#     @property
#     def is_tripped(self):
#         """Event is tripped now."""
#         return self._state == '1'

#     def as_dict(self):
#         """Callback for __dict__."""
#         cdict = self.__dict__.copy()
#         del cdict['callback']
#         del cdict['_device']
#         return cdict
