"""Stream profiles API.

 The Stream profile API makes it possible to create and manage stream profiles suitable
for different applications and devices when recording a video or requesting a live video.
 A stream profile contains a collection of parameters such as video codecs, resolutions,
frame rates and compressions, and should be used to retrieve a video stream from your Axis product.
 Lastly, all parameters that can be used in a video stream request (both HTTP or RTSP)
can be saved in a stream profile.
"""

import attr

from ..models.stream_profile import StreamProfile
from .api import APIItems, Body

URL = "/axis-cgi/streamprofile.cgi"

API_DISCOVERY_ID = "stream-profiles"
API_VERSION = "1.0"


class StreamProfiles(APIItems):
    """Stream profiles for Axis devices."""

    item_cls = StreamProfile
    path = URL

    async def update(self) -> None:
        """Refresh data."""
        raw = await self.list()
        self.process_raw(raw)

    @staticmethod
    def pre_process_raw(raw: dict) -> dict:
        """Return a dictionary of stream profiles."""
        if not raw:
            return {}

        if raw.get("data", {}).get("maxProfiles", 0) == 0:
            return {}

        profiles = raw["data"]["streamProfile"]
        return {profile["name"]: profile for profile in profiles}

    async def list(self, params: list = []) -> dict:
        """List the content of a stream profile.

        It is possible to list either one or multiple profiles and if the parameter
        streamProfileName is the empty list [] all available stream profiles will be listed.
        """
        return await self.vapix.request(
            "post",
            URL,
            json=attr.asdict(
                Body("list", API_VERSION, params={"streamProfileName": params}),
            ),
        )

    async def get_supported_versions(self) -> dict:
        """Retrieve a list of supported API versions."""
        return await self.vapix.request(
            "post",
            URL,
            json=attr.asdict(
                Body("getSupportedVersions", API_VERSION),
                filter=attr.filters.include(attr.fields(Body).method),
            ),
        )
