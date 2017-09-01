import logging
import socket
from threading import Thread, Timer, Lock

_LOGGER = logging.getLogger(__name__)

STATE_STARTING = 'starting'
STATE_PLAYING = 'playing'
STATE_STOPPED = 'stopped'
STATE_PAUSED = 'paused'

username = 'root'
password = 'pass'
url = '10.0.1.51'
video = 0
audio = 0
event_topics = 'onvif:VideoAnalytics/axis:MotionDetection'

rtsp = "rtsp://{0}:{1}@{2}/axis-media/media.amp".format(username,
                                                        password,
                                                        url)
#rtsp = "rtsp://{0}/axis-media/media.amp".format(url)
source = '?video={0}&audio={1}&event=on&eventtopic={2}'.format(video,
                                                               audio,
                                                               event_topics)
#source = '?event=on&eventtopic={0}'.format(event_topics)
metadata_url = rtsp + source
adr = metadata_url

LINE_SPLIT_STR = '\r\n'

RTSP_URL = '{}'
RTSP_VERSION = 'RTSP/1.0' + LINE_SPLIT_STR
USERAGENT = "User-Agent: {}" + LINE_SPLIT_STR
SEQUENCE = "CSeq: {}" + LINE_SPLIT_STR
TRANSPORT = "Transport: RTP/AVP;unicast;client_port={}-{}" + LINE_SPLIT_STR
SESSION = 'Session: {}' + LINE_SPLIT_STR
AUTHENTICATION = 'Authorization: {} {}' + LINE_SPLIT_STR


def print_response(response_string):
    """ Human readable RTSP response
    """
    for response in response_string.splitlines():
        print(response)
        _LOGGER.debug(response)


class MetaDataStream(object):
    """Gstreamer process."""

    def __init__(self, metadata_url):
        """Initialize process."""
        self.signal_parent = None
        self.stream_state = None
        self.auth_method = None
        self.prepare_session(metadata_url)

    def set_up_pipeline(self, metadata_url):
        self.prepare_session(metadata_url)

    def prepare_session(self, metadata_url):
        from urllib.parse import urlsplit
        self.metadata_url = metadata_url
        self.url = urlsplit(self.metadata_url).hostname
        self.username = urlsplit(self.metadata_url).username
        self.password = urlsplit(self.metadata_url).password

    def setup_rtsp(self):
        self.rtsp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.rtsp.settimeout(10)
        self.rtsp.connect((self.url, 554))
        print('connect')

    def setup_keep_alive(self):
        if self.session_timeout != 0:
            interval = self.session_timeout - 5
            #interval = 15
            self.keep_alive = Periodic(interval, self.send_request, 'OPTIONS')

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
            # logger generating basic authentication

    def send_request(self, method):
        request = method + ' ' + self.metadata_url + ' ' + RTSP_VERSION
        request += USERAGENT.format("Python RTSP Client 1.0")
        request += SEQUENCE.format(self.sequence)
        if self.auth_method:
            self.generate_authentication(method)
            request += self.authentication
        if self.session_id:
            request += SESSION.format(self.session_id)
        if method == 'SETUP':
            request += TRANSPORT.format(self.rtp_client.rtp_port,
                                        self.rtp_client.rtcp_port)
        request += LINE_SPLIT_STR

        print("*** SENDING " + method + "  ***")
        print(request)
        message = request.encode('UTF-8')
        try:
            self.rtsp.send(message)
        except:
            self.stop()
            self.on_data()
            return False
        rtsp_response = self.rtsp.recv(4096)
        response = rtsp_response.decode('UTF-8')
        print_response(response)
        return response

    def act_on_response(self, method, response):
        rtsp = RTSP_Response(response)

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

    def on_data(self):
        print(self.data)
        if self.signal_parent is not None:
            self.signal_parent()

    def start(self):
        """Change state to playing."""
        if self.stream_state in [None, STATE_STOPPED]:
            self.stream_state = STATE_STARTING
            self.authentication = None
            self.session_id = None
            self.session_timeout = None
            self.sequence = 0
            self.keep_alive = None
            self.rtp_client = threading_RTPClient(self.on_data)
            self.setup_rtsp()
            methods = ['OPTIONS', 'DESCRIBE', 'SETUP', 'PLAY']
            while self.sequence < len(methods):
                method = methods[self.sequence]
                response = self.send_request(method)
                action = self.act_on_response(method, response)
                if action is False:
                    print('Error starting stream')
                    return False
            self.setup_keep_alive()
            self.rtp_client.start()
            self.stream_state = STATE_PLAYING
            # _LOGGER.info("Stream started")

    def stop(self):
        """Change state to stop."""
        if self.stream_state in [STATE_STARTING, STATE_PLAYING, STATE_PAUSED]:
            self.stream_state = STATE_STOPPED
            self.sequence += 1
            self.send_request('TEARDOWN')
            self.rtsp.close()
            self.rtp_client.do_continue = False
            self.rtp_client.rtp.close()
            if self.rtp_client.is_alive():
                self.rtp_client.join()
            if self.keep_alive:
                self.keep_alive.stop()
            # _LOGGER.info("Stream stopped")

    @property
    def data(self):
        """Get metadata."""
        return self.rtp_client.data


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
            elif 'WWW-Authenticate: Basic' in line:
                self.basic = True
                self.realm = line.split('"')[1]
            elif 'WWW-Authenticate: Digest' in line:
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


class threading_RTPClient(Thread):

    def __init__(self, callback):
        Thread.__init__(self)
        self.callback = callback
        self.rtp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.rtp.bind(("", 0))
        self.rtp_port = self.rtp.getsockname()[1]
        self.rtcp_port = int(self.rtp_port) + 1
        self.rtp.settimeout(5)
        self.do_continue = True
        self._data = None

    def run(self):
        while(self.do_continue):
            try:
                rtp_response = self.rtp.recv(4096)
                response = rtp_response[12:]  # Remove RTP header
                self._data = response.decode('UTF-8')
                self.callback()
            except socket.timeout:
                # print('TIMEOUT')
                pass

    @property
    def data(self):
        """Get data."""
        return self._data


class Periodic(object):
    """
    A periodic task running in threading.Timers
    """

    def __init__(self, interval, function, *args, **kwargs):
        self._lock = Lock()
        self._timer = None
        self.function = function
        self.interval = interval
        self.args = args
        self.kwargs = kwargs
        self._stopped = True
        if kwargs.pop('autostart', True):
            self.start()

    def start(self, from_run=False):
        self._lock.acquire()
        if from_run or self._stopped:
            self._stopped = False
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
        self._lock.release()

    def _run(self):
        self.start(from_run=True)
        self.function(*self.args, **self.kwargs)

    def stop(self):
        self._lock.acquire()
        self._stopped = True
        self._timer.cancel()
        self._lock.release()


if __name__ == '__main__':
    # Running as a script
    stream = MetaDataStream(metadata_url)
    stream.start()
    from time import sleep
    sleep(15)
    #sleep(3600)

    stream.stop()


# RTSP/1.0 401 Unauthorized
# CSeq: 1
# WWW-Authenticate: Digest realm="AXIS_00408CFE6F45",
#    nonce="006a9bc1Y550601855bbd97cae8063796a4fb833637097", stale=FALSE
# WWW-Authenticate: Basic realm="AXIS_00408CFE6F45"
# Date: Thu, 10 Aug 2017 19:28:44 GMT
