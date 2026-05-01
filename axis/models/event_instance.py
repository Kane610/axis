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


def _as_simple_item_list(
    data: object,
) -> list[dict[str, Any]]:
    """Return a list representation for a simple-item payload."""
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return [data]
    return []


def _extract_source_values(
    source: dict[str, Any] | list[dict[str, Any]],
) -> tuple[str, list[str]]:
    """Extract the source name and source values.

    Keep behavior aligned with event stream parsing by selecting the first source item
    when multiple source items exist.
    """
    source_items = _as_simple_item_list(source)
    if not source_items:
        return "", [""]

    source_item = source_items[0]
    source_name = str(source_item.get("@Name", ""))
    values = source_item.get("Value", "")
    if isinstance(values, list):
        source_values = [str(value) for value in values]
        return source_name, source_values or [""]
    if values in (None, ""):
        return source_name, [""]
    return source_name, [str(values)]


def _extract_data_value(data: dict[str, Any] | list[dict[str, Any]]) -> str:
    """Extract a representative state value from data definition.

    Prefer the "active" item when available to align with Event._decode_from_bytes().
    """
    data_items = _as_simple_item_list(data)
    if not data_items:
        return ""

    data_item = next(
        (item for item in data_items if item.get("@Name", "") == "active"),
        data_items[0],
    )
    value = data_item.get("Value", "")
    if isinstance(value, list):
        return str(value[0]) if value else ""
    return "" if value is None else str(value)


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

    source: dict[str, Any] | list[dict[str, Any]]
    """Event source information."""

    data: dict[str, Any] | list[dict[str, Any]]
    """Event data description."""

    @classmethod
    def decode(cls, data: dict[str, Any]) -> Self:
        """Decode dict to class object."""
        message = data["data"].get("MessageInstance", {})
        return cls(
            id=data["topic"],
            topic=data["topic"],
            topic_filter=data["topic"]
            .replace("tns1", "onvif")
            .replace("tnsaxis", "axis"),
            is_available=data["data"]["@topic"] == "true",
            is_application_data=data["data"].get("@isApplicationData") == "true",
            name=data["data"].get("@NiceName", ""),
            stateful=message.get("@isProperty") == "true",
            stateless=message.get("@isProperty") != "true",
            source=message.get("SourceInstance", {}).get("SimpleItemInstance", {}),
            data=message.get("DataInstance", {}).get("SimpleItemInstance", {}),
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
