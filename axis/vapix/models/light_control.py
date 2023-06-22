"""Light Control API data model."""

from dataclasses import dataclass

import orjson
from typing_extensions import NotRequired, TypedDict

from .api import CONTEXT, APIItem, ApiItem, ApiRequest

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
    def from_dict(cls, data: LightInformationT) -> "LightInformation":
        """Create light information object from dict."""
        return LightInformation(
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
    def from_list(cls, data: list[LightInformationT]) -> dict[str, "LightInformation"]:
        """Create light information objects from list."""
        lights = [LightInformation.from_dict(item) for item in data]
        return {light.id: light for light in lights}


@dataclass
class GetLightInformation(ApiRequest[LightInformation]):
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

    def process_raw(self, raw: str) -> dict[str, LightInformation]:
        """Prepare light information dictionary."""
        data: GetLightInformationResponseT = orjson.loads(raw)
        return LightInformation.from_list(data["data"]["items"])


class Light(APIItem):
    """API Discovery item."""

    @property
    def light_id(self) -> str:
        """Id of light."""
        return self.raw["lightID"]

    @property
    def light_type(self) -> str:
        """Type of light."""
        return self.raw["lightType"]

    @property
    def enabled(self) -> bool:
        """Is light enabled."""
        return self.raw["enabled"]

    @property
    def synchronize_day_night_mode(self) -> bool:
        """Will synchronize with day night mode."""
        return self.raw["synchronizeDayNightMode"]

    @property
    def light_state(self) -> bool:
        """State of light."""
        return self.raw["lightState"]

    @property
    def automatic_intensity_mode(self) -> bool:
        """Automatic intensity mode."""
        return self.raw["automaticIntensityMode"]

    @property
    def automatic_angle_of_illumination_mode(self) -> bool:
        """Automatic angle of illumination mode."""
        return self.raw["automaticAngleOfIlluminationMode"]

    @property
    def number_of_leds(self) -> int:
        """Amount of LEDs."""
        return self.raw["nrOfLEDs"]

    @property
    def error(self) -> bool:
        """Error."""
        return self.raw["error"]

    @property
    def error_info(self) -> str:
        """Error info."""
        return self.raw["errorInfo"]
