"""Python library to enable Axis devices to be integrated in to Home Assistant."""

import logging

from .configuration import Configuration
from .vapix import Vapix, Parameters
from .streammanager import StreamManager

# PYTHON RTSP INSPIRATION
# https://github.com/timohoeting/python-mjpeg-over-rtsp-client/blob/master/rtsp_client.py
# http://codegist.net/snippet/python/rtsp_authenticationpy_crayfishapps_python
# https://github.com/perexg/satip-axe/blob/master/tools/multicast-rtp


_LOGGER = logging.getLogger(__name__)


class AxisDevice(Parameters):
    """Creates a new Axis device.self."""

    def __init__(self, loop, **kwargs):
        """Initialize device functionality."""
        self.config = Configuration(loop, **kwargs)
        self.vapix = Vapix(self.config)
        self.stream = StreamManager(self.config)

    def start(self):
        """Start functionality of device."""
        self.stream.start()

    def stop(self):
        """Stop functionality of device."""
        self.stream.stop()


## observe som hanterar device status tillganglig/otillganglig och skoter retry
