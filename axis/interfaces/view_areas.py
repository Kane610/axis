"""View area API.

The View Area API makes it possible to define the subsections of a camera's full view
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
    GetSupportedVersionsResponse,
    ListViewAreasRequest,
    ListViewAreasResponse,
    ResetGeometryRequest,
    SetGeometryRequest,
    ViewArea,
)
from .api_handler import ApiHandler


class ViewAreaHandler(ApiHandler[ViewArea]):
    """View areas for Axis devices."""

    api_id = ApiId.VIEW_AREA

    async def _api_request(self) -> dict[str, ViewArea]:
        """Get default data of stream profiles."""
        return await self.list_view_areas()

    async def list_view_areas(self) -> dict[str, ViewArea]:
        """List all view areas of device."""
        discovery_item = self.vapix.api_discovery[self.api_id]
        bytes_data = await self.vapix.api_request(
            ListViewAreasRequest(discovery_item.version)
        )
        response = ListViewAreasResponse.decode(bytes_data)
        return response.data

    async def set_geometry(self, id: int, geometry: Geometry) -> dict[str, ViewArea]:
        """Set geometry of a view area.

        Security level: Admin
        Method: POST
        """
        discovery_item = self.vapix.api_discovery[self.api_id]
        bytes_data = await self.vapix.api_request(
            SetGeometryRequest(
                id=id,
                geometry=geometry,
                api_version=discovery_item.version,
            )
        )
        response = ListViewAreasResponse.decode(bytes_data)
        return response.data

    async def reset_geometry(self, id: int) -> dict[str, ViewArea]:
        """Restore geometry of a view area back to default values.

        Security level: Admin
        Method: POST
        """
        discovery_item = self.vapix.api_discovery[self.api_id]
        bytes_data = await self.vapix.api_request(
            ResetGeometryRequest(id=id, api_version=discovery_item.version)
        )
        response = ListViewAreasResponse.decode(bytes_data)
        return response.data

    async def get_supported_versions(self) -> list[str]:
        """List supported API versions."""
        bytes_data = await self.vapix.api_request(GetSupportedVersionsRequest())
        response = GetSupportedVersionsResponse.decode(bytes_data)
        return response.data

    async def get_supported_config_versions(self) -> list[str]:
        """List supported configure API versions."""
        bytes_data = await self.vapix.api_request(GetSupportedConfigVersionsRequest())
        response = GetSupportedVersionsResponse.decode(bytes_data)
        return response.data
