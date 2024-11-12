"""Audio Device Control API.

https://www.axis.com/vapix-library/subjects/t10100065/section/t10169359/display

The Audio Device Control API helps you configure and control your Axis
audio devices.
"""

from typing import Any

from ..models.api_discovery import ApiId
from ..models.audio_device_control import (
    API_VERSION,
    AudioDevice,
    GetDevicesSettingsRequest,
    GetDevicesSettingsResponse,
    GetSupportedVersionsRequest,
    GetSupportedVersionsResponse,
    SetDevicesSettingsRequest,
)
from .api_handler import ApiHandler


class AudioDeviceControlHandler(ApiHandler[Any]):
    """Audio Device Control for Axis devices."""

    api_id = ApiId.AUDIO_DEVICE_CONTROL
    default_api_version = API_VERSION

    async def get_devices_settings(self) -> list[AudioDevice]:
        """Get audio devices settings."""
        bytes_data = await self.vapix.api_request(GetDevicesSettingsRequest())
        response = GetDevicesSettingsResponse.decode(bytes_data)
        return response.data

    async def mute(self) -> None:
        """Shortcut to mute the output audio device."""
        await self._set_gain_mute(mute=True)

    async def unmute(self) -> None:
        """Shortcut to unmute the output audio device."""
        await self._set_gain_mute(mute=False)

    async def set_gain(self, gain: int) -> None:
        """Shortcut to set the gain on the output audio device."""
        await self._set_gain_mute(gain=gain)

    async def _set_gain_mute(
        self, gain: int | None = None, mute: bool | None = None
    ) -> None:
        """Shortcut to control gain/mute state."""
        mute_param = {"mute": mute} if mute in (True, False) else {}
        gain_param = {"gain": gain} if gain else {}

        devices = [
            {
                "id": "0",
                "outputs": [
                    {
                        "id": "0",
                        "connectionTypes": [
                            {
                                "id": "internal",
                                "signalingTypes": [
                                    {
                                        "id": "unbalanced",
                                        "channels": [
                                            {
                                                "id": "0",
                                                **(gain_param),
                                                **(mute_param),
                                            }
                                        ],
                                    }
                                ],
                            }
                        ],
                    }
                ],
            }
        ]
        await self.vapix.api_request(SetDevicesSettingsRequest(devices))

    async def get_supported_versions(self) -> list[str]:
        """List supported API versions."""
        bytes_data = await self.vapix.api_request(GetSupportedVersionsRequest())
        response = GetSupportedVersionsResponse.decode(bytes_data)
        return response.data
