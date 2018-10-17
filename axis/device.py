"""Python library to enable Axis devices to integrate with Home Assistant."""

import logging

from .configuration import Configuration
from .vapix import Vapix
from .streammanager import StreamManager

_LOGGER = logging.getLogger(__name__)


class AxisDevice:
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



