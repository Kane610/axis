"""API Discovery api item."""

from dataclasses import dataclass
import enum
import logging

import orjson
from typing_extensions import NotRequired, TypedDict

from .api import CONTEXT, ApiItem, ApiRequest

API_VERSION = "1.0"

LOGGER = logging.getLogger(__name__)


class ApiId(enum.Enum):
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
        LOGGER.info("Unsupported API discovery ID %s", value)
        return ApiId.UNKNOWN


class ApiStatus(enum.Enum):
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
        LOGGER.warning("Unsupported API discovery status %s", value)
        return ApiStatus.UNKNOWN


class ErrorDataT(TypedDict):
    """Error data in response."""

    code: int
    message: str


class ApiDescriptionT(TypedDict):
    """Pir sensor configuration representation."""

    docLink: str
    id: str
    name: str
    status: str
    version: str


class ListApisDataT(TypedDict):
    """List of Pir sensor configuration data."""

    sensors: list[ApiDescriptionT]


class ListApisResponseT(TypedDict):
    """ListSensors response."""

    apiVersion: str
    context: str
    method: str
    data: ListApisDataT
    error: NotRequired[ErrorDataT]


class ApiVersionsT(TypedDict):
    """List of supported API versions."""

    apiVersions: list[str]


class GetSupportedVersionsResponseT(TypedDict):
    """ListSensors response."""

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


@dataclass
class Api(ApiItem):
    """API Discovery item."""

    name: str
    status: ApiStatus
    version: str

    @property
    def api_id(self) -> ApiId:
        """ID of API."""
        return ApiId(self.id)


ListApisT = dict[str, Api]


@dataclass
class ListApisRequest(ApiRequest[ListApisT]):
    """Request object for listing PIR sensors."""

    method = "post"
    path = "/axis-cgi/apidiscovery.cgi"
    content_type = "application/json"
    error_codes = error_codes

    api_version: str = API_VERSION
    context: str = CONTEXT

    def __post_init__(self) -> None:
        """Initialize request data."""
        self.data = {
            "apiVersion": self.api_version,
            "context": self.context,
            "method": "getApiList",
        }

    def process_raw(self, raw: str) -> ListApisT:
        """Prepare Pir sensor configuration dictionary."""
        data: ListApisResponseT = orjson.loads(raw)
        apis = data.get("data", {}).get("apiList", [])
        return {
            api["id"]: Api(
                id=api["id"],
                name=api["name"],
                status=ApiStatus(api.get("status", "")),
                version=api["version"],
            )
            for api in apis
        }


@dataclass
class GetSupportedVersionsRequest(ApiRequest[list[str]]):
    """Request object for listing supported API versions."""

    method = "post"
    path = "/axis-cgi/apidiscovery.cgi"
    content_type = "application/json"
    error_codes = error_codes

    context: str = CONTEXT

    def __post_init__(self) -> None:
        """Initialize request data."""
        self.data = {
            "context": self.context,
            "method": "getSupportedVersions",
        }

    def process_raw(self, raw: str) -> list[str]:
        """Process supported versions."""
        data: GetSupportedVersionsResponseT = orjson.loads(raw)
        return data.get("data", {}).get("apiVersions", [])
