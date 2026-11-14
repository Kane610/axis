"""Models for the VAPIX Light Control API and controllable illuminators."""

from dataclasses import dataclass
from typing import NotRequired, Self, TypedDict

import orjson

from .api import CONTEXT, ApiItem, ApiRequest, ApiResponse, BytesResponse

API_VERSION = "1.1"


class ErrorDataT(TypedDict):
    """Error code and message returned by the Light Control API."""

    code: int
    message: str


class LightInformationT(TypedDict):
    """State, capabilities, LED count, and error details for one light."""

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
    """Light entries returned by getLightInformation."""

    items: list[LightInformationT]


class GetLightInformationResponseT(TypedDict):
    """JSON envelope returned by getLightInformation."""

    apiVersion: str
    context: str
    method: str
    data: LightInformationItemsT
    error: NotRequired[ErrorDataT]


class ServiceCapabilitiesT(TypedDict):
    """Whether the device supports each Light Control operation."""

    automaticIntensitySupport: bool
    manualIntensitySupport: bool
    getCurrentIntensitySupport: bool
    individualIntensitySupport: bool
    automaticAngleOfIlluminationSupport: bool
    manualAngleOfIlluminationSupport: bool
    dayNightSynchronizeSupport: bool


class GetServiceCapabilitiesResponseT(TypedDict):
    """JSON envelope returned by getServiceCapabilities."""

    apiVersion: str
    context: str
    method: str
    data: ServiceCapabilitiesT
    error: NotRequired[ErrorDataT]


class LightStatusT(TypedDict):
    """Enabled state returned for a light."""

    status: bool


class GetLightStatusResponseT(TypedDict):
    """JSON envelope returned by getLightStatus."""

    apiVersion: str
    context: str
    method: str
    data: LightStatusT
    error: NotRequired[ErrorDataT]


class RangeT(TypedDict):
    """Inclusive low and high values for an intensity or angle setting."""

    low: int
    high: int


class ValidRangesT(TypedDict):
    """Supported value ranges returned by a Light Control query."""

    ranges: list[RangeT]


class GetValidRangesResponseT(TypedDict):
    """JSON envelope containing one or more supported value ranges."""

    apiVersion: str
    context: str
    method: str
    data: ValidRangesT
    error: NotRequired[ErrorDataT]


class IntensityT(TypedDict):
    """Intensity value returned by the API."""

    intensity: int


class GetIntensityResponseT(TypedDict):
    """JSON envelope returned by an intensity query."""

    apiVersion: str
    context: str
    method: str
    data: IntensityT
    error: NotRequired[ErrorDataT]


class AngleOfIlluminationT(TypedDict):
    """Angle-of-illumination value returned by the API."""

    angleOfIllumination: int


class GetAngleOfIlluminationResponseT(TypedDict):
    """JSON envelope returned by an angle-of-illumination query."""

    apiVersion: str
    context: str
    method: str
    data: AngleOfIlluminationT
    error: NotRequired[ErrorDataT]


class SynchronizeT(TypedDict):
    """Whether this light follows the camera's day/night mode."""

    synchronize: bool


class GetLightSynchronizationDayNightModeResponseT(TypedDict):
    """JSON envelope returned by the day/night synchronization query."""

    apiVersion: str
    context: str
    method: str
    data: SynchronizeT
    error: NotRequired[ErrorDataT]


class ApiVersionsT(TypedDict):
    """Light Control API versions supported by the device."""

    apiVersions: list[str]


class GetSupportedVersionsResponseT(TypedDict):
    """JSON envelope returned by getSupportedVersions."""

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
    """One light's enabled state, hardware type, modes, and reported errors."""

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
        """Convert one getLightInformation entry into a light model."""
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
    """Lowest and highest supported values for a light setting."""

    low: int
    high: int

    @classmethod
    def from_dict(cls, data: RangeT) -> Self:
        """Convert an API low/high pair into a Range model."""
        return cls(low=data["low"], high=data["high"])

    @classmethod
    def from_list(cls, data: list[RangeT]) -> list[Self]:
        """Convert each API low/high pair in a list into a Range model."""
        return [cls.from_dict(range) for range in data]


@dataclass
class GetLightInformationResponse(ApiResponse[dict[str, LightInformation]]):
    """Available lights indexed by their device-assigned IDs."""

    api_version: str
    context: str
    method: str
    data: dict[str, LightInformation]
    # error: ErrorDataT | None = None

    @classmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Parse the response and index decoded lights by ID."""
        data: GetLightInformationResponseT = orjson.loads(bytes_data)
        return cls(
            api_version=data["apiVersion"],
            context=data["context"],
            method=data["method"],
            data=LightInformation.decode_to_dict(data.get("data", {}).get("items", [])),
        )


@dataclass
class GetLightInformationRequest(ApiRequest[GetLightInformationResponse]):
    """Request the device's light inventory and each light's current settings."""

    method = "post"
    path = "/axis-cgi/lightcontrol.cgi"
    content_type = "application/json"
    response_type = GetLightInformationResponse
    error_codes = general_error_codes

    api_version: str = API_VERSION
    context: str = CONTEXT

    @property
    def content(self) -> bytes:
        """Encode a getLightInformation request as JSON."""
        return orjson.dumps(
            {
                "apiVersion": self.api_version,
                "context": self.context,
                "method": "getLightInformation",
            }
        )


@dataclass
class ServiceCapabilities:
    """Light Control operations supported by the device."""

    automatic_intensity_support: bool
    manual_intensity_support: bool
    get_current_intensity_support: bool
    individual_intensity_support: bool
    automatic_angle_of_illumination_support: bool
    manual_angle_of_illumination_support: bool
    day_night_synchronize_support: bool

    @classmethod
    def from_dict(cls, data: ServiceCapabilitiesT) -> Self:
        """Convert the API capability flags into a ServiceCapabilities model."""
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
class GetServiceCapabilitiesResponse(ApiResponse[ServiceCapabilities]):
    """Supported Light Control operations reported by the device."""

    api_version: str
    context: str
    method: str
    data: ServiceCapabilities
    # error: ErrorDataT | None = None

    @classmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Parse the capability flags from the response envelope."""
        data: GetServiceCapabilitiesResponseT = orjson.loads(bytes_data)
        return cls(
            api_version=data["apiVersion"],
            context=data["context"],
            method=data["method"],
            data=ServiceCapabilities.from_dict(data["data"]),
        )


@dataclass
class GetServiceCapabilitiesRequest(ApiRequest[GetServiceCapabilitiesResponse]):
    """Request the Light Control operations supported by the device."""

    method = "post"
    path = "/axis-cgi/lightcontrol.cgi"
    content_type = "application/json"
    response_type = GetServiceCapabilitiesResponse
    error_codes = general_error_codes

    api_version: str = API_VERSION
    context: str = CONTEXT

    @property
    def content(self) -> bytes:
        """Encode a getServiceCapabilities request as JSON."""
        return orjson.dumps(
            {
                "apiVersion": self.api_version,
                "context": self.context,
                "method": "getServiceCapabilities",
            }
        )


@dataclass
class ActivateLightRequest(ApiRequest[ApiResponse[bytes]]):
    """Activate a light by its device-assigned ID."""

    method = "post"
    path = "/axis-cgi/lightcontrol.cgi"
    content_type = "application/json"
    response_type = BytesResponse
    error_codes = general_error_codes

    light_id: str

    api_version: str = API_VERSION
    context: str = CONTEXT

    @property
    def content(self) -> bytes:
        """Encode an activateLight request for this light ID."""
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
    """Deactivate a light by its device-assigned ID."""

    @property
    def content(self) -> bytes:
        """Encode a deactivateLight request for this light ID."""
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
    """Enable a light so it can be controlled."""

    @property
    def content(self) -> bytes:
        """Encode an enableLight request for this light ID."""
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
    """Disable a light so it cannot be activated."""

    @property
    def content(self) -> bytes:
        """Encode a disableLight request for this light ID."""
        return orjson.dumps(
            {
                "apiVersion": self.api_version,
                "context": self.context,
                "method": "disableLight",
                "params": {"lightID": self.light_id},
            }
        )


@dataclass
class GetLightStatusResponse(ApiResponse[bool]):
    """Enabled or disabled state reported for the requested light."""

    api_version: str
    context: str
    method: str
    data: bool
    # error: ErrorDataT | None = None

    @classmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Extract the light's boolean status from the response envelope."""
        data: GetLightStatusResponseT = orjson.loads(bytes_data)
        return cls(
            api_version=data["apiVersion"],
            context=data["context"],
            method=data["method"],
            data=data["data"]["status"],
        )


@dataclass
class GetLightStatusRequest(ApiRequest[GetLightStatusResponse]):
    """Request the enabled state of one light."""

    method = "post"
    path = "/axis-cgi/lightcontrol.cgi"
    content_type = "application/json"
    response_type = GetLightStatusResponse
    error_codes = general_error_codes

    light_id: str

    api_version: str = API_VERSION
    context: str = CONTEXT

    @property
    def content(self) -> bytes:
        """Encode a getLightStatus request for this light ID."""
        return orjson.dumps(
            {
                "apiVersion": self.api_version,
                "context": self.context,
                "method": "getLightStatus",
                "params": {"lightID": self.light_id},
            }
        )


@dataclass
class SetAutomaticIntensityModeRequest(ApiRequest[ApiResponse[bytes]]):
    """Enable or disable automatic intensity adjustment for one light."""

    method = "post"
    path = "/axis-cgi/lightcontrol.cgi"
    content_type = "application/json"
    response_type = BytesResponse
    error_codes = general_error_codes

    light_id: str
    enabled: bool

    api_version: str = API_VERSION
    context: str = CONTEXT

    @property
    def content(self) -> bytes:
        """Encode the automatic-intensity setting for this light."""
        return orjson.dumps(
            {
                "apiVersion": self.api_version,
                "context": self.context,
                "method": "setAutomaticIntensityMode",
                "params": {"lightID": self.light_id, "enabled": self.enabled},
            }
        )


@dataclass
class GetValidIntensityResponse(ApiResponse[Range]):
    """Supported intensity range reported for a light."""

    api_version: str
    context: str
    method: str
    data: Range
    # error: ErrorDataT | None = None

    @classmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Extract the first supported intensity range from the response."""
        data: GetValidRangesResponseT = orjson.loads(bytes_data)
        return cls(
            api_version=data["apiVersion"],
            context=data["context"],
            method=data["method"],
            data=Range.from_dict(data["data"]["ranges"][0]),
        )


@dataclass
class GetValidIntensityRequest(ApiRequest[GetValidIntensityResponse]):
    """Request the intensity range accepted by one light."""

    method = "post"
    path = "/axis-cgi/lightcontrol.cgi"
    content_type = "application/json"
    response_type = GetValidIntensityResponse
    error_codes = general_error_codes

    light_id: str

    api_version: str = API_VERSION
    context: str = CONTEXT

    @property
    def content(self) -> bytes:
        """Encode a getValidIntensity request for this light ID."""
        return orjson.dumps(
            {
                "apiVersion": self.api_version,
                "context": self.context,
                "method": "getValidIntensity",
                "params": {"lightID": self.light_id},
            }
        )


@dataclass
class SetManualIntensityRequest(ApiRequest[ApiResponse[bytes]]):
    """Set a light's manually controlled intensity."""

    method = "post"
    path = "/axis-cgi/lightcontrol.cgi"
    content_type = "application/json"
    response_type = BytesResponse
    error_codes = general_error_codes

    light_id: str
    intensity: int

    api_version: str = API_VERSION
    context: str = CONTEXT

    @property
    def content(self) -> bytes:
        """Encode the requested manual intensity for this light."""
        return orjson.dumps(
            {
                "apiVersion": self.api_version,
                "context": self.context,
                "method": "setManualIntensity",
                "params": {"lightID": self.light_id, "intensity": self.intensity},
            }
        )


@dataclass
class GetManualIntensityResponse(ApiResponse[int]):
    """Manual intensity value currently configured for a light."""

    api_version: str
    context: str
    method: str
    data: int
    # error: ErrorDataT | None = None

    @classmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Extract the intensity value from the response envelope."""
        data: GetIntensityResponseT = orjson.loads(bytes_data)
        return cls(
            api_version=data["apiVersion"],
            context=data["context"],
            method=data["method"],
            data=data["data"]["intensity"],
        )


@dataclass
class GetManualIntensityRequest(ApiRequest[GetManualIntensityResponse]):
    """Request the manually configured intensity for one light."""

    method = "post"
    path = "/axis-cgi/lightcontrol.cgi"
    content_type = "application/json"
    response_type = GetManualIntensityResponse
    error_codes = general_error_codes

    light_id: str

    api_version: str = API_VERSION
    context: str = CONTEXT

    @property
    def content(self) -> bytes:
        """Encode a getManualIntensity request for this light ID."""
        return orjson.dumps(
            {
                "apiVersion": self.api_version,
                "context": self.context,
                "method": "getManualIntensity",
                "params": {"lightID": self.light_id},
            }
        )


@dataclass
class SetIndividualIntensityRequest(ApiRequest[ApiResponse[bytes]]):
    """Set the intensity of one LED within a light."""

    method = "post"
    path = "/axis-cgi/lightcontrol.cgi"
    content_type = "application/json"
    response_type = BytesResponse
    error_codes = general_error_codes

    light_id: str
    led_id: int
    intensity: int

    api_version: str = API_VERSION
    context: str = CONTEXT

    @property
    def content(self) -> bytes:
        """Encode the LED ID and requested intensity for this light."""
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
class GetIndividualIntensityResponse(ApiResponse[int]):
    """Intensity value reported for one LED."""

    api_version: str
    context: str
    method: str
    data: int
    # error: ErrorDataT | None = None

    @classmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Extract the LED intensity value from the response envelope."""
        data: GetIntensityResponseT = orjson.loads(bytes_data)
        return cls(
            api_version=data["apiVersion"],
            context=data["context"],
            method=data["method"],
            data=data["data"]["intensity"],
        )


@dataclass
class GetIndividualIntensityRequest(ApiRequest[GetIndividualIntensityResponse]):
    """Request the intensity of one LED within a light."""

    method = "post"
    path = "/axis-cgi/lightcontrol.cgi"
    content_type = "application/json"
    response_type = GetIndividualIntensityResponse
    error_codes = general_error_codes

    light_id: str
    led_id: int

    api_version: str = API_VERSION
    context: str = CONTEXT

    @property
    def content(self) -> bytes:
        """Encode the light and LED IDs in a getIndividualIntensity request."""
        return orjson.dumps(
            {
                "apiVersion": self.api_version,
                "context": self.context,
                "method": "getIndividualIntensity",
                "params": {"lightID": self.light_id, "LEDID": self.led_id},
            }
        )


@dataclass
class GetCurrentIntensityResponse(ApiResponse[int]):
    """Current intensity value reported for a light."""

    api_version: str
    context: str
    method: str
    data: int
    # error: ErrorDataT | None = None

    @classmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Extract the current intensity value from the response envelope."""
        data: GetIntensityResponseT = orjson.loads(bytes_data)
        return cls(
            api_version=data["apiVersion"],
            context=data["context"],
            method=data["method"],
            data=data["data"]["intensity"],
        )


@dataclass
class GetCurrentIntensityRequest(ApiRequest[GetCurrentIntensityResponse]):
    """Request the current intensity of one light."""

    method = "post"
    path = "/axis-cgi/lightcontrol.cgi"
    content_type = "application/json"
    response_type = GetCurrentIntensityResponse
    error_codes = general_error_codes

    light_id: str

    api_version: str = API_VERSION
    context: str = CONTEXT

    @property
    def content(self) -> bytes:
        """Encode a getCurrentIntensity request for this light ID."""
        return orjson.dumps(
            {
                "apiVersion": self.api_version,
                "context": self.context,
                "method": "getCurrentIntensity",
                "params": {"lightID": self.light_id},
            }
        )


@dataclass
class SetAutomaticAngleOfIlluminationModeRequest(ApiRequest[ApiResponse[bytes]]):
    """Enable or disable automatic angle adjustment for one light."""

    method = "post"
    path = "/axis-cgi/lightcontrol.cgi"
    content_type = "application/json"
    response_type = BytesResponse
    error_codes = general_error_codes

    light_id: str
    enabled: bool

    api_version: str = API_VERSION
    context: str = CONTEXT

    @property
    def content(self) -> bytes:
        """Encode the automatic-angle setting for this light."""
        return orjson.dumps(
            {
                "apiVersion": self.api_version,
                "context": self.context,
                "method": "setAutomaticAngleOfIlluminationMode",
                "params": {"lightID": self.light_id, "enabled": self.enabled},
            }
        )


@dataclass
class GetValidAngleOfIlluminationResponse(ApiResponse[list[Range]]):
    """Supported angle-of-illumination ranges reported for a light."""

    api_version: str
    context: str
    method: str
    data: list[Range]
    # error: ErrorDataT | None = None

    @classmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Convert each supported angle range in the response to a Range model."""
        data: GetValidRangesResponseT = orjson.loads(bytes_data)
        return cls(
            api_version=data["apiVersion"],
            context=data["context"],
            method=data["method"],
            data=Range.from_list(data["data"]["ranges"]),
        )


@dataclass
class GetValidAngleOfIlluminationRequest(
    ApiRequest[GetValidAngleOfIlluminationResponse]
):
    """Request the angle-of-illumination ranges accepted by one light."""

    method = "post"
    path = "/axis-cgi/lightcontrol.cgi"
    content_type = "application/json"
    response_type = GetValidAngleOfIlluminationResponse
    error_codes = general_error_codes

    light_id: str

    api_version: str = API_VERSION
    context: str = CONTEXT

    @property
    def content(self) -> bytes:
        """Encode a getValidAngleOfIllumination request for this light ID."""
        return orjson.dumps(
            {
                "apiVersion": self.api_version,
                "context": self.context,
                "method": "getValidAngleOfIllumination",
                "params": {"lightID": self.light_id},
            }
        )


@dataclass
class SetManualAngleOfIlluminationModeRequest(ApiRequest[ApiResponse[bytes]]):
    """Set a light's manually controlled angle of illumination."""

    method = "post"
    path = "/axis-cgi/lightcontrol.cgi"
    content_type = "application/json"
    response_type = BytesResponse
    error_codes = general_error_codes

    light_id: str
    angle_of_illumination: int

    api_version: str = API_VERSION
    context: str = CONTEXT

    @property
    def content(self) -> bytes:
        """Encode the requested manual angle for this light."""
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
class GetManualAngleOfIlluminationResponse(ApiResponse[int]):
    """Manually configured angle of illumination reported for a light."""

    api_version: str
    context: str
    method: str
    data: int
    # error: ErrorDataT | None = None

    @classmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Extract the configured angle from the response envelope."""
        data: GetAngleOfIlluminationResponseT = orjson.loads(bytes_data)
        return cls(
            api_version=data["apiVersion"],
            context=data["context"],
            method=data["method"],
            data=data["data"]["angleOfIllumination"],
        )


@dataclass
class GetManualAngleOfIlluminationRequest(
    ApiRequest[GetManualAngleOfIlluminationResponse]
):
    """Request the manually configured angle of one light."""

    method = "post"
    path = "/axis-cgi/lightcontrol.cgi"
    content_type = "application/json"
    response_type = GetManualAngleOfIlluminationResponse
    error_codes = general_error_codes

    light_id: str

    api_version: str = API_VERSION
    context: str = CONTEXT

    @property
    def content(self) -> bytes:
        """Encode a getManualAngleOfIllumination request for this light ID."""
        return orjson.dumps(
            {
                "apiVersion": self.api_version,
                "context": self.context,
                "method": "getManualAngleOfIllumination",
                "params": {"lightID": self.light_id},
            }
        )


@dataclass
class GetCurrentAngleOfIlluminationResponse(ApiResponse[int]):
    """Current angle of illumination reported for a light."""

    api_version: str
    context: str
    method: str
    data: int
    # error: ErrorDataT | None = None

    @classmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Extract the current angle from the response envelope."""
        data: GetAngleOfIlluminationResponseT = orjson.loads(bytes_data)
        return cls(
            api_version=data["apiVersion"],
            context=data["context"],
            method=data["method"],
            data=data["data"]["angleOfIllumination"],
        )


@dataclass
class GetCurrentAngleOfIlluminationRequest(
    ApiRequest[GetCurrentAngleOfIlluminationResponse]
):
    """Request the current angle of illumination for one light."""

    method = "post"
    path = "/axis-cgi/lightcontrol.cgi"
    content_type = "application/json"
    response_type = GetCurrentAngleOfIlluminationResponse
    error_codes = general_error_codes

    light_id: str

    api_version: str = API_VERSION
    context: str = CONTEXT

    @property
    def content(self) -> bytes:
        """Encode a getCurrentAngleOfIllumination request for this light ID."""
        return orjson.dumps(
            {
                "apiVersion": self.api_version,
                "context": self.context,
                "method": "getCurrentAngleOfIllumination",
                "params": {"lightID": self.light_id},
            }
        )


@dataclass
class SetLightSynchronizeDayNightModeRequest(ApiRequest[ApiResponse[bytes]]):
    """Enable or disable synchronization with the camera's day/night mode."""

    method = "post"
    path = "/axis-cgi/lightcontrol.cgi"
    content_type = "application/json"
    response_type = BytesResponse
    error_codes = general_error_codes

    light_id: str
    enabled: bool

    api_version: str = API_VERSION
    context: str = CONTEXT

    @property
    def content(self) -> bytes:
        """Encode the day/night synchronization setting for this light."""
        return orjson.dumps(
            {
                "apiVersion": self.api_version,
                "context": self.context,
                "method": "setLightSynchronizationDayNightMode",
                "params": {"lightID": self.light_id, "enabled": self.enabled},
            }
        )


@dataclass
class GetLightSynchronizeDayNightModeResponse(ApiResponse[bool]):
    """Whether a light follows the camera's day/night mode."""

    api_version: str
    context: str
    method: str
    data: bool
    # error: ErrorDataT | None = None

    @classmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Extract the synchronization setting from the response envelope."""
        data: GetLightSynchronizationDayNightModeResponseT = orjson.loads(bytes_data)
        return cls(
            api_version=data["apiVersion"],
            context=data["context"],
            method=data["method"],
            data=data["data"]["synchronize"],
        )


@dataclass
class GetLightSynchronizeDayNightModeRequest(
    ApiRequest[GetLightSynchronizeDayNightModeResponse]
):
    """Request whether one light follows the camera's day/night mode."""

    method = "post"
    path = "/axis-cgi/lightcontrol.cgi"
    content_type = "application/json"
    response_type = GetLightSynchronizeDayNightModeResponse
    error_codes = general_error_codes

    light_id: str

    api_version: str = API_VERSION
    context: str = CONTEXT

    @property
    def content(self) -> bytes:
        """Encode a day/night synchronization query for this light ID."""
        return orjson.dumps(
            {
                "apiVersion": self.api_version,
                "context": self.context,
                "method": "getLightSynchronizationDayNightMode",
                "params": {"lightID": self.light_id},
            }
        )


@dataclass
class GetSupportedVersionsResponse(ApiResponse[list[str]]):
    """Light Control API versions supported by the device."""

    api_version: str
    context: str
    method: str
    data: list[str]
    # error: ErrorDataT | None = None

    @classmethod
    def decode(cls, bytes_data: bytes) -> Self:
        """Parse the supported-version list from the response envelope."""
        data: GetSupportedVersionsResponseT = orjson.loads(bytes_data)
        return cls(
            api_version=data["apiVersion"],
            context=data["context"],
            method=data["method"],
            data=data.get("data", {}).get("apiVersions", []),
        )


@dataclass
class GetSupportedVersionsRequest(ApiRequest[GetSupportedVersionsResponse]):
    """Request the Light Control API versions supported by the device."""

    method = "post"
    path = "/axis-cgi/lightcontrol.cgi"
    content_type = "application/json"
    response_type = GetSupportedVersionsResponse
    error_codes = general_error_codes

    context: str = CONTEXT

    @property
    def content(self) -> bytes:
        """Encode a getSupportedVersions request as JSON."""
        return orjson.dumps(
            {
                "context": self.context,
                "method": "getSupportedVersions",
            }
        )
