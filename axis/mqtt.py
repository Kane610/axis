"""MQTT Client api."""

from dataclasses import asdict, dataclass, field

from .api import APIItem, APIItems

URL = "/axis-cgi/mqtt"
URL_CLIENT = f"{URL}/client.cgi"
URL_EVENT = f"{URL}/event.cgi"

APIVERSION = "1.0"
CONTEXT = "Axis library"

DEFAULT_TOPICS = ["//."]


@dataclass
class Server:
    """Represent server config."""

    host: str
    port: int = 1883
    protocol: str = "tcp"


@dataclass
class Message:
    """Base class for message."""

    useDefault: bool = True
    topic: str = None
    message: str = None
    retain: bool = None
    qos: int = None


@dataclass
class Ssl:
    """Represent SSL config."""

    validateServerCert: bool = False


@dataclass
class ClientConfig:
    """Represent client config."""

    server: Server
    lastWillTestament: Message
    connectMessage: Message
    disconnectMessage: Message
    ssl: Ssl
    activateOnReboot: bool = True
    username: str = None
    password: str = None
    clientId: str = ""
    keepAliveInterval: int = 60
    connectTimeout: int = 60
    cleanSession: bool = True
    autoReconnect: bool = True


@dataclass
class body:
    """Create MQTT Client request body."""

    method: str
    apiVersion: str = APIVERSION
    context: str = CONTEXT
    params: dict = field(default_factory=dict)


class MqttClient(APIItems):
    """MQTT Client for Axis devices."""

    def __init__(self, raw: str, request: object) -> None:
        super().__init__(raw, request, URL_CLIENT, Client)

    def configure_client(self, client_config: ClientConfig) -> None:
        """Configure MQTT Client."""
        self._request(
            "post",
            URL_CLIENT,
            data=asdict(body("configureClient", params=client_config)),
        )

    def activate(self) -> None:
        """Activate MQTT Client."""
        self._request("post", URL_CLIENT, data=asdict(body("activateClient")))

    def deactivate(self) -> None:
        """Deactivate MQTT Client."""
        self._request("post", URL_CLIENT, data=asdict(body("deactivateClient")))

    def status(self) -> dict:
        """Get MQTT Client status."""
        self._request("post", URL_CLIENT, data=asdict(body("getClientStatus")))

    def event_publication_config(self) -> dict:
        """Get MQTT Client event publication config."""
        self._request("post", URL_EVENT, data=asdict(body("getEventPublicationConfig")))

    def configure_event_publication(self, topics: list = DEFAULT_TOPICS) -> None:
        """Configure MQTT Client event publication."""
        event_filter = {"eventFilterList": [{"topicFilter": topic} for topic in topics]}
        self._request(
            "post",
            URL_EVENT,
            data=asdict(body("configureEventPublication", params=event_filter)),
        )


class Client(APIItem):
    """"""
