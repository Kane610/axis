"""API management class and base class for the different end points."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, ClassVar, Self

CONTEXT = "Axis library"


@dataclass(frozen=True)
class ApiItem(ABC):
    """API item class."""

    id: str

    @classmethod
    @abstractmethod
    def decode(cls, data: Any) -> Self:
        """Decode data to class object."""

    @classmethod
    def decode_to_list(cls, data_list: list[Any]) -> list[Self]:
        """Decode list of data to a list of class objects."""
        return [cls.decode(data) for data in data_list]

    @classmethod
    def decode_to_dict(cls, data: list[Any]) -> dict[str, Self]:
        """Decode list of data to a dict of class objects."""
        return {v.id: v for v in cls.decode_to_list(data)}


@dataclass
class ApiResponseSupportDecode(ABC):
    """Response from API request."""

    @classmethod
    @abstractmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Decode data to class object."""


@dataclass
class ApiResponse[ApiDataT](ApiResponseSupportDecode):
    """Response from API request."""

    data: ApiDataT
    # error: str


@dataclass
class ApiRequest:
    """Create API request body."""

    method: str = field(init=False)
    path: str = field(init=False)
    content_type: str = field(init=False)
    response_type: ClassVar[type[ApiResponseSupportDecode] | None] = None

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
    def headers(self) -> dict[str, str]:
        """Request headers."""
        return {"Content-Type": self.content_type}

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
