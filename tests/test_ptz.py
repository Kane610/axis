"""Test Axis PTZ control API.

pytest --cov-report term-missing --cov=axis.ptz tests/test_ptz.py
"""

from urllib.parse import urlencode

import pytest
import respx

from axis.device import AxisDevice
from axis.vapix.interfaces.ptz import PtzControl
from axis.vapix.models.ptz_cgi import PtzMove, PtzQuery, PtzRotation, PtzState, limit

from .conftest import HOST
from .test_param_cgi import response_param_cgi_ptz

UNSUPPORTED_COMMAND = "unsupported"


@pytest.fixture
def ptz_control(axis_device: AxisDevice) -> PtzControl:
    """Return the PTZ control mock object."""
    return axis_device.vapix.ptz


def test_limit():
    """Verify limit function works as expected."""
    assert limit(1, 0, 2) == 1
    assert limit(0, 0, 2) == 0
    assert limit(-1, 0, 2) == 0
    assert limit(2, 0, 2) == 2
    assert limit(3, 0, 2) == 2


@respx.mock
async def test_update_ptz(ptz_control: PtzControl):
    """Verify that update ptz works."""
    route = respx.get(
        f"http://{HOST}:80/axis-cgi/param.cgi?action=list%26group%3Droot.PTZ"
    ).respond(
        text=response_param_cgi_ptz,
        headers={"Content-Type": "text/plain"},
    )

    await ptz_control._update()

    assert route.called
    assert route.calls.last.request.method == "GET"
    assert route.calls.last.request.url.path == "/axis-cgi/param.cgi"

    ptz = ptz_control["0"]
    assert ptz.camera_default == 1
    assert ptz.number_of_cameras == 1
    assert ptz.number_of_serial_ports == 1
    assert ptz.cam_ports == {"Cam1Port": 1}

    assert len(ptz.limits) == 1
    limit = ptz.limits["1"]
    assert limit.max_brightness == 9999
    assert limit.min_brightness == 1
    assert limit.max_field_angle == 623
    assert limit.min_field_angle == 22
    assert limit.max_focus == 9999
    assert limit.min_focus == 770
    assert limit.max_iris == 9999
    assert limit.min_iris == 1
    assert limit.max_pan == 170
    assert limit.min_pan == -170
    assert limit.max_tilt == 90
    assert limit.min_tilt == -20
    assert limit.max_zoom == 9999
    assert limit.min_zoom == 1

    assert len(ptz.support) == 1
    support = ptz.support["1"]
    assert support.absolute_brightness
    assert support.absolute_focus
    assert support.absolute_iris
    assert support.absolute_pan
    assert support.absolute_tilt
    assert support.absolute_zoom
    assert support.action_notification
    assert support.area_zoom
    assert support.auto_focus
    assert support.auto_ir_cut_filter
    assert support.auto_iris
    assert support.auxiliary
    assert support.backLight
    assert support.continuous_brightness is False
    assert support.continuous_focus
    assert support.continuous_iris is False
    assert support.continuous_pan
    assert support.continuous_tilt
    assert support.continuousZoom
    assert support.device_preset is False
    assert support.digital_zoom
    assert support.generic_http is False
    assert support.ir_cut_filter
    assert support.joystick_emulation
    assert support.lens_offset is False
    assert support.osd_menu is False
    assert support.proportional_speed
    assert support.relative_brightness
    assert support.relative_focus
    assert support.relative_iris
    assert support.relative_pan
    assert support.relative_tilt
    assert support.relative_zoom
    assert support.server_preset
    assert support.speed_control

    assert len(ptz.various) == 1
    various = ptz.various["1"]
    assert various.control_queueing is False
    assert various.control_queue_limit
    assert various.control_queue_poll_time == 20
    assert various.home_preset_set
    assert various.locked is False
    assert various.max_proportional_speed == 200
    assert various.pan_enabled
    assert various.proportional_speed_enabled
    assert various.return_to_overview == 0
    assert various.speed_control_enabled
    assert various.tilt_enabled
    assert various.zoom_enabled


@respx.mock
async def test_ptz_control_no_input(ptz_control: PtzControl):
    """Verify that PTZ control without input doesn't send out anything."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi")
    await ptz_control.control()
    assert route.called
    assert route.calls.last.request.content == b""


@respx.mock
async def test_ptz_control_camera_no_output(ptz_control: PtzControl):
    """Verify that PTZ control does not send out camera input without additional commands."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi")
    await ptz_control.control(camera=1)
    assert route.called
    assert route.calls.last.request.content == b""


@respx.mock
async def test_ptz_control_camera_with_move(ptz_control: PtzControl):
    """Verify that PTZ control send out camera input with additional commands."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi")

    await ptz_control.control(camera=2, move=PtzMove.HOME)

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/com/ptz.cgi"
    assert (
        route.calls.last.request.content
        == urlencode({"camera": 2, "move": "home"}).encode()
    )


@respx.mock
async def test_ptz_control_center(ptz_control: PtzControl):
    """Verify that PTZ control can send out center input."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi")
    await ptz_control.control(center=(30, 60))
    assert route.calls.last.request.content == urlencode({"center": "30,60"}).encode()


@respx.mock
async def test_ptz_control_center_with_imagewidth(ptz_control: PtzControl):
    """Verify that PTZ control can send out center together with imagewidth."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi")
    await ptz_control.control(center=(30, 60), image_width=120)
    assert (
        route.calls.last.request.content
        == urlencode({"center": "30,60", "imagewidth": 120}).encode()
    )


@respx.mock
async def test_ptz_control_areazoom(ptz_control: PtzControl):
    """Verify that PTZ control can send out areazoom input."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi")
    await ptz_control.control(area_zoom=(30, 60, 90))
    assert (
        route.calls.last.request.content == urlencode({"areazoom": "30,60,90"}).encode()
    )


@respx.mock
async def test_ptz_control_areazoom_too_little_zoom(ptz_control: PtzControl):
    """Verify that PTZ control can send out areazoom input."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi")
    await ptz_control.control(area_zoom=(30, 60, 0))
    assert (
        route.calls.last.request.content == urlencode({"areazoom": "30,60,1"}).encode()
    )


@respx.mock
async def test_ptz_control_areazoom_with_imageheight(ptz_control: PtzControl):
    """Verify that PTZ control can send out areazoom with imageheight."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi")
    await ptz_control.control(area_zoom=(30, 60, 90), image_height=120)
    assert (
        route.calls.last.request.content
        == urlencode({"areazoom": "30,60,90", "imageheight": 120}).encode()
    )


@respx.mock
async def test_ptz_control_pan(ptz_control: PtzControl):
    """Verify that PTZ control can send out pan and its limits."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi")

    await ptz_control.control(pan=90)
    assert route.calls.last.request.content == urlencode({"pan": 90}).encode()

    await ptz_control.control(pan=200)
    assert route.calls.last.request.content == urlencode({"pan": 180}).encode()

    await ptz_control.control(pan=-200)
    assert route.calls.last.request.content == urlencode({"pan": -180}).encode()


@respx.mock
async def test_ptz_control_tilt(ptz_control: PtzControl):
    """Verify that PTZ control can send out tilt and its limits."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi")

    await ptz_control.control(tilt=90)
    assert route.calls.last.request.content == urlencode({"tilt": 90}).encode()

    await ptz_control.control(tilt=200)
    assert route.calls.last.request.content == urlencode({"tilt": 180}).encode()

    await ptz_control.control(tilt=-200)
    assert route.calls.last.request.content == urlencode({"tilt": -180}).encode()


@respx.mock
async def test_ptz_control_zoom(ptz_control: PtzControl):
    """Verify that PTZ control can send out zoom and its limits."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi")

    await ptz_control.control(zoom=90)
    assert route.calls.last.request.content == urlencode({"zoom": 90}).encode()

    await ptz_control.control(zoom=10000)
    assert route.calls.last.request.content == urlencode({"zoom": 9999}).encode()

    await ptz_control.control(zoom=0)
    assert route.calls.last.request.content == urlencode({"zoom": 1}).encode()


@respx.mock
async def test_ptz_control_focus(ptz_control: PtzControl):
    """Verify that PTZ control can send out focus and its limits."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi")

    await ptz_control.control(focus=90)
    assert route.calls.last.request.content == urlencode({"focus": 90}).encode()

    await ptz_control.control(focus=10000)
    assert route.calls.last.request.content == urlencode({"focus": 9999}).encode()

    await ptz_control.control(focus=0)
    assert route.calls.last.request.content == urlencode({"focus": 1}).encode()


@respx.mock
async def test_ptz_control_iris(ptz_control: PtzControl):
    """Verify that PTZ control can send out iris and its limits."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi")

    await ptz_control.control(iris=90)
    assert route.calls.last.request.content == urlencode({"iris": 90}).encode()

    await ptz_control.control(iris=10000)
    assert route.calls.last.request.content == urlencode({"iris": 9999}).encode()

    await ptz_control.control(iris=0)
    assert route.calls.last.request.content == urlencode({"iris": 1}).encode()


@respx.mock
async def test_ptz_control_brightness(ptz_control: PtzControl):
    """Verify that PTZ control can send out brightness and its limits."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi")

    await ptz_control.control(brightness=90)
    assert route.calls.last.request.content == urlencode({"brightness": 90}).encode()

    await ptz_control.control(brightness=10000)
    assert route.calls.last.request.content == urlencode({"brightness": 9999}).encode()

    await ptz_control.control(brightness=0)
    assert route.calls.last.request.content == urlencode({"brightness": 1}).encode()


@respx.mock
async def test_ptz_control_rpan(ptz_control: PtzControl):
    """Verify that PTZ control can send out rpan and its limits."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi")

    await ptz_control.control(relative_pan=90)
    assert route.calls.last.request.content == urlencode({"rpan": 90}).encode()

    await ptz_control.control(relative_pan=400)
    assert route.calls.last.request.content == urlencode({"rpan": 360}).encode()

    await ptz_control.control(relative_pan=-400)
    assert route.calls.last.request.content == urlencode({"rpan": -360}).encode()


@respx.mock
async def test_ptz_control_rtilt(ptz_control: PtzControl):
    """Verify that PTZ control can send out rtilt and its limits."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi")

    await ptz_control.control(relative_tilt=90)
    assert route.calls.last.request.content == urlencode({"rtilt": 90}).encode()

    await ptz_control.control(relative_tilt=400)
    assert route.calls.last.request.content == urlencode({"rtilt": 360}).encode()

    await ptz_control.control(relative_tilt=-400)
    assert route.calls.last.request.content == urlencode({"rtilt": -360}).encode()


@respx.mock
async def test_ptz_control_rzoom(ptz_control: PtzControl):
    """Verify that PTZ control can send out rzoom and its limits."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi")

    await ptz_control.control(relative_zoom=90)
    assert route.calls.last.request.content == urlencode({"rzoom": 90}).encode()

    await ptz_control.control(relative_zoom=10000)
    assert route.calls.last.request.content == urlencode({"rzoom": 9999}).encode()

    await ptz_control.control(relative_zoom=-10000)
    assert route.calls.last.request.content == urlencode({"rzoom": -9999}).encode()


@respx.mock
async def test_ptz_control_rfocus(ptz_control: PtzControl):
    """Verify that PTZ control can send out rfocus and its limits."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi")

    await ptz_control.control(relative_focus=90)
    assert route.calls.last.request.content == urlencode({"rfocus": 90}).encode()

    await ptz_control.control(relative_focus=10000)
    assert route.calls.last.request.content == urlencode({"rfocus": 9999}).encode()

    await ptz_control.control(relative_focus=-10000)
    assert route.calls.last.request.content == urlencode({"rfocus": -9999}).encode()


@respx.mock
async def test_ptz_control_riris(ptz_control: PtzControl):
    """Verify that PTZ control can send out riris and its limits."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi")

    await ptz_control.control(relative_iris=90)
    assert route.calls.last.request.content == urlencode({"riris": 90}).encode()

    await ptz_control.control(relative_iris=10000)
    assert route.calls.last.request.content == urlencode({"riris": 9999}).encode()

    await ptz_control.control(relative_iris=-10000)
    assert route.calls.last.request.content == urlencode({"riris": -9999}).encode()


@respx.mock
async def test_ptz_control_rbrightness(ptz_control: PtzControl):
    """Verify that PTZ control can send out rbrightness and its limits."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi")

    await ptz_control.control(relative_brightness=90)
    assert route.calls.last.request.content == urlencode({"rbrightness": 90}).encode()

    await ptz_control.control(relative_brightness=10000)
    assert route.calls.last.request.content == urlencode({"rbrightness": 9999}).encode()

    await ptz_control.control(relative_brightness=-10000)
    assert (
        route.calls.last.request.content == urlencode({"rbrightness": -9999}).encode()
    )


@respx.mock
async def test_ptz_control_continuouszoommove(ptz_control: PtzControl):
    """Verify that PTZ control can send out continuouszoommove and its limits."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi")

    await ptz_control.control(continuous_zoom_move=90)
    assert (
        route.calls.last.request.content
        == urlencode({"continuouszoommove": 90}).encode()
    )

    await ptz_control.control(continuous_zoom_move=200)
    assert (
        route.calls.last.request.content
        == urlencode({"continuouszoommove": 100}).encode()
    )

    await ptz_control.control(continuous_zoom_move=-200)
    assert (
        route.calls.last.request.content
        == urlencode({"continuouszoommove": -100}).encode()
    )


@respx.mock
async def test_ptz_control_continuousfocusmove(ptz_control: PtzControl):
    """Verify that PTZ control can send out continuousfocusmove and its limits."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi")

    await ptz_control.control(continuous_focus_move=90)
    assert (
        route.calls.last.request.content
        == urlencode({"continuousfocusmove": 90}).encode()
    )

    await ptz_control.control(continuous_focus_move=200)
    assert (
        route.calls.last.request.content
        == urlencode({"continuousfocusmove": 100}).encode()
    )

    await ptz_control.control(continuous_focus_move=-200)
    assert (
        route.calls.last.request.content
        == urlencode({"continuousfocusmove": -100}).encode()
    )


@respx.mock
async def test_ptz_control_continuousirismove(ptz_control: PtzControl):
    """Verify that PTZ control can send out continuousirismove and its limits."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi")

    await ptz_control.control(continuous_iris_move=90)
    assert (
        route.calls.last.request.content
        == urlencode({"continuousirismove": 90}).encode()
    )

    await ptz_control.control(continuous_iris_move=200)
    assert (
        route.calls.last.request.content
        == urlencode({"continuousirismove": 100}).encode()
    )

    await ptz_control.control(continuous_iris_move=-200)
    assert (
        route.calls.last.request.content
        == urlencode({"continuousirismove": -100}).encode()
    )


@respx.mock
async def test_ptz_control_continuousbrightnessmove(ptz_control: PtzControl):
    """Verify that PTZ control can send out continuousbrightnessmove and its limits."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi")

    await ptz_control.control(continuous_brightness_move=90)
    assert (
        route.calls.last.request.content
        == urlencode({"continuousbrightnessmove": 90}).encode()
    )

    await ptz_control.control(continuous_brightness_move=200)
    assert (
        route.calls.last.request.content
        == urlencode({"continuousbrightnessmove": 100}).encode()
    )

    await ptz_control.control(continuous_brightness_move=-200)
    assert (
        route.calls.last.request.content
        == urlencode({"continuousbrightnessmove": -100}).encode()
    )


@respx.mock
async def test_ptz_control_speed(ptz_control: PtzControl):
    """Verify that PTZ control can send out speed and its limits."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi")

    await ptz_control.control(speed=90)
    assert route.calls.last.request.content == urlencode({"speed": 90}).encode()

    await ptz_control.control(speed=200)
    assert route.calls.last.request.content == urlencode({"speed": 100}).encode()

    await ptz_control.control(speed=0)
    assert route.calls.last.request.content == urlencode({"speed": 1}).encode()


@respx.mock
async def test_ptz_control_autofocus(ptz_control: PtzControl):
    """Verify that PTZ control can send out autofocus."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi")

    await ptz_control.control(auto_focus=True)
    assert route.calls.last.request.content == urlencode({"autofocus": "on"}).encode()


@respx.mock
async def test_ptz_control_autoiris(ptz_control: PtzControl):
    """Verify that PTZ control can send out autoiris."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi")

    await ptz_control.control(auto_iris=False)
    assert route.calls.last.request.content == urlencode({"autoiris": "off"}).encode()


@respx.mock
async def test_ptz_control_backlight(ptz_control: PtzControl):
    """Verify that PTZ control can send out backlight."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi")

    await ptz_control.control(backlight=False)
    assert route.calls.last.request.content == urlencode({"backlight": "off"}).encode()


@respx.mock
async def test_ptz_control_ircutfilter(ptz_control: PtzControl):
    """Verify that PTZ control can send out ircutfilter."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi")

    await ptz_control.control(ir_cut_filter=PtzState.AUTO)
    assert (
        route.calls.last.request.content == urlencode({"ircutfilter": "auto"}).encode()
    )


@respx.mock
async def test_ptz_control_imagerotation(ptz_control: PtzControl):
    """Verify that PTZ control can send out imagerotation."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi")

    await ptz_control.control(image_rotation=PtzRotation.ROTATION_180)
    assert (
        route.calls.last.request.content == urlencode({"imagerotation": "180"}).encode()
    )


@respx.mock
async def test_ptz_control_continuouspantiltmove(ptz_control: PtzControl):
    """Verify that PTZ control can send out continuouspantiltmove and its limits."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi")

    await ptz_control.control(continuous_pantilt_move=(30, 60))
    assert (
        route.calls.last.request.content
        == urlencode({"continuouspantiltmove": "30,60"}).encode()
    )

    await ptz_control.control(continuous_pantilt_move=(200, 200))
    assert (
        route.calls.last.request.content
        == urlencode({"continuouspantiltmove": "100,100"}).encode()
    )

    await ptz_control.control(continuous_pantilt_move=(-200, -200))
    assert (
        route.calls.last.request.content
        == urlencode({"continuouspantiltmove": "-100,-100"}).encode()
    )


@respx.mock
async def test_ptz_control_auxiliary(ptz_control: PtzControl):
    """Verify that PTZ control can send out auxiliary."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi")
    await ptz_control.control(auxiliary="any")
    assert route.calls.last.request.content == urlencode({"auxiliary": "any"}).encode()


@respx.mock
async def test_ptz_control_gotoserverpresetname(ptz_control: PtzControl):
    """Verify that PTZ control can send out gotoserverpresetname."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi")
    await ptz_control.control(go_to_server_preset_name="any")
    assert (
        route.calls.last.request.content
        == urlencode({"gotoserverpresetname": "any"}).encode()
    )


@respx.mock
async def test_ptz_control_gotoserverpresetno(ptz_control: PtzControl):
    """Verify that PTZ control can send out gotoserverpresetno."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi")
    await ptz_control.control(go_to_server_preset_number=1)
    assert (
        route.calls.last.request.content
        == urlencode({"gotoserverpresetno": 1}).encode()
    )


@respx.mock
async def test_ptz_control_gotodevicepreset(ptz_control: PtzControl):
    """Verify that PTZ control can send out gotodevicepreset."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi")
    await ptz_control.control(go_to_device_preset=2)
    assert (
        route.calls.last.request.content == urlencode({"gotodevicepreset": 2}).encode()
    )


@respx.mock
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
async def test_query_limit(ptz_control, input, output):
    """Verify PTZ control query limits."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi").respond(
        text=output, headers={"Content-Type": "text/plain"}
    )

    response = await ptz_control.query(input)

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/com/ptz.cgi"
    assert (
        route.calls.last.request.content == urlencode({"query": input.value}).encode()
    )
    assert response == output.encode()


@respx.mock
async def test_get_configured_device_driver(ptz_control: PtzControl):
    """Verify listing configured device driver."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi").respond(
        text="Sony_camblock",
        headers={"Content-Type": "text/plain"},
    )

    response = await ptz_control.configured_device_driver()

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/com/ptz.cgi"
    assert route.calls.last.request.content == urlencode({"whoami": 1}).encode()

    assert response == b"Sony_camblock"


@respx.mock
async def test_get_available_ptz_commands(ptz_control: PtzControl):
    """Verify listing configured device driver."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi").respond(
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

    response = await ptz_control.available_ptz_commands()

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
