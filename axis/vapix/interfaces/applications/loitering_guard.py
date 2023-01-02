"""Loitering Guard API.

AXIS Loitering Guard tracks moving objects such as people and vehicles,
and triggers an alarm if they have been in a predefined area for too long.
"""

from ...models.applications.api import ApplicationAPIItem
from .api import ApplicationAPIItems

URL = "/local/loiteringguard/control.cgi"

API_VERSION = "1.3"

APPLICATION_NAME = "loiteringguard"

PARAM_CGI_KEY = "Properties.EmbeddedDevelopment.Version"
PARAM_CGI_VALUE = "2.13"


class LoiteringGuard(ApplicationAPIItems):
    """Loitering Guard application on Axis devices."""

    api_version = API_VERSION
    name = APPLICATION_NAME

    item_cls = ApplicationAPIItem
    path = URL
