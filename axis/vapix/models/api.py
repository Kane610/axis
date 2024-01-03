"""API management class and base class for the different end points."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable, Generic, List, TypeVar

from typing_extensions import Self

CONTEXT = "Axis library"


@dataclass
class ApiItem(ABC):
    """API item class."""

    id: str


ApiItemT = TypeVar("ApiItemT", bound=ApiItem)
ApiDataT = TypeVar("ApiDataT")


@dataclass
class ApiResponseSupportDecode(ABC):
    """Response from API request."""

    @classmethod
    @abstractmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Decode data to class object."""


@dataclass
class ApiResponse(ApiResponseSupportDecode, Generic[ApiDataT]):
    """Response from API request.

    Class with generic can't be used in a TypeVar("X", bound=class) statement.
    """

    data: ApiDataT
    # error: str


ApiResponseT = TypeVar("ApiResponseT", bound=ApiResponseSupportDecode)


@dataclass
class ApiRequest(ABC):
    """Create API request body."""

    method: str = field(init=False)
    path: str = field(init=False)

    @property
    def content(self) -> bytes | None:
        """Request content."""
        return None

    @property
    def data(self) -> dict[str, str] | None:
        """Request data.

        In:
          path: /axis-cgi/com/ptz.cgi
          data: {"camera": "2", "move": "home"}
        Out:
          url: /axis-cgi/com/ptz.cgi
          payload: {"camera": 2, "move": "home"}
        """
        return None

    @property
    def params(self) -> dict[str, str] | None:
        """Request query parameters.

        In:
          path: /axis-cgi/io/port.cgi
          params: {"action": "1:/"}
        Out:
          url: /axis-cgi/io/port.cgi?action=4%3A%5C"
        """
        return None


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
