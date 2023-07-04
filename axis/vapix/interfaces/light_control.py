"""Light Control API.

The Axis Light control API makes it possible to control the behavior
and functionality of IR and White light LEDs in the Axis devices.
"""


from ..models.api_discovery import ApiId
from ..models.light_control import (
    API_VERSION,
    ActivateLightRequest,
    DeactivateLightRequest,
    DisableLightRequest,
    EnableLightRequest,
    GetCurrentAngleOfIlluminationRequest,
    GetCurrentIntensityRequest,
    GetIndividualIntensityRequest,
    GetLightInformation,
    GetLightStatusRequest,
    GetLightSynchronizeDayNightModeRequest,
    GetManualAngleOfIlluminationRequest,
    GetManualIntensityRequest,
    GetServiceCapabilities,
    GetSupportedVersionsRequest,
    GetValidAngleOfIllumination,
    GetValidIntensityRequest,
    LightInformation,
    Range,
    ServiceCapabilities,
    SetAutomaticAngleOfIlluminationModeRequest,
    SetAutomaticIntensityModeRequest,
    SetIndividualIntensityRequest,
    SetLightSynchronizeDayNightModeRequest,
    SetManualAngleOfIlluminationModeRequest,
    SetManualIntensityRequest,
)
from .api_handler import ApiHandler


class LightHandler(ApiHandler[LightInformation]):
    """Light control for Axis devices."""

    api_id = ApiId.LIGHT_CONTROL
    api_request = GetLightInformation()
    default_api_version = API_VERSION

    async def get_light_information(self) -> dict[str, LightInformation]:
        """List the light control information."""
        api_version = self.api_version() or self.default_api_version
        return await self.vapix.request2(GetLightInformation(api_version))

    async def get_service_capabilities(self) -> ServiceCapabilities:
        """List the light control information."""
        api_version = self.api_version() or self.default_api_version
        return await self.vapix.request2(GetServiceCapabilities(api_version))

    async def activate_light(self, light_id: str) -> None:
        """Activate the light."""
        api_version = self.api_version() or self.default_api_version
        return await self.vapix.request2(
            ActivateLightRequest(api_version, light_id=light_id)
        )

    async def deactivate_light(self, light_id: str) -> None:
        """Deactivate the light."""
        api_version = self.api_version() or self.default_api_version
        return await self.vapix.request2(
            DeactivateLightRequest(api_version, light_id=light_id)
        )

    async def enable_light(self, light_id: str) -> None:
        """Activate the light."""
        api_version = self.api_version() or self.default_api_version
        return await self.vapix.request2(
            EnableLightRequest(api_version, light_id=light_id)
        )

    async def disable_light(self, light_id: str) -> None:
        """Deactivate the light."""
        api_version = self.api_version() or self.default_api_version
        return await self.vapix.request2(
            DisableLightRequest(api_version, light_id=light_id)
        )

    async def get_light_status(self, light_id: str) -> bool:
        """Get light status if its on or off."""
        api_version = self.api_version() or self.default_api_version
        return await self.vapix.request2(
            GetLightStatusRequest(api_version, light_id=light_id)
        )

    async def set_automatic_intensity_mode(self, light_id: str, enabled: bool) -> None:
        """Enable the automatic light intensity control."""
        api_version = self.api_version() or self.default_api_version
        return await self.vapix.request2(
            SetAutomaticIntensityModeRequest(
                api_version,
                light_id=light_id,
                enabled=enabled,
            )
        )

    async def get_valid_intensity(self, light_id: str) -> Range:
        """Enable the automatic light intensity control."""
        api_version = self.api_version() or self.default_api_version
        return await self.vapix.request2(
            GetValidIntensityRequest(api_version, light_id=light_id)
        )

    async def set_manual_intensity(self, light_id: str, intensity: int) -> None:
        """Manually sets the intensity."""
        api_version = self.api_version() or self.default_api_version
        return await self.vapix.request2(
            SetManualIntensityRequest(
                api_version,
                light_id=light_id,
                intensity=intensity,
            )
        )

    async def get_manual_intensity(self, light_id: str) -> int:
        """Enable the automatic light intensity control."""
        api_version = self.api_version() or self.default_api_version
        return await self.vapix.request2(
            GetManualIntensityRequest(api_version, light_id=light_id)
        )

    async def set_individual_intensity(
        self, light_id: str, led_id: int, intensity: int
    ) -> None:
        """Manually sets the intensity for an individual LED."""
        api_version = self.api_version() or self.default_api_version
        return await self.vapix.request2(
            SetIndividualIntensityRequest(
                api_version,
                light_id=light_id,
                led_id=led_id,
                intensity=intensity,
            )
        )

    async def get_individual_intensity(self, light_id: str, led_id: int) -> int:
        """Receives the intensity from the setIndividualIntensity request."""
        api_version = self.api_version() or self.default_api_version
        return await self.vapix.request2(
            GetIndividualIntensityRequest(
                api_version,
                light_id=light_id,
                led_id=led_id,
            )
        )

    async def get_current_intensity(self, light_id: str) -> int:
        """Receives the intensity from the setIndividualIntensity request."""
        api_version = self.api_version() or self.default_api_version
        return await self.vapix.request2(
            GetCurrentIntensityRequest(api_version, light_id=light_id)
        )

    async def set_automatic_angle_of_illumination_mode(
        self, light_id: str, enabled: bool
    ) -> None:
        """Automatically control the angle of illumination.

        Using this mode means that the angle of illumination
        is the same as the camera’s angle of view.
        """
        api_version = self.api_version() or self.default_api_version
        return await self.vapix.request2(
            SetAutomaticAngleOfIlluminationModeRequest(
                api_version, light_id=light_id, enabled=enabled
            )
        )

    async def get_valid_angle_of_illumination(self, light_id: str) -> list[Range]:
        """List the valid angle of illumination values."""
        api_version = self.api_version() or self.default_api_version
        return await self.vapix.request2(
            GetValidAngleOfIllumination(api_version, light_id=light_id)
        )

    async def set_manual_angle_of_illumination(
        self, light_id: str, angle_of_illumination: int
    ) -> None:
        """Set the manual angle of illumination.

        This is useful when the angle of illumination needs
        to be different from the camera’s view angle.
        """
        api_version = self.api_version() or self.default_api_version
        return await self.vapix.request2(
            SetManualAngleOfIlluminationModeRequest(
                api_version,
                light_id=light_id,
                angle_of_illumination=angle_of_illumination,
            )
        )

    async def get_manual_angle_of_illumination(self, light_id: str) -> int:
        """Get the angle of illumination."""
        api_version = self.api_version() or self.default_api_version
        return await self.vapix.request2(
            GetManualAngleOfIlluminationRequest(api_version, light_id=light_id)
        )

    async def get_current_angle_of_illumination(self, light_id: str) -> int:
        """Receive the current angle of illumination."""
        api_version = self.api_version() or self.default_api_version
        return await self.vapix.request2(
            GetCurrentAngleOfIlluminationRequest(api_version, light_id=light_id)
        )

    async def set_light_synchronization_day_night_mode(
        self, light_id: str, enabled: bool
    ) -> None:
        """Enable automatic synchronization with the day/night mode."""
        api_version = self.api_version() or self.default_api_version
        return await self.vapix.request2(
            SetLightSynchronizeDayNightModeRequest(
                api_version, light_id=light_id, enabled=enabled
            )
        )

    async def get_light_synchronization_day_night_mode(self, light_id: str) -> bool:
        """Check if the automatic synchronization is enabled with the day/night mode."""
        api_version = self.api_version() or self.default_api_version
        return await self.vapix.request2(
            GetLightSynchronizeDayNightModeRequest(api_version, light_id=light_id)
        )

    async def get_supported_versions(self) -> list[str]:
        """List supported API versions."""
        return await self.vapix.request2(GetSupportedVersionsRequest())
