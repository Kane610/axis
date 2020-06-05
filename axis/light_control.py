"""Light Control API.

The Axis Light control API makes it possible to control the behavior and functionality
of IR and White light LEDs in the Axis devices
"""

import attr

from .api import APIItem, APIItems, Body

URL = "/axis-cgi/lightcontrol.cgi"

API_DISCOVERY_ID = "light-control"
API_VERSION = "1.1"


class LightControl(APIItems):
    """Light control for Axis devices."""

    def __init__(self, raw: dict, request: object) -> None:
        super().__init__(raw, request, URL, APIItem)

    def get_service_capabilities(self) -> dict:
        """List the capabilities of the light controller."""
        return self._request(
            "post",
            URL,
            json=attr.asdict(
                Body("getServiceCapabilities", API_VERSION),
                filter=attr.filters.exclude(attr.fields(Body).params),
            ),
        )

    def get_light_information(self) -> dict:
        """List the capabilities of the light controller."""
        return self._request(
            "post",
            URL,
            json=attr.asdict(
                Body("getLightInformation", API_VERSION),
                filter=attr.filters.exclude(attr.fields(Body).params),
            ),
        )

    def get_supported_versions(self) -> dict:
        """Supported versions of light control."""
        return self._request(
            "post",
            URL,
            json=attr.asdict(
                Body("getSupportedVersions", API_VERSION),
                filter=attr.filters.include(attr.fields(Body).method),
            ),
        )
