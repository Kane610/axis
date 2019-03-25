"""Python library to enable Axis devices to integrate with Home Assistant."""

import logging

from .configuration import Configuration
from .vapix import Vapix
from .streammanager import StreamManager
from .event import EventManager

_LOGGER = logging.getLogger(__name__)


class AxisDevice:
    """Creates a new Axis device.self."""

    def __init__(self, **kwargs):
        """Initialize device functionality."""
        self.config = Configuration(**kwargs)
        self.vapix = Vapix(self.config)
        self.stream = StreamManager(self.config)
        self.event = None

    def start(self):
        """Start functionality of device."""
        self.stream.start()

    def stop(self):
        """Stop functionality of device."""
        self.stream.stop()

    def enable_events(self, events=True, event_callback=None):
        """Enable events for stream."""
        self.event = EventManager(events, event_callback)
        self.stream.event = self.event
