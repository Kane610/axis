"""Light Control API data model."""

from __future__ import annotations

from dataclasses import dataclass
from typing import NotRequired, Self

import orjson
from typing_extensions import TypedDict

from .api import CONTEXT, ApiItem, ApiRequest, ApiResponse

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


@dataclass(frozen=True)
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
    def decode(cls, data: LightInformationT) -> Self:
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


@dataclass
class Range:
    """High to low range."""

    low: int
    high: int

    @classmethod
    def from_dict(cls, data: RangeT) -> Self:
        """Create range object from dict."""
        return cls(low=data["low"], high=data["high"])

    @classmethod
    def from_list(cls, data: list[RangeT]) -> list[Self]:
        """Create range object from dict."""
        return [cls.from_dict(range) for range in data]


@dataclass
class GetLightInformationRequest(ApiRequest):
    """Request object for getting light information."""

    method = "post"
    path = "/axis-cgi/lightcontrol.cgi"
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
                "method": "getLightInformation",
            }
        )


@dataclass
class GetLightInformationResponse(ApiResponse[dict[str, LightInformation]]):
    """Response object for getting light information."""

    api_version: str
    context: str
    method: str
    data: dict[str, LightInformation]
    # error: ErrorDataT | None = None

    @classmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Prepare API description dictionary."""
        data: GetLightInformationResponseT = orjson.loads(bytes_data)
        return cls(
            api_version=data["apiVersion"],
            context=data["context"],
            method=data["method"],
            data=LightInformation.decode_to_dict(data.get("data", {}).get("items", [])),
        )


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
    def from_dict(cls, data: ServiceCapabilitiesT) -> Self:
        """Create service capabilities object from dict."""
        return cls(
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
class GetServiceCapabilitiesRequest(ApiRequest):
    """Request object for getting service capabilities."""

    method = "post"
    path = "/axis-cgi/lightcontrol.cgi"
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
                "method": "getServiceCapabilities",
            }
        )


@dataclass
class GetServiceCapabilitiesResponse(ApiResponse[ServiceCapabilities]):
    """Response object for getting service capabilities."""

    api_version: str
    context: str
    method: str
    data: ServiceCapabilities
    # error: ErrorDataT | None = None

    @classmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Prepare API description dictionary."""
        data: GetServiceCapabilitiesResponseT = orjson.loads(bytes_data)
        return cls(
            api_version=data["apiVersion"],
            context=data["context"],
            method=data["method"],
            data=ServiceCapabilities.from_dict(data["data"]),
        )


@dataclass
class ActivateLightRequest(ApiRequest):
    """Request object for activating light."""

    method = "post"
    path = "/axis-cgi/lightcontrol.cgi"
    content_type = "application/json"
    error_codes = general_error_codes

    light_id: str

    api_version: str = API_VERSION
    context: str = CONTEXT

    @property
    def content(self) -> bytes:
        """Initialize request data."""
        return orjson.dumps(
            {
                "apiVersion": self.api_version,
                "context": self.context,
                "method": "activateLight",
                "params": {"lightID": self.light_id},
            }
        )


@dataclass
class DeactivateLightRequest(ActivateLightRequest):
    """Request object for activating light."""

    @property
    def content(self) -> bytes:
        """Initialize request data."""
        return orjson.dumps(
            {
                "apiVersion": self.api_version,
                "context": self.context,
                "method": "deactivateLight",
                "params": {"lightID": self.light_id},
            }
        )


@dataclass
class EnableLightRequest(ActivateLightRequest):
    """Request object for enabling light."""

    @property
    def content(self) -> bytes:
        """Initialize request data."""
        return orjson.dumps(
            {
                "apiVersion": self.api_version,
                "context": self.context,
                "method": "enableLight",
                "params": {"lightID": self.light_id},
            }
        )


@dataclass
class DisableLightRequest(ActivateLightRequest):
    """Request object for disabling light."""

    @property
    def content(self) -> bytes:
        """Initialize request data."""
        return orjson.dumps(
            {
                "apiVersion": self.api_version,
                "context": self.context,
                "method": "disableLight",
                "params": {"lightID": self.light_id},
            }
        )


@dataclass
class GetLightStatusRequest(ApiRequest):
    """Request object for getting light status."""

    method = "post"
    path = "/axis-cgi/lightcontrol.cgi"
    content_type = "application/json"
    error_codes = general_error_codes

    light_id: str

    api_version: str = API_VERSION
    context: str = CONTEXT

    @property
    def content(self) -> bytes:
        """Initialize request data."""
        return orjson.dumps(
            {
                "apiVersion": self.api_version,
                "context": self.context,
                "method": "getLightStatus",
                "params": {"lightID": self.light_id},
            }
        )


@dataclass
class GetLightStatusResponse(ApiResponse[bool]):
    """Response object for getting light status."""

    api_version: str
    context: str
    method: str
    data: bool
    # error: ErrorDataT | None = None

    @classmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Prepare API description dictionary."""
        data: GetLightStatusResponseT = orjson.loads(bytes_data)
        return cls(
            api_version=data["apiVersion"],
            context=data["context"],
            method=data["method"],
            data=data["data"]["status"],
        )


@dataclass
class SetAutomaticIntensityModeRequest(ApiRequest):
    """Enable the automatic light intensity control."""

    method = "post"
    path = "/axis-cgi/lightcontrol.cgi"
    content_type = "application/json"
    error_codes = general_error_codes

    light_id: str
    enabled: bool

    api_version: str = API_VERSION
    context: str = CONTEXT

    @property
    def content(self) -> bytes:
        """Initialize request data."""
        return orjson.dumps(
            {
                "apiVersion": self.api_version,
                "context": self.context,
                "method": "setAutomaticIntensityMode",
                "params": {"lightID": self.light_id, "enabled": self.enabled},
            }
        )


@dataclass
class GetValidIntensityRequest(ApiRequest):
    """Request object for getting valid intensity range of light."""

    method = "post"
    path = "/axis-cgi/lightcontrol.cgi"
    content_type = "application/json"
    error_codes = general_error_codes

    light_id: str

    api_version: str = API_VERSION
    context: str = CONTEXT

    @property
    def content(self) -> bytes:
        """Initialize request data."""
        return orjson.dumps(
            {
                "apiVersion": self.api_version,
                "context": self.context,
                "method": "getValidIntensity",
                "params": {"lightID": self.light_id},
            }
        )


@dataclass
class GetValidIntensityResponse(ApiResponse[Range]):
    """Response object for getting valid intensity range of light."""

    api_version: str
    context: str
    method: str
    data: Range
    # error: ErrorDataT | None = None

    @classmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Prepare API description dictionary."""
        data: GetValidRangesResponseT = orjson.loads(bytes_data)
        return cls(
            api_version=data["apiVersion"],
            context=data["context"],
            method=data["method"],
            data=Range.from_dict(data["data"]["ranges"][0]),
        )


@dataclass
class SetManualIntensityRequest(ApiRequest):
    """Set manual light intensity."""

    method = "post"
    path = "/axis-cgi/lightcontrol.cgi"
    content_type = "application/json"
    error_codes = general_error_codes

    light_id: str
    intensity: int

    api_version: str = API_VERSION
    context: str = CONTEXT

    @property
    def content(self) -> bytes:
        """Initialize request data."""
        return orjson.dumps(
            {
                "apiVersion": self.api_version,
                "context": self.context,
                "method": "setManualIntensity",
                "params": {"lightID": self.light_id, "intensity": self.intensity},
            }
        )


@dataclass
class GetManualIntensityRequest(ApiRequest):
    """Request object for getting manual intensity."""

    method = "post"
    path = "/axis-cgi/lightcontrol.cgi"
    content_type = "application/json"
    error_codes = general_error_codes

    light_id: str

    api_version: str = API_VERSION
    context: str = CONTEXT

    @property
    def content(self) -> bytes:
        """Initialize request data."""
        return orjson.dumps(
            {
                "apiVersion": self.api_version,
                "context": self.context,
                "method": "getManualIntensity",
                "params": {"lightID": self.light_id},
            }
        )


@dataclass
class GetManualIntensityResponse(ApiResponse[int]):
    """Response object for getting manual intensity."""

    api_version: str
    context: str
    method: str
    data: int
    # error: ErrorDataT | None = None

    @classmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Prepare API description dictionary."""
        data: GetIntensityResponseT = orjson.loads(bytes_data)
        return cls(
            api_version=data["apiVersion"],
            context=data["context"],
            method=data["method"],
            data=data["data"]["intensity"],
        )


@dataclass
class SetIndividualIntensityRequest(ApiRequest):
    """Set individual light intensity."""

    method = "post"
    path = "/axis-cgi/lightcontrol.cgi"
    content_type = "application/json"
    error_codes = general_error_codes

    light_id: str
    led_id: int
    intensity: int

    api_version: str = API_VERSION
    context: str = CONTEXT

    @property
    def content(self) -> bytes:
        """Initialize request data."""
        return orjson.dumps(
            {
                "apiVersion": self.api_version,
                "context": self.context,
                "method": "setIndividualIntensity",
                "params": {
                    "lightID": self.light_id,
                    "LEDID": self.led_id,
                    "intensity": self.intensity,
                },
            }
        )


@dataclass
class GetIndividualIntensityRequest(ApiRequest):
    """Request object for getting individual intensity."""

    method = "post"
    path = "/axis-cgi/lightcontrol.cgi"
    content_type = "application/json"
    error_codes = general_error_codes

    light_id: str
    led_id: int

    api_version: str = API_VERSION
    context: str = CONTEXT

    @property
    def content(self) -> bytes:
        """Initialize request data."""
        return orjson.dumps(
            {
                "apiVersion": self.api_version,
                "context": self.context,
                "method": "getIndividualIntensity",
                "params": {"lightID": self.light_id, "LEDID": self.led_id},
            }
        )


@dataclass
class GetIndividualIntensityResponse(ApiResponse[int]):
    """Response object for getting individual intensity."""

    api_version: str
    context: str
    method: str
    data: int
    # error: ErrorDataT | None = None

    @classmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Prepare API description dictionary."""
        data: GetIntensityResponseT = orjson.loads(bytes_data)
        return cls(
            api_version=data["apiVersion"],
            context=data["context"],
            method=data["method"],
            data=data["data"]["intensity"],
        )


@dataclass
class GetCurrentIntensityRequest(ApiRequest):
    """Request object for getting current intensity."""

    method = "post"
    path = "/axis-cgi/lightcontrol.cgi"
    content_type = "application/json"
    error_codes = general_error_codes

    light_id: str

    api_version: str = API_VERSION
    context: str = CONTEXT

    @property
    def content(self) -> bytes:
        """Initialize request data."""
        return orjson.dumps(
            {
                "apiVersion": self.api_version,
                "context": self.context,
                "method": "getCurrentIntensity",
                "params": {"lightID": self.light_id},
            }
        )


@dataclass
class GetCurrentIntensityResponse(ApiResponse[int]):
    """Response object for getting current intensity."""

    api_version: str
    context: str
    method: str
    data: int
    # error: ErrorDataT | None = None

    @classmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Prepare API description dictionary."""
        data: GetIntensityResponseT = orjson.loads(bytes_data)
        return cls(
            api_version=data["apiVersion"],
            context=data["context"],
            method=data["method"],
            data=data["data"]["intensity"],
        )


@dataclass
class SetAutomaticAngleOfIlluminationModeRequest(ApiRequest):
    """Enable the automatic angle of illumination control."""

    method = "post"
    path = "/axis-cgi/lightcontrol.cgi"
    content_type = "application/json"
    error_codes = general_error_codes

    light_id: str
    enabled: bool

    api_version: str = API_VERSION
    context: str = CONTEXT

    @property
    def content(self) -> bytes:
        """Initialize request data."""
        return orjson.dumps(
            {
                "apiVersion": self.api_version,
                "context": self.context,
                "method": "setAutomaticAngleOfIlluminationMode",
                "params": {"lightID": self.light_id, "enabled": self.enabled},
            }
        )


@dataclass
class GetValidAngleOfIlluminationRequest(ApiRequest):
    """Request object for getting valid angle of illumination range."""

    method = "post"
    path = "/axis-cgi/lightcontrol.cgi"
    content_type = "application/json"
    error_codes = general_error_codes

    light_id: str

    api_version: str = API_VERSION
    context: str = CONTEXT

    @property
    def content(self) -> bytes:
        """Initialize request data."""
        return orjson.dumps(
            {
                "apiVersion": self.api_version,
                "context": self.context,
                "method": "getValidAngleOfIllumination",
                "params": {"lightID": self.light_id},
            }
        )


@dataclass
class GetValidAngleOfIlluminationResponse(ApiResponse[list[Range]]):
    """Response object for getting valid angle of illumination range."""

    api_version: str
    context: str
    method: str
    data: list[Range]
    # error: ErrorDataT | None = None

    @classmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Prepare API description dictionary."""
        data: GetValidRangesResponseT = orjson.loads(bytes_data)
        return cls(
            api_version=data["apiVersion"],
            context=data["context"],
            method=data["method"],
            data=Range.from_list(data["data"]["ranges"]),
        )


@dataclass
class SetManualAngleOfIlluminationModeRequest(ApiRequest):
    """Set the manual angle of illumination."""

    method = "post"
    path = "/axis-cgi/lightcontrol.cgi"
    content_type = "application/json"
    error_codes = general_error_codes

    light_id: str
    angle_of_illumination: int

    api_version: str = API_VERSION
    context: str = CONTEXT

    @property
    def content(self) -> bytes:
        """Initialize request data."""
        return orjson.dumps(
            {
                "apiVersion": self.api_version,
                "context": self.context,
                "method": "setManualAngleOfIllumination",
                "params": {
                    "lightID": self.light_id,
                    "angleOfIllumination": self.angle_of_illumination,
                },
            }
        )


@dataclass
class GetManualAngleOfIlluminationRequest(ApiRequest):
    """Request object for getting manual angle of illumination."""

    method = "post"
    path = "/axis-cgi/lightcontrol.cgi"
    content_type = "application/json"
    error_codes = general_error_codes

    light_id: str

    api_version: str = API_VERSION
    context: str = CONTEXT

    @property
    def content(self) -> bytes:
        """Initialize request data."""
        return orjson.dumps(
            {
                "apiVersion": self.api_version,
                "context": self.context,
                "method": "getManualAngleOfIllumination",
                "params": {"lightID": self.light_id},
            }
        )


@dataclass
class GetManualAngleOfIlluminationResponse(ApiResponse[int]):
    """Response object for getting manual angle of illumination."""

    api_version: str
    context: str
    method: str
    data: int
    # error: ErrorDataT | None = None

    @classmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Prepare API description dictionary."""
        data: GetAngleOfIlluminationResponseT = orjson.loads(bytes_data)
        return cls(
            api_version=data["apiVersion"],
            context=data["context"],
            method=data["method"],
            data=data["data"]["angleOfIllumination"],
        )


@dataclass
class GetCurrentAngleOfIlluminationRequest(ApiRequest):
    """Request object for getting current angle of illumination."""

    method = "post"
    path = "/axis-cgi/lightcontrol.cgi"
    content_type = "application/json"
    error_codes = general_error_codes

    light_id: str

    api_version: str = API_VERSION
    context: str = CONTEXT

    @property
    def content(self) -> bytes:
        """Initialize request data."""
        return orjson.dumps(
            {
                "apiVersion": self.api_version,
                "context": self.context,
                "method": "getCurrentAngleOfIllumination",
                "params": {"lightID": self.light_id},
            }
        )


@dataclass
class GetCurrentAngleOfIlluminationResponse(ApiResponse[int]):
    """Response object for getting current angle of illumination."""

    api_version: str
    context: str
    method: str
    data: int
    # error: ErrorDataT | None = None

    @classmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Prepare API description dictionary."""
        data: GetAngleOfIlluminationResponseT = orjson.loads(bytes_data)
        return cls(
            api_version=data["apiVersion"],
            context=data["context"],
            method=data["method"],
            data=data["data"]["angleOfIllumination"],
        )


@dataclass
class SetLightSynchronizeDayNightModeRequest(ApiRequest):
    """Enable automatic synchronization with the day/night mode."""

    method = "post"
    path = "/axis-cgi/lightcontrol.cgi"
    content_type = "application/json"
    error_codes = general_error_codes

    light_id: str
    enabled: bool

    api_version: str = API_VERSION
    context: str = CONTEXT

    @property
    def content(self) -> bytes:
        """Initialize request data."""
        return orjson.dumps(
            {
                "apiVersion": self.api_version,
                "context": self.context,
                "method": "setLightSynchronizationDayNightMode",
                "params": {"lightID": self.light_id, "enabled": self.enabled},
            }
        )


@dataclass
class GetLightSynchronizeDayNightModeRequest(ApiRequest):
    """Request object for getting day night mode synchronization setting."""

    method = "post"
    path = "/axis-cgi/lightcontrol.cgi"
    content_type = "application/json"
    error_codes = general_error_codes

    light_id: str

    api_version: str = API_VERSION
    context: str = CONTEXT

    @property
    def content(self) -> bytes:
        """Initialize request data."""
        return orjson.dumps(
            {
                "apiVersion": self.api_version,
                "context": self.context,
                "method": "getLightSynchronizationDayNightMode",
                "params": {"lightID": self.light_id},
            }
        )


@dataclass
class GetLightSynchronizeDayNightModeResponse(ApiResponse[bool]):
    """Response object for getting day night mode synchronization setting."""

    api_version: str
    context: str
    method: str
    data: bool
    # error: ErrorDataT | None = None

    @classmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Prepare API description dictionary."""
        data: GetLightSynchronizationDayNightModeResponseT = orjson.loads(bytes_data)
        return cls(
            api_version=data["apiVersion"],
            context=data["context"],
            method=data["method"],
            data=data["data"]["synchronize"],
        )


@dataclass
class GetSupportedVersionsRequest(ApiRequest):
    """Request object for listing supported API versions."""

    method = "post"
    path = "/axis-cgi/lightcontrol.cgi"
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

    api_version: str
    context: str
    method: str
    data: list[str]
    # error: ErrorDataT | None = None

    @classmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Prepare API description dictionary."""
        data: GetSupportedVersionsResponseT = orjson.loads(bytes_data)
        return cls(
            api_version=data["apiVersion"],
            context=data["context"],
            method=data["method"],
            data=data.get("data", {}).get("apiVersions", []),
        )
