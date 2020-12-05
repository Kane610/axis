"""VMD4 API."""

from .api import ApplicationAPIItems, ApplicationAPIItem

URL = "/local/vmd/control.cgi"

API_VERSION = "1.2"

APPLICATION_NAME = "vmd"

PARAM_CGI_KEY = "Properties.EmbeddedDevelopment.Version"
PARAM_CGI_VALUE = "2.12"


class Vmd4(ApplicationAPIItems):
    """VMD4 on Axis devices."""

    APPLICATION_NAME = APPLICATION_NAME

    def __init__(self, request: object) -> None:
        super().__init__(request, URL, ApplicationAPIItem, API_VERSION)
