"""VMD4 API."""

import attr

from .api import APIItem, APIItems, Body

URL = "/local/vmd/control.cgi"

API_VERSION = "1.4"

APPLICATION_NAME = "vmd"

PARAM_CGI_KEY = "Properties.EmbeddedDevelopment.Version"
PARAM_CGI_VALUE = "2.12"


class Vmd4(APIItems):
    """VMD4 on Axis devices."""

    def __init__(self, request: object) -> None:
        super().__init__({}, request, URL, Vmd4Profile)

    def update(self) -> None:
        """No update method."""
        raw = self.get_configuration()

        profiles = {}

        for profile in raw["data"]["profiles"]:
            camera = profile["camera"]
            uid = profile["uid"]
            profiles[f"Camera{camera}Profile{uid}"] = profile

        self.process_raw(profiles)

    def get_configuration(self) -> dict:
        """Current configuration of application."""
        return self._request(
            "post",
            URL,
            json=attr.asdict(
                Body("getConfiguration", API_VERSION),
                filter=attr.filters.exclude(attr.fields(Body).params),
            ),
        )


class Vmd4Profile(APIItem):
    """VMD4 profile."""

    @property
    def camera(self) -> int:
        """Camera ID."""
        return self.raw["camera"]

    @property
    def filters(self) -> list:
        """An array of exclude filters."""
        return self.raw["filters"]

    @property
    def name(self) -> str:
        """Nice name of profile."""
        return self.raw["name"]

    @property
    def triggers(self) -> list:
        """An array of triggers."""
        return self.raw["triggers"]

    @property
    def uid(self) -> int:
        """Unique ID of profile."""
        return self.raw["uid"]
