"""Event service and action service APIs available in Axis network products."""

import logging

import xmltodict

from .api import APIItem, APIItems

_LOGGER = logging.getLogger(__name__)

URL = "/vapix/services"
HEADERS = {
    "Content-Type": "application/soap+xml",
    "SOAPAction": "http://www.axis.com/vapix/ws/event1/GetEventInstances",
}
DATA = (
    '<s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope">'
    '<s:Body xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
    'xmlns:xsd="http://www.w3.org/2001/XMLSchema">'
    '<GetEventInstances xmlns="http://www.axis.com/vapix/ws/event1"/>'
    "</s:Body>"
    "</s:Envelope>"
)

NAMESPACES = {
    "http://www.onvif.org/ver10/schema": None,
    "http://www.onvif.org/ver10/topics": None,
    "http://docs.oasis-open.org/wsn/b-2": None,
    "http://docs.oasis-open.org/wsn/t-1": None,
    "http://www.axis.com/2009/event/topics": None,
    "http://www.axis.com/vapix/ws/event1": None,
}


class EventInstances(APIItems):
    """Initialize new events and update states of existing events."""

    def __init__(self, request: object) -> None:
        super().__init__({}, request, URL, EventInstance)

    async def update(self) -> None:
        """Prepare event."""
        raw = await self._request("post", URL, headers=HEADERS, data=DATA)
        self.process_raw(raw)

    @staticmethod
    def pre_process_raw(raw: bytes) -> dict:
        """Return a dictionary of initialized or changed events."""
        if not raw:
            return {}
        print(raw)
        raw = xmltodict.parse(raw, process_namespaces=True, namespaces=NAMESPACES)

        attributes = (
            "http://www.w3.org/2003/05/soap-envelope:Envelope",
            "http://www.w3.org/2003/05/soap-envelope:Body",
            "GetEventInstancesResponse",
            "TopicSet",  # Iterate until TopicSet?
        )
        for attribute in attributes:
            raw = raw[attribute]
        print(raw.keys())
        topic_sets = (
            "AudioSource",
            "CameraApplicationPlatform",
            "Device",
            "LightControl",
            "Media",
            "PTZController",
            "RecordingConfig",
            "RuleEngine",
            "Storage",
            "UserAlarm",
            "VideoSource",
        )

        for topic in topic_sets:
            # raw = raw[attribute]
            print(topic, raw[topic].keys())

        attrs = (
            "CameraApplicationPlatform",
            "VMD",
            "Camera1Profile1",  # @NiceName
            "MessageInstance",  # @topic
            "DataInstance",  # @isProperty
            "SimpleItemInstance",
        )
        for attr in attrs:
            raw = raw[attr]
            print(attr, raw.keys())
            print(raw)

        return {}


class EventInstance(APIItem):
    """"""