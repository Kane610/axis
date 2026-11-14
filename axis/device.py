"""Bring device controls, event handling, and streaming together for one Axis device."""

from typing import TYPE_CHECKING

from .interfaces.event_manager import EventManager
from .interfaces.vapix import Vapix
from .stream_manager import StreamManager

if TYPE_CHECKING:
    from .models.configuration import Configuration


class AxisDevice:
    """Provide access to one device's VAPIX APIs, event subscriptions, and stream."""

    def __init__(self, configuration: Configuration) -> None:
        """Create API, event, and stream helpers using the supplied connection settings."""
        self.config = configuration
        self.vapix = Vapix(self)
        self.stream = StreamManager(self)
        self.event = EventManager()

    def enable_events(self) -> None:
        """Include event messages when the stream is next started."""
        self.stream.event = True
