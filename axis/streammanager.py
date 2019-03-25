"""Python library to enable Axis devices to integrate with Home Assistant."""

import logging

from .rtsp import (
    RTSPClient, SIGNAL_DATA, SIGNAL_FAILED, SIGNAL_PLAYING, STATE_STOPPED)

_LOGGER = logging.getLogger(__name__)

RTSP_URL = 'rtsp://{host}/axis-media/media.amp'
RTSP_SOURCE = '?video={video}&audio={audio}&event={event}'

RETRY_TIMER = 15


class StreamManager(object):
    """Setup, start, stop and retry stream."""

    def __init__(self, config):
        """Start stream if any event type is specified."""
        self.config = config
        self.video = None  # Unsupported
        self.audio = None  # Unsupported
        self.event = None
        self.stream = None
        self.connection_status_callback = None

    @property
    def stream_url(self):
        """Build url for stream."""
        rtsp = RTSP_URL.format(host=self.config.host)
        source = RTSP_SOURCE.format(video=self.video_query,
                                    audio=self.audio_query,
                                    event=self.event.query)
        _LOGGER.debug(rtsp + source)
        return rtsp + source

    @property
    def video_query(self):
        """Generate video query, not supported."""
        return 0

    @property
    def audio_query(self):
        """Generate audio query, not supported."""
        return 0

    def session_callback(self, signal):
        """Signalling from stream session.

        Data - new data available for processing.
        Playing - Connection is healthy.
        Retry - if there is no connection to device.
        """
        print('session callback', signal)
        if signal == SIGNAL_DATA:
            self.event.new_event(self.data)
        elif signal == SIGNAL_FAILED:
            self.retry()
        if signal in [SIGNAL_PLAYING, SIGNAL_FAILED] and \
                self.connection_status_callback:
            self.connection_status_callback(signal)

    @property
    def data(self):
        """Get stream data."""
        return self.stream.rtp.data

    def start(self):
        """Start stream."""
        if not self.stream or self.stream.session.state == STATE_STOPPED:
            self.stream = RTSPClient(
                self.config.loop, self.stream_url, self.config.host,
                self.config.username, self.config.password,
                self.session_callback)

    def stop(self):
        """Stop stream."""
        if self.stream and self.stream.session.state != STATE_STOPPED:
            self.stream.stop()

    def retry(self):
        """No connection to device, retry connection after 15 seconds."""
        self.stream = None
        self.config.loop.call_later(RETRY_TIMER, self.start)
        _LOGGER.debug('Reconnecting to %s', self.config.host)
