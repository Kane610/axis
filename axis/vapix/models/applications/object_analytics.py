"""Object Analytics API data model."""

from dataclasses import dataclass
from typing import Any, Literal, NotRequired, Self, TypedDict

import orjson

from ..api import CONTEXT, ApiItem, ApiRequest, ApiResponse

API_VERSION = "1.0"


class ConfigurationDeviceDataT(TypedDict):
    """Device configuration data from response."""

    id: int
    type: Literal["camera"]
    rotation: int
    isActive: bool


class ConfigurationMetadataOverlayDataT(TypedDict):
    """Metadata overlay configuration data from response."""

    id: int
    drawOnAllResolutions: bool
    resolutions: list[str]


class ConfigurationPerspectiveDataT(TypedDict):
    """Perspective configuration data from response."""

    id: int
    bars: list


class ConfigurationScenarioDataT(TypedDict):
    """Scenario configuration data from response."""

    id: int
    name: str
    type: Literal["crosslinecounting", "fence", "motion", "occupancyInArea"]
    metadataOverlay: int
    alarmRate: str
    devices: list
    filters: list
    objectClassifications: list
    perspectives: list
    presets: list
    triggers: list


class ConfigurationDataT(TypedDict):
    """Configuration data from response."""

    devices: list[ConfigurationDeviceDataT]
    metadataOverlay: list[ConfigurationMetadataOverlayDataT]
    perspective: NotRequired[list[ConfigurationPerspectiveDataT]]
    scenarios: list[ConfigurationScenarioDataT]


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
    def decode_from_list(cls, data: list[ConfigurationDeviceDataT]) -> dict[str, Self]:
        """Decode list[dict] to list of class objects."""
        applications = [cls.decode(v) for v in data]
        return {app.id: app for app in applications}


@dataclass
class Configuration(ApiItem):
    """Object analytics configuration."""

    devices: list[ConfigurationDeviceDataT]
    """Container for the supported video devices."""

    metadata_overlay: list[ConfigurationMetadataOverlayDataT]
    """Container for the metadata overlay options."""

    perspectives: list[ConfigurationPerspectiveDataT]
    """Container for the perspective data."""

    scenarios: list[ConfigurationScenarioDataT]
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
