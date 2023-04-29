"""API handler class and base class for a API endpoint."""

from abc import ABC
from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    ItemsView,
    Iterator,
    KeysView,
    ValuesView,
)

if TYPE_CHECKING:
    from ..models.api_discovery import ApiId
    from ..vapix import Vapix

from ..models.api import ApiItemT, ApiRequest


class ApiHandler(ABC, Generic[ApiItemT]):
    """Base class for a map of API Items."""

    api_id: "ApiId"
    api_request: ApiRequest[dict[str, ApiItemT]]

    def __init__(self, vapix: "Vapix") -> None:
        """Initialize API items."""
        self.vapix = vapix
        self._items: dict[str, ApiItemT] = {}

    async def update(self) -> None:
        """Refresh data."""
        print("API HANDLER")
        self._items = await self.vapix.request2(self.api_request)

    def items(self) -> ItemsView[str, ApiItemT]:
        """Return items."""
        return self._items.items()

    def keys(self) -> KeysView[str]:
        """Return item keys."""
        return self._items.keys()

    def values(self) -> ValuesView[ApiItemT]:
        """Return item values."""
        return self._items.values()

    def get(self, obj_id: str, default: Any | None = None) -> ApiItemT | Any | None:
        """Get item value based on key, return default if no match."""
        if obj_id in self:
            return self[obj_id]
        return default

    def __getitem__(self, obj_id: str) -> ApiItemT:
        """Get item value based on key."""
        return self._items[obj_id]

    def __iter__(self) -> Iterator[str]:
        """Allow iterate over items."""
        return iter(self._items)

    def __contains__(self, obj_id: str) -> bool:
        """Validate membership of object ID."""
        return obj_id in self._items

    def __len__(self) -> int:
        """Return number of items in class."""
        return len(self._items)
