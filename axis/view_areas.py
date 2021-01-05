"""View area API.

The View Area API makes it possible to define the subsections of a camera’s full view
as individual, virtual channels. This means that a wide angle and/or high resolution
camera can provide multiple video streams at a lower resolution where each stream
covers a specific region of interest. The API is also able to simplify the installation
process by fine tuning an area digitally after the camera has been manually pointed at a scene.
"""

import attr
from typing import Optional

from .api import APIItem, APIItems, Body

URL = "/axis-cgi/viewarea"
URL_INFO = f"{URL}/info.cgi"
URL_CONFIG = f"{URL}/configure.cgi"

API_DISCOVERY_ID = "view-area"
API_VERSION = "1.0"


@attr.s
class Geometry:
    """Represent a geometry object."""

    horizontalOffset: int = attr.ib()
    horizontalSize: int = attr.ib()
    verticalOffset: int = attr.ib()
    verticalSize: int = attr.ib()


@attr.s
class Size:
    """Represent a size object."""

    horizontal: int = attr.ib()
    vertical: int = attr.ib()


class ViewArea(APIItem):
    """View area object."""

    @property
    def id(self) -> int:
        """Identity of view area."""
        return self.raw["id"]

    @property
    def source(self) -> int:
        """Image source that created view area."""
        return self.raw["source"]

    @property
    def camera(self) -> int:
        """View area used by streaming, PTZ and other APIs."""
        return self.raw["camera"]

    @property
    def configurable(self) -> bool:
        """Define if a view can be configured.

        Some view areas can not be configured and are thus unable to be changed
        with regards to geometry, etc.
        """
        return self.raw["configurable"]

    # These are only listed if the geometry of the view area can be configured.

    @property
    def canvas_size(self) -> Size:
        """Define size of the overview image that the view area geometry is defined on."""
        return Size(**self.raw["canvasSize"])

    @property
    def rectangular_geometry(self) -> Geometry:
        """Define a geometry for the view area as a rectangle related to the canvas."""
        return Geometry(**self.raw["rectangularGeometry"])

    @property
    def min_size(self) -> Size:
        """Define the minimum size that a view area can have."""
        return Size(**self.raw["minSize"])

    @property
    def max_size(self) -> Size:
        """Define the maximum size that a view area can have."""
        return Size(**self.raw["maxSize"])

    @property
    def grid(self) -> Geometry:
        """Define the grid that a geometry is applied to on the canvas due to device limitations."""
        return Geometry(**self.raw["grid"])


class ViewAreas(APIItems):
    """View areas for Axis devices."""

    def __init__(self, request: object) -> None:
        super().__init__({}, request, URL, ViewArea)

    async def update(self) -> None:
        raw = await self.list()
        self.process_raw(raw)

    @staticmethod
    def pre_process_raw(raw: dict) -> dict:
        """Return a dictionary of view areas."""
        view_area_data = raw.get("data", {}).get("viewAreas", [])
        return {api["id"]: api for api in view_area_data}

    async def list(self) -> dict:
        """This API method can be used to list the content of a view area.

        It is possible to list either one or multiple profiles and if the parameter
        streamProfileName is the empty list [] all available stream profiles will be listed.
        Security level: Viewer
        """
        return await self._request(
            "post",
            URL_INFO,
            json=attr.asdict(
                Body("list", API_VERSION),
                filter=attr.filters.exclude(attr.fields(Body).params),
            ),
        )

    async def get_supported_versions(self) -> dict:
        """This CGI method can be used to retrieve a list of supported API versions.

        Request info.cgi
        Security level: Viewer
        Method: POST
        """
        return await self._request(
            "post",
            URL_INFO,
            json=attr.asdict(
                Body("getSupportedVersions", API_VERSION),
                filter=attr.filters.include(attr.fields(Body).method),
            ),
        )

    async def set_geometry(
        self,
        geometry: Geometry,
        view_area_id: Optional[int] = None,
        view_area: Optional[ViewArea] = None,
    ) -> None:
        """Restore geometry of a view area back to default values.

        Security level: Admin
        Method: POST
        """
        if view_area:
            view_area_id = view_area.id

        raw = await self._request(
            "post",
            URL_CONFIG,
            json=attr.asdict(
                Body(
                    "setGeometry",
                    API_VERSION,
                    params={
                        "viewArea": {
                            "id": view_area_id,
                            "rectangularGeometry": attr.asdict(geometry),
                        }
                    },
                ),
            ),
        )

        self.process_raw(raw)

    async def reset_geometry(
        self,
        view_area_id: Optional[int] = None,
        view_area: Optional[ViewArea] = None,
    ) -> None:
        """Restore geometry of a view area back to default values.

        Security level: Admin
        Method: POST
        """
        if view_area:
            view_area_id = view_area.id

        raw = await self._request(
            "post",
            URL_CONFIG,
            json=attr.asdict(
                Body(
                    "resetGeometry",
                    API_VERSION,
                    params={"viewArea": {"id": view_area_id}},
                ),
            ),
        )
        self.process_raw(raw)

    async def get_supported_config_versions(self) -> dict:
        """This CGI method can be used to retrieve a list of supported API versions.

        Request info.cgi
        Security level: Viewer
        Method: POST
        """
        return await self._request(
            "post",
            URL_CONFIG,
            json=attr.asdict(
                Body("getSupportedVersions", API_VERSION),
                filter=attr.filters.include(attr.fields(Body).method),
            ),
        )
