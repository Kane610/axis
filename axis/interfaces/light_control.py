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
    GetCurrentAngleOfIlluminationResponse,
    GetCurrentIntensityRequest,
    GetCurrentIntensityResponse,
    GetIndividualIntensityRequest,
    GetIndividualIntensityResponse,
    GetLightInformationRequest,
    GetLightInformationResponse,
    GetLightStatusRequest,
    GetLightStatusResponse,
    GetLightSynchronizeDayNightModeRequest,
    GetLightSynchronizeDayNightModeResponse,
    GetManualAngleOfIlluminationRequest,
    GetManualAngleOfIlluminationResponse,
    GetManualIntensityRequest,
    GetManualIntensityResponse,
    GetServiceCapabilitiesRequest,
    GetServiceCapabilitiesResponse,
    GetSupportedVersionsRequest,
    GetSupportedVersionsResponse,
    GetValidAngleOfIlluminationRequest,
    GetValidAngleOfIlluminationResponse,
    GetValidIntensityRequest,
    GetValidIntensityResponse,
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
    default_api_version = API_VERSION

    @property
    def listed_in_parameters(self) -> bool:
        """Is API listed in parameters."""
        if prop := self.vapix.params.property_handler.get("0"):
            return prop.light_control
        return False

    async def _api_request(self) -> dict[str, LightInformation]:
        """Get default data of stream profiles."""
        return await self.get_light_information()

    async def get_light_information(self) -> dict[str, LightInformation]:
        """List the light control information."""
        bytes_data = await self.vapix.api_request(
            GetLightInformationRequest(api_version=self.default_api_version)
        )
        return GetLightInformationResponse.decode(bytes_data).data

    async def get_service_capabilities(self) -> ServiceCapabilities:
        """List the light control information."""
        bytes_data = await self.vapix.api_request(
            GetServiceCapabilitiesRequest(api_version=self.default_api_version)
        )
        return GetServiceCapabilitiesResponse.decode(bytes_data).data

    async def activate_light(self, light_id: str) -> None:
        """Activate the light."""
        await self.vapix.api_request(
            ActivateLightRequest(
                api_version=self.default_api_version, light_id=light_id
            )
        )

    async def deactivate_light(self, light_id: str) -> None:
        """Deactivate the light."""
        await self.vapix.api_request(
            DeactivateLightRequest(
                api_version=self.default_api_version, light_id=light_id
            )
        )

    async def enable_light(self, light_id: str) -> None:
        """Activate the light."""
        await self.vapix.api_request(
            EnableLightRequest(api_version=self.default_api_version, light_id=light_id)
        )

    async def disable_light(self, light_id: str) -> None:
        """Deactivate the light."""
        await self.vapix.api_request(
            DisableLightRequest(api_version=self.default_api_version, light_id=light_id)
        )

    async def get_light_status(self, light_id: str) -> bool:
        """Get light status if its on or off."""
        bytes_data = await self.vapix.api_request(
            GetLightStatusRequest(
                api_version=self.default_api_version, light_id=light_id
            )
        )
        return GetLightStatusResponse.decode(bytes_data).data

    async def set_automatic_intensity_mode(self, light_id: str, enabled: bool) -> None:
        """Enable the automatic light intensity control."""
        await self.vapix.api_request(
            SetAutomaticIntensityModeRequest(
                api_version=self.default_api_version,
                light_id=light_id,
                enabled=enabled,
            )
        )

    async def get_valid_intensity(self, light_id: str) -> Range:
        """Get valid intensity range for light."""
        bytes_data = await self.vapix.api_request(
            GetValidIntensityRequest(
                api_version=self.default_api_version, light_id=light_id
            )
        )
        return GetValidIntensityResponse.decode(bytes_data).data

    async def set_manual_intensity(self, light_id: str, intensity: int) -> None:
        """Manually sets the intensity."""
        await self.vapix.api_request(
            SetManualIntensityRequest(
                api_version=self.default_api_version,
                light_id=light_id,
                intensity=intensity,
            )
        )

    async def get_manual_intensity(self, light_id: str) -> int:
        """Enable the automatic light intensity control."""
        bytes_data = await self.vapix.api_request(
            GetManualIntensityRequest(
                api_version=self.default_api_version, light_id=light_id
            )
        )
        return GetManualIntensityResponse.decode(bytes_data).data

    async def set_individual_intensity(
        self, light_id: str, led_id: int, intensity: int
    ) -> None:
        """Manually sets the intensity for an individual LED."""
        await self.vapix.api_request(
            SetIndividualIntensityRequest(
                api_version=self.default_api_version,
                light_id=light_id,
                led_id=led_id,
                intensity=intensity,
            )
        )

    async def get_individual_intensity(self, light_id: str, led_id: int) -> int:
        """Receives the intensity from the setIndividualIntensity request."""
        bytes_data = await self.vapix.api_request(
            GetIndividualIntensityRequest(
                api_version=self.default_api_version,
                light_id=light_id,
                led_id=led_id,
            )
        )
        return GetIndividualIntensityResponse.decode(bytes_data).data

    async def get_current_intensity(self, light_id: str) -> int:
        """Receives the intensity from the setIndividualIntensity request."""
        bytes_data = await self.vapix.api_request(
            GetCurrentIntensityRequest(
                api_version=self.default_api_version, light_id=light_id
            )
        )
        return GetCurrentIntensityResponse.decode(bytes_data).data

    async def set_automatic_angle_of_illumination_mode(
        self, light_id: str, enabled: bool
    ) -> None:
        """Automatically control the angle of illumination.

        Using this mode means that the angle of illumination
        is the same as the camera's angle of view.
        """
        await self.vapix.api_request(
            SetAutomaticAngleOfIlluminationModeRequest(
                api_version=self.default_api_version, light_id=light_id, enabled=enabled
            )
        )

    async def get_valid_angle_of_illumination(self, light_id: str) -> list[Range]:
        """List the valid angle of illumination values."""
        bytes_data = await self.vapix.api_request(
            GetValidAngleOfIlluminationRequest(
                api_version=self.default_api_version, light_id=light_id
            )
        )
        return GetValidAngleOfIlluminationResponse.decode(bytes_data).data

    async def set_manual_angle_of_illumination(
        self, light_id: str, angle_of_illumination: int
    ) -> None:
        """Set the manual angle of illumination.

        This is useful when the angle of illumination needs
        to be different from the camera's view angle.
        """
        await self.vapix.api_request(
            SetManualAngleOfIlluminationModeRequest(
                api_version=self.default_api_version,
                light_id=light_id,
                angle_of_illumination=angle_of_illumination,
            )
        )

    async def get_manual_angle_of_illumination(self, light_id: str) -> int:
        """Get the angle of illumination."""
        bytes_data = await self.vapix.api_request(
            GetManualAngleOfIlluminationRequest(
                api_version=self.default_api_version, light_id=light_id
            )
        )
        return GetManualAngleOfIlluminationResponse.decode(bytes_data).data

    async def get_current_angle_of_illumination(self, light_id: str) -> int:
        """Receive the current angle of illumination."""
        bytes_data = await self.vapix.api_request(
            GetCurrentAngleOfIlluminationRequest(
                api_version=self.default_api_version, light_id=light_id
            )
        )
        return GetCurrentAngleOfIlluminationResponse.decode(bytes_data).data

    async def set_light_synchronization_day_night_mode(
        self, light_id: str, enabled: bool
    ) -> None:
        """Enable automatic synchronization with the day/night mode."""
        await self.vapix.api_request(
            SetLightSynchronizeDayNightModeRequest(
                api_version=self.default_api_version, light_id=light_id, enabled=enabled
            )
        )

    async def get_light_synchronization_day_night_mode(self, light_id: str) -> bool:
        """Check if the automatic synchronization is enabled with the day/night mode."""
        bytes_data = await self.vapix.api_request(
            GetLightSynchronizeDayNightModeRequest(
                api_version=self.default_api_version, light_id=light_id
            )
        )
        return GetLightSynchronizeDayNightModeResponse.decode(bytes_data).data

    async def get_supported_versions(self) -> list[str]:
        """List supported API versions."""
        bytes_data = await self.vapix.api_request(GetSupportedVersionsRequest())
        return GetSupportedVersionsResponse.decode(bytes_data).data
