"""MQTT Client api."""

from dataclasses import asdict, dataclass, field

import attr

from .api import APIItem, APIItems

URL = "/axis-cgi/mqtt"
URL_CLIENT = f"{URL}/client.cgi"
URL_EVENT = f"{URL}/event.cgi"

APIVERSION = "1.0"
CONTEXT = "Axis library"

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
    lastWillTestament: Message = attr.ib()
    connectMessage: Message = attr.ib()
    disconnectMessage: Message = attr.ib()
    ssl: Ssl = attr.ib()
    activateOnReboot: bool = attr.ib(default=True)
    username: str = attr.ib(default=None)
    password: str = attr.ib(default=None)
    clientId: str = attr.ib(default="")
    keepAliveInterval: int = attr.ib(default=60)
    connectTimeout: int = attr.ib(default=60)
    cleanSession: bool = attr.ib(default=True)
    autoReconnect: bool = attr.ib(default=True)


@attr.s
class body:
    """Create MQTT Client request body."""

    method: str = attr.ib()
    apiVersion: str = attr.ib(default=APIVERSION)
    context: str = attr.ib(default=CONTEXT)
    params: dict = attr.ib(factory=dict)


class MqttClient(APIItems):
    """MQTT Client for Axis devices."""

    def __init__(self, raw: str, request: object) -> None:
        super().__init__(raw, request, URL_CLIENT, Client)

    def configure_client(self, client_config: ClientConfig) -> None:
        """Configure MQTT Client."""
        self._request(
            "post",
            URL_CLIENT,
            data=attr.asdict(body("configureClient", params=client_config)),
        )

    def activate(self) -> None:
        """Activate MQTT Client."""
        self._request(
            "post",
            URL_CLIENT,
            data=attr.asdict(
                body("activateClient"),
                filter=attr.filters.exclude(attr.fields(body).params),
            ),
        )

    def deactivate(self) -> None:
        """Deactivate MQTT Client."""
        self._request(
            "post",
            URL_CLIENT,
            data=attr.asdict(
                body("deactivateClient"),
                filter=attr.filters.exclude(attr.fields(body).params),
            ),
        )

    def get_client_status(self) -> dict:
        """Get MQTT Client status."""
        return self._request(
            "post",
            URL_CLIENT,
            data=attr.asdict(
                body("getClientStatus"),
                filter=attr.filters.exclude(attr.fields(body).params),
            ),
        )

    def get_event_publication_config(self) -> dict:
        """Get MQTT Client event publication config."""
        return self._request(
            "post",
            URL_EVENT,
            data=attr.asdict(
                body("getEventPublicationConfig"),
                filter=attr.filters.exclude(attr.fields(body).params),
            ),
        )

    def configure_event_publication(self, topics: list = DEFAULT_TOPICS) -> None:
        """Configure MQTT Client event publication."""
        event_filter = {"eventFilterList": [{"topicFilter": topic} for topic in topics]}
        self._request(
            "post",
            URL_EVENT,
            data=attr.asdict(body("configureEventPublication", params=event_filter)),
        )


class Client(APIItem):
    """"""
