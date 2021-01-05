"""Object Analytics API.

AXIS Object Analytics.
"""

import attr

from .api import Body, ApplicationAPIItems, ApplicationAPIItem

URL = "/local/objectanalytics/control.cgi"

API_VERSION = "1.0"

APPLICATION_NAME = "objectanalytics"

PARAM_CGI_KEY = "Properties.EmbeddedDevelopment.Version"
PARAM_CGI_VALUE = "2.13"


class ObjectAnalytics(ApplicationAPIItems):
    """Object Analytics application on Axis devices"""

    APPLICATION_NAME = APPLICATION_NAME

    def __init__(self, request: object) -> None:
        super().__init__(request, URL, ObjectAnalyticsScenario, API_VERSION)

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
        """Current configuration of application."""
        return await self._request(
            "post",
            self._path,
            json=attr.asdict(
                Body("getConfiguration", self._api_version),
            ),
        )


class ObjectAnalyticsScenario(ApplicationAPIItem):
    """Object Analytics Scenario."""

    @property
    def camera(self) -> list:
        """Camera ID."""
        return self.raw["devices"]

    @property
    def object_classifications(self) -> list:
        """Classifications of objects to detect."""
        return self.raw["objectClassifications"]

    @property
    def perspectives(self) -> list:
        """Perspectives for improve triggers based on heights."""
        return self.raw.get("perspectives")

    @property
    def presets(self) -> list:
        """Presets."""
        return self.raw["presets"]

    @property
    def trigger_type(self) -> str:
        """Type of trigger."""
        return self.raw["type"]

    @property
    def uid(self) -> int:
        """Unique ID of scenario."""
        return self.raw["id"]