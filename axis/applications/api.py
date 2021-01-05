"""Base classes for applications."""

import attr

from axis.api import APIItem, APIItems, Body


class ApplicationAPIItems(APIItems):
    """Base Class for applications."""

    def __init__(
        self, request: object, path: str, item_cls: object, api_version: str
    ) -> None:
        self._api_version = api_version
        super().__init__({}, request, path, item_cls)

    async def update(self) -> None:
        """No update method."""
        raw = await self.get_configuration()
        self.process_raw(raw)

    @staticmethod
    def pre_process_raw(raw: dict) -> dict:
        """Prepare profiles data for process_raw."""
        profiles = {}

        for profile in raw.get("data", {}).get("profiles", {}):
            camera = profile["camera"]
            uid = profile["uid"]
            profiles[f"Camera{camera}Profile{uid}"] = profile

        return profiles

    async def get_configuration(self) -> dict:
        """Current configuration of application."""
        return await self._request(
            "post",
            self._path,
            json=attr.asdict(
                Body("getConfiguration", self._api_version),
                filter=attr.filters.exclude(attr.fields(Body).params),
            ),
        )


class ApplicationAPIItem(APIItem):
    """Base class for application profiles."""

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
