"""VMD4 API."""

from dataclasses import dataclass
from typing import Any, NotRequired, Self, TypedDict

import orjson

from ..api import CONTEXT, ApiItem, ApiRequest, ApiResponse

API_VERSION = "1.2"


class CameraConfigurationDataT(TypedDict):
    """Camera configuration data from response."""

    active: bool
    id: int
    rotation: int


class ProfileConfigurationDataT(TypedDict):
    """Profile configuration data from response."""

    camera: int
    filters: list[dict[str, Any]]
    name: str
    perspective: list[dict[str, Any]] | None
    presets: NotRequired[list[int]]
    triggers: list[dict[str, Any]]
    uid: int


class ConfigurationDataT(TypedDict):
    """Configuration data from response."""

    cameras: list[CameraConfigurationDataT]
    profiles: list[ProfileConfigurationDataT]
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

    presets: list[int]
    """For mechanical PTZ cameras, each profile can be connected to one preset.

    If a preset is added, the profile will only be active when the camera is at
    the given preset. If this parameter is omitted or the profile is not connected
    to any preset it will always be active.
    """

    triggers: list[dict[str, Any]]
    """Array of triggers."""

    @classmethod
    def decode(cls, data: ProfileConfigurationDataT) -> Self:
        """Decode dict to class object."""
        return cls(
            id=str(data["uid"]),
            camera=data["camera"],
            filters=data["filters"],
            name=data["name"],
            presets=data.get("presets", []),
            triggers=data["triggers"],
        )


@dataclass(frozen=True)
class Configuration(ApiItem):
    """VMD4 configuration."""

    cameras: list[CameraConfigurationDataT]
    """Cameras."""

    profiles: dict[str, ProfileConfiguration]
    """Profiles"""

    configuration_status: int

    @classmethod
    def decode(cls, data: ConfigurationDataT) -> Self:
        """Decode dict to class object."""
        return cls(
            id="vmd4",
            cameras=data["cameras"],
            profiles=ProfileConfiguration.decode_to_dict(data["profiles"]),
            configuration_status=data["configurationStatus"],
        )


@dataclass
class GetConfigurationRequest(ApiRequest):
    """Request object for listing VMD4 configuration."""

    method = "post"
    path = "/local/vmd/control.cgi"
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
    """Response object for VMD4 configuration."""

    api_version: str
    context: str
    method: str

    @classmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Prepare VMD4 configuration response data."""
        data: GetConfigurationResponseT = orjson.loads(bytes_data)
        return cls(
            api_version=data["apiVersion"],
            context=data["context"],
            method=data["method"],
            data=Configuration.decode(data["data"]),
        )
