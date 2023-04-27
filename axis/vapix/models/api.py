"""API management class and base class for the different end points."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Generic, List, TypeVar

CONTEXT = "Axis library"


@dataclass
class ApiItem(ABC):
    """API item class."""

    id: str


ApiItemT = TypeVar("ApiItemT", bound=ApiItem)
ApiDataT = TypeVar("ApiDataT")


@dataclass
class ApiRequest(ABC, Generic[ApiDataT]):
    """Create API request body."""

    method: str = field(init=False)
    path: str = field(init=False)
    data: dict[str, Any] = field(init=False)

    content_type: str = field(init=False)
    error_codes: dict[int, str] = field(init=False)

    @abstractmethod
    def process_raw(self, raw: str) -> ApiDataT:
        """Process raw data."""
        raise NotImplementedError


class APIItem:
    """Base class for all end points using APIItems class."""

    def __init__(self, id: str, raw: dict, request: Callable) -> None:
        """Initialize API item."""
        self._id = id
        self._raw = raw
        self._request = request

        self.observers: List[Callable] = []

    @property
    def id(self) -> str:
        """Read only ID."""
        return self._id

    @property
    def raw(self) -> dict:
        """Read only raw data."""
        return self._raw

    def update(self, raw: dict) -> None:
        """Update raw data and signal new data is available."""
        self._raw = raw

        for observer in self.observers:
            observer()

    def register_callback(self, callback: Callable) -> None:
        """Register callback for state updates."""
        self.observers.append(callback)

    def remove_callback(self, observer: Callable) -> None:
        """Remove observer."""
        if observer in self.observers:
            self.observers.remove(observer)
