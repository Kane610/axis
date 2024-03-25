"""PTZ control API.

Control the pan, tilt and zoom behavior of a PTZ unit.
The PTZ control is device-dependent. For information about supported parameters
and actual parameter values, check the specification of the Axis PTZ driver used.
"""

from ..models.parameters.ptz import PtzParam
from ..models.ptz_cgi import (
    DeviceDriverRequest,
    PtzCommandRequest,
    PtzControlRequest,
    PtzMove,
    PtzQuery,
    PtzRotation,
    PtzState,
    QueryRequest,
)
from .api_handler import ApiHandler


class PtzControl(ApiHandler[PtzParam]):
    """Configure and control the PTZ functionality."""

    async def _api_request(self) -> dict[str, PtzParam]:
        """Get API data method defined by subclass."""
        return await self.get_ptz()

    async def get_ptz(self) -> dict[str, PtzParam]:
        """Retrieve privilege rights for current user."""
        await self.vapix.params.ptz_handler.update()
        return self.process_ptz()

    def process_ptz(self) -> dict[str, PtzParam]:
        """Process ports."""
        return dict(self.vapix.params.ptz_handler.items())

    async def control(
        self,
        camera: int | None = None,
        center: tuple[int, int] | None = None,
        area_zoom: tuple[int, int, int] | None = None,
        image_width: int | None = None,
        image_height: int | None = None,
        move: PtzMove | None = None,
        pan: float | None = None,
        tilt: float | None = None,
        zoom: int | None = None,
        focus: int | None = None,
        iris: int | None = None,
        brightness: int | None = None,
        relative_pan: float | None = None,
        relative_tilt: float | None = None,
        relative_zoom: int | None = None,
        relative_focus: int | None = None,
        relative_iris: int | None = None,
        relative_brightness: int | None = None,
        auto_focus: bool | None = None,
        auto_iris: bool | None = None,
        continuous_pantilt_move: tuple[int, int] | None = None,
        continuous_zoom_move: int | None = None,
        continuous_focus_move: int | None = None,
        continuous_iris_move: int | None = None,
        continuous_brightness_move: int | None = None,
        auxiliary: str | None = None,
        go_to_server_preset_name: str | None = None,
        go_to_server_preset_number: int | None = None,
        go_to_device_preset: int | None = None,
        speed: int | None = None,
        image_rotation: PtzRotation | None = None,
        ir_cut_filter: PtzState | None = None,
        backlight: bool | None = None,
    ) -> None:
        """Control the pan, tilt and zoom behavior of a PTZ unit."""
        await self.vapix.api_request(
            PtzControlRequest(
                camera=camera,
                center=center,
                area_zoom=area_zoom,
                image_width=image_width,
                image_height=image_height,
                move=move,
                pan=pan,
                tilt=tilt,
                zoom=zoom,
                focus=focus,
                iris=iris,
                brightness=brightness,
                relative_pan=relative_pan,
                relative_tilt=relative_tilt,
                relative_zoom=relative_zoom,
                relative_focus=relative_focus,
                relative_iris=relative_iris,
                relative_brightness=relative_brightness,
                auto_focus=auto_focus,
                auto_iris=auto_iris,
                continuous_pantilt_move=continuous_pantilt_move,
                continuous_zoom_move=continuous_zoom_move,
                continuous_focus_move=continuous_focus_move,
                continuous_iris_move=continuous_iris_move,
                continuous_brightness_move=continuous_brightness_move,
                auxiliary=auxiliary,
                go_to_server_preset_name=go_to_server_preset_name,
                go_to_server_preset_number=go_to_server_preset_number,
                go_to_device_preset=go_to_device_preset,
                speed=speed,
                image_rotation=image_rotation,
                ir_cut_filter=ir_cut_filter,
                backlight=backlight,
            )
        )

    async def query(self, query: PtzQuery) -> bytes:
        """Retrieve current status."""
        return await self.vapix.api_request(QueryRequest(query))

    async def configured_device_driver(self) -> bytes:
        """Name of the system-configured device driver."""
        return await self.vapix.api_request(DeviceDriverRequest())

    async def available_ptz_commands(self) -> bytes:
        """Available PTZ commands."""
        return await self.vapix.api_request(PtzCommandRequest())
