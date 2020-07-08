"""VMD4 API."""

import attr

from .api import APIItem, APIItems, Body

URL = "/local/vmd/control.cgi"

API_VERSION = "1.3"

APPLICATION_NAME = "vmd"

PARAM_CGI_KEY = "Properties.EmbeddedDevelopment.Version"
PARAM_CGI_VALUE = "2.12"


class Vmd4(APIItems):
    """VMD4 on Axis devices."""

    def __init__(self, request: object) -> None:
        super().__init__({}, request, URL, APIItem)

    def update(self) -> None:
        raw = self.get_configuration()
        print(raw)

    def get_configuration(self) -> dict:
        """"""
        return self._request(
            "post",
            URL,
            json=attr.asdict(
                Body("getConfiguration", API_VERSION),
                filter=attr.filters.exclude(attr.fields(Body).params),
            ),
        )


class Vmd4Profile(APIItem):
    """VMD4 profile."""

    @property
    def camera(self):
        """"""
        return self.raw["camera"]

    @property
    def filters(self):
        """"""
        return self.raw["filters"]

    @property
    def name(self):
        """"""
        return self.raw["name"]

    @property
    def triggers(self):
        """"""
        return self.raw["triggers"]

    @property
    def uid(self):
        """"""
        return self.raw["uid"]


{
    "apiVersion": "1.4",
    "method": "getConfiguration",
    "context": "Axis library",
    "data": {
        "cameras": [{"id": 1, "rotation": 0, "active": True}],
        "configurationStatus": 2,
        "profiles": [
            {
                "filters": [
                    {"data": 1, "active": True, "type": "timeShortLivedLimit"},
                    {"data": 5, "active": True, "type": "distanceSwayingObject"},
                    {"data": [5, 5], "active": True, "type": "sizePercentage"},
                ],
                "camera": 1,
                "triggers": [
                    {
                        "type": "includeArea",
                        "data": [
                            [-0.97, -0.97],
                            [-0.97, 0.97],
                            [0.97, 0.97],
                            [0.97, -0.97],
                        ],
                    }
                ],
                "name": "Profile 1",
                "uid": 1,
            }
        ],
    },
}

