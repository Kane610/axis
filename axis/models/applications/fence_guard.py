"""Fence guard analytics application."""

from dataclasses import dataclass
from typing import Any, NotRequired, Self, TypedDict

import orjson

from ..api import CONTEXT, ApiItem, ApiRequest, ApiResponse

API_VERSION = "1.3"


class ConfigurationCameraDataT(TypedDict):
    """Camera configuration data from response."""

    active: bool
    id: int
    rotation: int


class ConfigurationProfileDataT(TypedDict):
    """Profile configuration data from response."""

    alarmOverlayEnabled: bool
    camera: int
    filters: list[dict[str, Any]]
    name: str
    perspective: NotRequired[list[dict[str, Any]]]
    presets: NotRequired[list[int]]
    triggers: list[dict[str, Any]]
    uid: int


class ConfigurationDataT(TypedDict):
    """Configuration data from response."""

    cameras: list[ConfigurationCameraDataT]
    profiles: list[ConfigurationProfileDataT]
    configurationStatus: int


class GetConfigurationResponseT(TypedDict):
    """Get configuration response."""

    apiVersion: str
    context: str
    method: str
    data: ConfigurationDataT
    # error: NotRequired[ErrorDataT]


@dataclass(frozen=True)
class ProfileConfiguration(ApiItem):
    """Profile configuration."""

    camera: int
    """Camera ID."""

    filters: list[dict[str, Any]]
    """Array of exclude filters."""

    name: str
    """Nice name of profile."""

    perspective: list[dict[str, Any]]
    """Perspective for improve triggers based on heights."""

    presets: list[int]
    """For mechanical PTZ cameras, each profile can be connected to one preset.

    If a preset is added, the profile will only be active when the camera is at
    the given preset. If this parameter is omitted or the profile is not connected
    to any preset it will always be active.
    """

    triggers: list[dict[str, Any]]
    """Array of triggers."""

    @classmethod
    def decode(cls, data: Any) -> Self:
        """Decode dict to class object."""
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
    """Fence guard configuration."""

    cameras: list[ConfigurationCameraDataT]
    """Cameras."""

    profiles: dict[str, ProfileConfiguration]
    """Profiles"""

    configuration_status: int

    @classmethod
    def decode(cls, data: ConfigurationDataT) -> Self:
        """Decode dict to class object."""
        return cls(
            id="fence guard",
            cameras=data["cameras"],
            profiles=ProfileConfiguration.decode_to_dict(data["profiles"]),
            configuration_status=data["configurationStatus"],
        )


@dataclass
class GetConfigurationRequest(ApiRequest):
    """Request object for listing Fence guard configuration."""

    method = "post"
    path = "/local/fenceguard/control.cgi"
    content_type = "application/json"

    api_version: str = API_VERSION
    context: str = CONTEXT

    @property
    def content(self) -> bytes:
        """Initialize request data."""
        return orjson.dumps(
            {
                "apiVersion": self.api_version,
                "context": self.context,
                "method": "getConfiguration",
            }
        )


@dataclass
class GetConfigurationResponse(ApiResponse[Configuration]):
    """Response object for Fence guard configuration."""

    api_version: str
    context: str
    method: str

    @classmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Prepare Fence guard configuration response data."""
        data: GetConfigurationResponseT = orjson.loads(bytes_data)
        return cls(
            api_version=data["apiVersion"],
            context=data["context"],
            method=data["method"],
            data=Configuration.decode(data["data"]),
        )
