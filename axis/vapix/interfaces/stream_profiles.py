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
    GetSupportedVersionsRequest,
    ListStreamProfilesRequest,
    ListStreamProfilesT,
    StreamProfile,
)
from .api_handler import ApiHandler


class StreamProfilesHandler(ApiHandler[StreamProfile]):
    """API Discovery for Axis devices."""

    api_id = ApiId.STREAM_PROFILES
    api_request = ListStreamProfilesRequest()

    async def list_stream_profiles(self) -> ListStreamProfilesT:
        """List all APIs registered on API Discovery service."""
        discovery_item = self.vapix.api_discovery[self.api_id.value]
        return await self.vapix.request2(
            ListStreamProfilesRequest(discovery_item.version)
        )

    async def get_supported_versions(self) -> list[str]:
        """List supported API versions."""
        return await self.vapix.request2(GetSupportedVersionsRequest())
