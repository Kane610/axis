"""Object Analytics API data model."""

from dataclasses import dataclass
from typing import Any, NotRequired, Self, TypedDict

import orjson

from ..api import CONTEXT, ApiItem, ApiRequest, ApiResponse
from .api import ApplicationAPIItem

API_VERSION = "1.0"


class ObjectAnalyticsScenario(ApplicationAPIItem):
    """Object Analytics Scenario."""

    @property
    def camera(self) -> list:  # type: ignore[override]
        """Camera ID."""
        return self.raw["devices"]

    @property
    def object_classifications(self) -> list:
        """Classifications of objects to detect."""
        return self.raw["objectClassifications"]

    @property
    def perspectives(self) -> list | None:
        """Perspectives for improve triggers based on heights."""
        return self.raw.get("perspectives")

    @property
    def presets(self) -> list:
        """Presets."""
        return self.raw["presets"]

    @property
    def trigger_type(self) -> str:
        """Type of trigger."""
        return self.raw["type"]

    @property
    def uid(self) -> int:
        """Scenario ID."""
        return self.raw["id"]


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

    devices: list
    metadataOverlay: list
    perspective: NotRequired[list]
    scenarios: list


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

    presets: list[int]
    """For mechanical PTZ cameras, each profile can be connected to one preset.

    If a preset is added, the profile will only be active when the camera is at
    the given preset. If this parameter is omitted or the profile is not connected
    to any preset it will always be active.
    """

    triggers: list[dict[str, Any]]
    """Array of triggers."""

    uid: int
    """Profile ID."""

    @classmethod
    def decode(cls, data: Any) -> Self:
        """Decode dict to class object."""
        return cls(
            id=data["name"],
            camera=data["camera"],
            filters=data["filters"],
            name=data["name"],
            presets=data.get("presets", []),
            triggers=data["triggers"],
            uid=data["uid"],
        )

    @classmethod
    def decode_from_list(cls, data: list[ProfileConfigurationDataT]) -> dict[str, Self]:
        """Decode list[dict] to list of class objects."""
        applications = [cls.decode(v) for v in data]
        return {app.id: app for app in applications}


@dataclass
class Configuration(ApiItem):
    """Object analytics configuration."""

    devices: list
    """Container for the supported video devices."""

    metadata_overlay: list
    """Container for the metadata overlay options."""

    perspectives: list
    """Container for the perspective data."""

    scenarios: list
    """Container for the scenario data."""

    @classmethod
    def decode(cls, data: ConfigurationDataT) -> Self:
        """Decode dict to class object."""
        return cls(
            id="object analytics",
            devices=data["devices"],
            metadata_overlay=data["metadataOverlay"],
            perspectives=data.get("perspective", []),
            scenarios=data["scenarios"],
        )


@dataclass
class GetConfigurationRequest(ApiRequest):
    """Request object for listing Object analytics configuration."""

    method = "post"
    path = "/local/objectanalytics/control.cgi"

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
    """Response object for Object analytics configuration."""

    api_version: str
    context: str
    method: str

    @classmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Prepare Object analytics configuration response data."""
        data: GetConfigurationResponseT = orjson.loads(bytes_data)
        return cls(
            api_version=data["apiVersion"],
            context=data["context"],
            method=data["method"],
            data=Configuration.decode(data["data"]),
        )
