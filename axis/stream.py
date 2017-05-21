import logging
import gi  # pylint: disable=import-error
gi.require_version('Gst', '1.0')
from gi.repository import Gst

Gst.init(None)

_LOGGER = logging.getLogger(__name__)

STATE_PLAYING = 'playing'
STATE_STOPPED = 'stopped'
STATE_PAUSED = 'paused'


class MetaDataStream(object):
    """Gstreamer process."""

    def __init__(self, rtsp_url):
        """Initialize process."""
        self._data = None
        self.stream_state = None
        self.signal_parent = None
        self.pipeline_string = None

        self.set_up_pipeline(rtsp_url)
        self.set_up_stream()

    def set_up_pipeline(self, rtsp_url):
        """Set up pipeline describing how gstreamer will be configured."""
        pipeline = [
            'rtspsrc',
            'location=%s' % (rtsp_url),
            'latency=10', '!',
            'appsink', 'name=sink',
        ]
        self.pipeline_string = " ".join(pipeline)

    def set_up_stream(self):
        """Configure gstreamer with pipeline and appsink."""
        self.stream_state = None
        # Simplest way to create a pipeline
        self._stream = Gst.parse_launch(self.pipeline_string)
        # Getting the sink by its name set in pipeline_string
        appsink = self._stream.get_by_name("sink")
        # Prevent the app to consume huge part of memory
        appsink.set_property("max-buffers", 20)
        # Tell sink to emit signals
        appsink.set_property('emit-signals', True)
        # No sync to make decoding as fast as possible
        appsink.set_property('sync', False)
        # Connect signal to callable func
        appsink.connect('new-sample', self._on_new_buffer)
        bus = self._stream.get_bus()
        bus.set_sync_handler(self._on_message, self._stream)

    def _on_new_buffer(self, appsink):
        sample = appsink.emit('pull-sample')
        buf = sample.get_buffer()  # get the buffer
        data = buf.extract_dup(0, buf.get_size())  # extract data as string
        data = data[12:]  # remove 12 trash bytes from rtp header
        data = data.decode('UTF-8')  # decode byte string
        self._data = data
        self.signal_parent()  # tell parent new data is available
        return False

    def start(self):
        """Change state to playing."""
        if self.stream_state == STATE_STOPPED:
            # Connection has been closed, new set up required
            self.set_up_stream()

        if self.stream_state in [None, STATE_PAUSED]:
            self._stream.set_state(Gst.State.PLAYING)
            _LOGGER.info("Stream started")
            self.stream_state = STATE_PLAYING

    def stop(self):
        """Stop pipeline."""
        if self.stream_state in [STATE_PLAYING, STATE_PAUSED]:
            self._stream.set_state(Gst.State.NULL)
            _LOGGER.info("Stream stopped")
            self.stream_state = STATE_STOPPED

    def pause(self):
        """Pause pipeline."""
        if self.stream_state == STATE_PLAYING:
            self._stream.set_state(Gst.State.PAUSED)
            _LOGGER.info("Stream paused")
            self.stream_state = STATE_PAUSED

    @property
    def data(self):
        """Get metadata."""
        return self._data

    def _on_message(self, bus, message, pipeline):
        """When a message is received from Gstreamer."""
        if message.type in [Gst.MessageType.EOS, Gst.MessageType.ERROR]:
            self.stream_state = STATE_STOPPED
            self.signal_parent()
            _LOGGER.info('No connection to device')

        if message.type == Gst.MessageType.ERROR:
            err, _ = message.parse_error()
            _LOGGER.debug('%s', err)
        else:
            _LOGGER.debug('metadatastream bus message type:', message.type)
        return Gst.BusSyncReply.PASS
