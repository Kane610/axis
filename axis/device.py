"""Python library to enable Axis devices to integrate with Home Assistant."""

import logging

from .configuration import Configuration
from .vapix import Vapix
from .streammanager import StreamManager
from .event_stream import EventManager

_LOGGER = logging.getLogger(__name__)


class AxisDevice:
    """Creates a new Axis device.self."""

    def __init__(self, configuration: Configuration) -> None:
        """Initialize device functionality."""
        self.config = configuration
        self.vapix = Vapix(self.config)
        self.stream = StreamManager(self.config)
        self.event = None

    def enable_events(self, event_callback=None) -> None:
        """Enable events for stream."""
        self.event = EventManager(event_callback)
        self.stream.event = self.event
