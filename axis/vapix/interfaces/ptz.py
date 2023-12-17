"""PTZ control API.

Control the pan, tilt and zoom behavior of a PTZ unit.
The PTZ control is device-dependent. For information about supported parameters
and actual parameter values, check the specification of the Axis PTZ driver used.
"""

from ..models.parameters.ptz import GetPtzResponse, PtzItem
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


class PtzControl(ApiHandler[PtzItem]):
    """Configure and control the PTZ functionality."""

    async def _api_request(self) -> dict[str, PtzItem]:
        """Get API data method defined by subclass."""
        return await self.get_ptz()

    async def get_ptz(self) -> dict[str, PtzItem]:
        """Retrieve privilege rights for current user."""
        await self.vapix.params.update("PTZ")
        return self.process_ptz()

    def process_ptz(self) -> dict[str, PtzItem]:
        """Process ports."""
        return GetPtzResponse.from_dict(self.vapix.params.get_param("PTZ")).data

    async def control(
        self,
        camera: int | None = None,
        center: tuple[int, int] | None = None,
        areazoom: tuple[int, int, int] | None = None,
        imagewidth: int | None = None,
        imageheight: int | None = None,
        move: PtzMove | None = None,
        pan: float | None = None,
        tilt: float | None = None,
        zoom: int | None = None,
        focus: int | None = None,
        iris: int | None = None,
        brightness: int | None = None,
        rpan: float | None = None,
        rtilt: float | None = None,
        rzoom: int | None = None,
        rfocus: int | None = None,
        riris: int | None = None,
        rbrightness: int | None = None,
        autofocus: bool | None = None,
        autoiris: bool | None = None,
        continuouspantiltmove: tuple[int, int] | None = None,
        continuouszoommove: int | None = None,
        continuousfocusmove: int | None = None,
        continuousirismove: int | None = None,
        continuousbrightnessmove: int | None = None,
        auxiliary: str | None = None,
        gotoserverpresetname: str | None = None,
        gotoserverpresetno: int | None = None,
        gotodevicepreset: int | None = None,
        speed: int | None = None,
        imagerotation: PtzRotation | None = None,
        ircutfilter: PtzState | None = None,
        backlight: bool | None = None,
    ) -> None:
        """Control the pan, tilt and zoom behavior of a PTZ unit."""
        await self.vapix.new_request(
            PtzControlRequest(
                camera,
                center,
                areazoom,
                imagewidth,
                imageheight,
                move,
                pan,
                tilt,
                zoom,
                focus,
                iris,
                brightness,
                rpan,
                rtilt,
                rzoom,
                rfocus,
                riris,
                rbrightness,
                autofocus,
                autoiris,
                continuouspantiltmove,
                continuouszoommove,
                continuousfocusmove,
                continuousirismove,
                continuousbrightnessmove,
                auxiliary,
                gotoserverpresetname,
                gotoserverpresetno,
                gotodevicepreset,
                speed,
                imagerotation,
                ircutfilter,
                backlight,
            )
        )

    async def query(self, query: PtzQuery) -> bytes:
        """Retrieve current status."""
        return await self.vapix.new_request(QueryRequest(query))

    async def configured_device_driver(self) -> bytes:
        """Name of the system-configured device driver."""
        return await self.vapix.new_request(DeviceDriverRequest())

    async def available_ptz_commands(self) -> bytes:
        """Available PTZ commands."""
        return await self.vapix.new_request(PtzCommandRequest())
