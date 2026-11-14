"""Models for configuring the VAPIX MQTT client and publishing device events."""

from dataclasses import dataclass
import enum
from typing import Any, Literal, NotRequired, Self, TypedDict

import orjson

from .api import CONTEXT, ApiRequest, ApiResponse, BytesResponse

API_VERSION = "1.0"


class ErrorDataT(TypedDict):
    """Error code and message returned by the MQTT API."""

    code: int
    message: str


class MessageT(TypedDict):
    """MQTT message options used for connect, disconnect, or last-will messages."""

    useDefault: bool
    message: NotRequired[str]
    qos: NotRequired[Literal[0, 1, 2]]
    retain: NotRequired[bool]
    topic: NotRequired[str]


class ServerT(TypedDict):
    """Broker address and optional transport settings in the client configuration."""

    host: str
    protocol: NotRequired[Literal["ssl", "tcp", "ws", "wss"]]
    alpnProtocol: NotRequired[str]
    basepath: NotRequired[str]
    port: NotRequired[int]


class SslT(TypedDict):
    """TLS certificate validation and client-certificate settings."""

    validateServerCert: bool
    CACertID: NotRequired[str]
    clientCertID: NotRequired[str]


class ConfigT(TypedDict):
    """Connection, authentication, and message settings for the MQTT client."""

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
    """Connection state and activation state reported for the MQTT client."""

    connectionStatus: Literal["connected", "disconnected", "not connected"]
    state: Literal["active", "inactive"]


class ClientStatusDataT(TypedDict):
    """MQTT client configuration and its current status."""

    config: ConfigT
    status: StatusT


class GetClientStatusResponseT(TypedDict):
    """JSON envelope returned by getClientStatus."""

    apiVersion: str
    context: str
    method: str
    data: ClientStatusDataT
    error: NotRequired[ErrorDataT]


class EventFilterT(TypedDict):
    """Topic and optional delivery settings for filtering published events."""

    topicFilter: str
    qos: NotRequired[int]
    retain: NotRequired[str]


class EventPublicationConfigT(TypedDict):
    """Topic naming, payload, and filtering options for MQTT event publication."""

    appendEventTopic: NotRequired[bool]
    customTopicPrefix: NotRequired[str]
    eventFilterList: NotRequired[list[EventFilterT]]
    includeTopicNamespaces: NotRequired[bool]
    includeSerialNumberInPayload: NotRequired[bool]
    topicPrefix: NotRequired[str]


class EventPublicationConfigDataT(TypedDict):
    """Event publication settings nested in an API response."""

    eventPublicationConfig: EventPublicationConfigT


class GetEventPublicationConfigResponseT(TypedDict):
    """JSON envelope returned by getEventPublicationConfig."""

    apiVersion: str
    context: str
    method: str
    data: EventPublicationConfigDataT
    error: NotRequired[ErrorDataT]


def mqtt_json_to_event(msg: bytes | bytearray | memoryview | str) -> dict[str, Any]:
    """Map an Axis MQTT event message to the event fields used by Event.decode."""
    message = orjson.loads(msg)
    topic = source = source_idx = data_type = data_value = ""

    if "topic" in message:
        topic = message["topic"].replace("onvif", "tns1").replace("axis", "tnsaxis")

    msg_message = message.get("message", {})
    if isinstance(msg_message, dict):
        if source_dict := msg_message.get("source"):
            source, source_idx = next(iter(source_dict.items()))
        if data_dict := msg_message.get("data"):
            data_type, data_value = next(iter(data_dict.items()))
            if "active" in data_dict:
                data_type, data_value = "active", data_dict["active"]

    return {
        "topic": topic,
        "source": source,
        "source_idx": source_idx,
        "type": data_type,
        "value": data_value,
    }


general_error_codes = {
    1100: "Internal error",
    2100: "API version not supported",
    2101: "Invalid JSON",
    2102: "Method not supported",
    2103: "Required parameter missing",
    2104: "Invalid parameter value specified",
}


class ClientState(enum.StrEnum):
    """Whether the MQTT client is active or inactive."""

    ACTIVE = "active"
    INACTIVE = "inactive"


class ClientConnectionState(enum.StrEnum):
    """Broker connection state reported for the MQTT client."""

    CONNECTED = "connected"
    DISCONNECTED = "disconnected"

    @classmethod
    def _missing_(cls, value: object) -> ClientConnectionState:
        """Set default enum member if an unknown value is provided.

        Some firmwares report "not connected" instead of "disconnected".
        """
        return cls.DISCONNECTED


class ServerProtocol(enum.StrEnum):
    """Transport protocols accepted in MQTT broker configuration."""

    SSL = "ssl"
    TCP = "tcp"
    WS = "ws"
    WSS = "wss"


@dataclass
class Message:
    """Optional MQTT message sent on connection or disconnection events."""

    use_default: bool = True
    """Specifies if the default configuration should be used.

    If set to true, other options in this parameter will be discarded.
    If false, the configured topic, payload, retain flag, and QoS are used.
    """
    topic: str | None = None
    """Topic to publish this message to."""
    message: str | None = None
    """Payload to publish on the configured topic."""
    retain: bool | None = None
    """Whether the broker should retain the most recent message for new subscribers."""
    qos: Literal[0, 1, 2] | None = None
    """MQTT delivery quality level: at most once, at least once, or exactly once."""

    @classmethod
    def from_dict(cls, data: MessageT) -> Self:
        """Convert API message options into a Message model."""
        return cls(
            use_default=data["useDefault"],
            topic=data.get("topic"),
            message=data.get("message"),
            retain=data.get("retain"),
            qos=data.get("qos"),
        )

    @classmethod
    def from_dict_or_none(cls, data: MessageT | None) -> Self | None:
        """Convert message options when present, otherwise return None."""
        return cls.from_dict(data) if data is not None else None

    def to_dict(self) -> MessageT:
        """Serialize configured message options using API field names."""
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
    """MQTT broker address, transport protocol, and optional connection settings."""

    host: str
    """The Broker location, i.e. the Hostname or IP address."""
    protocol: ServerProtocol = ServerProtocol.TCP
    """Transport used to connect to the broker.

    Possible values are:
    - tcp: MQTT over TCP
    - ssl: MQTT over SSL
    - ws: MQTT over Websocket
    - wss: MQTT over Websocket Secure
    """
    alpn_protocol: str | None = None
    """ALPN protocol to negotiate for an SSL or WSS connection.

    If the string value is empty the ALPN will not be used.
    Default value is empty and the maximum length of the protocol is 255 bytes.
    """
    basepath: str | None = None
    """Path suffix for the broker URL used with WebSocket transports.

    The default is an empty string.
    """
    port: int | None = None
    """Broker port.

    Default values for the protocols are:
    - tcp: 1883
    - ssl: 8883
    - ws: 80
    - wss: 443
    """

    @classmethod
    def from_dict(cls, data: ServerT) -> Self:
        """Convert broker connection options from the API payload."""
        return cls(
            host=data["host"],
            protocol=ServerProtocol(data["protocol"]),
            alpn_protocol=data.get("alpnProtocol"),
            basepath=data.get("basepath"),
            port=data.get("port"),
        )

    def to_dict(self) -> ServerT:
        """Serialize broker settings using the MQTT API field names."""
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
    """TLS verification and certificate selection for a secure broker connection."""

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
        """Convert TLS options from the API payload."""
        return cls(
            validate_server_cert=data["validateServerCert"],
            ca_cert_id=data.get("CACertID"),
            client_cert_id=data.get("clientCertID"),
        )

    @classmethod
    def from_dict_or_none(cls, data: SslT | None) -> Self | None:
        """Convert TLS options when present, otherwise return None."""
        return cls.from_dict(data) if data is not None else None

    def to_dict(self) -> SslT:
        """Serialize TLS settings using the MQTT API field names."""
        data: SslT = {"validateServerCert": self.validate_server_cert}
        if self.ca_cert_id is not None:
            data["CACertID"] = self.ca_cert_id
        if self.client_cert_id is not None:
            data["clientCertID"] = self.client_cert_id
        return data


@dataclass
class ClientConfig:
    """Broker, credentials, reconnect policy, and message settings for the client."""

    server: Server
    """Contains the address and protocol related information."""
    activate_on_reboot: bool | None = None
    auto_reconnect: bool | None = None
    """Specifies if the client should reconnect on an unintentional disconnect."""
    clean_session: bool | None = None
    """Whether the client and broker discard session state when the client disconnects.

    True discards the state; False preserves it for a later connection.
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
    """Maximum seconds between communication with the broker.

    The client sends at least one message during each interval to detect an
    unavailable broker before the TCP timeout. The default is 60 seconds.
    """
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
        """Convert the API client configuration into nested model objects."""
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
        """Serialize the configured client options using API field names."""
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
    """Normalized MQTT activation and broker-connection state."""

    connection_status: ClientConnectionState
    state: ClientState
    active: bool
    """True when the MQTT client is enabled."""
    connected: bool
    """True when the client is connected to its broker."""

    @classmethod
    def from_dict(cls, data: StatusT) -> Self:
        """Convert device status strings into enums and boolean flags."""
        return cls(
            connection_status=ClientConnectionState(data["connectionStatus"].lower()),
            state=ClientState(data["state"].lower()),
            active=data["state"] == "active",
            connected=data["connectionStatus"] == "connected",
        )


@dataclass
class ClientConfigStatus:
    """Client settings and connection state returned together by getClientStatus."""

    config: ClientConfig
    """Broker and connection options currently configured on the client."""
    status: ClientStatus
    """Current activation and broker-connection state."""

    @classmethod
    def from_dict(cls, data: ClientStatusDataT) -> Self:
        """Convert the API's configuration and status objects into models."""
        return cls(
            config=ClientConfig.from_dict(data["config"]),
            status=ClientStatus.from_dict(data["status"]),
        )


@dataclass
class EventFilter:
    """Topic filter and optional MQTT delivery settings for published events."""

    topic_filter: str
    qos: int | None = None
    retain: str | None = None

    @classmethod
    def from_dict(cls, data: EventFilterT) -> Self:
        """Convert one API event-filter entry into a model."""
        return cls(
            topic_filter=data["topicFilter"],
            qos=data.get("qos"),
            retain=data.get("retain"),
        )

    @classmethod
    def from_list(cls, data: list[EventFilterT]) -> list[Self]:
        """Convert a list of API event-filter entries into models."""
        return [cls.from_dict(item) for item in data]

    def to_dict(self) -> EventFilterT:
        """Serialize this filter using the API's field names."""
        data: EventFilterT = {"topicFilter": self.topic_filter}
        if self.qos is not None:
            data["qos"] = self.qos
        if self.retain is not None:
            data["retain"] = self.retain
        return data

    @classmethod
    def to_list(cls, data: list[EventFilter]) -> list[EventFilterT]:
        """Serialize a list of filters for an API request."""
        return [item.to_dict() for item in data]


@dataclass
class EventPublicationConfig:
    """Topic naming and filtering options for events published over MQTT."""

    topic_prefix: str | None = None
    custom_topic_prefix: str | None = None
    append_event_topic: bool | None = None
    include_topic_namespaces: bool | None = None
    include_serial_number_in_payload: bool | None = None
    event_filter_list: list[EventFilter] | None = None

    @classmethod
    def from_dict(cls, data: EventPublicationConfigT) -> Self:
        """Convert the API event-publication options into a model."""
        return cls(
            topic_prefix=data["topicPrefix"],
            custom_topic_prefix=data["customTopicPrefix"],
            append_event_topic=data["appendEventTopic"],
            include_topic_namespaces=data["includeTopicNamespaces"],
            include_serial_number_in_payload=data["includeSerialNumberInPayload"],
            event_filter_list=EventFilter.from_list(data["eventFilterList"]),
        )

    def to_dict(self) -> EventPublicationConfigT:
        """Serialize configured publication options using API field names."""
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
class GetClientStatusResponse(ApiResponse[ClientConfigStatus]):
    """MQTT client configuration and status returned by getClientStatus."""

    api_version: str
    context: str
    method: str
    data: ClientConfigStatus
    # error: ErrorDataT | None = None

    @classmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Parse the JSON envelope and normalize its client configuration and status."""
        data: GetClientStatusResponseT = orjson.loads(bytes_data)
        return cls(
            api_version=data["apiVersion"],
            context=data["context"],
            method=data["method"],
            data=ClientConfigStatus.from_dict(data["data"]),
        )


@dataclass
class GetEventPublicationConfigResponse(ApiResponse[EventPublicationConfig]):
    """MQTT topic and filtering settings returned by getEventPublicationConfig."""

    api_version: str
    context: str
    method: str
    data: EventPublicationConfig
    # error: ErrorDataT | None = None

    @classmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Parse and normalize the event-publication settings in the response."""
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
class ConfigureClientRequest(ApiRequest[ApiResponse[bytes]]):
    """Replace the MQTT client's broker, credentials, and connection settings."""

    method = "post"
    path = "/axis-cgi/mqtt/client.cgi"
    content_type = "application/json"
    response_type = BytesResponse
    error_codes = general_error_codes

    client_config: ClientConfig

    api_version: str = API_VERSION
    context: str = CONTEXT

    @property
    def content(self) -> bytes:
        """Encode the client configuration as a configureClient request."""
        return orjson.dumps(
            {
                "apiVersion": self.api_version,
                "context": self.context,
                "method": "configureClient",
                "params": self.client_config.to_dict(),
            }
        )


@dataclass
class ActivateClientRequest(ApiRequest[ApiResponse[bytes]]):
    """Enable the MQTT client on the device."""

    method = "post"
    path = "/axis-cgi/mqtt/client.cgi"
    content_type = "application/json"
    response_type = BytesResponse
    error_codes = general_error_codes

    api_version: str = API_VERSION
    context: str = CONTEXT

    @property
    def content(self) -> bytes:
        """Encode an activateClient request as JSON."""
        return orjson.dumps(
            {
                "apiVersion": self.api_version,
                "context": self.context,
                "method": "activateClient",
            }
        )


@dataclass
class DeactivateClientRequest(ActivateClientRequest):
    """Disable the MQTT client on the device."""

    @property
    def content(self) -> bytes:
        """Encode a deactivateClient request as JSON."""
        return orjson.dumps(
            {
                "apiVersion": self.api_version,
                "context": self.context,
                "method": "deactivateClient",
            }
        )


@dataclass
class GetClientStatusRequest(ApiRequest[GetClientStatusResponse]):
    """Request the MQTT client's configuration and current connection status."""

    method = "post"
    path = "/axis-cgi/mqtt/client.cgi"
    content_type = "application/json"
    response_type = GetClientStatusResponse
    error_codes = general_error_codes

    api_version: str = API_VERSION
    context: str = CONTEXT

    @property
    def content(self) -> bytes:
        """Encode a getClientStatus request as JSON."""
        return orjson.dumps(
            {
                "apiVersion": self.api_version,
                "context": self.context,
                "method": "getClientStatus",
            }
        )


@dataclass
class GetEventPublicationConfigRequest(ApiRequest[GetEventPublicationConfigResponse]):
    """Request the device's MQTT event-publication settings."""

    method = "post"
    path = "/axis-cgi/mqtt/event.cgi"
    content_type = "application/json"
    response_type = GetEventPublicationConfigResponse
    error_codes = general_error_codes

    api_version: str = API_VERSION
    context: str = CONTEXT

    @property
    def content(self) -> bytes:
        """Encode a getEventPublicationConfig request as JSON."""
        return orjson.dumps(
            {
                "apiVersion": self.api_version,
                "context": self.context,
                "method": "getEventPublicationConfig",
            }
        )


@dataclass
class ConfigureEventPublicationRequest(ApiRequest[ApiResponse[bytes]]):
    """Set topic naming and filtering for events published over MQTT."""

    method = "post"
    path = "/axis-cgi/mqtt/event.cgi"
    content_type = "application/json"
    response_type = BytesResponse
    error_codes = general_error_codes

    config: EventPublicationConfig

    api_version: str = API_VERSION
    context: str = CONTEXT

    @property
    def content(self) -> bytes:
        """Encode the publication settings as a configureEventPublication request."""
        return orjson.dumps(
            {
                "apiVersion": self.api_version,
                "context": self.context,
                "method": "configureEventPublication",
                "params": self.config.to_dict(),
            }
        )
