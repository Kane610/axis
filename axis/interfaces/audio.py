"""Audio api.

https://www.axis.com/vapix-library/subjects/t10100065/section/t10036015/display

The Audio API helps you transmit audio to your Axis device.
"""

from ..models.api_discovery import ApiId
from ..models.audio import API_VERSION, TransmitAudioRequest
from ..models.parameters.audio import AudioParam
from .api_handler import ApiHandler


class AudioHandler(ApiHandler[AudioParam]):
    """Audio support for Axis devices."""

    api_id = ApiId.AUDIO_STREAMING_CAPABILITIES
    default_api_version = API_VERSION

    @property
    def listed_in_parameters(self) -> bool:
        """Is API listed in parameters."""
        if prop := self.vapix.params.property_handler.get("0"):
            return prop.audio
        return False

    async def _api_request(self) -> dict[str, AudioParam]:
        """Get API data method defined by subclass."""
        return await self.get_audio_params()

    async def get_audio_params(self) -> dict[str, AudioParam]:
        """Retrieve audio params."""
        await self.vapix.params.audio_handler.update()
        return dict(self.vapix.params.audio_handler.items())

    async def transmit(self, audio: bytes) -> None:
        """Transmit audio to play on the speaker."""
        await self.vapix.api_request(TransmitAudioRequest(audio=audio))
