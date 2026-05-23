"""Temperature control API."""

from ..models.api_discovery import ApiId
from ..models.temperature_control import (
    API_VERSION,
    GetStatusAllRequest,
    TemperatureControlStatus,
)
from .api_handler import ApiHandler, HandlerGroup


class TemperatureControlHandler(ApiHandler[TemperatureControlStatus]):
    """Temperature control status for Axis devices."""

    api_id = ApiId.TEMPERATURE_CONTROL
    default_api_version = API_VERSION
    handler_groups = (HandlerGroup.API_DISCOVERY,)

    async def _api_request(self) -> dict[str, TemperatureControlStatus]:
        """Get default temperature status data."""
        return await self.get_status_all()

    async def get_status_all(self) -> dict[str, TemperatureControlStatus]:
        """Retrieve current status for all temperature devices."""
        response = await self.vapix.api_request(GetStatusAllRequest())
        return response.data
