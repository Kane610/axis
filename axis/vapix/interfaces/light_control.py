"""Light Control API.

The Axis Light control API makes it possible to control the behavior and functionality
of IR and White light LEDs in the Axis devices
"""

import attr

from ..models.light_control import Light
from .api import APIItems, Body

URL = "/axis-cgi/lightcontrol.cgi"

API_DISCOVERY_ID = "light-control"
API_VERSION = "1.1"


class LightControl(APIItems):
    """Light control for Axis devices."""

    item_cls = Light
    path = URL

    async def update(self) -> None:
        """Refresh data."""
        raw = await self.get_light_information()
        self.process_raw(raw)

    @staticmethod
    def pre_process_raw(raw: dict) -> dict:
        """Return a dictionary of lights."""
        light_control_data = raw.get("data", {}).get("items", [])
        return {api["lightID"]: api for api in light_control_data}

    async def get_service_capabilities(self) -> dict:
        """List the capabilities of the light controller."""
        return await self.vapix.request(
            "post",
            URL,
            json=attr.asdict(
                Body("getServiceCapabilities", API_VERSION),
                filter=attr.filters.exclude(attr.fields(Body).params),
            ),
        )

    async def get_light_information(self) -> dict:
        """List the light control information."""
        return await self.vapix.request(
            "post",
            URL,
            json=attr.asdict(
                Body("getLightInformation", API_VERSION),
                filter=attr.filters.exclude(attr.fields(Body).params),
            ),
        )

    async def activate_light(self, light_id: str) -> None:
        """Activate the light."""
        await self.vapix.request(
            "post",
            URL,
            json=attr.asdict(
                Body("activateLight", API_VERSION, params={"lightID": light_id})
            ),
        )

    async def deactivate_light(self, light_id: str) -> None:
        """Deactivate the light."""
        await self.vapix.request(
            "post",
            URL,
            json=attr.asdict(
                Body("deactivateLight", API_VERSION, params={"lightID": light_id})
            ),
        )

    async def enable_light(self, light_id: str) -> None:
        """Enable the light functionality."""
        await self.vapix.request(
            "post",
            URL,
            json=attr.asdict(
                Body("enableLight", API_VERSION, params={"lightID": light_id})
            ),
        )

    async def disable_light(self, light_id: str) -> None:
        """Disable the light functionality."""
        await self.vapix.request(
            "post",
            URL,
            json=attr.asdict(
                Body("disableLight", API_VERSION, params={"lightID": light_id})
            ),
        )

    async def get_light_status(self, light_id: str) -> dict:
        """List the light control information."""
        return await self.vapix.request(
            "post",
            URL,
            json=attr.asdict(
                Body("getLightStatus", API_VERSION, params={"lightID": light_id}),
            ),
        )

    async def set_automatic_intensity_mode(self, light_id: str, enabled: bool) -> dict:
        """Enable the automatic light intensity control."""
        return await self.vapix.request(
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

    async def get_valid_intensity(self, light_id: str) -> dict:
        """List the valid light intensity values."""
        return await self.vapix.request(
            "post",
            URL,
            json=attr.asdict(
                Body("getValidIntensity", API_VERSION, params={"lightID": light_id}),
            ),
        )

    async def set_manual_intensity(self, light_id: str, intensity: int) -> dict:
        """Manually sets the intensity."""
        return await self.vapix.request(
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

    async def get_manual_intensity(self, light_id: str) -> dict:
        """Receives the intensity from the setManualIntensity request."""
        return await self.vapix.request(
            "post",
            URL,
            json=attr.asdict(
                Body("getManualIntensity", API_VERSION, params={"lightID": light_id}),
            ),
        )

    async def set_individual_intensity(
        self, light_id: str, led_id: int, intensity: int
    ) -> None:
        """Manually sets the intensity for an individual LED."""
        return await self.vapix.request(
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

    async def get_individual_intensity(self, light_id: str, led_id: int) -> dict:
        """Receives the intensity from the setIndividualIntensity request."""
        return await self.vapix.request(
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

    async def get_current_intensity(self, light_id: str) -> dict:
        """Receives the current intensity."""
        return await self.vapix.request(
            "post",
            URL,
            json=attr.asdict(
                Body("getCurrentIntensity", API_VERSION, params={"lightID": light_id}),
            ),
        )

    async def set_automatic_angle_of_illumination_mode(
        self, light_id: str, enabled: bool
    ) -> None:
        """Automatically control the angle of illumination.

        Using this mode means that the angle of illumination is the same as the camera’s angle of view.
        """
        return await self.vapix.request(
            "post",
            URL,
            json=attr.asdict(
                Body(
                    "setAutomaticAngleOfIlluminationMode",
                    API_VERSION,
                    params={"lightID": light_id, "enabled": enabled},
                ),
            ),
        )

    async def get_valid_angle_of_illumination(self, light_id: str) -> dict:
        """List the valid angle of illumination values."""
        return await self.vapix.request(
            "post",
            URL,
            json=attr.asdict(
                Body(
                    "getValidAngleOfIllumination",
                    API_VERSION,
                    params={"lightID": light_id},
                ),
            ),
        )

    async def set_manual_angle_of_illumination(
        self, light_id: str, angle_of_illumination: int
    ) -> None:
        """Set the manual angle of illumination.

        This is useful when the angle of illumination needs to be different from the camera’s view angle.
        """
        await self.vapix.request(
            "post",
            URL,
            json=attr.asdict(
                Body(
                    "setManualAngleOfIllumination",
                    API_VERSION,
                    params={
                        "lightID": light_id,
                        "angleOfIllumination": angle_of_illumination,
                    },
                ),
            ),
        )

    async def get_manual_angle_of_illumination(self, light_id: str) -> dict:
        """Receive the angle of illumination from the setManualAngleOfIllumination request."""
        return await self.vapix.request(
            "post",
            URL,
            json=attr.asdict(
                Body(
                    "getManualAngleOfIllumination",
                    API_VERSION,
                    params={"lightID": light_id},
                ),
            ),
        )

    async def get_current_angle_of_illumination(self, light_id: str) -> dict:
        """Receive the current angle of illumination."""
        return await self.vapix.request(
            "post",
            URL,
            json=attr.asdict(
                Body(
                    "getCurrentAngleOfIllumination",
                    API_VERSION,
                    params={"lightID": light_id},
                ),
            ),
        )

    async def set_light_synchronization_day_night_mode(
        self, light_id: str, enabled: bool
    ) -> None:
        """Enable automatic synchronization with the day/night mode."""
        return await self.vapix.request(
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

    async def get_light_synchronization_day_night_mode(self, light_id: str) -> dict:
        """Check if the automatic synchronization is enabled with the day/night mode."""
        return await self.vapix.request(
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

    async def get_supported_versions(self) -> dict:
        """Supported versions of light control."""
        return await self.vapix.request(
            "post",
            URL,
            json=attr.asdict(
                Body("getSupportedVersions", API_VERSION),
                filter=attr.filters.include(attr.fields(Body).method),
            ),
        )
