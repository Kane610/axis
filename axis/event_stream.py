"""Python library to enable Axis devices to integrate with Home Assistant."""

from collections.abc import Callable
import logging
from typing import TYPE_CHECKING, Any

from .models.event import Event, EventOperation, EventTopic

if TYPE_CHECKING:
    from .device import AxisDevice


SubscriptionCallback = Callable[[Event], None]
SubscriptionType = tuple[
    SubscriptionCallback,
    tuple[EventTopic, ...] | None,
    tuple[EventOperation, ...] | None,
]
UnsubscribeType = Callable[[], None]

ID_FILTER_ALL = "*"

BLACK_LISTED_TOPICS = [
    "tnsaxis:CameraApplicationPlatform/VMD/xinternal_data",
    "tnsaxis:CameraApplicationPlatform/ObjectAnalytics/xinternal_data",
]
LOGGER = logging.getLogger(__name__)


class EventManager:
    """Initialize new events and update states of existing events."""

    def __init__(self, device: "AxisDevice") -> None:
        """Ready information about events."""
        self.device = device
        self._known_topics: set[str] = set()
        self._subscribers: dict[str, list[SubscriptionType]] = {ID_FILTER_ALL: []}

    def handler(self, data: bytes | dict[str, Any]) -> None:
        """Create event and pass it along to subscribers."""
        event = Event.decode(data)
        if LOGGER.isEnabledFor(logging.DEBUG):
            LOGGER.debug(event)

        if event.topic_base == EventTopic.UNKNOWN or event.topic in BLACK_LISTED_TOPICS:
            return

        known = (unique_topic := f"{event.topic}_{event.id}") not in self._known_topics
        self._known_topics.add(unique_topic)

        if event.operation == EventOperation.UNKNOWN:
            # MQTT events does not report operation
            event.operation = (
                EventOperation.INITIALIZED if known else EventOperation.CHANGED
            )

        subscribers: list[SubscriptionType] = (
            self._subscribers.get(event.id, []) + self._subscribers[ID_FILTER_ALL]
        )
        for callback, topic_filter, operation_filter in subscribers:
            if topic_filter is not None and event.topic_base not in topic_filter:
                continue
            if operation_filter is not None and event.operation not in operation_filter:
                continue
            callback(event)

    def subscribe(
        self,
        callback: SubscriptionCallback,
        id_filter: tuple[str] | str | None = None,
        topic_filter: tuple[EventTopic, ...] | EventTopic | None = None,
        operation_filter: tuple[EventOperation, ...] | EventOperation | None = None,
    ) -> UnsubscribeType:
        """Subscribe to events.

        "callback" - callback function to call when on event.
        Return function to unsubscribe.
        """
        if isinstance(topic_filter, EventTopic):
            topic_filter = (topic_filter,)
        if isinstance(operation_filter, EventOperation):
            operation_filter = (operation_filter,)
        subscription = (callback, topic_filter, operation_filter)

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

    def __len__(self) -> int:
        """List number of subscribers."""
        return sum(len(s) for s in self._subscribers.values())
