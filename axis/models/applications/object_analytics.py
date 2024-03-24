"""Object Analytics API data model."""

from dataclasses import dataclass
import enum
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
    bars: list[dict[str, Any]]


class ConfigurationScenarioDataT(TypedDict):
    """Scenario configuration data from response."""

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
    """Configuration data from response."""

    devices: list[ConfigurationDeviceDataT]
    metadataOverlay: list[ConfigurationMetadataOverlayDataT]
    perspectives: NotRequired[list[ConfigurationPerspectiveDataT]]
    scenarios: list[ConfigurationScenarioDataT]


class GetConfigurationResponseT(TypedDict):
    """Get configuration response."""

    apiVersion: str
    context: str
    method: str
    data: ConfigurationDataT
    # error: NotRequired[ErrorDataT]


class ScenarioType(enum.StrEnum):
    """Scenario types."""

    CROSS_LINE_COUNTING = "crosslinecounting"
    """Crossline Counting scenario count objects crossing a defined
    counting line. The line has a polyline shape and is triggered by objects passing
    the line in a specified direction.
    """
    FENCE = "fence"
    """This scenario makes it possible to define a special fence trigger with a
    polyline shape activated by objects passing the line in a certain direction.
    """
    MOTION = "motion"
    """This scenario makes it possible to define an include area which acts
    as a trigger zone for moving objects. Additionally, filters can be configured to
    exclude objects based on other criteria, such as size.
    """
    OCCUPANCY_IN_AREA = "occupancyInArea"
    """Occupancy in Area scenario allows defining an include area which are
    able to count objects. This include stationary objects.
    """


@dataclass(frozen=True)
class ScenarioConfiguration(ApiItem):
    """Profile configuration."""

    devices: list[dict[str, int]]
    """Lists the devices that the scenario should be applied to."""

    filters: list[dict[str, Any]]
    """Array of exclude filters."""

    name: str
    """Nice name of scenario."""

    object_classifications: list[dict[str, str]]
    """Identifies the object type and additional subtype."""

    perspectives: list[int]
    """A list of perspective IDs used in the scenario."""

    presets: list[int]
    """For mechanical PTZ cameras, each profile can be connected to one preset.

    If a preset is added, the profile will only be active when the camera is at
    the given preset. If this parameter is omitted or the profile is not connected
    to any preset it will always be active.

    -2 - Tracking is always enabled, except when camera is moving.
    -1 - Tracking is done on all preset positions.
    No tracking is done if the PTZ device is not set to a preset.
    1 - Tracking on the home position of the PTZ device.
    2... - Tracking on specific presets only.
    """

    triggers: list[dict[str, Any]]
    """Array of triggers."""

    type: ScenarioType
    """Possible scenario types."""

    @classmethod
    def decode(cls, data: ConfigurationScenarioDataT) -> Self:
        """Decode dict to class object."""
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
    """Object analytics configuration."""

    devices: list[ConfigurationDeviceDataT]
    """Container for the supported video devices."""

    metadata_overlay: list[ConfigurationMetadataOverlayDataT]
    """Container for the metadata overlay options."""

    perspectives: list[ConfigurationPerspectiveDataT]
    """Container for the perspective data."""

    scenarios: dict[str, ScenarioConfiguration]
    """Container for the scenario data."""

    @classmethod
    def decode(cls, data: ConfigurationDataT) -> Self:
        """Decode dict to class object."""
        return cls(
            id="object analytics",
            devices=data["devices"],
            metadata_overlay=data["metadataOverlay"],
            perspectives=data.get("perspectives", []),
            scenarios=ScenarioConfiguration.decode_to_dict(data["scenarios"]),
        )


@dataclass
class GetConfigurationRequest(ApiRequest):
    """Request object for listing Object analytics configuration."""

    method = "post"
    path = "/local/objectanalytics/control.cgi"
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
                "params": {},  # Early version of AOA (v1.0-20) requires this
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
