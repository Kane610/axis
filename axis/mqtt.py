"""MQTT Client api."""

import attr
import json

from .api import APIItem, APIItems, Body
from .event_stream import OPERATION_CHANGED

URL = "/axis-cgi/mqtt"
URL_CLIENT = f"{URL}/client.cgi"
URL_EVENT = f"{URL}/event.cgi"

API_DISCOVERY_ID = "mqtt-client"
API_VERSION = "1.0"

DEFAULT_TOPICS = ["//."]


@attr.s
class Server:
    """Represent server config."""

    host: str = attr.ib()
    port: int = attr.ib(default=1883)
    protocol: str = attr.ib(default="tcp")


@attr.s
class Message:
    """Base class for message."""

    useDefault: bool = attr.ib(default=True)
    topic: str = attr.ib(default=None)
    message: str = attr.ib(default=None)
    retain: bool = attr.ib(default=None)
    qos: int = attr.ib(default=None)


@attr.s
class Ssl:
    """Represent SSL config."""

    validateServerCert: bool = attr.ib(default=False)


@attr.s
class ClientConfig:
    """Represent client config."""

    server: Server = attr.ib()
    lastWillTestament: Message = attr.ib(default=Message())
    connectMessage: Message = attr.ib(default=Message())
    disconnectMessage: Message = attr.ib(default=Message())
    ssl: Ssl = attr.ib(default=Ssl())
    activateOnReboot: bool = attr.ib(default=True)
    username: str = attr.ib(default=None)
    password: str = attr.ib(default=None)
    clientId: str = attr.ib(default="")
    keepAliveInterval: int = attr.ib(default=60)
    connectTimeout: int = attr.ib(default=60)
    cleanSession: bool = attr.ib(default=True)
    autoReconnect: bool = attr.ib(default=True)


def mqtt_json_to_event(msg: str) -> dict:
    """Convert JSON message from MQTT to event format."""
    message = json.loads(msg)
    topic = message["topic"].replace("onvif", "tns1").replace("axis", "tnsaxis")

    source = source_idx = ""
    if message["message"]["source"]:
        source, source_idx = next(iter(message["message"]["source"].items()))

    data_type = data_value = ""
    if message["message"]["data"]:
        data_type, data_value = next(iter(message["message"]["data"].items()))

    return {
        "operation": OPERATION_CHANGED,
        "topic": topic,
        "source": source,
        "source_idx": source_idx,
        "type": data_type,
        "value": data_value,
    }


class MqttClient(APIItems):
    """MQTT Client for Axis devices."""

    def __init__(self, request: object) -> None:
        super().__init__({}, request, URL_CLIENT, Client)

    async def update(self) -> None:
        """No update method"""

    async def configure_client(self, client_config: ClientConfig) -> None:
        """Configure MQTT Client."""
        await self._request(
            "post",
            URL_CLIENT,
            json=attr.asdict(
                Body("configureClient", API_VERSION, params=client_config),
                filter=lambda attr, value: value is not None,
            ),
        )

    async def activate(self) -> None:
        """Activate MQTT Client."""
        await self._request(
            "post",
            URL_CLIENT,
            json=attr.asdict(Body("activateClient", API_VERSION)),
        )

    async def deactivate(self) -> None:
        """Deactivate MQTT Client."""
        await self._request(
            "post",
            URL_CLIENT,
            json=attr.asdict(Body("deactivateClient", API_VERSION)),
        )

    async def get_client_status(self) -> dict:
        """Get MQTT Client status."""
        return await self._request(
            "post",
            URL_CLIENT,
            json=attr.asdict(Body("getClientStatus", API_VERSION)),
        )

    async def get_event_publication_config(self) -> dict:
        """Get MQTT Client event publication config."""
        return await self._request(
            "post",
            URL_EVENT,
            json=attr.asdict(
                Body("getEventPublicationConfig", API_VERSION),
                filter=attr.filters.exclude(attr.fields(Body).params),
            ),
        )

    async def configure_event_publication(self, topics: list = DEFAULT_TOPICS) -> None:
        """Configure MQTT Client event publication."""
        event_filter = {"eventFilterList": [{"topicFilter": topic} for topic in topics]}
        await self._request(
            "post",
            URL_EVENT,
            json=attr.asdict(
                Body("configureEventPublication", API_VERSION, params=event_filter)
            ),
        )


class Client(APIItem):
    """"""
