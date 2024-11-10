"""Audio api.

The Audio API helps you transmit audio to your Axis device.
"""

from ..models.api_discovery import ApiId
from ..models.audio import (
    API_VERSION,
    Audio,
)
from .api_handler import ApiHandler


class AudioHandler(ApiHandler[Audio]):
    """Audio support for Axis devices."""

    api_id = ApiId.AUDIO_STREAMING_CAPABILITIES
    default_api_version = API_VERSION

    @property
    def listed_in_parameters(self) -> bool:
        """Is API listed in parameters."""
        if prop := self.vapix.params.property_handler.get("0"):
            return prop.audio
        return False

    async def _api_request(self) -> dict[str, Audio]:
        """No default data available for Audio API."""
        return {}
