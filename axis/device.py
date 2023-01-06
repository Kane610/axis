"""Python library to enable Axis devices to integrate with Home Assistant."""

from .configuration import Configuration
from .event_stream import EventManager
from .stream_manager import StreamManager
from .vapix.vapix import Vapix


class AxisDevice:
    """Creates a new Axis device.self."""

    def __init__(self, configuration: Configuration) -> None:
        """Initialize device functionality."""
        self.config = configuration
        self.vapix = Vapix(self)
        self.stream = StreamManager(self)
        self.event = EventManager(self)

    def enable_events(self) -> None:
        """Enable events for stream."""
        self.stream.event = True
