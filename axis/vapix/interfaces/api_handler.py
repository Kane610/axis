"""API handler class and base class for an API endpoint."""

from abc import ABC
from collections.abc import Callable, ItemsView, Iterator, KeysView, ValuesView
from typing import TYPE_CHECKING, Any, Generic, final

from ...errors import PathNotFound, Unauthorized

if TYPE_CHECKING:
    from ..models.api_discovery import ApiId
    from ..vapix import Vapix

from ..models.api import ApiItemT

CallbackType = Callable[[str], None]
SubscriptionType = CallbackType
UnsubscribeType = Callable[[], None]

ID_FILTER_ALL = "*"


class SubscriptionHandler(ABC):
    """Manage subscription and notification to subscribers."""

    def __init__(self) -> None:
        """Initialize subscription handler."""
        self._subscribers: dict[str, list[SubscriptionType]] = {ID_FILTER_ALL: []}

    def signal_subscribers(self, obj_id: str) -> None:
        """Signal subscribers."""
        subscribers: list[SubscriptionType] = (
            self._subscribers.get(obj_id, []) + self._subscribers[ID_FILTER_ALL]
        )
        for callback in subscribers:
            callback(obj_id)

    def subscribe(
        self,
        callback: CallbackType,
        id_filter: tuple[str] | str | None = None,
    ) -> UnsubscribeType:
        """Subscribe to added events."""
        subscription = callback

        _id_filter: tuple[str]
        if id_filter is None:
            _id_filter = (ID_FILTER_ALL,)
        elif isinstance(id_filter, str):
            _id_filter = (id_filter,)

        for obj_id in _id_filter:
            if obj_id not in self._subscribers:
                self._subscribers[obj_id] = []
            self._subscribers[obj_id].append(subscription)

        def unsubscribe() -> None:
            for obj_id in _id_filter:
                if obj_id not in self._subscribers:
                    continue
                if subscription not in self._subscribers[obj_id]:
                    continue
                self._subscribers[obj_id].remove(subscription)

        return unsubscribe


class ApiHandler(SubscriptionHandler, Generic[ApiItemT]):
    """Base class for a map of API Items."""

    api_id: "ApiId"
    default_api_version: str | None = None
    skip_support_check = False

    def __init__(self, vapix: "Vapix") -> None:
        """Initialize API items."""
        super().__init__()
        self.vapix = vapix
        self._items: dict[str, ApiItemT] = {}
        self.initialized = False

    def supported(self) -> bool:
        """Is API supported by the device."""
        return self.api_id.value in self.vapix.api_discovery

    @final
    async def update(self, skip_support_check=False) -> bool:
        """Try update of API."""
        skip_support_check = skip_support_check or self.skip_support_check
        if not skip_support_check and not self.supported():
            return False

        try:
            await self._update()
        except Unauthorized:  # Probably a viewer account
            return False
        except PathNotFound:  # Device doesn't support the endpoint
            return False
        return self.initialized

    @property
    def api_version(self) -> str | None:
        """Latest API version supported."""
        if (
            discovery_item := self.vapix.api_discovery.get(self.api_id.value)
        ) is not None:
            return discovery_item.version
        return self.default_api_version

    async def _api_request(self) -> dict[str, ApiItemT]:
        """Get API data method defined by subclass."""
        raise NotImplementedError

    async def _update(self) -> None:
        """Refresh data."""
        try:
            self._items = await self._api_request()
        except NotImplementedError:
            pass
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
