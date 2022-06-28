"""Stream profiles API.

 A stream profile contains a collection of parameters such as
video codecs, resolutions, frame rates and compressions,
and should be used to retrieve a video stream from your Axis product.
"""

from .api import APIItem


class StreamProfile(APIItem):
    """Stream profile item."""

    @property
    def name(self) -> str:
        """Name of stream profile."""
        return self.raw["name"]

    @property
    def description(self) -> str:
        """Stream profile description."""
        return self.raw["description"]

    @property
    def parameters(self) -> str:
        """Parameters of stream profile."""
        return self.raw["parameters"]
