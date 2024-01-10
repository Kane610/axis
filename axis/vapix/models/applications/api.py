"""Base class for applications."""


from ..api import APIItem

API_VERSION = "1.3"


class ApplicationAPIItem(APIItem):
    """Base class for application profiles."""

    @property
    def camera(self) -> int:
        """Camera ID."""
        return self.raw["camera"]

    @property
    def filters(self) -> list:
        """Array of exclude filters."""
        return self.raw["filters"]

    @property
    def name(self) -> str:
        """Nice name of profile."""
        return self.raw["name"]

    @property
    def perspective(self) -> list | None:
        """Perspective for improve triggers based on heights."""
        return self.raw.get("perspective")

    @property
    def triggers(self) -> list:
        """Array of triggers."""
        return self.raw["triggers"]

    @property
    def uid(self) -> int:
        """Profile ID."""
        return self.raw["uid"]
