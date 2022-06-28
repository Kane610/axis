"""API Discovery api item."""

from .api import APIItem


class Api(APIItem):
    """API Discovery item."""

    @property
    def name(self):
        """Name of API."""
        return self.raw["name"]

    @property
    def version(self):
        """Version of API."""
        return self.raw["version"]
