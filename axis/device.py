"""Python library to enable Axis devices to integrate with Home Assistant."""

from .configuration import Configuration
from .interfaces.event_manager import EventManager
from .interfaces.vapix import Vapix
from .stream_manager import StreamManager


class AxisDevice:
    """Creates a new Axis device.self."""

    def __init__(self, configuration: Configuration) -> None:
        """Initialize device functionality."""
        self.config = configuration
        self.vapix = Vapix(self)
        self.stream = StreamManager(self)
        self.event = EventManager()

    def enable_events(self) -> None:
        """Enable events for stream."""
        self.stream.event = True
