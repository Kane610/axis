"""Share API support checks, cached device data, and update notifications between handlers."""

from collections.abc import (
    Callable,
    ItemsView,
    Iterator,
    KeysView,
    Sequence,
    ValuesView,
)
import enum
from typing import TYPE_CHECKING, final

from ..errors import Forbidden, PathNotFound, Unauthorized

if TYPE_CHECKING:
    from ..models.api_discovery import ApiId
    from .vapix import Vapix

from ..models.api import ApiItem

type CallbackType = Callable[[str], None]
type SubscriptionType = CallbackType
type UnsubscribeType = Callable[[], None]

ID_FILTER_ALL = "*"


class HandlerGroup(enum.Enum):
    """Choose when a handler loads data during device initialization."""

    API_DISCOVERY = "api_discovery"
    PARAM_CGI_FALLBACK = "param_cgi_fallback"
    APPLICATION = "application"


class SubscriptionHandler:
    """Call registered functions when an item ID is updated."""

    def __init__(self) -> None:
        """Start with no registered update callbacks."""
        self._subscribers: dict[str, list[SubscriptionType]] = {ID_FILTER_ALL: []}

    def signal_subscribers(self, obj_id: str) -> None:
        """Notify callbacks registered for this item ID or for all items."""
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
        """Register an item-update callback and return a function to unsubscribe."""
        subscription = callback

        _id_filter: tuple[str]
        if id_filter is None:
            _id_filter = (ID_FILTER_ALL,)
        elif isinstance(id_filter, str):
            _id_filter = (id_filter,)
        else:
            _id_filter = id_filter

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


class ApiHandler[ApiItemT: ApiItem](SubscriptionHandler):
    """Check API availability, cache items by ID, and notify subscribers after updates."""

    api_id: ApiId | None = None
    default_api_version: str | None = None
    handler_groups: tuple[HandlerGroup, ...] = ()
    skip_support_check = False

    def __init__(self, vapix: Vapix) -> None:
        """Register the handler with VAPIX and start with empty cached data."""
        super().__init__()
        self.vapix = vapix
        self.vapix._register_handler(self)
        self._items: dict[str, ApiItemT] = {}
        self.initialized = False

    @property
    def supported(self) -> bool:
        """Return whether discovery or parameters advertise support for this API."""
        return self.listed_in_api_discovery or self.listed_in_parameters

    @property
    def listed_in_api_discovery(self) -> bool:
        """Check whether the cached API discovery data lists this API."""
        if self.api_id is None:
            return False
        return self.api_id in self.vapix.api_discovery

    @property
    def listed_in_parameters(self) -> bool:
        """Check for parameter-based support; subclasses define feature-specific checks."""
        return False

    def should_initialize_in_group(self, group: HandlerGroup) -> bool:
        """Return whether handler should initialize in the given group."""
        return True

    async def _api_request(self) -> dict[str, ApiItemT]:
        """Read this API's items; subclasses implement the device request."""
        raise NotImplementedError

    async def _update(self) -> Sequence[str]:
        """Merge received data into cached items and return the received item IDs.

        Mark class as initialized if update request completed.
        """
        try:
            objects = await self._api_request()
        except NotImplementedError:
            return []
        self._items.update(objects)
        self.initialized = True
        return list(objects.keys())

    @final
    async def update(self) -> bool:
        """Refresh cached data and notify subscribers, returning whether initialization succeeded."""
        try:
            obj_ids = await self._update()
        except Unauthorized:  # Probably a viewer account
            return False
        except Forbidden:  # Invalid permissions
            return False
        except PathNotFound:  # Device doesn't support the endpoint
            return False
        for obj_id in obj_ids:
            self.signal_subscribers(obj_id)
        return self.initialized

    @property
    def api_version(self) -> str:
        """Choose the API version from device discovery, then the library default.

        Return an empty string if neither source provides a version.

        """
        discovery_version = self._get_api_discovery_version()
        if discovery_version is not None:
            return discovery_version
        return self.default_api_version or ""

    def _get_api_discovery_version(self) -> str | None:
        """Get API version from discovery data when available."""
        if self.api_id is None:
            return None

        discovery_item = self.vapix.api_discovery.get(self.api_id)
        if discovery_item is None:
            return None

        discovery_version = getattr(discovery_item, "version", None)
        if isinstance(discovery_version, str):
            return discovery_version

        return None

    def items(self) -> ItemsView[str, ApiItemT]:
        """Return a view of cached item IDs and their data."""
        return self._items.items()

    def update_items(self, items: dict[str, ApiItemT]) -> None:
        """Merge new items into the handler storage."""
        self._items.update(items)

    def keys(self) -> KeysView[str]:
        """Return a view of cached item IDs."""
        return self._items.keys()

    def values(self) -> ValuesView[ApiItemT]:
        """Return a view of cached item data."""
        return self._items.values()

    def get(self, obj_id: str) -> ApiItemT | None:
        """Return cached data for an item ID, or None if it is missing."""
        return self._items.get(obj_id)

    def __getitem__(self, obj_id: str) -> ApiItemT:
        """Return cached data for the requested item ID."""
        return self._items[obj_id]

    def __iter__(self) -> Iterator[str]:
        """Iterate over cached item IDs."""
        return iter(self._items)

    def __contains__(self, obj_id: str) -> bool:
        """Check whether an item ID has cached data."""
        return obj_id in self._items

    def __len__(self) -> int:
        """Return the number of cached items."""
        return len(self._items)
