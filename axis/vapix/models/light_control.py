"""Light Control API data model."""

from .api import APIItem


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
