"""API handler class and base class for an API endpoint."""

from abc import ABC, abstractmethod
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
    api_request: ApiRequest[dict[str, ApiItemT]] | None
    default_api_version: str | None = None

    def __init__(self, vapix: "Vapix") -> None:
        """Initialize API items."""
        self.vapix = vapix
        self._items: dict[str, ApiItemT] = {}
        self.initialized = False

    def supported(self) -> bool:
        """Is API supported by the device."""
        return self.api_id.value in self.vapix.api_discovery

    def api_version(self) -> str | None:
        """Latest API version supported."""
        if (discovery_item := self.vapix.api_discovery[self.api_id.value]) is not None:
            return discovery_item.version
        return self.default_api_version

    async def update(self) -> None:
        """Refresh data."""
        if self.api_request is None:
            return
        self.initialized = True
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


class ApiHandler2(ABC, Generic[ApiItemT]):
    """Base class for a map of API Items."""

    api_id: "ApiId"
    default_api_version: str | None = None

    def __init__(self, vapix: "Vapix") -> None:
        """Initialize API items."""
        self.vapix = vapix
        self._items: dict[str, ApiItemT] = {}
        self.initialized = False

    def supported(self) -> bool:
        """Is API supported by the device."""
        return self.api_id.value in self.vapix.api_discovery

    @property
    def api_version(self) -> str | None:
        """Latest API version supported."""
        if (
            discovery_item := self.vapix.api_discovery.get(self.api_id.value)
        ) is not None:
            return discovery_item.version
        return self.default_api_version

    @abstractmethod
    async def _api_request(self) -> dict[str, ApiItemT]:
        """Get API data method defined by subsclass."""

    async def update(self) -> None:
        """Refresh data."""
        self._items = await self._api_request()
        self.initialized = True

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
