"""Object Analytics API.

AXIS Object Analytics.
"""

import attr

from ...models.applications.object_analytics import ObjectAnalyticsScenario
from .api import ApplicationAPIItems, Body

URL = "/local/objectanalytics/control.cgi"

API_VERSION = "1.0"

APPLICATION_NAME = "objectanalytics"

PARAM_CGI_KEY = "Properties.EmbeddedDevelopment.Version"
PARAM_CGI_VALUE = "2.13"


class ObjectAnalytics(ApplicationAPIItems):
    """Object Analytics application on Axis devices."""

    APPLICATION_NAME = APPLICATION_NAME

    def __init__(self, vapix: object) -> None:
        """Initialize object analyticz manager."""
        super().__init__(vapix, URL, ObjectAnalyticsScenario, API_VERSION)

    @staticmethod
    def pre_process_raw(raw: dict) -> dict:
        """Prepare scenarios data for process_raw."""
        scenarios = {}

        for scenario in raw.get("data", {}).get("scenarios", {}):
            device = scenario["devices"][0]["id"]
            uid = scenario["id"]
            scenarios[f"Device{device}Scenario{uid}"] = scenario

        return scenarios

    async def get_configuration(self) -> dict:
        """Retrieve configuration of application."""
        return await self.vapix.request(
            "post",
            self._path,
            json=attr.asdict(
                Body("getConfiguration", self._api_version),
            ),
        )
