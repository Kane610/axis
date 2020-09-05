"""Base classes for applications belonging to Axis Guard Suite."""

import attr

from axis.api import APIItem, APIItems, Body


class GuardSuiteBase(APIItems):
    """Base Class for Guard Suite Applications."""

    def __init__(
        self, request: object, path: str, item_cls: object, api_version: str
    ) -> None:
        self._api_version = api_version
        super().__init__({}, request, path, item_cls)

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
            self._path,
            json=attr.asdict(
                Body("getConfiguration", self._api_version),
                filter=attr.filters.exclude(attr.fields(Body).params),
            ),
        )


class GuardSuiteProfileBase(APIItem):
    """Base class for Guard Suite Profiles."""

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
    def perspective(self) -> list:
        """Perspective for improve triggers based on heights."""
        return self.raw.get("perspective")

    @property
    def triggers(self) -> list:
        """An array of triggers."""
        return self.raw["triggers"]

    @property
    def uid(self) -> int:
        """Unique ID of profile."""
        return self.raw["uid"]
