"""API Discovery api."""

import attr

from .api import APIItem, APIItems

URL = "/axis-cgi/apidiscovery.cgi"

API_DISCOVERY_ID = "api-discovery"

APIVERSION = "1.0"
CONTEXT = "Axis library"


@attr.s
class body:
    """Create API Discovery request body."""

    method: str = attr.ib()
    apiVersion: str = attr.ib(default=APIVERSION)


class ApiDiscovery(APIItems):
    """API Discovery for Axis devices."""

    def __init__(self, raw: dict, request: object) -> None:
        super().__init__(raw, request, URL, Api)

    def update(self, path=None) -> None:
        raw = self.get_api_list()
        self.process_raw(raw)

    def process_raw(self, raw: dict) -> None:
        """Pre-process raw json dict.

        Prepare parameters to work with APIItems.
        """
        raw_apis = {api["id"]: api for api in raw.get("data", {}).get("apiList", [])}

        super().process_raw(raw_apis)

    def get_api_list(self) -> dict:
        """List all APIs registered on API Discovery service."""
        return self._request("post", URL, json=attr.asdict(body("getApiList")))

    def get_supported_versions(self) -> dict:
        """Supported versions of API Discovery API."""
        return self._request(
            "post",
            URL,
            json=attr.asdict(
                body("getSupportedVersions"),
                filter=attr.filters.include(attr.fields(body).method),
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
