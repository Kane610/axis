"""API Discovery api item."""

from dataclasses import dataclass
import enum
import logging
from typing import NotRequired, Self

import orjson
from typing_extensions import TypedDict

from .api import CONTEXT, ApiItem, ApiRequest, ApiResponse

API_VERSION = "1.0"

LOGGER = logging.getLogger(__name__)


class ApiId(enum.StrEnum):
    """The API discovery ID."""

    ANALYTICS_METADATA_CONFIG = "analytics-metadata-config"
    API_DISCOVERY = "api-discovery"
    AUDIO_ANALYTICS = "audio-analytics"
    AUDIO_DEVICE_CONTROL = "audio-device-control"
    AUDIO_MIXER = "audio-mixer"
    AUDIO_STREAMING_CAPABILITIES = "audio-streaming-capabilities"
    BASIC_DEVICE_INFO = "basic-device-info"
    CAPTURE_MODE = "capture-mode"
    CUSTOM_HTTP_HEADER = "customhttpheader"
    CUSTOM_FIRMWARE_CERTIFICATE = "custom-firmware-certificate"
    DISK_MANAGEMENT = "disk-management"
    DISK_NETWORK_SHARE = "disk-network-share"
    DISK_PROPERTIES = "disk-properties"
    DYNAMIC_OVERLAY = "dynamicoverlay"
    EVENT_MQTT_BRIDGE = "event-mqtt-bridge"
    EVENT_STREAMING_OVER_WEBSOCKET = "event-streaming-over-websocket"
    FEATURE_FLAG = "feature-flag"
    FIRMWARE_MANAGER = "fwmgr"
    GUARD_TOUR = "guard-tour"
    IMAGE_SIZE = "image-size"
    IO_PORT_MANAGEMENT = "io-port-management"
    LIGHT_CONTROL = "light-control"
    MEDIA_CLIP = "mediaclip"
    MDNS_SD = "mdnssd"
    MQTT_CLIENT = "mqtt-client"
    NETWORK_SETTINGS = "network-settings"
    NETWORK_SPEAKER_PAIRING = "network-speaker-pairing"
    NTP = "ntp"
    OAK = "oak"
    ON_SCREEN_CONTROLS = "onscreencontrols"
    OVERLAY_IMAGE = "overlayimage"
    PACKAGE_MANAGER = "packagemanager"
    PARAM_CGI = "param-cgi"
    PIR_SENSOR_CONFIGURATION = "pir-sensor-configuration"
    PRIVACY_MASK = "privacy-mask"
    PTZ_CONTROL = "ptz-control"
    RECORDING = "recording"
    RECORDING_EXPORT = "recording-export"
    RECORDING_GROUP = "recording-group"
    RECORDING_STORAGE_LIMIT = "recording-storage-limit"
    REMOTE_SERVICE = "remoteservice"
    REMOTE_SYSLOG = "remote-syslog"
    RTSP_OVER_WEBSOCKET = "rtsp-over-websocket"
    SHUTTERGAIN_CGI = "shuttergain-cgi"
    SIGNED_VIDEO = "signed-video"
    SIP = "sip"
    SSH = "ssh"
    STREAM_PROFILES = "stream-profiles"
    SYSTEM_READY = "systemready"
    TEMPERATURE_CONTROL = "temperaturecontrol"
    TIME_SERVICE = "time-service"
    UPNP = "upnp"
    USER_MANAGEMENT = "user-management"
    VIEW_AREA = "view-area"
    ZIP_STREAM = "zipstream"

    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls, value: object) -> "ApiId":
        """Set default enum member if an unknown value is provided."""
        LOGGER.info("Unsupported API discovery ID '%s'", value)
        return ApiId.UNKNOWN


class ApiStatus(enum.StrEnum):
    """The API discovery status."""

    OFFICIAL = "official"
    RELEASED = "released"
    BETA = "beta"
    ALPHA = "alpha"
    DEPRECATED = "deprecated"

    UNKNOWN = "unknown"

    @classmethod
    def _missing_(cls, value: object) -> "ApiStatus":
        """Set default enum member if an unknown value is provided."""
        LOGGER.debug("Unsupported API discovery status '%s'", value)
        return ApiStatus.UNKNOWN


class ErrorDataT(TypedDict):
    """Error data in response."""

    code: int
    message: str


class ApiDescriptionT(TypedDict):
    """API description representation."""

    docLink: str
    id: str
    name: str
    status: NotRequired[str]
    version: str


class ListApisDataT(TypedDict):
    """List of API description data."""

    apiList: list[ApiDescriptionT]


class ListApisResponseT(TypedDict):
    """ListApis response."""

    apiVersion: str
    context: str
    method: str
    data: ListApisDataT
    error: NotRequired[ErrorDataT]


class ApiVersionsT(TypedDict):
    """List of supported API versions."""

    apiVersions: list[str]


class GetSupportedVersionsResponseT(TypedDict):
    """ListApis response."""

    apiVersion: str
    context: str
    method: str
    data: ApiVersionsT
    error: NotRequired[ErrorDataT]


error_codes = {
    1000: "Invalid parameter value specified",
    2002: "HTTP request type not supported. Only POST is supported",
    2003: "Requested API version is not supported",
    2004: "Method not supported",
    4000: "Invalid JSON",
    4002: "Required parameter missing or invalid",
    8000: "Internal error",
}


@dataclass(frozen=True)
class Api(ApiItem):
    """API Discovery item."""

    name: str
    status: ApiStatus
    version: str

    @property
    def api_id(self) -> ApiId:
        """ID of API."""
        return ApiId(self.id)

    @classmethod
    def decode(cls, data: ApiDescriptionT) -> Self:
        """Decode dict to class object."""
        return cls(
            id=data["id"],
            name=data["name"],
            status=ApiStatus(data.get("status", "")),
            version=data["version"],
        )


@dataclass
class GetAllApisResponse(ApiResponse[dict[str, Api]]):
    """Response object for basic device info."""

    api_version: str
    context: str
    method: str
    data: dict[str, Api]
    # error: ErrorDataT | None = None

    @classmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Prepare API description dictionary."""
        data: ListApisResponseT = orjson.loads(bytes_data)
        return cls(
            api_version=data["apiVersion"],
            context=data["context"],
            method=data["method"],
            data=Api.decode_to_dict(data["data"]["apiList"]),
        )


@dataclass
class ListApisRequest(ApiRequest):
    """Request object for listing API descriptions."""

    method = "post"
    path = "/axis-cgi/apidiscovery.cgi"
    content_type = "application/json"
    error_codes = error_codes

    api_version: str = API_VERSION
    context: str = CONTEXT

    @property
    def content(self) -> bytes:
        """Initialize request data."""
        return orjson.dumps(
            {
                "apiVersion": self.api_version,
                "context": self.context,
                "method": "getApiList",
            }
        )


@dataclass
class GetSupportedVersionsResponse(ApiResponse[list[str]]):
    """Response object for supported versions."""

    api_version: str
    context: str
    method: str
    data: list[str]
    # error: ErrorDataT | None = None

    @classmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Prepare API description dictionary."""
        data: GetSupportedVersionsResponseT = orjson.loads(bytes_data)
        return cls(
            api_version=data["apiVersion"],
            context=data["context"],
            method=data["method"],
            data=data.get("data", {}).get("apiVersions", []),
        )


@dataclass
class GetSupportedVersionsRequest(ApiRequest):
    """Request object for listing supported API versions."""

    method = "post"
    path = "/axis-cgi/apidiscovery.cgi"
    content_type = "application/json"
    error_codes = error_codes

    context: str = CONTEXT

    @property
    def content(self) -> bytes:
        """Initialize request data."""
        return orjson.dumps(
            {
                "context": self.context,
                "method": "getSupportedVersions",
            }
        )
