"""Models for reading Fence Guard profiles and cameras through its control API."""

from dataclasses import dataclass
from typing import Any, NotRequired, Self, TypedDict

import orjson

from ..api import CONTEXT, ApiItem, ApiRequest, ApiResponse

API_VERSION = "1.3"


class ConfigurationCameraDataT(TypedDict):
    """Camera active state and image rotation in a Fence Guard response."""

    active: bool
    id: int
    rotation: int


class ConfigurationProfileDataT(TypedDict):
    """Fence Guard profile fields as returned by the control API."""

    alarmOverlayEnabled: bool
    camera: int
    filters: list[dict[str, Any]]
    name: str
    perspective: NotRequired[list[dict[str, Any]]]
    presets: NotRequired[list[int]]
    triggers: list[dict[str, Any]]
    uid: int


class ConfigurationDataT(TypedDict):
    """Camera, profile, and revision data in a configuration response."""

    cameras: list[ConfigurationCameraDataT]
    profiles: list[ConfigurationProfileDataT]
    configurationStatus: int


class GetConfigurationResponseT(TypedDict):
    """JSON envelope returned by getConfiguration."""

    apiVersion: str
    context: str
    method: str
    data: ConfigurationDataT
    # error: NotRequired[ErrorDataT]


@dataclass(frozen=True)
class ProfileConfiguration(ApiItem):
    """Fence Guard profile with its camera, filters, triggers, and PTZ presets."""

    camera: int
    """Camera ID."""

    filters: list[dict[str, Any]]
    """Filters that exclude detections from this profile."""

    name: str
    """Display name assigned to the profile."""

    perspective: list[dict[str, Any]]
    """Perspective calibration data used to account for object height."""

    presets: list[int]
    """For mechanical PTZ cameras, each profile can be connected to one preset.

    If a preset is added, the profile will only be active when the camera is at
    the given preset. If this parameter is omitted or the profile is not connected
    to any preset it will always be active.
    """

    triggers: list[dict[str, Any]]
    """Detection trigger regions and settings configured for this profile."""

    @classmethod
    def decode(cls, data: Any) -> Self:
        """Convert one Fence Guard profile payload to a model."""
        return cls(
            id=str(data["uid"]),
            camera=data["camera"],
            filters=data["filters"],
            name=data["name"],
            perspective=data.get("perspective", []),
            presets=data.get("presets", []),
            triggers=data["triggers"],
        )


@dataclass(frozen=True)
class Configuration(ApiItem):
    """Current Fence Guard camera and profile configuration."""

    cameras: list[ConfigurationCameraDataT]
    """Camera settings returned by the Fence Guard control API."""

    profiles: dict[str, ProfileConfiguration]
    """Profiles indexed by their device-assigned identifiers."""

    configuration_status: int

    @classmethod
    def decode(cls, data: ConfigurationDataT) -> Self:
        """Convert the response configuration into cameras and indexed profiles."""
        return cls(
            id="fence guard",
            cameras=data["cameras"],
            profiles=ProfileConfiguration.decode_to_dict(data["profiles"]),
            configuration_status=data["configurationStatus"],
        )


@dataclass
class GetConfigurationResponse(ApiResponse[Configuration]):
    """Fence Guard configuration returned by getConfiguration."""

    api_version: str
    context: str
    method: str

    @classmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Parse the JSON envelope and decode its Fence Guard configuration."""
        data: GetConfigurationResponseT = orjson.loads(bytes_data)
        return cls(
            api_version=data["apiVersion"],
            context=data["context"],
            method=data["method"],
            data=Configuration.decode(data["data"]),
        )


@dataclass
class GetConfigurationRequest(ApiRequest[GetConfigurationResponse]):
    """Request the current Fence Guard camera and profile configuration."""

    method = "post"
    path = "/local/fenceguard/control.cgi"
    content_type = "application/json"
    response_type = GetConfigurationResponse

    api_version: str = API_VERSION
    context: str = CONTEXT

    @property
    def content(self) -> bytes:
        """Encode a getConfiguration request as JSON."""
        return orjson.dumps(
            {
                "apiVersion": self.api_version,
                "context": self.context,
                "method": "getConfiguration",
            }
        )
