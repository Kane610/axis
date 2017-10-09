import logging

from .configuration import Configuration
from .vapix import Vapix, Parameters
from .streammanager import StreamManager

# import aiohttp
# PYTHON RTSP INSPIRATION
# https://github.com/timohoeting/python-mjpeg-over-rtsp-client/blob/master/rtsp_client.py
# http://codegist.net/snippet/python/rtsp_authenticationpy_crayfishapps_python
# https://github.com/perexg/satip-axe/blob/master/tools/multicast-rtp


_LOGGER = logging.getLogger(__name__)


class AxisDevice(Parameters, StreamManager):
    """Creates a new Axis device.self.
    """

    def __init__(self, loop, **kwargs):
        """Initialize device functionality.
        """
        self.config = Configuration(loop, **kwargs)
        self.vapix = Vapix(self.config)
        loop.create_task(StreamManager.__init__(self))


## observe som hanterar device status tillgånglig/otillgänglig och sköter retry
