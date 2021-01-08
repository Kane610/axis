"""Event service and action service APIs available in Axis network products."""

from typing import List, Union

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

NAMESPACES = {
    "http://docs.oasis-open.org/wsn/t-1": None,
    "http://www.onvif.org/ver10/topics": "tns1",
    "http://www.axis.com/2009/event/topics": "tnsaxis",
    "http://www.axis.com/vapix/ws/event1": None,
}

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

        if "@topic" in value:
            m = value["MessageInstance"]
            events.append(
                {
                    "topic": key,
                    "is_available": value["@topic"] == "true",
                    "is_application_data": value.get("@isApplicationData") == "true",
                    "name": value.get("@NiceName", ""),
                    "message": {
                        "stateful": m.get("@isProperty", "false") == "true",
                        "stateless": m.get("@isProperty", "false") == "false",
                        "source": m.get("SourceInstance", {}).get(
                            "SimpleItemInstance", {}
                        ),
                        "data": m.get("DataInstance", {}).get("SimpleItemInstance", {}),
                    },
                }
            )
            continue

        event_list = get_events(value)
        for event in event_list:
            event["topic"] = f'{key}/{event["topic"]}'
            events.append(event)

    return events


class EventInstances(APIItems):
    """Initialize new events and update states of existing events."""

    def __init__(self, request: object) -> None:
        """Initialize class."""
        super().__init__({}, request, URL, EventInstance)

    async def update(self) -> None:
        """Prepare event."""
        raw = await self._request(
            "post",
            URL,
            headers=REQUEST_HEADERS,
            data=REQUEST_DATA,
            kwargs_xmltodict={"process_namespaces": True, "namespaces": NAMESPACES},
        )
        self.process_raw(raw)

    @staticmethod
    def pre_process_raw(raw: dict) -> dict:
        """Return a dictionary of initialized or changed events."""
        if not raw:
            return {}

        raw_events = traverse(raw, EVENT_INSTANCE)
        event_list = get_events(raw_events)

        events = {}
        for event in event_list:
            source = event["message"]["source"]
            if isinstance(source, list):
                source = source[0]
            id = f'{event["topic"]}_{source.get("Value", "")}'
            events[id] = event

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
    def is_available(self) -> str:
        """Means the event is available."""
        return self.raw["is_available"]

    @property
    def is_application_data(self) -> str:
        """Indicate event and/or data is produced for specific system or application.

        Events with isApplicationData=true are usually intended
        to be used only by the specific system or application, that is,
        they are not intended to be used as triggers in an action rule in the Axis product.
        """
        return self.raw["is_application_data"]

    @property
    def name(self) -> str:
        """User-friendly and human-readable name describing the event."""
        return self.raw["name"]

    @property
    def stateful(self) -> bool:
        """Stateful event is a property (a state variable) with a number of states.

        The event is always in one of its states.
        Example: The Motion detection event is in state true when motion is detected
        and in state false when motion is not detected.
        """
        return self.raw["message"]["stateful"]

    @property
    def stateless(self) -> bool:
        """Stateless event is a momentary occurrence (a pulse).

        Example: Storage device removed.
        """
        return self.raw["message"]["stateless"]

    @property
    def source(self) -> Union[dict, list, None]:
        """A SourceInstance that provides information about the source of the event."""
        return self.raw["message"]["source"]

    @property
    def data(self) -> Union[dict, list]:
        """A DataInstance that specifies the event data."""
        return self.raw["message"]["data"]
