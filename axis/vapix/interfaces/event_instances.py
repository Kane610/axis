"""Event service and action service APIs available in Axis network device."""

from typing import List

from ...models.event import traverse
from ..models.event_instance import EventInstance
from .api import APIItems

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

    item_cls = EventInstance
    path = URL

    async def update(self) -> None:
        """Retrieve event instances from device."""
        raw = await self.vapix.request(
            "post",
            URL,
            headers=REQUEST_HEADERS,
            content=REQUEST_DATA,
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
