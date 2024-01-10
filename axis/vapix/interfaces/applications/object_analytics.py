"""Object Analytics API.

AXIS Object Analytics.
"""


from ...models.applications.object_analytics import (
    Configuration,
    GetConfigurationRequest,
    GetConfigurationResponse,
)
from .application_handler import ApplicationHandler

URL = "/local/objectanalytics/control.cgi"

API_VERSION = "1.0"

APPLICATION_NAME = "objectanalytics"

PARAM_CGI_KEY = "Properties.EmbeddedDevelopment.Version"
PARAM_CGI_VALUE = "2.13"


# class ObjectAnalytics(ApplicationAPIItems):
#     """Object Analytics application on Axis devices."""

#     api_version = API_VERSION
#     name = APPLICATION_NAME

#     item_cls = ObjectAnalyticsScenario
#     path = URL

#     @staticmethod
#     def pre_process_raw(raw: dict) -> dict:
#         """Prepare scenarios data for process_raw."""
#         scenarios = {}

#         for scenario in raw.get("data", {}).get("scenarios", {}):
#             device = scenario["devices"][0]["id"]
#             uid = scenario["id"]
#             scenarios[f"Device{device}Scenario{uid}"] = scenario

#         return scenarios

#     async def get_configuration(self) -> dict:
#         """Retrieve configuration of application."""
#         return await self.vapix.request(
#             "post",
#             self.path,
#             json=attr.asdict(
#                 Body("getConfiguration", self.api_version),  # type: ignore[call-arg]
#             ),
#         )


class ObjectAnalyticsHandler(ApplicationHandler[Configuration]):
    """Object analytics handler for Axis devices."""

    app_name = "objectanalytics"

    async def _api_request(self) -> dict[str, Configuration]:
        """Get default configuration."""
        return {"0": await self.get_configuration()}

    async def get_configuration(self) -> Configuration:
        """Get configuration of object analytics application."""
        bytes_data = await self.vapix.new_request(GetConfigurationRequest())
        response = GetConfigurationResponse.decode(bytes_data)
        return response.data
