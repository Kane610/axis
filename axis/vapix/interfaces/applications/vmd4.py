"""VMD4 API."""

from ...models.applications.api import ApplicationAPIItem
from .api import ApplicationAPIItems

URL = "/local/vmd/control.cgi"

API_VERSION = "1.2"

APPLICATION_NAME = "vmd"

PARAM_CGI_KEY = "Properties.EmbeddedDevelopment.Version"
PARAM_CGI_VALUE = "2.12"


class Vmd4(ApplicationAPIItems):
    """VMD4 on Axis devices."""

    APPLICATION_NAME = APPLICATION_NAME
    api_version = API_VERSION

    item_cls = ApplicationAPIItem
    path = URL
