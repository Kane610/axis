import asyncio
import logging

import requests
from requests.auth import HTTPDigestAuth  # , HTTPBasicAuth

try:
    from .rtsp import RTSPClient
except SystemError:
    from rtsp import RTSPClient

try:
    from .event import EventManager
except SystemError:
    from event import EventManager

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
