"""Base classes for applications."""


import attr

from ..api import APIItems, Body


class ApplicationAPIItems(APIItems):
    """Base Class for applications."""

    api_version: str
    name: str

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
        return await self.vapix.request(
            "post",
            self.path,
            json=attr.asdict(
                Body("getConfiguration", self.api_version),
                filter=attr.filters.exclude(attr.fields(Body).params),
            ),
        )
