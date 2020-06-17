"""Stream profiles API.

 The Stream profile API makes it possible to create and manage stream profiles suitable
for different applications and devices when recording a video or requesting a live video.
 A stream profile contains a collection of parameters such as video codecs, resolutions,
frame rates and compressions, and should be used to retrieve a video stream from your Axis product.
 Lastly, all parameters that can be used in a video stream request (both HTTP or RTSP)
can be saved in a stream profile.
"""

import attr

from .api import APIItem, APIItems, Body

URL = "/axis-cgi/streamprofile.cgi"

API_DISCOVERY_ID = "stream-profiles"
API_VERSION = "1.0"


class StreamProfiles(APIItems):
    """Stream profiles for Axis devices."""

    def __init__(self, request: object) -> None:
        super().__init__({}, request, URL, StreamProfile)

    def update(self, path=None) -> None:
        raw = self.list()
        if raw["data"]["maxProfiles"] > 0:
            self.process_raw(raw["data"]["streamProfile"])

    def process_raw(self, raw: dict) -> None:
        """Pre-process raw json list.

        Prepare parameters to work with APIItems.
        """
        raw_profiles = {profile["name"]: profile for profile in raw}

        super().process_raw(raw_profiles)

    def list(self, params: list = []) -> dict:
        """This API method can be used to list the content of a stream profile.

        It is possible to list either one or multiple profiles and if the parameter
        streamProfileName is the empty list [] all available stream profiles will be listed.
        """
        return self._request(
            "post",
            URL,
            json=attr.asdict(
                Body("list", API_VERSION, params={"streamProfileName": params}),
            ),
        )

    def get_supported_versions(self) -> dict:
        """This CGI method can be used to retrieve a list of supported API versions."""
        return self._request(
            "post",
            URL,
            json=attr.asdict(
                Body("getSupportedVersions", API_VERSION),
                filter=attr.filters.include(attr.fields(Body).method),
            ),
        )


class StreamProfile(APIItem):
    """Stream profile item."""

    @property
    def name(self):
        """Name of stream profile."""
        return self.raw["name"]

    @property
    def description(self):
        """Description of API."""
        return self.raw["description"]

    @property
    def parameters(self):
        """Parameters of API."""
        return self.raw["parameters"]
