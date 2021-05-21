"""Python library to enable Axis devices to integrate with Home Assistant."""

import logging
from typing import Callable, Optional

from .configuration import Configuration
from .event_stream import EventManager
from .streammanager import StreamManager
from .vapix import Vapix

_LOGGER = logging.getLogger(__name__)


class AxisDevice:
    """Creates a new Axis device.self."""

    def __init__(self, configuration: Configuration) -> None:
        """Initialize device functionality."""
        self.config = configuration
        self.vapix = Vapix(self.config)
        self.stream = StreamManager(self.config)
        self.event: Optional[EventManager] = None

    def enable_events(self, event_callback: Optional[Callable] = None) -> None:
        """Enable events for stream."""
        self.event = EventManager(event_callback)
        # Event should be changed to a callback
        self.stream.event = self.event  # type: ignore[assignment]
