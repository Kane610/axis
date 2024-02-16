"""MQTT Client api."""

from dataclasses import dataclass
import enum
from typing import Literal, NotRequired, Self

import orjson
from typing_extensions import TypedDict

from .api import CONTEXT, ApiRequest, ApiResponse

API_VERSION = "1.0"


class ErrorDataT(TypedDict):
    """Error data in response."""

    code: int
    message: str


class MessageT(TypedDict):
    """Represent a message object."""

    useDefault: bool
    message: NotRequired[str]
    qos: NotRequired[int]
    retain: NotRequired[bool]
    topic: NotRequired[str]


class ServerT(TypedDict):
    """Represent a server object."""

    host: str
    protocol: NotRequired[Literal["ssl", "tcp", "ws", "wss"]]
    alpnProtocol: NotRequired[str]
    basepath: NotRequired[str]
    port: NotRequired[int]


class SslT(TypedDict):
    """Represent a SSL object."""

    validateServerCert: bool
    CACertID: NotRequired[str]
    clientCertID: NotRequired[str]


class ConfigT(TypedDict):
    """Represent client config."""

    server: ServerT
    activateOnReboot: NotRequired[bool]
    autoReconnect: NotRequired[bool]
    cleanSession: NotRequired[bool]
    clientId: NotRequired[str]
    connectMessage: NotRequired[MessageT]
    connectTimeout: NotRequired[int]
    deviceTopicPrefix: NotRequired[str]
    disconnectMessage: NotRequired[MessageT]
    lastWillTestament: NotRequired[MessageT]
    password: NotRequired[str]
    keepAliveInterval: NotRequired[int]
    keepExistingPassword: NotRequired[bool]
    ssl: NotRequired[SslT]
    username: NotRequired[str]


class StatusT(TypedDict):
    """Represent a status object."""

    connectionStatus: Literal["connected", "disconnected"]
    state: Literal["active", "inactive"]


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


class EventFilterT(TypedDict):
    """Event filter."""

    topicFilter: str
    qos: NotRequired[int]
    retain: NotRequired[str]


class EventPublicationConfigT(TypedDict):
    """Event publication config."""

    appendEventTopic: NotRequired[bool]
    customTopicPrefix: NotRequired[str]
    eventFilterList: NotRequired[list[EventFilterT]]
    includeTopicNamespaces: NotRequired[bool]
    includeSerialNumberInPayload: NotRequired[bool]
    topicPrefix: NotRequired[str]


class EventPublicationConfigDataT(TypedDict):
    """Event publication config data."""

    eventPublicationConfig: EventPublicationConfigT


class GetEventPublicationConfigResponseT(TypedDict):
    """Represent event publication config."""

    apiVersion: str
    context: str
    method: str
    data: EventPublicationConfigDataT
    error: NotRequired[ErrorDataT]


general_error_codes = {
    1100: "Internal error",
    2100: "API version not supported",
    2101: "Invalid JSON",
    2102: "Method not supported",
    2103: "Required parameter missing",
    2104: "Invalid parameter value specified",
}


class ClientState(enum.StrEnum):
    """The current state of the client."""

    ACTIVE = "active"
    INACTIVE = "inactive"


class ClientConnectionState(enum.StrEnum):
    """The current connection state of the client."""

    CONNECTED = "connected"
    DISCONNECTED = "disconnected"


class ServerProtocol(enum.StrEnum):
    """Connection protocols used in the server configuration."""

    SSL = "ssl"
    TCP = "tcp"
    WS = "ws"
    WSS = "wss"


@dataclass
class Message:
    """Message description."""

    use_default: bool = True
    topic: str | None = None
    message: str | None = None
    retain: bool | None = None
    qos: int | None = None

    def to_dict(self) -> MessageT:
        """Create json dict from object."""
        data: MessageT = {"useDefault": self.use_default}
        if self.topic is not None:
            data["topic"] = self.topic
        if self.message is not None:
            data["message"] = self.message
        if self.retain is not None:
            data["retain"] = self.retain
        if self.qos is not None:
            data["qos"] = self.qos
        return data


@dataclass
class Server:
    """Represent server config."""

    host: str
    protocol: ServerProtocol = ServerProtocol.TCP
    alpn_protocol: str | None = None
    basepath: str | None = None
    port: int | None = None

    @classmethod
    def from_dict(cls, data: ServerT) -> "Server":
        """Create server object from dict."""
        return Server(
            host=data["host"],
            protocol=ServerProtocol(data["protocol"]),
            alpn_protocol=data.get("alpnProtocol"),
            basepath=data.get("basepath"),
            port=data.get("port"),
        )

    def to_dict(self) -> ServerT:
        """Create json dict from object."""
        data: ServerT = {"host": self.host, "protocol": self.protocol.value}
        if self.alpn_protocol is not None:
            data["alpnProtocol"] = self.alpn_protocol
        if self.basepath is not None:
            data["basepath"] = self.basepath
        if self.port is not None:
            data["port"] = self.port
        return data


@dataclass
class Ssl:
    """Represent SSL config."""

    validate_server_cert: bool = False
    ca_cert_id: str | None = None
    client_cert_id: str | None = None

    def to_dict(self) -> SslT:
        """Create json dict from object."""
        data: SslT = {"validateServerCert": self.validate_server_cert}
        if self.ca_cert_id is not None:
            data["CACertID"] = self.ca_cert_id
        if self.client_cert_id is not None:
            data["clientCertID"] = self.client_cert_id
        return data


@dataclass
class ClientConfig:
    """Represent client config."""

    server: Server
    activate_on_reboot: bool | None = None
    auto_reconnect: bool | None = None
    clean_session: bool | None = None
    client_id: str | None = None
    connect_message: Message | None = None
    connect_timeout: int | None = None
    disconnect_message: Message | None = None
    keep_alive_interval: int | None = None
    last_will_testament: Message | None = None
    password: str | None = None
    ssl: Ssl | None = None
    username: str | None = None

    @classmethod
    def from_dict(cls, data: ConfigT) -> "ClientConfig":
        """Create client status object from dict."""
        return ClientConfig(server=Server.from_dict(data["server"]))

    def to_dict(self) -> ConfigT:
        """Create json dict from object."""
        data: ConfigT = {"server": self.server.to_dict()}
        if self.activate_on_reboot is not None:
            data["activateOnReboot"] = self.activate_on_reboot
        if self.auto_reconnect is not None:
            data["autoReconnect"] = self.auto_reconnect
        if self.clean_session is not None:
            data["cleanSession"] = self.clean_session
        if self.client_id is not None:
            data["clientId"] = self.client_id
        if self.connect_message is not None:
            data["connectMessage"] = self.connect_message.to_dict()
        if self.connect_timeout is not None:
            data["connectTimeout"] = self.connect_timeout
        if self.disconnect_message is not None:
            data["disconnectMessage"] = self.disconnect_message.to_dict()
        if self.keep_alive_interval is not None:
            data["keepAliveInterval"] = self.keep_alive_interval
        if self.last_will_testament is not None:
            data["lastWillTestament"] = self.last_will_testament.to_dict()
        if self.password is not None:
            data["password"] = self.password
        if self.ssl is not None:
            data["ssl"] = self.ssl.to_dict()
        if self.username is not None:
            data["username"] = self.username
        return data


@dataclass
class ClientStatus:
    """Represent client status."""

    connection_status: ClientConnectionState
    state: ClientState

    @classmethod
    def from_dict(cls, data: StatusT) -> "ClientStatus":
        """Create client status object from dict."""
        # Note to investigate closer, documentation say lower case.
        return ClientStatus(
            connection_status=ClientConnectionState(data["connectionStatus"].lower()),
            state=ClientState(data["state"].lower()),
        )


@dataclass
class ClientConfigStatus:
    """GetClientStatus response."""

    config: ClientConfig
    status: ClientStatus

    @classmethod
    def from_dict(cls, data: ClientStatusDataT) -> "ClientConfigStatus":
        """Create client config status object from dict."""
        return ClientConfigStatus(
            config=ClientConfig.from_dict(data["config"]),
            status=ClientStatus.from_dict(data["status"]),
        )


@dataclass
class EventFilter:
    """Event filter."""

    topic_filter: str
    qos: int | None = None
    retain: str | None = None

    @classmethod
    def from_dict(cls, data: EventFilterT) -> "EventFilter":
        """Create event filter object from dict."""
        return EventFilter(
            topic_filter=data["topicFilter"],
            qos=data.get("qos"),
            retain=data.get("retain"),
        )

    @classmethod
    def from_list(cls, data: list[EventFilterT]) -> "list[EventFilter]":
        """Create event filter object from dict."""
        return [EventFilter.from_dict(item) for item in data]

    def to_dict(self) -> EventFilterT:
        """Create json dict from object."""
        data: EventFilterT = {"topicFilter": self.topic_filter}
        if self.qos is not None:
            data["qos"] = self.qos
        if self.retain is not None:
            data["retain"] = self.retain
        return data

    @classmethod
    def to_list(cls, data: "list[EventFilter]") -> list[EventFilterT]:
        """Create json list from object."""
        return [item.to_dict() for item in data]


@dataclass
class EventPublicationConfig:
    """Event publication config."""

    topic_prefix: str | None = None
    custom_topic_prefix: str | None = None
    append_event_topic: bool | None = None
    include_topic_namespaces: bool | None = None
    include_serial_number_in_payload: bool | None = None
    event_filter_list: list[EventFilter] | None = None

    @classmethod
    def from_dict(cls, data: EventPublicationConfigT) -> "EventPublicationConfig":
        """Create client config status object from dict."""
        return EventPublicationConfig(
            topic_prefix=data["topicPrefix"],
            custom_topic_prefix=data["customTopicPrefix"],
            append_event_topic=data["appendEventTopic"],
            include_topic_namespaces=data["includeTopicNamespaces"],
            include_serial_number_in_payload=data["includeSerialNumberInPayload"],
            event_filter_list=EventFilter.from_list(data["eventFilterList"]),
        )

    def to_dict(self) -> EventPublicationConfigT:
        """Create json dict from object."""
        data: EventPublicationConfigT = {}
        if self.topic_prefix is not None:
            data["topicPrefix"] = self.topic_prefix
        if self.custom_topic_prefix is not None:
            data["customTopicPrefix"] = self.custom_topic_prefix
        if self.append_event_topic is not None:
            data["appendEventTopic"] = self.append_event_topic
        if self.include_topic_namespaces is not None:
            data["includeTopicNamespaces"] = self.include_topic_namespaces
        if self.include_serial_number_in_payload is not None:
            data["includeSerialNumberInPayload"] = self.include_serial_number_in_payload
        if self.event_filter_list is not None:
            data["eventFilterList"] = EventFilter.to_list(self.event_filter_list)
        return data


@dataclass
class ConfigureClientRequest(ApiRequest):
    """Request object for configuring MQTT client."""

    method = "post"
    path = "/axis-cgi/mqtt/client.cgi"
    content_type = "application/json"
    error_codes = general_error_codes

    client_config: ClientConfig

    api_version: str = API_VERSION
    context: str = CONTEXT

    @property
    def content(self) -> bytes:
        """Initialize request data."""
        return orjson.dumps(
            {
                "apiVersion": self.api_version,
                "context": self.context,
                "method": "configureClient",
                "params": self.client_config.to_dict(),
            }
        )


@dataclass
class ActivateClientRequest(ApiRequest):
    """Request object for activating MQTT client."""

    method = "post"
    path = "/axis-cgi/mqtt/client.cgi"
    content_type = "application/json"
    error_codes = general_error_codes

    api_version: str = API_VERSION
    context: str = CONTEXT

    @property
    def content(self) -> bytes:
        """Initialize request data."""
        return orjson.dumps(
            {
                "apiVersion": self.api_version,
                "context": self.context,
                "method": "activateClient",
            }
        )


@dataclass
class DeactivateClientRequest(ActivateClientRequest):
    """Request object for deactivating MQTT client."""

    @property
    def content(self) -> bytes:
        """Initialize request data."""
        return orjson.dumps(
            {
                "apiVersion": self.api_version,
                "context": self.context,
                "method": "deactivateClient",
            }
        )


@dataclass
class GetClientStatusResponse(ApiResponse[ClientConfigStatus]):
    """Response object for get client status request."""

    api_version: str
    context: str
    method: str
    data: ClientConfigStatus
    # error: ErrorDataT | None = None

    @classmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Prepare response data."""
        data: GetClientStatusResponseT = orjson.loads(bytes_data)
        return cls(
            api_version=data["apiVersion"],
            context=data["context"],
            method=data["method"],
            data=ClientConfigStatus.from_dict(data["data"]),
        )


@dataclass
class GetClientStatusRequest(ApiRequest):
    """Request object for getting MQTT client status."""

    method = "post"
    path = "/axis-cgi/mqtt/client.cgi"
    content_type = "application/json"
    error_codes = general_error_codes

    api_version: str = API_VERSION
    context: str = CONTEXT

    @property
    def content(self) -> bytes:
        """Initialize request data."""
        return orjson.dumps(
            {
                "apiVersion": self.api_version,
                "context": self.context,
                "method": "getClientStatus",
            }
        )


@dataclass
class GetEventPublicationConfigResponse(ApiResponse[EventPublicationConfig]):
    """Response object for event publication config get request."""

    api_version: str
    context: str
    method: str
    data: EventPublicationConfig
    # error: ErrorDataT | None = None

    @classmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Prepare response data."""
        data: GetEventPublicationConfigResponseT = orjson.loads(bytes_data)
        return cls(
            api_version=data["apiVersion"],
            context=data["context"],
            method=data["method"],
            data=EventPublicationConfig.from_dict(
                data["data"]["eventPublicationConfig"]
            ),
        )


@dataclass
class GetEventPublicationConfigRequest(ApiRequest):
    """Request object for getting MQTT event publication config."""

    method = "post"
    path = "/axis-cgi/mqtt/event.cgi"
    content_type = "application/json"
    error_codes = general_error_codes

    api_version: str = API_VERSION
    context: str = CONTEXT

    @property
    def content(self) -> bytes:
        """Initialize request data."""
        return orjson.dumps(
            {
                "apiVersion": self.api_version,
                "context": self.context,
                "method": "getEventPublicationConfig",
            }
        )


@dataclass
class ConfigureEventPublicationRequest(ApiRequest):
    """Request object for configuring event publication over MQTT."""

    method = "post"
    path = "/axis-cgi/mqtt/event.cgi"
    content_type = "application/json"
    error_codes = general_error_codes

    config: EventPublicationConfig

    api_version: str = API_VERSION
    context: str = CONTEXT

    @property
    def content(self) -> bytes:
        """Initialize request data."""
        return orjson.dumps(
            {
                "apiVersion": self.api_version,
                "context": self.context,
                "method": "configureEventPublication",
                "params": self.config.to_dict(),
            }
        )
