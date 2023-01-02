"""Base classes for applications."""

from typing import Type

import attr

from ...models.applications.api import ApplicationAPIItem
from ..api import APIItems, Body


class ApplicationAPIItems(APIItems):
    """Base Class for applications."""

    def __init__(
        self,
        vapix: object,
        path: str,
        item_cls: Type[ApplicationAPIItem],
        api_version: str,
    ) -> None:
        """Initialize API items."""
        self._api_version = api_version
        super().__init__(vapix, {}, path, item_cls)

    async def update(self) -> None:
        """Refresh data."""
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
        """Retrieve configuration of application."""
        return await self._request(
            "post",
            self._path,
            json=attr.asdict(
                Body("getConfiguration", self._api_version),
                filter=attr.filters.exclude(attr.fields(Body).params),
            ),
        )
