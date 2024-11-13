"""Audio api.

https://www.axis.com/vapix-library/subjects/t10100065/section/t10036015/display

The Audio API helps you transmit audio to your Axis device.
"""

from dataclasses import dataclass

import httpx

from .api import DEFAULT_TIMEOUT, ApiRequest

API_VERSION = "1.0"


@dataclass
class TransmitAudioRequest(ApiRequest):
    """Transmit audio to the Axis speaker to play."""

    method = "post"
    path = "/axis-cgi/audio/transmit.cgi"
    content_type = "audio/axis-mulaw-128"

    # short read timeout since the call will block until the audio is played
    timeout = httpx.Timeout(DEFAULT_TIMEOUT, read=5)

    audio: bytes

    @property
    def content(self) -> bytes:
        """Initialize request data."""
        return self.audio
