"""API Discovery api."""

from dataclasses import asdict, dataclass

from .api import APIItem, APIItems

URL = "/axis-cgi/apidiscovery.cgi"

APIVERSION = "1.0"
CONTEXT = "Axis library"


@dataclass
class body:
    """Create API Discovery request body."""

    method: str
    apiVersion: str = APIVERSION


class ApiDiscovery(APIItems):
    """API Discovery for Axis devices."""

    def __init__(self, raw: str, request: object) -> None:
        super().__init__(raw, request, URL, object)

    def api_list(self) -> None:
        """List all APIs registered on API Discovery service."""
        self._request("post", URL, data=asdict(body("getApiList")))

    def supported_versions(self) -> None:
        """Supported versions of API Discovery API."""
        self._request("post", URL, data=asdict(body("getSupportedVersions")))
