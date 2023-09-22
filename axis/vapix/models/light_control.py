"""Light Control API data model."""

from dataclasses import dataclass

import orjson
from typing_extensions import NotRequired, Self, TypedDict

from .api import CONTEXT, ApiItem, ApiRequest

API_VERSION = "1.1"


class ErrorDataT(TypedDict):
    """Error data in response."""

    code: int
    message: str


class LightInformationT(TypedDict):
    """Light information."""

    enabled: bool
    lightID: str
    lightState: bool
    lightType: str
    nrOfLEDs: int
    automaticAngleOfIlluminationMode: bool
    automaticIntensityMode: bool
    synchronizeDayNightMode: bool
    error: bool
    errorInfo: str


class LightInformationItemsT(TypedDict):
    """Represent list of light information objects."""

    items: list[LightInformationT]


class GetLightInformationResponseT(TypedDict):
    """Represent get light information response."""

    apiVersion: str
    context: str
    method: str
    data: LightInformationItemsT
    error: NotRequired[ErrorDataT]


class ServiceCapabilitiesT(TypedDict):
    """Service capability."""

    automaticIntensitySupport: bool
    manualIntensitySupport: bool
    getCurrentIntensitySupport: bool
    individualIntensitySupport: bool
    automaticAngleOfIlluminationSupport: bool
    manualAngleOfIlluminationSupport: bool
    dayNightSynchronizeSupport: bool


class GetServiceCapabilitiesResponseT(TypedDict):
    """Represent get service capability response."""

    apiVersion: str
    context: str
    method: str
    data: ServiceCapabilitiesT
    error: NotRequired[ErrorDataT]


class LightStatusT(TypedDict):
    """Light status."""

    status: bool


class GetLightStatusResponseT(TypedDict):
    """Represent get light status response."""

    apiVersion: str
    context: str
    method: str
    data: LightStatusT
    error: NotRequired[ErrorDataT]


class RangeT(TypedDict):
    """Range."""

    low: int
    high: int


class ValidRangesT(TypedDict):
    """Light status."""

    ranges: list[RangeT]


class GetValidRangesResponseT(TypedDict):
    """Represent valid intensity response."""

    apiVersion: str
    context: str
    method: str
    data: ValidRangesT
    error: NotRequired[ErrorDataT]


class IntensityT(TypedDict):
    """Light intensity."""

    intensity: int


class GetIntensityResponseT(TypedDict):
    """Represent a get intensity response."""

    apiVersion: str
    context: str
    method: str
    data: IntensityT
    error: NotRequired[ErrorDataT]


class AngleOfIlluminationT(TypedDict):
    """Light intensity."""

    angleOfIllumination: int


class GetAngleOfIlluminationResponseT(TypedDict):
    """Represent a get angle of illumination response."""

    apiVersion: str
    context: str
    method: str
    data: AngleOfIlluminationT
    error: NotRequired[ErrorDataT]


class SynchronizeT(TypedDict):
    """Synchronize day night mode."""

    synchronize: bool


class GetLightSynchronizationDayNightModeResponseT(TypedDict):
    """Represent a get light synchronization day night mode response."""

    apiVersion: str
    context: str
    method: str
    data: SynchronizeT
    error: NotRequired[ErrorDataT]


class ApiVersionsT(TypedDict):
    """List of supported API versions."""

    apiVersions: list[str]


class GetSupportedVersionsResponseT(TypedDict):
    """Get supported versions response."""

    apiVersion: str
    context: str
    method: str
    data: ApiVersionsT
    error: NotRequired[ErrorDataT]


general_error_codes = {
    1100: "Internal error",
    2100: "API version not supported",
    2101: "Invalid JSON",
    2102: "Method not supported",
    2103: "Required parameter missing",
    2104: "Invalid parameter value specified",
}


@dataclass
class LightInformation(ApiItem):
    """Light information item."""

    enabled: bool
    light_state: bool
    light_type: str
    number_of_leds: int
    automatic_intensity_mode: bool
    automatic_angle_of_illumination_mode: bool
    synchronize_day_night_mode: bool
    error: bool
    error_info: str

    @classmethod
    def from_dict(cls, data: LightInformationT) -> Self:
        """Create light information object from dict."""
        return cls(
            id=data["lightID"],
            enabled=data["enabled"],
            light_state=data["lightState"],
            light_type=data["lightType"],
            number_of_leds=data["nrOfLEDs"],
            automatic_intensity_mode=data["automaticIntensityMode"],
            automatic_angle_of_illumination_mode=data[
                "automaticAngleOfIlluminationMode"
            ],
            synchronize_day_night_mode=data["synchronizeDayNightMode"],
            error=data["error"],
            error_info=data["errorInfo"],
        )

    @classmethod
    def from_list(cls, data: list[LightInformationT]) -> dict[str, Self]:
        """Create light information objects from list."""
        lights = [cls.from_dict(item) for item in data]
        return {light.id: light for light in lights}


@dataclass
class Range:
    """High to low range."""

    low: int
    high: int

    @classmethod
    def from_dict(cls, data: RangeT) -> "Range":
        """Create range object from dict."""
        return Range(low=data["low"], high=data["high"])

    @classmethod
    def from_list(cls, data: list[RangeT]) -> list["Range"]:
        """Create range object from dict."""
        return [Range.from_dict(range) for range in data]


@dataclass
class GetLightInformation(ApiRequest[dict[str, LightInformation]]):
    """Request object for getting light information."""

    method = "post"
    path = "/axis-cgi/lightcontrol.cgi"
    content_type = "application/json"
    error_codes = general_error_codes

    api_version: str = API_VERSION
    context: str = CONTEXT

    def __post_init__(self) -> None:
        """Initialize request data."""
        self.data = {
            "apiVersion": self.api_version,
            "context": self.context,
            "method": "getLightInformation",
        }

    def process_raw(self, raw: bytes) -> dict[str, LightInformation]:
        """Prepare light information dictionary."""
        data: GetLightInformationResponseT = orjson.loads(raw)
        return LightInformation.from_list(data["data"]["items"])


@dataclass
class ServiceCapabilities:
    """Service capabilities item."""

    automatic_intensity_support: bool
    manual_intensity_support: bool
    get_current_intensity_support: bool
    individual_intensity_support: bool
    automatic_angle_of_illumination_support: bool
    manual_angle_of_illumination_support: bool
    day_night_synchronize_support: bool

    @classmethod
    def from_dict(cls, data: ServiceCapabilitiesT) -> "ServiceCapabilities":
        """Create service capabilities object from dict."""
        return ServiceCapabilities(
            automatic_intensity_support=data["automaticIntensitySupport"],
            manual_intensity_support=data["manualIntensitySupport"],
            get_current_intensity_support=data["getCurrentIntensitySupport"],
            individual_intensity_support=data["individualIntensitySupport"],
            automatic_angle_of_illumination_support=data[
                "automaticAngleOfIlluminationSupport"
            ],
            manual_angle_of_illumination_support=data[
                "manualAngleOfIlluminationSupport"
            ],
            day_night_synchronize_support=data["dayNightSynchronizeSupport"],
        )


@dataclass
class GetServiceCapabilities(ApiRequest[ServiceCapabilities]):
    """Request object for getting light information."""

    method = "post"
    path = "/axis-cgi/lightcontrol.cgi"
    content_type = "application/json"
    error_codes = general_error_codes

    api_version: str = API_VERSION
    context: str = CONTEXT

    def __post_init__(self) -> None:
        """Initialize request data."""
        self.data = {
            "apiVersion": self.api_version,
            "context": self.context,
            "method": "getServiceCapabilities",
        }

    def process_raw(self, raw: bytes) -> ServiceCapabilities:
        """Prepare light information dictionary."""
        data: GetServiceCapabilitiesResponseT = orjson.loads(raw)
        return ServiceCapabilities.from_dict(data["data"])


@dataclass
class ActivateLightRequest(ApiRequest[None]):
    """Request object for activating light."""

    method = "post"
    path = "/axis-cgi/lightcontrol.cgi"
    content_type = "application/json"
    error_codes = general_error_codes

    api_version: str = API_VERSION
    context: str = CONTEXT
    light_id: str | None = None

    def __post_init__(self) -> None:
        """Initialize request data."""
        assert self.light_id is not None
        self.data = {
            "apiVersion": self.api_version,
            "context": self.context,
            "method": "activateLight",
            "params": {"lightID": self.light_id},
        }

    def process_raw(self, raw: bytes) -> None:
        """No return data to process."""


@dataclass
class DeactivateLightRequest(ActivateLightRequest):
    """Request object for activating light."""

    def __post_init__(self) -> None:
        """Initialize request data."""
        assert self.light_id is not None
        self.data = {
            "apiVersion": self.api_version,
            "context": self.context,
            "method": "deactivateLight",
            "params": {"lightID": self.light_id},
        }


@dataclass
class EnableLightRequest(ActivateLightRequest):
    """Request object for enabling light."""

    def __post_init__(self) -> None:
        """Initialize request data."""
        assert self.light_id is not None
        self.data = {
            "apiVersion": self.api_version,
            "context": self.context,
            "method": "enableLight",
            "params": {"lightID": self.light_id},
        }


@dataclass
class DisableLightRequest(ActivateLightRequest):
    """Request object for disabling light."""

    def __post_init__(self) -> None:
        """Initialize request data."""
        assert self.light_id is not None
        self.data = {
            "apiVersion": self.api_version,
            "context": self.context,
            "method": "disableLight",
            "params": {"lightID": self.light_id},
        }


@dataclass
class GetLightStatusRequest(ApiRequest[bool]):
    """Request object for getting light status."""

    method = "post"
    path = "/axis-cgi/lightcontrol.cgi"
    content_type = "application/json"
    error_codes = general_error_codes

    api_version: str = API_VERSION
    context: str = CONTEXT
    light_id: str | None = None

    def __post_init__(self) -> None:
        """Initialize request data."""
        assert self.light_id is not None
        self.data = {
            "apiVersion": self.api_version,
            "context": self.context,
            "method": "getLightStatus",
            "params": {"lightID": self.light_id},
        }

    def process_raw(self, raw: bytes) -> bool:
        """If light is on or off."""
        data: GetLightStatusResponseT = orjson.loads(raw)
        return data["data"]["status"]


@dataclass
class SetAutomaticIntensityModeRequest(ApiRequest[None]):
    """Enable the automatic light intensity control."""

    method = "post"
    path = "/axis-cgi/lightcontrol.cgi"
    content_type = "application/json"
    error_codes = general_error_codes

    api_version: str = API_VERSION
    context: str = CONTEXT
    light_id: str | None = None
    enabled: bool | None = None

    def __post_init__(self) -> None:
        """Initialize request data."""
        assert self.light_id is not None
        assert self.enabled is not None
        self.data = {
            "apiVersion": self.api_version,
            "context": self.context,
            "method": "setAutomaticIntensityMode",
            "params": {"lightID": self.light_id, "enabled": self.enabled},
        }

    def process_raw(self, raw: bytes) -> None:
        """No return data to process."""


@dataclass
class GetValidIntensityRequest(ApiRequest[Range]):
    """Request object for getting light status."""

    method = "post"
    path = "/axis-cgi/lightcontrol.cgi"
    content_type = "application/json"
    error_codes = general_error_codes

    api_version: str = API_VERSION
    context: str = CONTEXT
    light_id: str | None = None

    def __post_init__(self) -> None:
        """Initialize request data."""
        assert self.light_id is not None
        self.data = {
            "apiVersion": self.api_version,
            "context": self.context,
            "method": "getValidIntensity",
            "params": {"lightID": self.light_id},
        }

    def process_raw(self, raw: bytes) -> Range:
        """If light is on or off."""
        data: GetValidRangesResponseT = orjson.loads(raw)
        return Range.from_dict(data["data"]["ranges"][0])


@dataclass
class SetManualIntensityRequest(ApiRequest[None]):
    """Set manual light intensity."""

    method = "post"
    path = "/axis-cgi/lightcontrol.cgi"
    content_type = "application/json"
    error_codes = general_error_codes

    api_version: str = API_VERSION
    context: str = CONTEXT
    light_id: str | None = None
    intensity: int | None = None

    def __post_init__(self) -> None:
        """Initialize request data."""
        assert self.light_id is not None
        assert self.intensity is not None
        self.data = {
            "apiVersion": self.api_version,
            "context": self.context,
            "method": "setManualIntensity",
            "params": {"lightID": self.light_id, "intensity": self.intensity},
        }

    def process_raw(self, raw: bytes) -> None:
        """No return data to process."""


@dataclass
class GetManualIntensityRequest(ApiRequest[int]):
    """Request object for getting manual intensity."""

    method = "post"
    path = "/axis-cgi/lightcontrol.cgi"
    content_type = "application/json"
    error_codes = general_error_codes

    api_version: str = API_VERSION
    context: str = CONTEXT
    light_id: str | None = None

    def __post_init__(self) -> None:
        """Initialize request data."""
        assert self.light_id is not None
        self.data = {
            "apiVersion": self.api_version,
            "context": self.context,
            "method": "getManualIntensity",
            "params": {"lightID": self.light_id},
        }

    def process_raw(self, raw: bytes) -> int:
        """If light is on or off."""
        data: GetIntensityResponseT = orjson.loads(raw)
        return data["data"]["intensity"]


@dataclass
class SetIndividualIntensityRequest(ApiRequest[None]):
    """Set individual light intensity."""

    method = "post"
    path = "/axis-cgi/lightcontrol.cgi"
    content_type = "application/json"
    error_codes = general_error_codes

    api_version: str = API_VERSION
    context: str = CONTEXT
    light_id: str | None = None
    led_id: int | None = None
    intensity: int | None = None

    def __post_init__(self) -> None:
        """Initialize request data."""
        assert self.light_id is not None
        assert self.led_id is not None
        assert self.intensity is not None
        self.data = {
            "apiVersion": self.api_version,
            "context": self.context,
            "method": "setIndividualIntensity",
            "params": {
                "lightID": self.light_id,
                "LEDID": self.led_id,
                "intensity": self.intensity,
            },
        }

    def process_raw(self, raw: bytes) -> None:
        """No return data to process."""


@dataclass
class GetIndividualIntensityRequest(ApiRequest[int]):
    """Request object for getting individual intensity."""

    method = "post"
    path = "/axis-cgi/lightcontrol.cgi"
    content_type = "application/json"
    error_codes = general_error_codes

    api_version: str = API_VERSION
    context: str = CONTEXT
    light_id: str | None = None
    led_id: int | None = None

    def __post_init__(self) -> None:
        """Initialize request data."""
        assert self.light_id is not None
        assert self.led_id is not None
        self.data = {
            "apiVersion": self.api_version,
            "context": self.context,
            "method": "getIndividualIntensity",
            "params": {"lightID": self.light_id, "LEDID": self.led_id},
        }

    def process_raw(self, raw: bytes) -> int:
        """Process light intensity."""
        data: GetIntensityResponseT = orjson.loads(raw)
        return data["data"]["intensity"]


@dataclass
class GetCurrentIntensityRequest(ApiRequest[int]):
    """Request object for getting manual intensity."""

    method = "post"
    path = "/axis-cgi/lightcontrol.cgi"
    content_type = "application/json"
    error_codes = general_error_codes

    api_version: str = API_VERSION
    context: str = CONTEXT
    light_id: str | None = None

    def __post_init__(self) -> None:
        """Initialize request data."""
        assert self.light_id is not None
        self.data = {
            "apiVersion": self.api_version,
            "context": self.context,
            "method": "getCurrentIntensity",
            "params": {"lightID": self.light_id},
        }

    def process_raw(self, raw: bytes) -> int:
        """If light is on or off."""
        data: GetIntensityResponseT = orjson.loads(raw)
        return data["data"]["intensity"]


@dataclass
class SetAutomaticAngleOfIlluminationModeRequest(ApiRequest[None]):
    """Enable the automatic angle of illumination control."""

    method = "post"
    path = "/axis-cgi/lightcontrol.cgi"
    content_type = "application/json"
    error_codes = general_error_codes

    api_version: str = API_VERSION
    context: str = CONTEXT
    light_id: str | None = None
    enabled: bool | None = None

    def __post_init__(self) -> None:
        """Initialize request data."""
        assert self.light_id is not None
        assert self.enabled is not None
        self.data = {
            "apiVersion": self.api_version,
            "context": self.context,
            "method": "setAutomaticAngleOfIlluminationMode",
            "params": {"lightID": self.light_id, "enabled": self.enabled},
        }

    def process_raw(self, raw: bytes) -> None:
        """No return data to process."""


@dataclass
class GetValidAngleOfIllumination(ApiRequest[list[Range]]):
    """Request object for getting angle of illumination range."""

    method = "post"
    path = "/axis-cgi/lightcontrol.cgi"
    content_type = "application/json"
    error_codes = general_error_codes

    api_version: str = API_VERSION
    context: str = CONTEXT
    light_id: str | None = None

    def __post_init__(self) -> None:
        """Initialize request data."""
        assert self.light_id is not None
        self.data = {
            "apiVersion": self.api_version,
            "context": self.context,
            "method": "getValidAngleOfIllumination",
            "params": {"lightID": self.light_id},
        }

    def process_raw(self, raw: bytes) -> list[Range]:
        """If light is on or off."""
        data: GetValidRangesResponseT = orjson.loads(raw)
        return Range.from_list(data["data"]["ranges"])


@dataclass
class SetManualAngleOfIlluminationModeRequest(ApiRequest[None]):
    """Set the manual angle of illumination."""

    method = "post"
    path = "/axis-cgi/lightcontrol.cgi"
    content_type = "application/json"
    error_codes = general_error_codes

    api_version: str = API_VERSION
    context: str = CONTEXT
    light_id: str | None = None
    angle_of_illumination: int | None = None

    def __post_init__(self) -> None:
        """Initialize request data."""
        assert self.light_id is not None
        assert self.angle_of_illumination is not None
        self.data = {
            "apiVersion": self.api_version,
            "context": self.context,
            "method": "setManualAngleOfIllumination",
            "params": {
                "lightID": self.light_id,
                "angleOfIllumination": self.angle_of_illumination,
            },
        }

    def process_raw(self, raw: bytes) -> None:
        """No return data to process."""


@dataclass
class GetManualAngleOfIlluminationRequest(ApiRequest[int]):
    """Request object for getting manual angle of illumination."""

    method = "post"
    path = "/axis-cgi/lightcontrol.cgi"
    content_type = "application/json"
    error_codes = general_error_codes

    api_version: str = API_VERSION
    context: str = CONTEXT
    light_id: str | None = None

    def __post_init__(self) -> None:
        """Initialize request data."""
        assert self.light_id is not None
        self.data = {
            "apiVersion": self.api_version,
            "context": self.context,
            "method": "getManualAngleOfIllumination",
            "params": {"lightID": self.light_id},
        }

    def process_raw(self, raw: bytes) -> int:
        """Angle of illumination."""
        data: GetAngleOfIlluminationResponseT = orjson.loads(raw)
        return data["data"]["angleOfIllumination"]


@dataclass
class GetCurrentAngleOfIlluminationRequest(ApiRequest[int]):
    """Request object for getting current angle of illumination."""

    method = "post"
    path = "/axis-cgi/lightcontrol.cgi"
    content_type = "application/json"
    error_codes = general_error_codes

    api_version: str = API_VERSION
    context: str = CONTEXT
    light_id: str | None = None

    def __post_init__(self) -> None:
        """Initialize request data."""
        assert self.light_id is not None
        self.data = {
            "apiVersion": self.api_version,
            "context": self.context,
            "method": "getCurrentAngleOfIllumination",
            "params": {"lightID": self.light_id},
        }

    def process_raw(self, raw: bytes) -> int:
        """Angle of illumination."""
        data: GetAngleOfIlluminationResponseT = orjson.loads(raw)
        return data["data"]["angleOfIllumination"]


@dataclass
class SetLightSynchronizeDayNightModeRequest(ApiRequest[None]):
    """Enable automatic synchronization with the day/night mode."""

    method = "post"
    path = "/axis-cgi/lightcontrol.cgi"
    content_type = "application/json"
    error_codes = general_error_codes

    api_version: str = API_VERSION
    context: str = CONTEXT
    light_id: str | None = None
    enabled: bool | None = None

    def __post_init__(self) -> None:
        """Initialize request data."""
        assert self.light_id is not None
        assert self.enabled is not None
        self.data = {
            "apiVersion": self.api_version,
            "context": self.context,
            "method": "setLightSynchronizationDayNightMode",
            "params": {"lightID": self.light_id, "enabled": self.enabled},
        }

    def process_raw(self, raw: bytes) -> None:
        """No return data to process."""


@dataclass
class GetLightSynchronizeDayNightModeRequest(ApiRequest[bool]):
    """Request object for getting current angle of illumination."""

    method = "post"
    path = "/axis-cgi/lightcontrol.cgi"
    content_type = "application/json"
    error_codes = general_error_codes

    api_version: str = API_VERSION
    context: str = CONTEXT
    light_id: str | None = None

    def __post_init__(self) -> None:
        """Initialize request data."""
        assert self.light_id is not None
        self.data = {
            "apiVersion": self.api_version,
            "context": self.context,
            "method": "getLightSynchronizationDayNightMode",
            "params": {"lightID": self.light_id},
        }

    def process_raw(self, raw: bytes) -> bool:
        """If light is on or off."""
        data: GetLightSynchronizationDayNightModeResponseT = orjson.loads(raw)
        return data["data"]["synchronize"]


@dataclass
class GetSupportedVersionsRequest(ApiRequest[list[str]]):
    """Request object for listing supported API versions."""

    method = "post"
    path = "/axis-cgi/lightcontrol.cgi"
    content_type = "application/json"
    error_codes = general_error_codes

    context: str = CONTEXT

    def __post_init__(self) -> None:
        """Initialize request data."""
        self.data = {
            "context": self.context,
            "method": "getSupportedVersions",
        }

    def process_raw(self, raw: bytes) -> list[str]:
        """Process supported versions."""
        data: GetSupportedVersionsResponseT = orjson.loads(raw)
        return data.get("data", {}).get("apiVersions", [])
