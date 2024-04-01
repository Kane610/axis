"""MQTT Client api."""

from __future__ import annotations

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
    qos: NotRequired[Literal[0, 1, 2]]
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

    connectionStatus: Literal["connected", "disconnected", "not connected"]
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

    @classmethod
    def _missing_(cls, value: object) -> ClientConnectionState:
        """Set default enum member if an unknown value is provided.

        Some firmwares report "not connected" instead of "disconnected".
        """
        return cls.DISCONNECTED


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
    """Specifies if the default configuration should be used.

    If set to true, other options in this parameter will be discarded.
    If set to false, topic, messages, retained and qos options are required and used.
    """
    topic: str | None = None
    """The topic that should be used with the message."""
    message: str | None = None
    """The message that should be used with the message."""
    retain: bool | None = None
    """The retained option that should be used with the message."""
    qos: Literal[0, 1, 2] | None = None
    """The QoS option that should be used with the message."""

    @classmethod
    def from_dict(cls, data: MessageT) -> Self:
        """Create message object from dict."""
        return cls(
            use_default=data["useDefault"],
            topic=data.get("topic"),
            message=data.get("message"),
            retain=data.get("retain"),
            qos=data.get("qos"),
        )

    @classmethod
    def from_dict_or_none(cls, data: MessageT | None) -> Self | None:
        """Create class instance if data is not None."""
        return cls.from_dict(data) if data is not None else None

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
    """The Broker location, i.e. the Hostname or IP address."""
    protocol: ServerProtocol = ServerProtocol.TCP
    """Contains the protocols used by params.server.

    Possible values are:
    - tcp: MQTT over TCP
    - ssl: MQTT over SSL
    - ws: MQTT over Websocket
    - wss: MQTT over Websocket Secure
    """
    alpn_protocol: str | None = None
    """The ALPN protocol that should be used if the selected protocol was ssl or wss.

    If the string value is empty the ALPN will not be used.
    Default value is empty and the maximum length of the protocol is 255 bytes.
    """
    basepath: str | None = None
    """The path that should be used as a suffix for the constructed URL.

    Will only be used for the ws and wss connections.
    The default value is empty string.
    """
    port: int | None = None
    """The port that should be used.

    Default values for the protocols are:
    - tcp: 1883
    - ssl: 8883
    - ws: 80
    - wss: 443
    """

    @classmethod
    def from_dict(cls, data: ServerT) -> Self:
        """Create server object from dict."""
        return cls(
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
    """Specifies if the server certificate shall be validated."""
    ca_cert_id: str | None = None
    """Specifies the CA Certificate that should be used to validate the server certificate.

    The certificates are managed through the user interface or via ONVIF services.
    """
    client_cert_id: str | None = None
    """Specifies the client certificate and key that should be used.

    The certificates are managed through the user interface or via ONVIF services.
    """

    @classmethod
    def from_dict(cls, data: SslT) -> Self:
        """Create client status object from dict."""
        return cls(
            validate_server_cert=data["validateServerCert"],
            ca_cert_id=data.get("CACertID"),
            client_cert_id=data.get("clientCertID"),
        )

    @classmethod
    def from_dict_or_none(cls, data: SslT | None) -> Self | None:
        """Create class instance if data is not None."""
        return cls.from_dict(data) if data is not None else None

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
    """Contains the address and protocol related information."""
    activate_on_reboot: bool | None = None
    auto_reconnect: bool | None = None
    """Specifies if the client should reconnect on an unintentional disconnect."""
    clean_session: bool | None = None
    """This parameter controls the behavior during connection and disconnection time.

    Affects both the client and the server when this parameters is true,
    the state information is discarded when the client and server change state.
    Setting the parameter to false means that the state information is kept.
    """
    client_id: str | None = None
    """The client identifier sent to the server when the client connects to it."""
    connect_message: Message | None = None
    """Specifies if a message should be sent when a connection is established.

    Contains options related to connect announcements.
    If this object is not defined this message won't be sent.
    """
    connect_timeout: int | None = None
    """The timed interval (in seconds) to allow a connect to finish.

    The default value is 60.
    """
    device_topic_prefix: str | None = None
    """Specifies a prefix on MQTT topics in various scenarios.

    Such as when you want to configure the translation of events into MQTT messages
    or prefix all published MQTT messages with a common prefix.
    The default value is axis/{device serial number}.
    """
    disconnect_message: Message | None = None
    """Specifies if a message should be sent when the client is manually disconnected.

    Contains options related to manual disconnect announcements.
    If this object is not defined this message won't be sent.
    This message should not be confused with LWT,
    as it is used when the connection is lost and managed by the broker.
    """
    keep_alive_interval: int | None = None
    """Defines the maximum time (in seconds).

    Time intervalthat should pass without communication between the client and server.
    At least one message will be sent over the network by the client
    during each keep alive period and the interval makes it possible to detect
    when the server is no longer available without having to
    wait for the TCP/IP timeout.
    The default value is 60."""
    last_will_testament: Message | None = None
    """Contains the options related to LWT.

    If LWT is not required, this parameter is not included.
    """
    password: str | None = None
    """The password that should be used for authentication."""
    ssl: Ssl | None = None
    """Contains the options related to the SSL connection.

    This object should only be present if the connection type is ssl or wss.
    """
    username: str | None = None
    """The user name that should be used for authentication and authorization."""

    @classmethod
    def from_dict(cls, data: ConfigT) -> Self:
        """Create client status object from dict."""
        return cls(
            server=Server.from_dict(data["server"]),
            activate_on_reboot=data.get("activateOnReboot"),
            auto_reconnect=data.get("autoReconnect"),
            clean_session=data.get("cleanSession"),
            client_id=data.get("clientId"),
            connect_message=Message.from_dict_or_none(data.get("connectMessage")),
            connect_timeout=data.get("connectTimeout"),
            device_topic_prefix=data.get("deviceTopicPrefix"),
            disconnect_message=Message.from_dict_or_none(data.get("disconnectMessage")),
            keep_alive_interval=data.get("keepAliveInterval"),
            last_will_testament=Message.from_dict_or_none(
                data.get("lastWillTestament")
            ),
            password=data.get("password"),
            ssl=Ssl.from_dict_or_none(data.get("ssl")),
            username=data.get("username"),
        )

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
    active: bool
    """The current state of the client. Possible values are active and inactive."""
    connected: bool
    """The current connection state of your client. Possible values are connected, disconnected."""

    @classmethod
    def from_dict(cls, data: StatusT) -> Self:
        """Create client status object from dict."""
        return cls(
            connection_status=ClientConnectionState(data["connectionStatus"].lower()),
            state=ClientState(data["state"].lower()),
            active=data["state"] == "active",
            connected=data["connectionStatus"] == "connected",
        )


@dataclass
class ClientConfigStatus:
    """GetClientStatus response."""

    config: ClientConfig
    """The Config of the MQTT client."""
    status: ClientStatus
    """The Status of the MQTT client."""

    @classmethod
    def from_dict(cls, data: ClientStatusDataT) -> Self:
        """Create client config status object from dict."""
        return cls(
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
    def from_dict(cls, data: EventFilterT) -> Self:
        """Create event filter object from dict."""
        return cls(
            topic_filter=data["topicFilter"],
            qos=data.get("qos"),
            retain=data.get("retain"),
        )

    @classmethod
    def from_list(cls, data: list[EventFilterT]) -> list[Self]:
        """Create event filter object from dict."""
        return [cls.from_dict(item) for item in data]

    def to_dict(self) -> EventFilterT:
        """Create json dict from object."""
        data: EventFilterT = {"topicFilter": self.topic_filter}
        if self.qos is not None:
            data["qos"] = self.qos
        if self.retain is not None:
            data["retain"] = self.retain
        return data

    @classmethod
    def to_list(cls, data: list[EventFilter]) -> list[EventFilterT]:
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
    def from_dict(cls, data: EventPublicationConfigT) -> Self:
        """Create client config status object from dict."""
        return cls(
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
