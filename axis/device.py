"""Python library to enable Axis devices to integrate with Home Assistant."""

from typing import TYPE_CHECKING

from .interfaces.event_manager import EventManager
from .interfaces.vapix import Vapix
from .stream_manager import StreamManager

if TYPE_CHECKING:
    from .models.configuration import Configuration


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
