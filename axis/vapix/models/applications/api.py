"""Base class for applications."""

from dataclasses import dataclass
from typing import Any, NotRequired, Self, TypedDict

import orjson

from ..api import APIItem, ApiItem, ApiRequest, ApiResponse


class ApplicationAPIItem(APIItem):
    """Base class for application profiles."""

    @property
    def camera(self) -> int:
        """Camera ID."""
        return self.raw["camera"]

    @property
    def filters(self) -> list:
        """Array of exclude filters."""
        return self.raw["filters"]

    @property
    def name(self) -> str:
        """Nice name of profile."""
        return self.raw["name"]

    @property
    def perspective(self) -> list | None:
        """Perspective for improve triggers based on heights."""
        return self.raw.get("perspective")

    @property
    def triggers(self) -> list:
        """Array of triggers."""
        return self.raw["triggers"]

    @property
    def uid(self) -> int:
        """Profile ID."""
        return self.raw["uid"]


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


@dataclass
class ProfileConfiguration(ApiItem):
    """Profile configuration."""

    camera: int
    """Camera ID."""

    filters: list[dict[str, Any]]
    """Array of exclude filters."""

    name: str
    """Nice name of profile."""

    perspective: list[dict[str, Any]] | None
    """Perspective for improve triggers based on heights."""

    triggers: list[dict[str, Any]]
    """Array of triggers."""

    uid: int
    """Profile ID."""

    @classmethod
    def decode(cls, data: Any) -> Self:
        """Decode dict to class object."""
        return cls(
            id=data["Name"],
            camera=data["camera"],
            filters=data["filters"],
            name=data["name"],
            perspective=data.get("perspective"),
            triggers=data["triggers"],
            uid=data["uid"],
        )

    @classmethod
    def decode_from_list(cls, data: list[ProfileConfigurationDataT]) -> dict[str, Self]:
        """Decode list[dict] to list of class objects."""
        applications = [cls.decode(v) for v in data]
        return {app.id: app for app in applications}


@dataclass
class ApplicationConfiguration(ApiItem):
    """Base class for application profiles."""

    cameras: list[CameraConfigurationDataT]
    """Cameras."""

    profiles: dict[str, ProfileConfiguration]
    """Profiles"""

    configuration_status: int

    @classmethod
    def decode(cls, data: ConfigurationDataT) -> Self:
        """Decode dict to class object."""
        return cls(
            id="Application configuration",
            cameras=data["cameras"],
            profiles=ProfileConfiguration.decode_from_list(data["profiles"]),
            configuration_status=data["configurationStatus"],
        )


@dataclass
class GetApplicationConfigurationRequest(ApiRequest):
    """Request object for listing application configuration."""

    method = "post"
    # path = "/axis-cgi/applications/list.cgi"


@dataclass
class GetApplicationConfigurationResponse(ApiResponse[ApplicationConfiguration]):
    """Response object for application configuration."""

    api_version: str
    context: str
    method: str

    @classmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Prepare API description dictionary."""
        data: GetConfigurationResponseT = orjson.loads(bytes_data)
        return cls(
            api_version=data["apiVersion"],
            context=data["context"],
            method=data["method"],
            data=ApplicationConfiguration.decode(data["data"]),
        )
