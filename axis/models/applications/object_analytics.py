"""Models for Object Analytics scenarios, cameras, overlays, and perspectives."""

from dataclasses import dataclass
import enum
from typing import Any, Literal, NotRequired, Self, TypedDict

import orjson

from ..api import CONTEXT, ApiItem, ApiRequest, ApiResponse

API_VERSION = "1.0"


class ConfigurationDeviceDataT(TypedDict):
    """Camera identifier, rotation, and active state in a configuration response."""

    id: int
    type: Literal["camera"]
    rotation: int
    isActive: bool


class ConfigurationMetadataOverlayDataT(TypedDict):
    """Metadata overlay ID and video resolutions where it is drawn."""

    id: int
    drawOnAllResolutions: bool
    resolutions: list[str]


class ConfigurationPerspectiveDataT(TypedDict):
    """Perspective calibration ID and its calibration bars."""

    id: int
    bars: list[dict[str, Any]]


class ConfigurationScenarioDataT(TypedDict):
    """Detection scenario settings returned by the Object Analytics API."""

    id: int
    name: str
    type: Literal["crosslinecounting", "fence", "motion", "occupancyInArea"]
    metadataOverlay: int
    alarmRate: str
    devices: list[dict[str, Any]]
    filters: list[dict[str, Any]]
    objectClassifications: NotRequired[list[dict[str, str]]]
    perspectives: NotRequired[list[int]]
    presets: NotRequired[list[int]]
    triggers: list[dict[str, Any]]


class ConfigurationDataT(TypedDict):
    """Cameras, overlays, perspectives, and scenarios in the configuration."""

    devices: list[ConfigurationDeviceDataT]
    metadataOverlay: list[ConfigurationMetadataOverlayDataT]
    perspectives: NotRequired[list[ConfigurationPerspectiveDataT]]
    scenarios: list[ConfigurationScenarioDataT]


class GetConfigurationResponseT(TypedDict):
    """JSON envelope returned by getConfiguration."""

    apiVersion: str
    context: str
    method: str
    data: ConfigurationDataT
    # error: NotRequired[ErrorDataT]


class ScenarioType(enum.StrEnum):
    """Detection tasks that an Object Analytics scenario can perform."""

    CROSS_LINE_COUNTING = "crosslinecounting"
    """Count objects crossing a configured line in the selected direction."""
    FENCE = "fence"
    """Trigger when objects cross a configured line in the selected direction."""
    MOTION = "motion"
    """Trigger on moving objects in an included area, with optional exclusion filters."""
    OCCUPANCY_IN_AREA = "occupancyInArea"
    """Count objects inside an included area, including stationary objects."""


@dataclass(frozen=True)
class ScenarioConfiguration(ApiItem):
    """Object Analytics scenario and its detection settings."""

    devices: list[dict[str, int]]
    """Video devices to which this scenario applies."""

    filters: list[dict[str, Any]]
    """Filters that exclude detections from the scenario."""

    name: str
    """Display name assigned to the scenario."""

    object_classifications: list[dict[str, str]]
    """Object categories and subtypes included in this scenario."""

    perspectives: list[int]
    """Perspective calibration IDs used to estimate object size or height."""

    presets: list[int]
    """For mechanical PTZ cameras, tracking can be limited to preset positions.

    -2 tracks whenever the camera is stationary.
    -1 tracks at all preset positions, but not when no preset is selected.
    1 tracks at the home position; values above 1 select specific presets.
    """

    triggers: list[dict[str, Any]]
    """Trigger regions and settings configured for this scenario."""

    type: ScenarioType
    """Detection task performed by this scenario."""

    @classmethod
    def decode(cls, data: ConfigurationScenarioDataT) -> Self:
        """Convert one Object Analytics scenario payload to a model."""
        return cls(
            id=str(data["id"]),
            devices=data["devices"],
            filters=data.get("filters", []),
            name=data["name"],
            object_classifications=data.get("objectClassifications", []),
            perspectives=data.get("perspectives", []),
            presets=data.get("presets", []),
            triggers=data["triggers"],
            type=ScenarioType(data["type"]),
        )


@dataclass(frozen=True)
class Configuration(ApiItem):
    """Current Object Analytics cameras, overlays, perspectives, and scenarios."""

    devices: list[ConfigurationDeviceDataT]
    """Video devices available to scenarios, including each camera's active state."""

    metadata_overlay: list[ConfigurationMetadataOverlayDataT]
    """Metadata overlay settings and the resolutions where overlays are drawn."""

    perspectives: list[ConfigurationPerspectiveDataT]
    """Perspective calibration data used by scenarios."""

    scenarios: dict[str, ScenarioConfiguration]
    """Scenarios indexed by their device-assigned identifiers."""

    @classmethod
    def decode(cls, data: ConfigurationDataT) -> Self:
        """Convert the response configuration into indexed scenario models."""
        return cls(
            id="object analytics",
            devices=data["devices"],
            metadata_overlay=data["metadataOverlay"],
            perspectives=data.get("perspectives", []),
            scenarios=ScenarioConfiguration.decode_to_dict(data["scenarios"]),
        )


@dataclass
class GetConfigurationResponse(ApiResponse[Configuration]):
    """Object Analytics configuration returned by getConfiguration."""

    api_version: str
    context: str
    method: str

    @classmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Parse the JSON envelope and decode its Object Analytics configuration."""
        data: GetConfigurationResponseT = orjson.loads(bytes_data)
        return cls(
            api_version=data["apiVersion"],
            context=data["context"],
            method=data["method"],
            data=Configuration.decode(data["data"]),
        )


@dataclass
class GetConfigurationRequest(ApiRequest[GetConfigurationResponse]):
    """Request the current Object Analytics configuration."""

    method = "post"
    path = "/local/objectanalytics/control.cgi"
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
                "params": {},  # Early version of AOA (v1.0-20) requires this
            }
        )
