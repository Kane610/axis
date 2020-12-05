"""Motion Guard API.

AXIS Motion Guard is a video motion detection application that detects
and triggers an alarm whenever an object, such as a person or vehicle,
moves within predefined areas in a camera’s field of view.
"""

from .api import ApplicationAPIItems, ApplicationAPIItem

URL = "/local/motionguard/control.cgi"

API_VERSION = "1.3"

APPLICATION_NAME = "motionguard"

PARAM_CGI_KEY = "Properties.EmbeddedDevelopment.Version"
PARAM_CGI_VALUE = "2.13"


class MotionGuard(ApplicationAPIItems):
    """Motion Guard application on Axis devices"""

    APPLICATION_NAME = APPLICATION_NAME

    def __init__(self, request: object) -> None:
        super().__init__(request, URL, ApplicationAPIItem, API_VERSION)
