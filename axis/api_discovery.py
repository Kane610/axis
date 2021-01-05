"""API Discovery api.

The AXIS API Discovery service makes it possible to retrieve information about APIs supported on their products.
"""

import attr

from .api import APIItem, APIItems, Body

URL = "/axis-cgi/apidiscovery.cgi"

API_DISCOVERY_ID = "api-discovery"
API_VERSION = "1.0"


class ApiDiscovery(APIItems):
    """API Discovery for Axis devices."""

    def __init__(self, request: object) -> None:
        super().__init__({}, request, URL, Api)

    async def update(self) -> None:
        raw = await self.get_api_list()
        self.process_raw(raw)

    @staticmethod
    def pre_process_raw(raw: dict) -> dict:
        """Return a dictionary of discovered APIs."""
        api_data = raw.get("data", {}).get("apiList", [])
        return {api["id"]: api for api in api_data}

    async def get_api_list(self) -> dict:
        """List all APIs registered on API Discovery service."""
        return await self._request(
            "post",
            URL,
            json=attr.asdict(
                Body("getApiList", API_VERSION),
                filter=attr.filters.exclude(attr.fields(Body).params),
            ),
        )

    async def get_supported_versions(self) -> dict:
        """Supported versions of API Discovery API."""
        return await self._request(
            "post",
            URL,
            json=attr.asdict(
                Body("getSupportedVersions", API_VERSION),
                filter=attr.filters.include(attr.fields(Body).method),
            ),
        )


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
