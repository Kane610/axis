"""Event service and action service APIs available in Axis network products."""

from typing import Callable, List, Optional, Union

from .api import APIItem, APIItems
from .event_stream import traverse

URL = "/vapix/services"

REQUEST_HEADERS = {
    "Content-Type": "application/soap+xml",
    "SOAPAction": "http://www.axis.com/vapix/ws/event1/GetEventInstances",
}

REQUEST_DATA = (
    '<s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope">'
    '<s:Body xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
    'xmlns:xsd="http://www.w3.org/2001/XMLSchema">'
    '<GetEventInstances xmlns="http://www.axis.com/vapix/ws/event1"/>'
    "</s:Body>"
    "</s:Envelope>"
)

# Namespace filter for xmltodict
NAMESPACES = {
    "http://docs.oasis-open.org/wsn/t-1": None,
    "http://www.onvif.org/ver10/topics": "tns1",
    "http://www.axis.com/2009/event/topics": "tnsaxis",
    "http://www.axis.com/vapix/ws/event1": None,
}

XMLTODICT_KWARGS = {
    "dict_constructor": dict,  # Use dict rather than ordered_dict
    "namespaces": NAMESPACES,  # Replace or remove defined namespaces
    "process_namespaces": True,
}

# Initial layers of event instance dictionary
EVENT_INSTANCE = (
    "http://www.w3.org/2003/05/soap-envelope:Envelope",
    "http://www.w3.org/2003/05/soap-envelope:Body",
    "GetEventInstancesResponse",
    "TopicSet",
)


def get_events(data: dict) -> List[dict]:
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


class EventInstances(APIItems):
    """Initialize new events and update states of existing events."""

    def __init__(self, request: Callable[..., Optional[dict]]) -> None:
        """Initialize class."""
        super().__init__({}, request, URL, EventInstance)

    async def update(self) -> None:
        """Retrieve event instances from device."""
        raw = await self._request(
            "post",
            URL,
            headers=REQUEST_HEADERS,
            data=REQUEST_DATA,
            kwargs_xmltodict=XMLTODICT_KWARGS,
        )
        self.process_raw(raw)

    @staticmethod
    def pre_process_raw(raw: dict) -> dict:
        """Return a dictionary of events."""
        if not raw:
            return {}

        raw_events = traverse(raw, EVENT_INSTANCE)  # Move past the irrelevant keys
        event_list = get_events(raw_events)  # Create topic/data dictionary of events

        return {event["topic"]: event for event in event_list}


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
    def source(self) -> Union[dict, list]:
        """Source instance providing information about source of the event."""
        message = self.raw["data"]["MessageInstance"]
        return message.get("SourceInstance", {}).get("SimpleItemInstance", {})

    @property
    def data(self) -> Union[dict, list]:
        """Data instance providing information about data of the event."""
        message = self.raw["data"]["MessageInstance"]
        return message.get("DataInstance", {}).get("SimpleItemInstance", {})
