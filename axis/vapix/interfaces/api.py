"""API management class and base class for the different end points."""

import logging
from pprint import pformat
from typing import Any, ItemsView, Iterator, KeysView, Optional, ValuesView

import attr

from ..models.api import APIItem

LOGGER = logging.getLogger(__name__)

CONTEXT = "Axis library"


@attr.s
class Body:
    """Create API request body."""

    method: str = attr.ib()
    apiVersion: str = attr.ib()
    context: str = attr.ib(default=CONTEXT)
    params: Any = attr.ib(factory=dict)


class APIItems:
    """Base class for a map of API Items."""

    item_cls: Any
    path: str

    def __init__(self, vapix, raw=None) -> None:
        """Initialize API items."""
        self.vapix = vapix
        self._items: dict = {}
        if raw is not None:
            self.process_raw(raw)
            LOGGER.debug(pformat(raw))

    async def update(self) -> None:
        """Refresh data."""
        raw = await self.vapix.request("get", self.path)
        self.process_raw(raw)

    @staticmethod
    def pre_process_raw(raw: dict) -> dict:
        """Allow childs to pre-process raw data."""
        return raw

    def process_raw(self, raw: Any) -> set:
        """Process raw and return a set of new IDs."""
        new_items = set()

        for id, raw_item in self.pre_process_raw(raw).items():
            obj = self._items.get(id)

            if obj is not None:
                obj.update(raw_item)
            else:
                self._items[id] = self.item_cls(id, raw_item, self.vapix.request)
                new_items.add(id)

        return new_items

    def items(self) -> ItemsView[str, APIItem]:
        """Return items."""
        return self._items.items()

    def keys(self) -> KeysView[str]:
        """Return item keys."""
        return self._items.keys()

    def values(self) -> ValuesView[APIItem]:
        """Return item values."""
        return self._items.values()

    def get(self, obj_id: str, default: Optional[Any] = None):
        """Get item value based on key, return default if no match."""
        if obj_id in self:
            return self[obj_id]
        return default

    def __getitem__(self, obj_id: str) -> APIItem:
        """Get item value based on key."""
        return self._items[obj_id]

    def __iter__(self) -> Iterator[str]:
        """Allow iterate over items."""
        return iter(self._items)

    def __contains__(self, obj_id: str) -> bool:
        """Validate membership of item ID."""
        return obj_id in self._items

    def __len__(self) -> int:
        """Return number of items in class."""
        return len(self._items)

    def __bool__(self) -> bool:
        """Return True.

        Needs to define this because __len__ asserts false on length 0.
        """
        return True
