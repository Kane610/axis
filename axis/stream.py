import logging
import gi  # pylint: disable=import-error
gi.require_version('Gst', '1.0')
from gi.repository import Gst

Gst.init(None)

_LOGGER = logging.getLogger(__name__)

STATE_PLAYING = 'playing'
STATE_PAUSED = 'paused'


class MetaDataStream(object):
    """Gstreamer process."""

    def __init__(self, rtsp_url=None):
        """Initialize process."""
        self._data = None
        self._stream_state = None
        self.signal_parent = None

        if not rtsp_url:
            _LOGGER.error('No device url to stream from')
            return False

        pipeline = [
            'rtspsrc',
            'location=%s' % (rtsp_url),
            'latency=10', '!',
            'appsink', 'name=sink',
        ]
        pipeline_string = " ".join(pipeline)
        # Simplest way to create a pipeline
        self._stream = Gst.parse_launch(pipeline_string)
        # Getting the sink by its name set in CLI
        self._appsink = self._stream.get_by_name("sink")
        # Prevent the app to consume huge part of memory
        self._appsink.set_property("max-buffers", 20)
        # Tell sink to emit signals
        self._appsink.set_property('emit-signals', True)
        # No sync to make decoding as fast as possible
        self._appsink.set_property('sync', False)
        # Connect signal to callable func
        self._appsink.connect('new-sample', self._on_new_buffer)
        bus = self._stream.get_bus()
        bus.add_signal_watch()
        bus.connect('message', self._on_message)

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
        if self._stream_state is None:
            self._stream.set_state(Gst.State.PLAYING)
            print("stream started")
            self._stream_state = STATE_PLAYING

    def stop(self):
        """Stop pipeline."""
        self._stream.set_state(Gst.State.NULL)
        print("stream stopped")

    @property
    def data(self):
        """Get metadata."""
        return self._data

    def _on_message(self, bus, message):
        """When a message is received from Gstreamer."""
        print('metadatastream bus message type:', message.type)
        if message.type == Gst.MessageType.EOS:
            self.stop()
        elif message.type == Gst.MessageType.ERROR:
            self.stop()
            err, _ = message.parse_error()
            _LOGGER.error('%s', err)
        # else:
        #     print('metadatastream bus message type:', message.type)
