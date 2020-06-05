"""Light Control API.

The Axis Light control API makes it possible to control the behavior and functionality
of IR and White light LEDs in the Axis devices
"""

import attr

from .api import APIItem, APIItems, Body

URL = "/axis-cgi/lightcontrol.cgi"

API_DISCOVERY_ID = "light-control"
API_VERSION = "1.1"


class LightControl(APIItems):
    """Light control for Axis devices."""

    def __init__(self, raw: dict, request: object) -> None:
        super().__init__(raw, request, URL, APIItem)

    def get_service_capabilities(self) -> dict:
        """List the capabilities of the light controller."""
        return self._request(
            "post",
            URL,
            json=attr.asdict(
                Body("getServiceCapabilities", API_VERSION),
                filter=attr.filters.exclude(attr.fields(Body).params),
            ),
        )

    def get_light_information(self) -> dict:
        """List the light control information."""
        return self._request(
            "post",
            URL,
            json=attr.asdict(
                Body("getLightInformation", API_VERSION),
                filter=attr.filters.exclude(attr.fields(Body).params),
            ),
        )

    def activate_light(self, light_id: str) -> None:
        """Activate the light."""
        self._request(
            "post",
            URL,
            json=attr.asdict(
                Body("activateLight", API_VERSION, params={"lightID": light_id})
            ),
        )

    def deactivate_light(self, light_id: str) -> None:
        """Deactivate the light."""
        self._request(
            "post",
            URL,
            json=attr.asdict(
                Body("deactivateLight", API_VERSION, params={"lightID": light_id})
            ),
        )

    def enable_light(self, light_id: str) -> None:
        """Enable the light functionality."""
        self._request(
            "post",
            URL,
            json=attr.asdict(
                Body("enableLight", API_VERSION, params={"lightID": light_id})
            ),
        )

    def disable_light(self, light_id: str) -> None:
        """Disable the light functionality."""
        self._request(
            "post",
            URL,
            json=attr.asdict(
                Body("disableLight", API_VERSION, params={"lightID": light_id})
            ),
        )

    def get_light_status(self, light_id: str) -> dict:
        """List the light control information."""
        return self._request(
            "post",
            URL,
            json=attr.asdict(
                Body("getLightStatus", API_VERSION, params={"lightID": light_id}),
            ),
        )

    def set_automatic_intensity_mode(self, light_id: str, enabled: bool) -> dict:
        """Enable the automatic light intensity control."""
        return self._request(
            "post",
            URL,
            json=attr.asdict(
                Body(
                    "setAutomaticIntensityMode",
                    API_VERSION,
                    params={"lightID": light_id, "enabled": enabled},
                ),
            ),
        )

    def get_valid_intensity(self, light_id: str) -> dict:
        """List the valid light intensity values."""
        return self._request(
            "post",
            URL,
            json=attr.asdict(
                Body("getValidIntensity", API_VERSION, params={"lightID": light_id}),
            ),
        )

    def set_manual_intensity(self, light_id: str, intensity: int) -> dict:
        """Manually sets the intensity."""
        return self._request(
            "post",
            URL,
            json=attr.asdict(
                Body(
                    "setManualIntensity",
                    API_VERSION,
                    params={"lightID": light_id, "intensity": intensity},
                ),
            ),
        )

    def get_manual_intensity(self, light_id: str) -> dict:
        """Receives the intensity from the setManualIntensity request."""
        return self._request(
            "post",
            URL,
            json=attr.asdict(
                Body("getManualIntensity", API_VERSION, params={"lightID": light_id}),
            ),
        )

    def set_individual_intensity(
        self, light_id: str, led_id: int, intensity: int
    ) -> None:
        """Manually sets the intensity for an individual LED."""
        return self._request(
            "post",
            URL,
            json=attr.asdict(
                Body(
                    "setIndividualIntensity",
                    API_VERSION,
                    params={
                        "lightID": light_id,
                        "LEDID": led_id,
                        "intensity": intensity,
                    },
                ),
            ),
        )

    def get_individual_intensity(self, light_id: str, led_id: int) -> dict:
        """Receives the intensity from the setIndividualIntensity request."""
        return self._request(
            "post",
            URL,
            json=attr.asdict(
                Body(
                    "getIndividualIntensity",
                    API_VERSION,
                    params={"lightID": light_id, "LEDID": led_id},
                ),
            ),
        )

    def get_current_intensity(self, light_id: str) -> dict:
        """Receives the current intensity."""
        return self._request(
            "post",
            URL,
            json=attr.asdict(
                Body("getCurrentIntensity", API_VERSION, params={"lightID": light_id}),
            ),
        )

    def set_light_synchronization_day_night_mode(
        self, light_id: str, enabled: bool
    ) -> None:
        """Enable automatic synchronization with the day/night mode."""
        return self._request(
            "post",
            URL,
            json=attr.asdict(
                Body(
                    "setLightSynchronizationDayNightMode",
                    API_VERSION,
                    params={"lightID": light_id, "enabled": enabled},
                ),
            ),
        )

    def get_light_synchronization_day_night_mode(self, light_id: str) -> dict:
        """Check if the automatic synchronization is enabled with the day/night mode."""
        return self._request(
            "post",
            URL,
            json=attr.asdict(
                Body(
                    "getLightSynchronizationDayNightMode",
                    API_VERSION,
                    params={"lightID": light_id},
                ),
            ),
        )

    def get_supported_versions(self) -> dict:
        """Supported versions of light control."""
        return self._request(
            "post",
            URL,
            json=attr.asdict(
                Body("getSupportedVersions", API_VERSION),
                filter=attr.filters.include(attr.fields(Body).method),
            ),
        )
