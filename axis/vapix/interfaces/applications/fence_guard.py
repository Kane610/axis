"""Fence Guard API.

AXIS Fence Guard allows you to set up virtual fences in a camera's field of view
to protect an area from intrusion. The application automatically triggers an alarm
when it detects a moving object, such as a person or vehicle, crossing a user-defined
virtual line.
"""

from ...models.applications.api import ApplicationAPIItem
from .api import ApplicationAPIItems

URL = "/local/fenceguard/control.cgi"

API_VERSION = "1.3"

APPLICATION_NAME = "fenceguard"

PARAM_CGI_KEY = "Properties.EmbeddedDevelopment.Version"
PARAM_CGI_VALUE = "2.13"


class FenceGuard(ApplicationAPIItems):
    """Fence Guard application on Axis devices."""

    APPLICATION_NAME = APPLICATION_NAME

    def __init__(self, request: object) -> None:
        """Initialize fence guard manager."""
        super().__init__(request, URL, ApplicationAPIItem, API_VERSION)
