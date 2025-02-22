"""Audio Device Control API.

https://www.axis.com/vapix-library/subjects/t10100065/section/t10169359/display

The Audio Device Control API helps you configure and control your Axis
audio devices.
"""

from dataclasses import dataclass
from typing import Any, NotRequired, Self

import orjson
from typing_extensions import TypedDict

from .api import CONTEXT, ApiItem, ApiRequest, ApiResponse

API_VERSION = "1.0"


class ErrorDataT(TypedDict):
    """Error data in response."""

    code: int
    message: str


class ApiVersionsT(TypedDict):
    """List of supported API versions."""

    apiVersions: list[str]


class GetSupportedVersionsResponseT(TypedDict):
    """GetSupportedVersions response."""

    context: str
    method: str
    data: ApiVersionsT
    error: NotRequired[ErrorDataT]


class ChannelT(TypedDict):
    """Audio device channel."""

    id: int
    gain: int
    mute: bool


class SignalingTypeT(TypedDict):
    """Audio device signaling."""

    id: str
    powerType: str | None
    channels: list[ChannelT]


class ConnectionT(TypedDict):
    """Audio device connection."""

    id: str
    signalingTypeSelected: str
    signalingTypes: list[SignalingTypeT]


class InputOutputT(TypedDict):
    """Audio device input/output."""

    id: str
    name: str
    connectionTypeSelected: str
    connectionTypes: list[ConnectionT]


class AudioDeviceT(TypedDict):
    """Audio device settings."""

    id: str
    name: str
    inputs: list[InputOutputT]
    outputs: list[InputOutputT]


class DeviceDataT(TypedDict):
    """Audio devices."""

    devices: list[AudioDeviceT]


class GetDevicesSettingsResponseT(TypedDict):
    """GetDevicesSettings response."""

    apiVersion: str
    context: str
    method: str
    data: DeviceDataT
    error: NotRequired[ErrorDataT]


class SetDevicesSettingsResponseT(TypedDict):
    """SetDevicesSettings response."""

    apiVersion: str
    context: str
    method: str
    error: NotRequired[ErrorDataT]


general_error_codes = {
    1100: "Internal error",
    2100: "API version not supported",
    2101: "Invalid JSON",
    2102: "Method not supported",
    2103: "Required parameter missing",
    2104: "Invalid parameter value specified",
    2105: "Authorization failed",
    2106: "Authentication failed",
    2107: "Transport level error",
}


@dataclass
class Channel:
    """Audio device channel."""

    id: int
    gain: int
    mute: bool

    @classmethod
    def from_dict(cls, data: ChannelT) -> "Channel":
        """Create Channel object from dict."""
        return cls(
            id=int(data["id"]),
            gain=int(data["gain"]),
            mute=bool(data["mute"]),
        )


@dataclass
class SignalingType:
    """Audio device signaling type."""

    id: str
    power_type: str | None
    channels: list[Channel]

    @classmethod
    def from_dict(cls, data: SignalingTypeT) -> "SignalingType":
        """Create Signaling object from dict."""
        return cls(
            id=str(data["id"]),
            power_type=data.get("powerType", None),
            channels=[Channel.from_dict(chan) for chan in data["channels"]],
        )


@dataclass
class Connection:
    """Audio device connection."""

    id: str
    signaling_type_selected: str
    signaling_types: list[SignalingType]

    @classmethod
    def from_dict(cls, data: ConnectionT) -> "Connection":
        """Create Connection object from dict."""
        return cls(
            id=str(data["id"]),
            signaling_type_selected=data["signalingTypeSelected"],
            signaling_types=[
                SignalingType.from_dict(signal) for signal in data["signalingTypes"]
            ],
        )


@dataclass
class InputOutput:
    """Audio device input/output."""

    id: str
    name: str
    connection_type_selected: str
    connection_types: list[Connection]

    @classmethod
    def from_dict(cls, data: InputOutputT) -> "InputOutput":
        """Create size object from dict."""
        return cls(
            id=data["id"],
            name=data["name"],
            connection_type_selected=data["connectionTypeSelected"],
            connection_types=[
                Connection.from_dict(conn) for conn in data["connectionTypes"]
            ],
        )


@dataclass(frozen=True)
class AudioDevice(ApiItem):
    """Audio device settings representation."""

    id: str
    name: str
    inputs: list[InputOutput]
    outputs: list[InputOutput]

    @classmethod
    def decode(cls, data: AudioDeviceT) -> Self:
        """Decode dict to class object."""
        return cls(
            id=str(data["id"]),
            name=data["name"],
            inputs=[InputOutput.from_dict(iput) for iput in data["inputs"]],
            outputs=[InputOutput.from_dict(oput) for oput in data["outputs"]],
        )


@dataclass
class GetDevicesSettingsRequest(ApiRequest):
    """Request object for audio devices settings."""

    method = "post"
    path = "/axis-cgi/audiodevicecontrol.cgi"
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
                "method": "getDevicesSettings",
            }
        )


@dataclass
class GetDevicesSettingsResponse(ApiResponse[list[AudioDevice]]):
    """Response object for audio devices settings."""

    api_version: str
    context: str
    method: str
    data: list[AudioDevice]
    # error: ErrorDataT | None = None

    @classmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Prepare response data."""
        data: GetDevicesSettingsResponseT = orjson.loads(bytes_data)
        return cls(
            api_version=data["apiVersion"],
            context=data["context"],
            method=data["method"],
            data=AudioDevice.decode_to_list(data["data"]["devices"]),
        )


@dataclass
class SetDevicesSettingsRequest(ApiRequest):
    """Request object for setting audio device settings."""

    method = "post"
    path = "/axis-cgi/audiodevicecontrol.cgi"
    content_type = "application/json"
    error_codes = general_error_codes

    devices: Any
    api_version: str = API_VERSION
    context: str = CONTEXT

    @property
    def content(self) -> bytes:
        """Initialize request data."""
        return orjson.dumps(
            {
                "apiVersion": self.api_version,
                "context": self.context,
                "method": "setDevicesSettings",
                "params": {"devices": self.devices},
            }
        )


@dataclass
class GetSupportedVersionsRequest(ApiRequest):
    """Request object for listing supported API versions."""

    method = "post"
    path = "/axis-cgi/audiodevicecontrol.cgi"
    content_type = "application/json"
    error_codes = general_error_codes

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


@dataclass
class GetSupportedVersionsResponse(ApiResponse[list[str]]):
    """Response object for supported versions."""

    context: str
    method: str
    data: list[str]
    # error: ErrorDataT | None = None

    @classmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Prepare response data."""
        data: GetSupportedVersionsResponseT = orjson.loads(bytes_data)
        return cls(
            context=data["context"],
            method=data["method"],
            data=data.get("data", {}).get("apiVersions", []),
        )
