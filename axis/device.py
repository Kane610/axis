"""Python library to enable Axis devices to integrate with Home Assistant."""

from typing import Callable, Optional

from .configuration import Configuration
from .event_stream import EventManager
from .streammanager import StreamManager
from .vapix.vapix import Vapix


class AxisDevice:
    """Creates a new Axis device.self."""

    def __init__(self, configuration: Configuration) -> None:
        """Initialize device functionality."""
        self.config = configuration
        self.vapix = Vapix(self.config)
        self.stream = StreamManager(self.config)
        self.event: Optional[EventManager] = None

    def enable_events(self, event_callback: Callable) -> None:
        """Enable events for stream."""
        self.event = EventManager(self.vapix, event_callback)
        self.stream.event = self.event.update  # type: ignore[assignment]
