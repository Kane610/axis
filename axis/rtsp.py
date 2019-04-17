"""Python library to enable Axis devices to integrate with Home Assistant."""

# PYTHON RTSP INSPIRATION
# https://github.com/timohoeting/python-mjpeg-over-rtsp-client/blob/master/rtsp_client.py
# http://codegist.net/snippet/python/rtsp_authenticationpy_crayfishapps_python
# https://github.com/perexg/satip-axe/blob/master/tools/multicast-rtp

import asyncio
import logging
import socket

_LOGGER = logging.getLogger(__name__)

RTSP_PORT = 554

STATE_PAUSED = 'paused'
STATE_PLAYING = 'playing'
STATE_STARTING = 'starting'
STATE_STOPPED = 'stopped'

SIGNAL_DATA = 'data'
SIGNAL_FAILED = 'failed'
SIGNAL_PLAYING = 'playing'

TIME_OUT_LIMIT = 5


class RTSPClient(asyncio.Protocol):
    """RTSP transport, session handling, message generation."""

    def __init__(self, loop, url, host, username, password, callback):
        """RTSP."""
        self.loop = loop
        self.callback = callback
        self.rtp = RTPClient(loop, callback)
        self.session = RTSPSession(url, host, username, password)
        self.session.rtp_port = self.rtp.port
        self.session.rtcp_port = self.rtp.rtcp_port
        self.method = RTSPMethods(self.session)
        self.transport = None
        self.time_out_handle = None

    def start(self):
        """Start session."""
        conn = self.loop.create_connection(
            lambda: self, self.session.host, self.session.port)
        task = self.loop.create_task(conn)
        task.add_done_callback(self.init_done)

    def init_done(self, fut):
        """Server ready.

        If we get OSError during init the device is not available.
        """
        try:
            if fut.exception():
                fut.result()
        except OSError as err:
            _LOGGER.debug('RTSP got exception %s', err)
            self.stop()
            self.callback(SIGNAL_FAILED)

    def stop(self):
        """Stop session."""
        if self.transport:
            self.transport.write(self.method.TEARDOWN().encode())
            self.transport.close()
        self.rtp.stop()

    def connection_made(self, transport):
        """Connect to device is successful.

        Start configuring RTSP session.
        Schedule time out handle in case device doesn't respond.
        """
        self.transport = transport
        self.transport.write(self.method.message.encode())
        self.time_out_handle = self.loop.call_later(
            TIME_OUT_LIMIT, self.time_out)

    def data_received(self, data):
        """Got response on RTSP session.

        Manage time out handle since response came in a reasonable time.
        Update session parameters with latest response.
        If state is playing schedule keep-alive.
        """
        self.time_out_handle.cancel()
        self.session.update(data.decode())

        if self.session.state == STATE_STARTING:
            self.transport.write(self.method.message.encode())
            self.time_out_handle = self.loop.call_later(
                TIME_OUT_LIMIT, self.time_out)

        elif self.session.state == STATE_PLAYING:
            self.callback(SIGNAL_PLAYING)

            if self.session.session_timeout != 0:
                interval = self.session.session_timeout - 5
                self.loop.call_later(interval, self.keep_alive)

        else:
            self.stop()

    def keep_alive(self):
        """Keep RTSP session alive per negotiated time interval."""
        self.transport.write(self.method.message.encode())
        self.time_out_handle = self.loop.call_later(
            TIME_OUT_LIMIT, self.time_out)

    def time_out(self):
        """If we don't get a response within time the RTSP request time out.

        This usually happens if device isn't available on specified IP.
        """
        _LOGGER.warning('Response timed out %s', self.session.host)
        self.stop()
        self.callback(SIGNAL_FAILED)

    def connection_lost(self, exc):
        """Happens when device closes connection or stop() has been called."""
        _LOGGER.debug('RTSP session lost connection')


class RTPClient(object):
    """Data connection to device.

    When data is received send a signal on callback to whoever is interested.
    """

    def __init__(self, loop, callback=None):
        """Configure and bind socket.

        Store port for RTSP session setup.
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('', 0))
        self.port = sock.getsockname()[1]
        self.client = self.UDPClient(callback)
        # conn = loop.create_datagram_endpoint(lambda: self.client, sock=sock)
        # conn = loop.create_datagram_endpoint(lambda: self.client, local_addr=('0.0.0.0', 0))
        conn = loop.create_datagram_endpoint(
            lambda: self.client, local_addr=('0.0.0.0', self.port))
        loop.create_task(conn)
        # self.port = self.client.transport.get_extra_info('sockname')[1]
        self.rtcp_port = self.port + 1

    def stop(self):
        """Close transport from receiving any more packages."""
        if self.client.transport:
            self.client.transport.close()

    @property
    def data(self):
        """Refer to most recently received data."""
        return self.client.data

    class UDPClient:
        """Datagram recepient for device data."""

        def __init__(self, callback):
            """Signal events to subscriber using callback."""
            self.callback = callback
            self.data = None
            self.transport = None

        def connection_made(self, transport):
            """Execute when port is up and listening.

            Save reference to transport for future control.
            """
            _LOGGER.debug('Stream listener online')
            self.transport = transport

        def connection_lost(self, exc):
            """Signal retry if RTSP session fails to get a response."""
            _LOGGER.debug('Stream recepient offline')

        def datagram_received(self, data, addr):
            """Signals when new data is available."""
            if self.callback:
                self.data = data[12:]
                self.callback('data')


class RTSPMethods(object):
    """Generate RTSP messages based on session data."""

    def __init__(self, session):
        """Define message methods."""
        self.session = session
        self.message_methods = {'OPTIONS': self.OPTIONS,
                                'DESCRIBE': self.DESCRIBE,
                                'SETUP': self.SETUP,
                                'PLAY': self.PLAY,
                                'KEEP-ALIVE': self.KEEP_ALIVE,
                                'TEARDOWN': self.TEARDOWN}

    @property
    def message(self):
        """Return RTSP method based on sequence number from session."""
        message = self.message_methods[self.session.method]()
        _LOGGER.debug(message)
        return message

    def KEEP_ALIVE(self):
        """Keep-Alive messages doesn't need authentication."""
        return self.OPTIONS(False)

    def OPTIONS(self, authenticate=True):
        """Request options device supports."""
        message = "OPTIONS " + self.session.url + " RTSP/1.0\r\n"
        message += self.sequence
        message += self.authentication if authenticate else ''
        message += self.user_agent
        message += self.session_id
        message += '\r\n'
        return message

    def DESCRIBE(self):
        """Request description of what services RTSP server make available."""
        message = "DESCRIBE " + self.session.url + " RTSP/1.0\r\n"
        message += self.sequence
        message += self.authentication
        message += self.user_agent
        message += "Accept: application/sdp\r\n"
        message += '\r\n'
        return message

    def SETUP(self):
        """Set up stream transport."""
        message = "SETUP " + self.session.control_url + " RTSP/1.0\r\n"
        message += self.sequence
        message += self.authentication
        message += self.user_agent
        message += self.transport
        message += '\r\n'
        return message

    def PLAY(self):
        """RTSP session is ready to send data."""
        message = "PLAY " + self.session.url + " RTSP/1.0\r\n"
        message += self.sequence
        message += self.authentication
        message += self.user_agent
        message += self.session_id
        message += '\r\n'
        return message

    def TEARDOWN(self):
        """Tell device to tear down session."""
        message = "TEARDOWN " + self.session.url + " RTSP/1.0\r\n"
        message += self.sequence
        message += self.authentication
        message += self.user_agent
        message += self.session_id
        message += '\r\n'
        return message

    @property
    def sequence(self):
        """Generate sequence string."""
        return "CSeq: " + str(self.session.sequence) + '\r\n'

    @property
    def authentication(self):
        """Generate authentication string."""
        if self.session.digest:
            authentication = self.session.generate_digest()
        elif self.session.basic:
            authentication = self.session.generate_basic()
        else:
            return ''
        return "Authorization: " + authentication + '\r\n'

    @property
    def user_agent(self):
        """Generate user-agent string."""
        return "User-Agent: " + self.session.user_agent + '\r\n'

    @property
    def session_id(self):
        """Generate session string."""
        if self.session.session_id:
            return "Session: " + self.session.session_id + '\r\n'
        return ''

    @property
    def transport(self):
        """Generate transport string."""
        transport = "Transport: RTP/AVP;unicast;client_port={}-{}\r\n"
        return transport.format(
            str(self.session.rtp_port), str(self.session.rtcp_port))


class RTSPSession(object):
    """All RTSP session data.

    Stores device stream configuration and session data.
    """

    def __init__(self, url, host, username, password):
        """Session parameters."""
        self.url = url
        self.host = host
        self.port = RTSP_PORT
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
        self.session_timeout = 0
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
        """Which state the session is in.

        Starting - all messages needed to get stream started.
        Playing - keep-alive messages every self.session_timeout.
        """
        if self.method in ['OPTIONS', 'DESCRIBE', 'SETUP', 'PLAY']:
            state = STATE_STARTING
        elif self.method in ['KEEP-ALIVE']:
            state = STATE_PLAYING
        else:
            state = STATE_STOPPED
        _LOGGER.debug('RTSP session (%s) state %s', self.host, state)
        return state

    def update(self, response):
        """Update session information from device response.

        Increment sequence number when starting stream, not when playing.
        If device requires authentication resend previous message with auth.
        """
        data = response.splitlines()
        _LOGGER.debug('Received data %s from %s', data, self.host)
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
            _LOGGER.debug(
                "%s RTSP %s %s", self.host, self.status_code, self.status_text)

    def generate_digest(self):
        """RFC 2617."""
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
        """RFC 2617."""
        from base64 import b64encode
        if not self.basic_auth:
            creds = self.username + ':' + self.password
            self.basic_auth = 'Basic '
            self.basic_auth += b64encode(creds.encode('UTF-8')).decode('UTF-8')
        return self.basic_auth
