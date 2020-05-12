"""API management class and base class for the different end points."""

from abc import ABC, abstractmethod
import logging

from pprint import pformat

LOGGER = logging.getLogger(__name__)


class APIItems:
    """Base class for a map of API Items."""

    def __init__(self, raw, request, path, item_cls) -> None:
        self._request = request
        self._path = path
        self._item_cls = item_cls
        self._items = {}
        self.process_raw(raw)
        LOGGER.debug(pformat(raw))

    def update(self, path=None) -> None:
        if not path:
            path = self._path
        raw = self._request("get", path)
        self.process_raw(raw)

    def process_raw(self, raw: dict) -> None:
        for id, raw_item in raw.items():
            obj = self._items.get(id)

            if obj is not None:
                obj.raw = raw_item
            else:
                self._items[id] = self._item_cls(id, raw_item, self._request)

    def values(self):
        return self._items.values()

    def __getitem__(self, obj_id: str):
        return self._items[obj_id]

    def __iter__(self):
        return iter(self._items)


class APIItem:
    """Base class for all end points using APIItems class."""

    def __init__(self, raw: dict, request) -> None:
        self._raw = raw
        self._request = request

        self.observers = set()

    @property
    def raw(self) -> dict:
        """Read only raw data."""
        return self._raw

    def update(self, raw: dict) -> None:
        """Update raw data and signal new data is available."""
        self._raw = raw

        for observer in self.observers:
            # observer.update()
            observer()


class APIItemObserver(ABC):
    """To register observer to an APIItem."""

    @abstractmethod
    def update(self):
        raise NotImplementedError
