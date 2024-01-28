"""Stream profiles API.

 The Stream profile API makes it possible to create and manage stream profiles suitable
for different applications and devices when recording a video or requesting a live video.
 A stream profile contains a collection of parameters such as video codecs, resolutions,
frame rates and compressions, and should be used to retrieve a video stream from your Axis product.
 Lastly, all parameters that can be used in a video stream request (both HTTP or RTSP)
can be saved in a stream profile.
"""

from ..models.api_discovery import ApiId
from ..models.stream_profile import (
    API_VERSION,
    GetSupportedVersionsRequest,
    GetSupportedVersionsResponse,
    ListStreamProfilesRequest,
    ListStreamProfilesResponse,
    StreamProfile,
)
from .api_handler import ApiHandler


class StreamProfilesHandler(ApiHandler[StreamProfile]):
    """API Discovery for Axis devices."""

    api_id = ApiId.STREAM_PROFILES
    default_api_version = API_VERSION

    async def _api_request(self) -> dict[str, StreamProfile]:
        """Get default data of stream profiles."""
        return await self.list_stream_profiles()

    async def list_stream_profiles(self) -> dict[str, StreamProfile]:
        """List all stream profiles."""
        discovery_item = self.vapix.api_discovery[self.api_id]
        bytes_data = await self.vapix.api_request(
            ListStreamProfilesRequest(api_version=discovery_item.version)
        )
        response = ListStreamProfilesResponse.decode(bytes_data)
        return response.data

    async def get_supported_versions(self) -> list[str]:
        """List supported API versions."""
        bytes_data = await self.vapix.api_request(GetSupportedVersionsRequest())
        response = GetSupportedVersionsResponse.decode(bytes_data)
        return response.data
