"""Base request, response, and item models for Axis API endpoints."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, ClassVar, Protocol, Self

CONTEXT = "Axis library"


@dataclass(frozen=True)
class ApiItem(ABC):
    """Base for decoded API items that have an identifier."""

    id: str

    @classmethod
    @abstractmethod
    def decode(cls, data: Any) -> Self:
        """Build an item from its decoded API payload."""

    @classmethod
    def decode_to_list(cls, data_list: list[Any]) -> list[Self]:
        """Build one item for each payload in a list."""
        return [cls.decode(data) for data in data_list]

    @classmethod
    def decode_to_dict(cls, data: list[Any]) -> dict[str, Self]:
        """Build items from a list and index them by their identifiers."""
        return {v.id: v for v in cls.decode_to_list(data)}


class ApiResponseDecoder[DecodedT](Protocol):
    """Decoder contract for API request responses."""

    @classmethod
    def decode(cls, bytes_data: bytes) -> DecodedT:
        """Decode raw bytes into a typed response payload."""


@dataclass
class ApiResponse[ApiDataT](ABC):
    """Typed data returned by an API request."""

    data: ApiDataT
    # error: str

    @classmethod
    @abstractmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Parse the response bytes into this response type."""


@dataclass
class BytesResponse(ApiResponse[bytes]):
    """Response wrapper for APIs that only return raw bytes."""

    @classmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Wrap raw response payload bytes in an ApiResponse object."""
        return cls(data=bytes_data)


@dataclass
class ApiRequest[ResponseT = ApiResponse[bytes]]:
    """Describe an HTTP request and the response type expected from it."""

    method: str = field(init=False)
    path: str = field(init=False)
    content_type: str = field(init=False)
    response_type: ClassVar[type[ApiResponseDecoder[ResponseT]]]
    # Some APIs reject the Axis-Orig-Sw parameter used by Companion devices
    supports_companion_param: ClassVar[bool] = True

    @property
    def content(self) -> bytes | None:
        """Return the encoded request body, if this endpoint has one."""
        return None

    @property
    def data(self) -> dict[str, str] | None:
        """Return form or query data to send with this request.

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
        """Return headers required to send this request."""
        return {"Content-Type": self.content_type}

    @property
    def params(self) -> dict[str, str] | None:
        """Return URL query parameters for this request, if any."""
        return None
