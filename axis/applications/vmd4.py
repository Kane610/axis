"""VMD4 API."""

from .guard_suite_base import GuardSuiteBase, GuardSuiteProfileBase

URL = "/local/vmd/control.cgi"

API_VERSION = "1.4"

APPLICATION_NAME = "vmd"

PARAM_CGI_KEY = "Properties.EmbeddedDevelopment.Version"
PARAM_CGI_VALUE = "2.12"


class Vmd4(GuardSuiteBase):
    """VMD4 on Axis devices."""

    APPLICATION_NAME = APPLICATION_NAME

    def __init__(self, request: object) -> None:
        super().__init__(request, URL, GuardSuiteProfileBase, API_VERSION)
