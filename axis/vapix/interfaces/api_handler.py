"""API handler class and base class for a API endpoint."""

from abc import ABC
from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    ItemsView,
    Iterator,
    KeysView,
    Type,
    TypeVar,
    ValuesView,
)

if TYPE_CHECKING:
    from ..models.api import ApiItem
    from ..models.api_discovery import ApiId
    from ..vapix import Vapix

_ItemT = TypeVar("_ItemT", bound="ApiItem")


class ApiHandler(ABC, Generic[_ItemT]):
    """Base class for a map of API Items."""

    api_id: "ApiId"
    item_cls: Type[_ItemT]
    path: str

    def __init__(self, vapix: "Vapix") -> None:
        """Initialize API items."""
        self.vapix = vapix
        self._items: dict[str, _ItemT] = {}

    async def update(self) -> None:
        """Refresh data."""
        raise NotImplementedError

    def process_raw(self, raw: dict[str, Any]) -> set:
        """Process raw and return a set of new IDs."""
        new_items: set[str] = set()

        for id in raw:
            if id in self._items:
                new_items.add(id)
            self._items[id] = self.item_cls(*raw[id])

        return new_items

    def items(self) -> ItemsView[str, _ItemT]:
        """Return items."""
        return self._items.items()

    def keys(self) -> KeysView[str]:
        """Return item keys."""
        return self._items.keys()

    def values(self) -> ValuesView[_ItemT]:
        """Return item values."""
        return self._items.values()

    def get(self, obj_id: str, default: Any | None = None) -> _ItemT | Any | None:
        """Get item value based on key, return default if no match."""
        if obj_id in self:
            return self[obj_id]
        return default

    def __getitem__(self, obj_id: str) -> _ItemT:
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
