"""Test Axis PTZ control API."""

from typing import TYPE_CHECKING
from urllib.parse import urlencode

import pytest

from axis.models.parameters.param_cgi import ParamRequest
from axis.models.ptz_cgi import (
    PtzControlRequest,
    PtzMove,
    PtzQuery,
    PtzRotation,
    PtzState,
)

from .parameters.test_ptz import PTZ_RESPONSE

from tests.conftest import MockApiRequestAssertions, MockApiResponseSpec

if TYPE_CHECKING:
    from axis.device import AxisDevice
    from axis.interfaces.ptz import PtzControl


@pytest.fixture
def ptz_control_handler(axis_device: AxisDevice) -> PtzControl:
    """Return the PTZ control mock object."""
    return axis_device.vapix.ptz


@pytest.fixture
def mock_ptz_request(mock_api_request):
    """Register PTZ control route mocks via ApiRequest classes."""

    def _register(
        *,
        text: str | None = None,
        content: bytes | None = None,
        status_code: int = 200,
        headers: dict[str, str] | None = None,
    ):
        if text is None and content is None and status_code == 200 and headers is None:
            return mock_api_request(PtzControlRequest)

        return mock_api_request(
            PtzControlRequest,
            response=MockApiResponseSpec(
                text=text,
                content=content,
                status_code=status_code,
                headers=headers,
            ),
        )

    return _register


@pytest.fixture
def mock_param_request(mock_api_request):
    """Register Param CGI route mocks via ApiRequest classes."""

    def _register(
        *,
        text: str | None = None,
        content: bytes | None = None,
        headers: dict[str, str] | None = None,
        assertions: MockApiRequestAssertions | None = None,
    ):
        return mock_api_request(
            ParamRequest,
            response=MockApiResponseSpec(text=text, content=content, headers=headers),
            assertions=assertions,
        )

    return _register


async def test_ptz_control_handler(
    mock_ptz_request, mock_param_request, ptz_control_handler: PtzControl
):
    """Verify that update ptz works."""
    route = mock_param_request(
        text=PTZ_RESPONSE,
        headers={"Content-Type": "text/plain"},
        assertions=MockApiRequestAssertions(
            content={"action": "list", "group": "root.PTZ"}
        ),
    )

    await ptz_control_handler.update()

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/param.cgi"

    assert ptz_control_handler.initialized

    ptz = ptz_control_handler["0"]
    assert ptz.camera_default == 1
    assert ptz.number_of_cameras == 1
    assert ptz.number_of_serial_ports == 1
    assert ptz.cam_ports == {"Cam1Port": 1}


async def test_ptz_control_no_input(
    mock_ptz_request, mock_param_request, ptz_control_handler: PtzControl
):
    """Verify that PTZ control without input doesn't send out anything."""
    route = mock_ptz_request()
    await ptz_control_handler.control()
    assert route.called
    assert route.calls.last.request.content == b""


async def test_ptz_control_camera_no_output(
    mock_ptz_request, mock_param_request, ptz_control_handler: PtzControl
):
    """Verify that PTZ control does not send out camera input without additional commands."""
    route = mock_ptz_request()
    await ptz_control_handler.control(camera=1)
    assert route.called
    assert route.calls.last.request.content == b""


async def test_ptz_control_camera_with_move(
    mock_ptz_request, mock_param_request, ptz_control_handler: PtzControl
):
    """Verify that PTZ control send out camera input with additional commands."""
    route = mock_ptz_request()

    await ptz_control_handler.control(camera=2, move=PtzMove.HOME)

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/com/ptz.cgi"
    assert (
        route.calls.last.request.content
        == urlencode({"camera": 2, "move": "home"}).encode()
    )


async def test_ptz_control_center(
    mock_ptz_request, mock_param_request, ptz_control_handler: PtzControl
):
    """Verify that PTZ control can send out center input."""
    route = mock_ptz_request()
    await ptz_control_handler.control(center=(30, 60))
    assert route.calls.last.request.content == urlencode({"center": "30,60"}).encode()


async def test_ptz_control_center_with_imagewidth(
    mock_ptz_request, mock_param_request, ptz_control_handler: PtzControl
):
    """Verify that PTZ control can send out center together with imagewidth."""
    route = mock_ptz_request()
    await ptz_control_handler.control(center=(30, 60), image_width=120)
    assert (
        route.calls.last.request.content
        == urlencode({"center": "30,60", "imagewidth": 120}).encode()
    )


async def test_ptz_control_areazoom(
    mock_ptz_request, mock_param_request, ptz_control_handler: PtzControl
):
    """Verify that PTZ control can send out areazoom input."""
    route = mock_ptz_request()
    await ptz_control_handler.control(area_zoom=(30, 60, 90))
    assert (
        route.calls.last.request.content == urlencode({"areazoom": "30,60,90"}).encode()
    )


async def test_ptz_control_areazoom_too_little_zoom(
    mock_ptz_request, mock_param_request, ptz_control_handler: PtzControl
):
    """Verify that PTZ control can send out areazoom input."""
    route = mock_ptz_request()
    await ptz_control_handler.control(area_zoom=(30, 60, 0))
    assert (
        route.calls.last.request.content == urlencode({"areazoom": "30,60,1"}).encode()
    )


async def test_ptz_control_areazoom_with_imageheight(
    mock_ptz_request, mock_param_request, ptz_control_handler: PtzControl
):
    """Verify that PTZ control can send out areazoom with imageheight."""
    route = mock_ptz_request()
    await ptz_control_handler.control(area_zoom=(30, 60, 90), image_height=120)
    assert (
        route.calls.last.request.content
        == urlencode({"areazoom": "30,60,90", "imageheight": 120}).encode()
    )


async def test_ptz_control_pan(
    mock_ptz_request, mock_param_request, ptz_control_handler: PtzControl
):
    """Verify that PTZ control can send out pan and its limits."""
    route = mock_ptz_request()

    await ptz_control_handler.control(pan=90)
    assert route.calls.last.request.content == urlencode({"pan": 90}).encode()

    await ptz_control_handler.control(pan=200)
    assert route.calls.last.request.content == urlencode({"pan": 180}).encode()

    await ptz_control_handler.control(pan=-200)
    assert route.calls.last.request.content == urlencode({"pan": -180}).encode()


async def test_ptz_control_tilt(
    mock_ptz_request, mock_param_request, ptz_control_handler: PtzControl
):
    """Verify that PTZ control can send out tilt and its limits."""
    route = mock_ptz_request()

    await ptz_control_handler.control(tilt=90)
    assert route.calls.last.request.content == urlencode({"tilt": 90}).encode()

    await ptz_control_handler.control(tilt=200)
    assert route.calls.last.request.content == urlencode({"tilt": 180}).encode()

    await ptz_control_handler.control(tilt=-200)
    assert route.calls.last.request.content == urlencode({"tilt": -180}).encode()


async def test_ptz_control_zoom(
    mock_ptz_request, mock_param_request, ptz_control_handler: PtzControl
):
    """Verify that PTZ control can send out zoom and its limits."""
    route = mock_ptz_request()

    await ptz_control_handler.control(zoom=90)
    assert route.calls.last.request.content == urlencode({"zoom": 90}).encode()

    await ptz_control_handler.control(zoom=10000)
    assert route.calls.last.request.content == urlencode({"zoom": 9999}).encode()

    await ptz_control_handler.control(zoom=0)
    assert route.calls.last.request.content == urlencode({"zoom": 1}).encode()


async def test_ptz_control_focus(
    mock_ptz_request, mock_param_request, ptz_control_handler: PtzControl
):
    """Verify that PTZ control can send out focus and its limits."""
    route = mock_ptz_request()

    await ptz_control_handler.control(focus=90)
    assert route.calls.last.request.content == urlencode({"focus": 90}).encode()

    await ptz_control_handler.control(focus=10000)
    assert route.calls.last.request.content == urlencode({"focus": 9999}).encode()

    await ptz_control_handler.control(focus=0)
    assert route.calls.last.request.content == urlencode({"focus": 1}).encode()


async def test_ptz_control_iris(
    mock_ptz_request, mock_param_request, ptz_control_handler: PtzControl
):
    """Verify that PTZ control can send out iris and its limits."""
    route = mock_ptz_request()

    await ptz_control_handler.control(iris=90)
    assert route.calls.last.request.content == urlencode({"iris": 90}).encode()

    await ptz_control_handler.control(iris=10000)
    assert route.calls.last.request.content == urlencode({"iris": 9999}).encode()

    await ptz_control_handler.control(iris=0)
    assert route.calls.last.request.content == urlencode({"iris": 1}).encode()


async def test_ptz_control_brightness(
    mock_ptz_request, mock_param_request, ptz_control_handler: PtzControl
):
    """Verify that PTZ control can send out brightness and its limits."""
    route = mock_ptz_request()

    await ptz_control_handler.control(brightness=90)
    assert route.calls.last.request.content == urlencode({"brightness": 90}).encode()

    await ptz_control_handler.control(brightness=10000)
    assert route.calls.last.request.content == urlencode({"brightness": 9999}).encode()

    await ptz_control_handler.control(brightness=0)
    assert route.calls.last.request.content == urlencode({"brightness": 1}).encode()


async def test_ptz_control_rpan(
    mock_ptz_request, mock_param_request, ptz_control_handler: PtzControl
):
    """Verify that PTZ control can send out rpan and its limits."""
    route = mock_ptz_request()

    await ptz_control_handler.control(relative_pan=90)
    assert route.calls.last.request.content == urlencode({"rpan": 90}).encode()

    await ptz_control_handler.control(relative_pan=400)
    assert route.calls.last.request.content == urlencode({"rpan": 360}).encode()

    await ptz_control_handler.control(relative_pan=-400)
    assert route.calls.last.request.content == urlencode({"rpan": -360}).encode()


async def test_ptz_control_rtilt(
    mock_ptz_request, mock_param_request, ptz_control_handler: PtzControl
):
    """Verify that PTZ control can send out rtilt and its limits."""
    route = mock_ptz_request()

    await ptz_control_handler.control(relative_tilt=90)
    assert route.calls.last.request.content == urlencode({"rtilt": 90}).encode()

    await ptz_control_handler.control(relative_tilt=400)
    assert route.calls.last.request.content == urlencode({"rtilt": 360}).encode()

    await ptz_control_handler.control(relative_tilt=-400)
    assert route.calls.last.request.content == urlencode({"rtilt": -360}).encode()


async def test_ptz_control_rzoom(
    mock_ptz_request, mock_param_request, ptz_control_handler: PtzControl
):
    """Verify that PTZ control can send out rzoom and its limits."""
    route = mock_ptz_request()

    await ptz_control_handler.control(relative_zoom=90)
    assert route.calls.last.request.content == urlencode({"rzoom": 90}).encode()

    await ptz_control_handler.control(relative_zoom=10000)
    assert route.calls.last.request.content == urlencode({"rzoom": 9999}).encode()

    await ptz_control_handler.control(relative_zoom=-10000)
    assert route.calls.last.request.content == urlencode({"rzoom": -9999}).encode()


async def test_ptz_control_rfocus(
    mock_ptz_request, mock_param_request, ptz_control_handler: PtzControl
):
    """Verify that PTZ control can send out rfocus and its limits."""
    route = mock_ptz_request()

    await ptz_control_handler.control(relative_focus=90)
    assert route.calls.last.request.content == urlencode({"rfocus": 90}).encode()

    await ptz_control_handler.control(relative_focus=10000)
    assert route.calls.last.request.content == urlencode({"rfocus": 9999}).encode()

    await ptz_control_handler.control(relative_focus=-10000)
    assert route.calls.last.request.content == urlencode({"rfocus": -9999}).encode()


async def test_ptz_control_riris(
    mock_ptz_request, mock_param_request, ptz_control_handler: PtzControl
):
    """Verify that PTZ control can send out riris and its limits."""
    route = mock_ptz_request()

    await ptz_control_handler.control(relative_iris=90)
    assert route.calls.last.request.content == urlencode({"riris": 90}).encode()

    await ptz_control_handler.control(relative_iris=10000)
    assert route.calls.last.request.content == urlencode({"riris": 9999}).encode()

    await ptz_control_handler.control(relative_iris=-10000)
    assert route.calls.last.request.content == urlencode({"riris": -9999}).encode()


async def test_ptz_control_rbrightness(
    mock_ptz_request, mock_param_request, ptz_control_handler: PtzControl
):
    """Verify that PTZ control can send out rbrightness and its limits."""
    route = mock_ptz_request()

    await ptz_control_handler.control(relative_brightness=90)
    assert route.calls.last.request.content == urlencode({"rbrightness": 90}).encode()

    await ptz_control_handler.control(relative_brightness=10000)
    assert route.calls.last.request.content == urlencode({"rbrightness": 9999}).encode()

    await ptz_control_handler.control(relative_brightness=-10000)
    assert (
        route.calls.last.request.content == urlencode({"rbrightness": -9999}).encode()
    )


async def test_ptz_control_continuouszoommove(
    mock_ptz_request, mock_param_request, ptz_control_handler: PtzControl
):
    """Verify that PTZ control can send out continuouszoommove and its limits."""
    route = mock_ptz_request()

    await ptz_control_handler.control(continuous_zoom_move=90)
    assert (
        route.calls.last.request.content
        == urlencode({"continuouszoommove": 90}).encode()
    )

    await ptz_control_handler.control(continuous_zoom_move=200)
    assert (
        route.calls.last.request.content
        == urlencode({"continuouszoommove": 100}).encode()
    )

    await ptz_control_handler.control(continuous_zoom_move=-200)
    assert (
        route.calls.last.request.content
        == urlencode({"continuouszoommove": -100}).encode()
    )


async def test_ptz_control_continuousfocusmove(
    mock_ptz_request, mock_param_request, ptz_control_handler: PtzControl
):
    """Verify that PTZ control can send out continuousfocusmove and its limits."""
    route = mock_ptz_request()

    await ptz_control_handler.control(continuous_focus_move=90)
    assert (
        route.calls.last.request.content
        == urlencode({"continuousfocusmove": 90}).encode()
    )

    await ptz_control_handler.control(continuous_focus_move=200)
    assert (
        route.calls.last.request.content
        == urlencode({"continuousfocusmove": 100}).encode()
    )

    await ptz_control_handler.control(continuous_focus_move=-200)
    assert (
        route.calls.last.request.content
        == urlencode({"continuousfocusmove": -100}).encode()
    )


async def test_ptz_control_continuousirismove(
    mock_ptz_request, mock_param_request, ptz_control_handler: PtzControl
):
    """Verify that PTZ control can send out continuousirismove and its limits."""
    route = mock_ptz_request()

    await ptz_control_handler.control(continuous_iris_move=90)
    assert (
        route.calls.last.request.content
        == urlencode({"continuousirismove": 90}).encode()
    )

    await ptz_control_handler.control(continuous_iris_move=200)
    assert (
        route.calls.last.request.content
        == urlencode({"continuousirismove": 100}).encode()
    )

    await ptz_control_handler.control(continuous_iris_move=-200)
    assert (
        route.calls.last.request.content
        == urlencode({"continuousirismove": -100}).encode()
    )


async def test_ptz_control_continuousbrightnessmove(
    mock_ptz_request, mock_param_request, ptz_control_handler: PtzControl
):
    """Verify that PTZ control can send out continuousbrightnessmove and its limits."""
    route = mock_ptz_request()

    await ptz_control_handler.control(continuous_brightness_move=90)
    assert (
        route.calls.last.request.content
        == urlencode({"continuousbrightnessmove": 90}).encode()
    )

    await ptz_control_handler.control(continuous_brightness_move=200)
    assert (
        route.calls.last.request.content
        == urlencode({"continuousbrightnessmove": 100}).encode()
    )

    await ptz_control_handler.control(continuous_brightness_move=-200)
    assert (
        route.calls.last.request.content
        == urlencode({"continuousbrightnessmove": -100}).encode()
    )


async def test_ptz_control_speed(
    mock_ptz_request, mock_param_request, ptz_control_handler: PtzControl
):
    """Verify that PTZ control can send out speed and its limits."""
    route = mock_ptz_request()

    await ptz_control_handler.control(speed=90)
    assert route.calls.last.request.content == urlencode({"speed": 90}).encode()

    await ptz_control_handler.control(speed=200)
    assert route.calls.last.request.content == urlencode({"speed": 100}).encode()

    await ptz_control_handler.control(speed=0)
    assert route.calls.last.request.content == urlencode({"speed": 1}).encode()


async def test_ptz_control_autofocus(
    mock_ptz_request, mock_param_request, ptz_control_handler: PtzControl
):
    """Verify that PTZ control can send out autofocus."""
    route = mock_ptz_request()

    await ptz_control_handler.control(auto_focus=True)
    assert route.calls.last.request.content == urlencode({"autofocus": "on"}).encode()


async def test_ptz_control_autoiris(
    mock_ptz_request, mock_param_request, ptz_control_handler: PtzControl
):
    """Verify that PTZ control can send out autoiris."""
    route = mock_ptz_request()

    await ptz_control_handler.control(auto_iris=False)
    assert route.calls.last.request.content == urlencode({"autoiris": "off"}).encode()


async def test_ptz_control_backlight(
    mock_ptz_request, mock_param_request, ptz_control_handler: PtzControl
):
    """Verify that PTZ control can send out backlight."""
    route = mock_ptz_request()

    await ptz_control_handler.control(backlight=False)
    assert route.calls.last.request.content == urlencode({"backlight": "off"}).encode()


async def test_ptz_control_ircutfilter(
    mock_ptz_request, mock_param_request, ptz_control_handler: PtzControl
):
    """Verify that PTZ control can send out ircutfilter."""
    route = mock_ptz_request()

    await ptz_control_handler.control(ir_cut_filter=PtzState.AUTO)
    assert (
        route.calls.last.request.content == urlencode({"ircutfilter": "auto"}).encode()
    )


async def test_ptz_control_imagerotation(
    mock_ptz_request, mock_param_request, ptz_control_handler: PtzControl
):
    """Verify that PTZ control can send out imagerotation."""
    route = mock_ptz_request()

    await ptz_control_handler.control(image_rotation=PtzRotation.ROTATION_180)
    assert (
        route.calls.last.request.content == urlencode({"imagerotation": "180"}).encode()
    )


async def test_ptz_control_continuouspantiltmove(
    mock_ptz_request, mock_param_request, ptz_control_handler: PtzControl
):
    """Verify that PTZ control can send out continuouspantiltmove and its limits."""
    route = mock_ptz_request()

    await ptz_control_handler.control(continuous_pantilt_move=(30, 60))
    assert (
        route.calls.last.request.content
        == urlencode({"continuouspantiltmove": "30,60"}).encode()
    )

    await ptz_control_handler.control(continuous_pantilt_move=(200, 200))
    assert (
        route.calls.last.request.content
        == urlencode({"continuouspantiltmove": "100,100"}).encode()
    )

    await ptz_control_handler.control(continuous_pantilt_move=(-200, -200))
    assert (
        route.calls.last.request.content
        == urlencode({"continuouspantiltmove": "-100,-100"}).encode()
    )


async def test_ptz_control_auxiliary(
    mock_ptz_request, mock_param_request, ptz_control_handler: PtzControl
):
    """Verify that PTZ control can send out auxiliary."""
    route = mock_ptz_request()
    await ptz_control_handler.control(auxiliary="any")
    assert route.calls.last.request.content == urlencode({"auxiliary": "any"}).encode()


async def test_ptz_control_gotoserverpresetname(
    mock_ptz_request, mock_param_request, ptz_control_handler: PtzControl
):
    """Verify that PTZ control can send out gotoserverpresetname."""
    route = mock_ptz_request()
    await ptz_control_handler.control(go_to_server_preset_name="any")
    assert (
        route.calls.last.request.content
        == urlencode({"gotoserverpresetname": "any"}).encode()
    )


async def test_ptz_control_gotoserverpresetno(
    mock_ptz_request, mock_param_request, ptz_control_handler: PtzControl
):
    """Verify that PTZ control can send out gotoserverpresetno."""
    route = mock_ptz_request()
    await ptz_control_handler.control(go_to_server_preset_number=1)
    assert (
        route.calls.last.request.content
        == urlencode({"gotoserverpresetno": 1}).encode()
    )


async def test_ptz_control_gotodevicepreset(
    mock_ptz_request, mock_param_request, ptz_control_handler: PtzControl
):
    """Verify that PTZ control can send out gotodevicepreset."""
    route = mock_ptz_request()
    await ptz_control_handler.control(go_to_device_preset=2)
    assert (
        route.calls.last.request.content == urlencode({"gotodevicepreset": 2}).encode()
    )


@pytest.mark.parametrize(
    ("input", "output"),
    [
        (
            PtzQuery.LIMITS,
            """MinPan=-170
MaxPan=170
MinTilt=-20
MaxTilt=90
MinZoom=1
MaxZoom=9999
MinIris=1
MaxIris=9999
MinFocus=770
MaxFocus=9999
MinFieldAngle=22
MaxFieldAngle=623
MinBrightness=1
MaxBrightness=9999""",
        ),
        (PtzQuery.MODE, "mode=normal"),
        (
            PtzQuery.POSITION,
            """pan=51.2891
tilt=46.1914
zoom=1
iris=6427
focus=8265
brightness=4999
autofocus=off
autoiris=on""",
        ),
        (
            PtzQuery.PRESETPOSALL,
            """Preset Positions for camera 1\npresetposno1=Home""",
        ),
        (
            PtzQuery.PRESETPOSCAM,
            """Preset Positions for camera 1\npresetposno1=Home""",
        ),
        (
            PtzQuery.PRESETPOSCAMDATA,
            """Preset Positions for camera 1\npresetposno1=Home""",
        ),
        (PtzQuery.SPEED, "speed=100"),
    ],
)
async def test_query_limit(
    mock_ptz_request, mock_param_request, ptz_control_handler, input, output
):
    """Verify PTZ control query limits."""
    route = mock_ptz_request(text=output, headers={"Content-Type": "text/plain"})

    response = await ptz_control_handler.query(input)

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/com/ptz.cgi"
    assert route.calls.last.request.content == urlencode({"query": input}).encode()
    assert response == output.encode()


async def test_get_configured_device_driver(
    mock_ptz_request, mock_param_request, ptz_control_handler: PtzControl
):
    """Verify listing configured device driver."""
    route = mock_ptz_request(
        text="Sony_camblock",
        headers={"Content-Type": "text/plain"},
    )

    response = await ptz_control_handler.configured_device_driver()

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/com/ptz.cgi"
    assert route.calls.last.request.content == urlencode({"whoami": 1}).encode()

    assert response == b"Sony_camblock"


async def test_get_available_ptz_commands(
    mock_ptz_request, mock_param_request, ptz_control_handler: PtzControl
):
    """Verify listing configured device driver."""
    route = mock_ptz_request(
        text="""Available commands
:
{camera=[n]}
whoami=yes
center=[x],[y]
   imagewidth=[n]
   imageheight=[n]
areazoom=[x],[y],[z]
   imagewidth=[n]
   imageheight=[n]
move={ home | up | down | left | right | upleft | upright | downleft | downright | stop }
pan=[abspos]
tilt=[abspos]
zoom=[n]
focus=[n]
iris=[n]
brightness=[offset]
rpan=[offset]
rtilt=[offset]
rzoom=[offset]
rfocus=[offset]
riris=[offset]
rbrightness=[offset]
autofocus={ on | off }
autoiris={ on | off }
ircutfilter={ on | off | auto }
backlight={ on | off }
continuouspantiltmove=[x-speed],[y-speed]
continuouszoommove=[speed]
continuousfocusmove=[speed]
auxiliary=[function]
setserverpresetname=[name]
setserverpresetno=[n]
removeserverpresetname=[name]
removeserverpresetno=[n]
gotoserverpresetname=[name]
gotoserverpresetno=[n]
speed=[n]
query={ speed | position | limits | presetposcam | presetposall }""",
        headers={"Content-Type": "text/plain"},
    )

    response = await ptz_control_handler.available_ptz_commands()

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/com/ptz.cgi"
    assert route.calls.last.request.content == urlencode({"info": 1}).encode()

    assert (
        response
        == b"""Available commands
:
{camera=[n]}
whoami=yes
center=[x],[y]
   imagewidth=[n]
   imageheight=[n]
areazoom=[x],[y],[z]
   imagewidth=[n]
   imageheight=[n]
move={ home | up | down | left | right | upleft | upright | downleft | downright | stop }
pan=[abspos]
tilt=[abspos]
zoom=[n]
focus=[n]
iris=[n]
brightness=[offset]
rpan=[offset]
rtilt=[offset]
rzoom=[offset]
rfocus=[offset]
riris=[offset]
rbrightness=[offset]
autofocus={ on | off }
autoiris={ on | off }
ircutfilter={ on | off | auto }
backlight={ on | off }
continuouspantiltmove=[x-speed],[y-speed]
continuouszoommove=[speed]
continuousfocusmove=[speed]
auxiliary=[function]
setserverpresetname=[name]
setserverpresetno=[n]
removeserverpresetname=[name]
removeserverpresetno=[n]
gotoserverpresetname=[name]
gotoserverpresetno=[n]
speed=[n]
query={ speed | position | limits | presetposcam | presetposall }"""
    )
