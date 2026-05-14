"""Event service and action service APIs available in Axis network device."""

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
    """Get all events.

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
    """Typed representation of a single event-instance simple item."""

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
    """Structured source definition for an event instance."""

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
        """Return source values for event synthesis."""
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
    """Structured data definition for an event instance."""

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
        """Return a representative value for state synthesis."""
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
    """Events are emitted when the Axis product detects an occurrence of some kind.

    For example motion in camera field of view or a change of status from an I/O port.
    The events can be used to trigger actions in the Axis product or in other systems
    and can also be stored together with video and audio data for later access.
    """

    topic: str
    """Event topic.

    Event declaration namespace.
    """

    topic_filter: str
    """Event topic.

    Event topic filter namespace.
    """

    is_available: bool
    """Means the event is available."""

    is_application_data: bool
    """Indicate event and/or data is produced for specific system or application.

    Events with isApplicationData=true are usually intended
    to be used only by the specific system or application, that is,
    they are not intended to be used as triggers in an action rule in the Axis product.
    """

    name: str
    """User-friendly and human-readable name describing the event."""

    stateful: bool
    """Stateful event is a property (a state variable) with a number of states.

    The event is always in one of its states.
    Example: The Motion detection event is in state true when motion is detected
    and in state false when motion is not detected.
    """

    stateless: bool
    """Stateless event is a momentary occurrence (a pulse).

    Example: Storage device removed.
    """

    source: EventInstanceSource
    """Event source information."""

    data: EventInstanceData
    """Event data description."""

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
        """Decode dict to class object."""
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
        """Synthesize normalized expected events from event-instance schema data.

        Topics are preserved exactly as they are declared by event instances so topic
        representation stays identical to emitted event topics.
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
class ListEventInstancesRequest(ApiRequest):
    """Request object for listing installed applications."""

    method = "post"
    path = "/vapix/services"
    content_type = "application/soap+xml"

    @property
    def content(self) -> bytes:
        """Request content."""
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
        """Request headers."""
        return {
            "Content-Type": "application/soap+xml",
            "SOAPAction": "http://www.axis.com/vapix/ws/event1/GetEventInstances",
        }


@dataclass
class ListEventInstancesResponse(ApiResponse[dict[str, Any]]):
    """Response object for listing all applications."""

    data: dict[str, Any]

    @classmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Prepare API description dictionary."""
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
