"""Python library to enable Axis devices to integrate with Home Assistant."""

from typing import Callable

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

    def enable_events(self, event_callback: Callable) -> None:
        """Enable events for stream."""
        self.event.signal = event_callback
        self.stream.event = self.event.update  # type: ignore[assignment]
