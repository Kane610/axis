"""Event service and action service APIs available in Axis network device."""

from dataclasses import dataclass
from typing import Any, Self

import xmltodict

from ...models.event import traverse
from .api import APIItem, ApiRequest, ApiResponse

EVENT_INSTANCE = (
    "http://www.w3.org/2003/05/soap-envelope:Envelope",
    "http://www.w3.org/2003/05/soap-envelope:Body",
    "GetEventInstancesResponse",
    "TopicSet",
)
# Namespace filter for xmltodict
NAMESPACES = {
    "http://docs.oasis-open.org/wsn/t-1": None,
    "http://www.onvif.org/ver10/topics": "tns1",
    "http://www.axis.com/2009/event/topics": "tnsaxis",
    "http://www.axis.com/vapix/ws/event1": None,
}


def get_events(data: dict) -> list[dict]:
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
            event["topic"] = f'{key}/{event["topic"]}'  # Compose the topic
            events.append(event)

    return events


class EventInstance(APIItem):
    """Events are emitted when the Axis product detects an occurrence of some kind.

    For example motion in camera field of view or a change of status from an I/O port.
    The events can be used to trigger actions in the Axis product or in other systems
    and can also be stored together with video and audio data for later access.
    """

    @property
    def topic(self) -> str:
        """Event topic.

        Event declaration namespae.
        """
        return self.raw["topic"]

    @property
    def topic_filter(self) -> str:
        """Event topic.

        Event topic filter namespae.
        """
        return self.raw["topic"].replace("tns1", "onvif").replace("tnsaxis", "axis")

    @property
    def is_available(self) -> bool:
        """Means the event is available."""
        return self.raw["data"]["@topic"] == "true"

    @property
    def is_application_data(self) -> bool:
        """Indicate event and/or data is produced for specific system or application.

        Events with isApplicationData=true are usually intended
        to be used only by the specific system or application, that is,
        they are not intended to be used as triggers in an action rule in the Axis product.
        """
        return self.raw["data"].get("@isApplicationData") == "true"

    @property
    def name(self) -> str:
        """User-friendly and human-readable name describing the event."""
        return self.raw["data"].get("@NiceName", "")

    @property
    def stateful(self) -> bool:
        """Stateful event is a property (a state variable) with a number of states.

        The event is always in one of its states.
        Example: The Motion detection event is in state true when motion is detected
        and in state false when motion is not detected.
        """
        return self.raw["data"]["MessageInstance"].get("@isProperty") == "true"

    @property
    def stateless(self) -> bool:
        """Stateless event is a momentary occurrence (a pulse).

        Example: Storage device removed.
        """
        return self.raw["data"]["MessageInstance"].get("@isProperty") != "true"

    @property
    def source(self) -> dict | list:
        """Event source information."""
        message = self.raw["data"]["MessageInstance"]
        return message.get("SourceInstance", {}).get("SimpleItemInstance", {})

    @property
    def data(self) -> dict | list:
        """Event data description."""
        message = self.raw["data"]["MessageInstance"]
        return message.get("DataInstance", {}).get("SimpleItemInstance", {})


@dataclass
class ListEventInstancesRequest(ApiRequest):
    """Request object for listing installed applications."""

    method = "post"
    path = "/vapix/services"

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
            dict_constructor=dict,  # Use dict rather than ordered_dict
            namespaces=NAMESPACES,  # Replace or remove defined namespaces
            process_namespaces=True,
        )
        raw_events = traverse(data, EVENT_INSTANCE)  # Move past the irrelevant keys
        event_list = get_events(raw_events)  # Create topic/data dictionary of events
        return cls(data={event["topic"]: event for event in event_list})
        # data = xmltodict.parse(bytes_data, attr_prefix="", force_list={"application"})
        # apps: list[Any] = data.get("reply", {}).get("application", [])
        # return cls(data=Application.decode_from_list(apps))
