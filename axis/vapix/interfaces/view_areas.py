"""View area API.

The View Area API makes it possible to define the subsections of a camera’s full view
as individual, virtual channels. This means that a wide angle and/or high resolution
camera can provide multiple video streams at a lower resolution where each stream
covers a specific region of interest. The API is also able to simplify the installation
process by fine tuning an area digitally after the camera has been manually pointed at a scene.
"""

from typing import Optional

import attr

from ..models.view_area import Geometry, ViewArea
from .api import APIItems, Body

URL = "/axis-cgi/viewarea"
URL_INFO = f"{URL}/info.cgi"
URL_CONFIG = f"{URL}/configure.cgi"

API_DISCOVERY_ID = "view-area"
API_VERSION = "1.0"


class ViewAreas(APIItems):
    """View areas for Axis devices."""

    item_cls = ViewArea
    path = URL

    async def update(self) -> None:
        """Refresh data."""
        raw = await self.list()
        self.process_raw(raw)

    @staticmethod
    def pre_process_raw(raw: dict) -> dict:
        """Return a dictionary of view areas."""
        view_area_data = raw.get("data", {}).get("viewAreas", [])
        return {str(api["id"]): api for api in view_area_data}

    async def list(self) -> dict:
        """List the content of a view area.

        It is possible to list either one or multiple profiles and if the parameter
        streamProfileName is the empty list [] all available stream profiles will be listed.
        Security level: Viewer
        """
        return await self.vapix.request(
            "post",
            URL_INFO,
            json=attr.asdict(
                Body("list", API_VERSION),
                filter=attr.filters.exclude(attr.fields(Body).params),
            ),
        )

    async def get_supported_versions(self) -> dict:
        """Retrieve a list of supported API versions.

        Request info.cgi
        Security level: Viewer
        Method: POST
        """
        return await self.vapix.request(
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
            view_area_id = int(view_area.id)

        raw = await self.vapix.request(
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
            view_area_id = int(view_area.id)

        raw = await self.vapix.request(
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
        """Retrieve a list of supported API versions.

        Request info.cgi
        Security level: Viewer
        Method: POST
        """
        return await self.vapix.request(
            "post",
            URL_CONFIG,
            json=attr.asdict(
                Body("getSupportedVersions", API_VERSION),
                filter=attr.filters.include(attr.fields(Body).method),
            ),
        )
