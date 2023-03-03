"""API Discovery api item."""

import enum
import logging

from .api import APIItem

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


class Api(APIItem):
    """API Discovery item."""

    @property
    def api_id(self) -> ApiId:
        """ID of API."""
        return ApiId(self.raw["id"])

    @property
    def name(self) -> str:
        """Name of API."""
        return self.raw["name"]

    @property
    def status(self) -> ApiStatus:
        """Status of API."""
        return ApiStatus(self.raw.get("status", ""))

    @property
    def version(self) -> str:
        """Version of API."""
        return self.raw["version"]
