"""MQTT Client api."""

from dataclasses import dataclass

from typing_extensions import NotRequired, TypedDict

from .api import CONTEXT, APIItem, ApiRequest

# from typing import Literal


API_VERSION = "1.0"


class ErrorDataT(TypedDict):
    """Error data in response."""

    code: int
    message: str


class MessageT(TypedDict):
    """Represent a message object."""

    message: str
    qos: int
    retain: bool
    topic: str
    useDefault: bool


class ServerT(TypedDict):
    """Represent a server object."""

    host: str
    port: int
    protocol: str
    # protocol: Literal["ssl", "tcp", "ws", "wss"]


class SslT(TypedDict):
    """Represent a SSL object."""

    validateServerCert: bool


class ConfigT(TypedDict):
    """Represent client config."""

    autoReconnect: bool
    cleanSession: bool
    clientId: str
    connectMessage: MessageT
    connectTimeout: int
    deviceTopicPrefix: str
    disconnectMessage: MessageT
    keepAliveInterval: int
    lastWillTestament: MessageT
    password: str
    server: ServerT
    ssl: SslT
    username: str


class StatusT(TypedDict):
    """Represent a status object."""

    connectionStatus: str
    state: str


class ClientStatusDataT(TypedDict):
    """Client status data."""

    config: ConfigT
    status: StatusT


class GetClientStatusResponseT(TypedDict):
    """Represent client config."""

    apiVersion: str
    context: str
    method: str
    data: ClientStatusDataT
    error: NotRequired[ErrorDataT]


general_error_codes = {
    1100: "Internal error",
    2100: "API version not supported",
    2101: "Invalid JSON",
    2102: "Method not supported",
    2103: "Required parameter missing",
    2104: "Invalid parameter value specified",
}


class Client(APIItem):
    """MQTT client."""


@dataclass
class ListViewAreasRequest(ApiRequest[None]):
    """Request object for listing view areas."""

    method = "post"
    path = "/axis-cgi/mqtt/client.cgi"
    content_type = "application/json"
    error_codes = general_error_codes

    api_version: str = API_VERSION
    context: str = CONTEXT

    def __post_init__(self) -> None:
        """Initialize request data."""
        self.data = {
            "apiVersion": self.api_version,
            "context": self.context,
            "method": "configureClient",
            "params": None,
        }

    def process_raw(self, raw: str) -> None:
        """Prepare view area dictionary."""
