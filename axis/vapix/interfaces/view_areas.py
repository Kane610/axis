"""View area API.

The View Area API makes it possible to define the subsections of a camera’s full view
as individual, virtual channels. This means that a wide angle and/or high resolution
camera can provide multiple video streams at a lower resolution where each stream
covers a specific region of interest. The API is also able to simplify the installation
process by fine tuning an area digitally after the camera has been manually pointed at a scene.
"""


from ..models.api_discovery import ApiId
from ..models.view_area import (
    Geometry,
    GetSupportedConfigVersionsRequest,
    GetSupportedVersionsRequest,
    ListViewAreasRequest,
    ListViewAreasT,
    ResetGeometryRequest,
    SetGeometryRequest,
    ViewArea,
)
from .api_handler import ApiHandler


class ViewAreaHandler(ApiHandler[ViewArea]):
    """View areas for Axis devices."""

    api_id = ApiId.VIEW_AREA
    api_request = ListViewAreasRequest()

    async def list_view_areas(self) -> ListViewAreasT:
        """List all view areas of device."""
        discovery_item = self.vapix.api_discovery[self.api_id.value]
        return await self.vapix.request2(ListViewAreasRequest(discovery_item.version))

    async def set_geometry(self, id: int, geometry: Geometry) -> ListViewAreasT:
        """Set geometry of a view area.

        Security level: Admin
        Method: POST
        """
        discovery_item = self.vapix.api_discovery[self.api_id.value]
        return await self.vapix.request2(
            SetGeometryRequest(
                id=id,
                geometry=geometry,
                api_version=discovery_item.version,
            )
        )

    async def reset_geometry(self, id: int) -> ListViewAreasT:
        """Restore geometry of a view area back to default values.

        Security level: Admin
        Method: POST
        """
        discovery_item = self.vapix.api_discovery[self.api_id.value]
        return await self.vapix.request2(
            ResetGeometryRequest(id=id, api_version=discovery_item.version)
        )

    async def get_supported_versions(self) -> list[str]:
        """List supported API versions."""
        return await self.vapix.request2(GetSupportedVersionsRequest())

    async def get_supported_config_versions(self) -> list[str]:
        """List supported configure API versions."""
        return await self.vapix.request2(GetSupportedConfigVersionsRequest())
