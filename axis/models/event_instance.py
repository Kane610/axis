"""Models for the VAPIX Event Service GetEventInstances SOAP operation."""

from dataclasses import dataclass
import enum
from typing import Any, Self

import xmltodict

from .api import ApiItem, ApiRequest, ApiResponse
from .event import (
    EVENT_OPERATION,
    EVENT_SOURCE,
    EVENT_SOURCE_IDX,
    EVENT_TOPIC,
    EVENT_VALUE,
    Event,
    EventOperation,
    EventTopic,
    traverse,
)

EVENT_INSTANCE = (
    "http://www.w3.org/2003/05/soap-envelope:Envelope",
    "http://www.w3.org/2003/05/soap-envelope:Body",
    "GetEventInstancesResponse",
    "TopicSet",
)

# Namespace filter for xmltodict
NAMESPACES = {
    "http://docs.oasis-open.org/wsn/t-1": None,
    # "http://www.onvif.org/ver10/topics": "onvif",
    # "http://www.axis.com/2009/event/topics": "axis",
    "http://www.onvif.org/ver10/topics": "tns1",
    "http://www.axis.com/2009/event/topics": "tnsaxis",
    "http://www.axis.com/vapix/ws/event1": None,
}


def get_events(data: dict[str, Any]) -> list[dict[str, Any]]:
    """Flatten the SOAP topic tree into event declarations with full topic paths.

    Ignore keys with "@" while traversing structure. Indicates an attribute in value.
    When @topic is reached, return event data and build topic structure.
    """
    events = []
    for key, value in data.items():
        if key.startswith("@"):  # Value is an attribute so skip
            continue

        if "@topic" in value:  # Designates the end of the topic structure
            events.append({"topic": key, "data": value})
            continue

        event_list = get_events(value)  # Recursive call

        for event in event_list:
            event["topic"] = f"{key}/{event['topic']}"  # Compose the topic
            events.append(event)

    return events


def _as_simple_item_list(data: object) -> list[dict[str, Any]]:
    """Return a list representation for a simple-item payload."""
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and data:
        return [data]
    return []


def _as_dict(data: object) -> dict[str, Any]:
    """Return dict for mapping-like payloads and normalize other values to empty."""
    if isinstance(data, dict):
        return data
    return {}


@dataclass(frozen=True)
class EventInstanceSimpleItem:
    """Name, display name, value type, and values of one event simple item."""

    name: str = ""
    nice_name: str = ""
    value_type: str = ""
    values: tuple[str, ...] = ()
    is_property_state: bool = False

    @classmethod
    def from_raw(cls, data: object) -> Self:
        """Decode a raw simple-item payload into a typed item."""
        item = _as_dict(data)
        raw_values = item.get("Value", "")
        if isinstance(raw_values, list):
            values = tuple(str(value) for value in raw_values)
        elif raw_values in (None, ""):
            values = ()
        else:
            values = (str(raw_values),)

        return cls(
            name=str(item.get("@Name", "")),
            nice_name=str(item.get("@NiceName", "")),
            value_type=str(item.get("@Type", "")),
            values=values,
            is_property_state=item.get("@isPropertyState") == "true",
        )

    @property
    def value(self) -> str:
        """Return the first value when available."""
        return self.values[0] if self.values else ""

    def as_raw(self) -> dict[str, Any]:
        """Return the backward-compatible raw dictionary representation."""
        data: dict[str, Any] = {
            "@Name": self.name,
            "@NiceName": self.nice_name,
            "@Type": self.value_type,
        }
        if self.values:
            data["Value"] = (
                self.values[0] if len(self.values) == 1 else list(self.values)
            )
        if self.is_property_state:
            data["@isPropertyState"] = "true"
        return {key: value for key, value in data.items() if value != ""}


@dataclass(frozen=True)
class EventInstanceSource:
    """Typed source items that identify where an event instance originates."""

    items: tuple[EventInstanceSimpleItem, ...] = ()

    @classmethod
    def from_raw(cls, data: object) -> Self:
        """Decode raw source-instance payload into typed items."""
        return cls(
            items=tuple(
                EventInstanceSimpleItem.from_raw(item)
                for item in _as_simple_item_list(data)
            )
        )

    @property
    def primary_item(self) -> EventInstanceSimpleItem | None:
        """Return the first source item when available."""
        return self.items[0] if self.items else None

    @property
    def name(self) -> str:
        """Return the primary source name."""
        return self.primary_item.name if self.primary_item else ""

    @property
    def values(self) -> tuple[str, ...]:
        """Return primary source values, using an empty value when none are declared."""
        if self.primary_item is None:
            return ("",)
        return self.primary_item.values or ("",)

    def as_raw(self) -> dict[str, Any] | list[dict[str, Any]]:
        """Return source in the historical dict-or-list shape."""
        raw_items = [item.as_raw() for item in self.items]
        if not raw_items:
            return {}
        if len(raw_items) == 1:
            return raw_items[0]
        return raw_items


@dataclass(frozen=True)
class EventInstanceData:
    """Typed state or event values declared by an event instance."""

    items: tuple[EventInstanceSimpleItem, ...] = ()

    @classmethod
    def from_raw(cls, data: object) -> Self:
        """Decode raw data-instance payload into typed items."""
        return cls(
            items=tuple(
                EventInstanceSimpleItem.from_raw(item)
                for item in _as_simple_item_list(data)
            )
        )

    @property
    def primary_item(self) -> EventInstanceSimpleItem | None:
        """Return the first data item when available."""
        return self.items[0] if self.items else None

    @property
    def state_item(self) -> EventInstanceSimpleItem | None:
        """Prefer the active item to align with stream event decoding."""
        return next(
            (item for item in self.items if item.name == "active"), self.primary_item
        )

    @property
    def state_value(self) -> str:
        """Return the active item's value, or the first item's value if no active item exists."""
        if self.state_item is None:
            return ""
        return self.state_item.value

    def as_raw(self) -> dict[str, Any] | list[dict[str, Any]]:
        """Return data in the historical dict-or-list shape."""
        raw_items = [item.as_raw() for item in self.items]
        if not raw_items:
            return {}
        if len(raw_items) == 1:
            return raw_items[0]
        return raw_items


def _extract_source_values(source: EventInstanceSource) -> tuple[str, list[str]]:
    """Extract the source name and source values.

    Keep behavior aligned with event stream parsing by selecting the first source item
    when multiple source items exist.
    """
    return source.name, list(source.values)


def _extract_data_value(data: EventInstanceData) -> str:
    """Extract a representative state value from data definition.

    Prefer the "active" item when available to align with Event._decode_from_bytes().
    """
    return data.state_value


TOPIC_TO_INACTIVE_STATE = {
    EventTopic.LIGHT_STATUS.value: "OFF",
    EventTopic.RELAY.value: "inactive",
}


class EventProtocol(enum.StrEnum):
    """Protocols that consume normalized expected events."""

    METADATA_STREAM = "metadata_stream"
    WEBSOCKET = "websocket"
    MQTT = "mqtt"


def _default_inactive_state(topic: str) -> str:
    """Return a default inactive state for expected event synthesis."""
    return TOPIC_TO_INACTIVE_STATE.get(topic, "0")


@dataclass(frozen=True)
class EventInstance(ApiItem):
    """An event declaration returned by GetEventInstances.

    The declaration describes its topic, availability, statefulness, source, and data.
    It can also be converted into a normalized event for consumers of event streams.
    """

    topic: str
    """Namespace-qualified topic under which the device publishes the event."""

    topic_filter: str
    """Same topic with namespace prefixes converted for event-filter matching."""

    is_available: bool
    """Whether the device marks this event topic as available."""

    is_application_data: bool
    """Whether this event or its data is reserved for a specific system or app.

    Events with isApplicationData=true are usually intended
    to be used only by the specific system or application, that is,
    they are not intended to be used as triggers in an action rule in the Axis product.
    """

    name: str
    """User-friendly and human-readable name describing the event."""

    stateful: bool
    """Whether the event describes a persistent property that can change state.

    For example, motion detection remains true while motion is detected and false
    when no motion is detected.
    """

    stateless: bool
    """Stateless event is a momentary occurrence (a pulse).

    Example: Storage device removed.
    """

    source: EventInstanceSource
    """Source item names and values declared for this event."""

    data: EventInstanceData
    """State or event-data item names, types, and values declared by this event."""

    @property
    def raw_source(self) -> dict[str, Any] | list[dict[str, Any]]:
        """Return the source field in the previous raw structure."""
        return self.source.as_raw()

    @property
    def raw_data(self) -> dict[str, Any] | list[dict[str, Any]]:
        """Return the data field in the previous raw structure."""
        return self.data.as_raw()

    @classmethod
    def decode(cls, data: dict[str, Any]) -> Self:
        """Convert one parsed topic declaration into a typed event instance."""
        event_data = _as_dict(data.get("data"))
        message = _as_dict(event_data.get("MessageInstance"))
        source_instance = _as_dict(message.get("SourceInstance"))
        data_instance = _as_dict(message.get("DataInstance"))

        return cls(
            id=data["topic"],
            topic=data["topic"],
            topic_filter=data["topic"]
            .replace("tns1", "onvif")
            .replace("tnsaxis", "axis"),
            is_available=event_data.get("@topic") == "true",
            is_application_data=event_data.get("@isApplicationData") == "true",
            name=event_data.get("@NiceName", ""),
            stateful=message.get("@isProperty") == "true",
            stateless=message.get("@isProperty") != "true",
            source=EventInstanceSource.from_raw(
                source_instance.get("SimpleItemInstance", {})
            ),
            data=EventInstanceData.from_raw(
                data_instance.get("SimpleItemInstance", {})
            ),
        )

    def to_events(self) -> list[Event]:
        """Create initial normalized events for the sources declared by this topic.

        Topics are preserved exactly as declared, and an empty data value is replaced
        by the topic's default inactive state.
        """
        source_name, source_values = _extract_source_values(self.source)
        state_value = _extract_data_value(self.data)
        if state_value == "":
            state_value = _default_inactive_state(self.topic)

        return [
            Event.decode(
                {
                    EVENT_OPERATION: EventOperation.INITIALIZED,
                    EVENT_TOPIC: self.topic,
                    EVENT_SOURCE: source_name,
                    EVENT_SOURCE_IDX: source_value,
                    EVENT_VALUE: state_value,
                }
            )
            for source_value in source_values
        ]


@dataclass
class ListEventInstancesResponse(ApiResponse[dict[str, Any]]):
    """Event declarations returned by the Event Service, indexed by topic."""

    data: dict[str, Any]

    @classmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Parse the SOAP XML topic tree and decode each event declaration."""
        data = xmltodict.parse(
            bytes_data,
            # attr_prefix="",
            dict_constructor=dict,  # Use dict rather than ordered_dict
            namespaces=NAMESPACES,  # Replace or remove defined namespaces
            process_namespaces=True,
        )
        raw_events = traverse(data, EVENT_INSTANCE)  # Move past the irrelevant keys
        events = get_events(raw_events)  # Create topic/data dictionary of events
        return cls(data=EventInstance.decode_to_dict(events))


@dataclass
class ListEventInstancesRequest(ApiRequest[ListEventInstancesResponse]):
    """Request all event declarations from the VAPIX Event Service."""

    method = "post"
    path = "/vapix/services"
    content_type = "application/soap+xml"
    response_type = ListEventInstancesResponse

    @property
    def content(self) -> bytes:
        """Return the SOAP envelope that calls GetEventInstances."""
        return (
            b'<s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope">'
            b'<s:Body xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
            b'xmlns:xsd="http://www.w3.org/2001/XMLSchema">'
            b'<GetEventInstances xmlns="http://www.axis.com/vapix/ws/event1"/>'
            b"</s:Body>"
            b"</s:Envelope>"
        )

    @property
    def headers(self) -> dict[str, str]:
        """Return the SOAP content type and action required by the Event Service."""
        return {
            "Content-Type": "application/soap+xml",
            "SOAPAction": "http://www.axis.com/vapix/ws/event1/GetEventInstances",
        }
