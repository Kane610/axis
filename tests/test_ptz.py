"""Test Axis PTZ control API.

pytest --cov-report term-missing --cov=axis.ptz tests/test_ptz.py
"""

import pytest
from urllib.parse import urlencode

import respx

from axis.ptz import (
    AUTO,
    MOVE_HOME,
    OFF,
    ON,
    PtzControl,
    QUERY_LIMITS,
    QUERY_MODE,
    QUERY_POSITION,
    QUERY_PRESETPOSALL,
    QUERY_PRESETPOSCAM,
    QUERY_PRESETPOSCAMDATA,
    QUERY_SPEED,
    limit,
)

from .conftest import HOST

UNSUPPORTED_COMMAND = "unsupported"


@pytest.fixture
def ptz_control(axis_device) -> PtzControl:
    """Returns the PTZ control mock object."""
    return PtzControl(axis_device.vapix.request)


def test_limit():
    """Verify limit function works as expected."""
    assert limit(1, 0, 2) == 1
    assert limit(0, 0, 2) == 0
    assert limit(-1, 0, 2) == 0
    assert limit(2, 0, 2) == 2
    assert limit(3, 0, 2) == 2


@respx.mock
@pytest.mark.asyncio
async def test_ptz_control_no_input(ptz_control):
    """Verify that PTZ control without input doesn't send out anything."""
    route = respx.get(f"http://{HOST}:80/axis-cgi/com/ptz.cgi")
    await ptz_control.control()
    assert not route.called


@respx.mock
@pytest.mark.asyncio
async def test_ptz_control_camera_no_output(ptz_control):
    """Verify that PTZ control does not send out camera input without additional commands."""
    route = respx.get(f"http://{HOST}:80/axis-cgi/com/ptz.cgi")
    await ptz_control.control(camera=1)
    assert not route.called


@respx.mock
@pytest.mark.asyncio
async def test_ptz_control_camera_with_move(ptz_control):
    """Verify that PTZ control send out camera input with additional commands."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi")

    await ptz_control.control(camera=2, move=MOVE_HOME)

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/com/ptz.cgi"
    assert (
        route.calls.last.request.content
        == urlencode({"camera": 2, "move": MOVE_HOME}).encode()
    )


@respx.mock
@pytest.mark.asyncio
async def test_ptz_control_center(ptz_control):
    """Verify that PTZ control can send out center input."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi")
    await ptz_control.control(center=(30, 60))
    assert route.calls.last.request.content == urlencode({"center": "30,60"}).encode()


@respx.mock
@pytest.mark.asyncio
async def test_ptz_control_center_with_imagewidth(ptz_control):
    """Verify that PTZ control can send out center together with imagewidth."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi")
    await ptz_control.control(center=(30, 60), imagewidth=120)
    assert (
        route.calls.last.request.content
        == urlencode({"center": "30,60", "imagewidth": 120}).encode()
    )


@respx.mock
@pytest.mark.asyncio
async def test_ptz_control_areazoom(ptz_control):
    """Verify that PTZ control can send out areazoom input."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi")
    await ptz_control.control(areazoom=(30, 60, 90))
    assert (
        route.calls.last.request.content == urlencode({"areazoom": "30,60,90"}).encode()
    )


@respx.mock
@pytest.mark.asyncio
async def test_ptz_control_areazoom_too_little_zoom(ptz_control):
    """Verify that PTZ control can send out areazoom input."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi")
    await ptz_control.control(areazoom=(30, 60, 0))
    assert (
        route.calls.last.request.content == urlencode({"areazoom": "30,60,1"}).encode()
    )


@respx.mock
@pytest.mark.asyncio
async def test_ptz_control_areazoom_with_imageheight(ptz_control):
    """Verify that PTZ control can send out areazoom with imageheight."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi")
    await ptz_control.control(areazoom=(30, 60, 90), imageheight=120)
    assert (
        route.calls.last.request.content
        == urlencode({"areazoom": "30,60,90", "imageheight": 120}).encode()
    )


@respx.mock
@pytest.mark.asyncio
async def test_ptz_control_camera_with_unsupported_move(ptz_control):
    """Verify that PTZ control only send out supported moves."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi")
    await ptz_control.control(move=UNSUPPORTED_COMMAND)
    assert not route.called


@respx.mock
@pytest.mark.asyncio
async def test_ptz_control_pan(ptz_control):
    """Verify that PTZ control can send out pan and its limits."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi")

    await ptz_control.control(pan=90)
    assert route.calls.last.request.content == urlencode({"pan": 90}).encode()

    await ptz_control.control(pan=200)
    assert route.calls.last.request.content == urlencode({"pan": 180}).encode()

    await ptz_control.control(pan=-200)
    assert route.calls.last.request.content == urlencode({"pan": -180}).encode()


@respx.mock
@pytest.mark.asyncio
async def test_ptz_control_tilt(ptz_control):
    """Verify that PTZ control can send out tilt and its limits."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi")

    await ptz_control.control(tilt=90)
    assert route.calls.last.request.content == urlencode({"tilt": 90}).encode()

    await ptz_control.control(tilt=200)
    assert route.calls.last.request.content == urlencode({"tilt": 180}).encode()

    await ptz_control.control(tilt=-200)
    assert route.calls.last.request.content == urlencode({"tilt": -180}).encode()


@respx.mock
@pytest.mark.asyncio
async def test_ptz_control_zoom(ptz_control):
    """Verify that PTZ control can send out zoom and its limits."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi")

    await ptz_control.control(zoom=90)
    assert route.calls.last.request.content == urlencode({"zoom": 90}).encode()

    await ptz_control.control(zoom=10000)
    assert route.calls.last.request.content == urlencode({"zoom": 9999}).encode()

    await ptz_control.control(zoom=0)
    assert route.calls.last.request.content == urlencode({"zoom": 1}).encode()


@respx.mock
@pytest.mark.asyncio
async def test_ptz_control_focus(ptz_control):
    """Verify that PTZ control can send out focus and its limits."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi")

    await ptz_control.control(focus=90)
    assert route.calls.last.request.content == urlencode({"focus": 90}).encode()

    await ptz_control.control(focus=10000)
    assert route.calls.last.request.content == urlencode({"focus": 9999}).encode()

    await ptz_control.control(focus=0)
    assert route.calls.last.request.content == urlencode({"focus": 1}).encode()


@respx.mock
@pytest.mark.asyncio
async def test_ptz_control_iris(ptz_control):
    """Verify that PTZ control can send out iris and its limits."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi")

    await ptz_control.control(iris=90)
    assert route.calls.last.request.content == urlencode({"iris": 90}).encode()

    await ptz_control.control(iris=10000)
    assert route.calls.last.request.content == urlencode({"iris": 9999}).encode()

    await ptz_control.control(iris=0)
    assert route.calls.last.request.content == urlencode({"iris": 1}).encode()


@respx.mock
@pytest.mark.asyncio
async def test_ptz_control_brightness(ptz_control):
    """Verify that PTZ control can send out brightness and its limits."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi")

    await ptz_control.control(brightness=90)
    assert route.calls.last.request.content == urlencode({"brightness": 90}).encode()

    await ptz_control.control(brightness=10000)
    assert route.calls.last.request.content == urlencode({"brightness": 9999}).encode()

    await ptz_control.control(brightness=0)
    assert route.calls.last.request.content == urlencode({"brightness": 1}).encode()


@respx.mock
@pytest.mark.asyncio
async def test_ptz_control_rpan(ptz_control):
    """Verify that PTZ control can send out rpan and its limits."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi")

    await ptz_control.control(rpan=90)
    assert route.calls.last.request.content == urlencode({"rpan": 90}).encode()

    await ptz_control.control(rpan=400)
    assert route.calls.last.request.content == urlencode({"rpan": 360}).encode()

    await ptz_control.control(rpan=-400)
    assert route.calls.last.request.content == urlencode({"rpan": -360}).encode()


@respx.mock
@pytest.mark.asyncio
async def test_ptz_control_rtilt(ptz_control):
    """Verify that PTZ control can send out rtilt and its limits."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi")

    await ptz_control.control(rtilt=90)
    assert route.calls.last.request.content == urlencode({"rtilt": 90}).encode()

    await ptz_control.control(rtilt=400)
    assert route.calls.last.request.content == urlencode({"rtilt": 360}).encode()

    await ptz_control.control(rtilt=-400)
    assert route.calls.last.request.content == urlencode({"rtilt": -360}).encode()


@respx.mock
@pytest.mark.asyncio
async def test_ptz_control_rzoom(ptz_control):
    """Verify that PTZ control can send out rzoom and its limits."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi")

    await ptz_control.control(rzoom=90)
    assert route.calls.last.request.content == urlencode({"rzoom": 90}).encode()

    await ptz_control.control(rzoom=10000)
    assert route.calls.last.request.content == urlencode({"rzoom": 9999}).encode()

    await ptz_control.control(rzoom=-10000)
    assert route.calls.last.request.content == urlencode({"rzoom": -9999}).encode()


@respx.mock
@pytest.mark.asyncio
async def test_ptz_control_rfocus(ptz_control):
    """Verify that PTZ control can send out rfocus and its limits."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi")

    await ptz_control.control(rfocus=90)
    assert route.calls.last.request.content == urlencode({"rfocus": 90}).encode()

    await ptz_control.control(rfocus=10000)
    assert route.calls.last.request.content == urlencode({"rfocus": 9999}).encode()

    await ptz_control.control(rfocus=-10000)
    assert route.calls.last.request.content == urlencode({"rfocus": -9999}).encode()


@respx.mock
@pytest.mark.asyncio
async def test_ptz_control_riris(ptz_control):
    """Verify that PTZ control can send out riris and its limits."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi")

    await ptz_control.control(riris=90)
    assert route.calls.last.request.content == urlencode({"riris": 90}).encode()

    await ptz_control.control(riris=10000)
    assert route.calls.last.request.content == urlencode({"riris": 9999}).encode()

    await ptz_control.control(riris=-10000)
    assert route.calls.last.request.content == urlencode({"riris": -9999}).encode()


@respx.mock
@pytest.mark.asyncio
async def test_ptz_control_rbrightness(ptz_control):
    """Verify that PTZ control can send out rbrightness and its limits."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi")

    await ptz_control.control(rbrightness=90)
    assert route.calls.last.request.content == urlencode({"rbrightness": 90}).encode()

    await ptz_control.control(rbrightness=10000)
    assert route.calls.last.request.content == urlencode({"rbrightness": 9999}).encode()

    await ptz_control.control(rbrightness=-10000)
    assert (
        route.calls.last.request.content == urlencode({"rbrightness": -9999}).encode()
    )


@respx.mock
@pytest.mark.asyncio
async def test_ptz_control_continuouszoommove(ptz_control):
    """Verify that PTZ control can send out continuouszoommove and its limits."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi")

    await ptz_control.control(continuouszoommove=90)
    assert (
        route.calls.last.request.content
        == urlencode({"continuouszoommove": 90}).encode()
    )

    await ptz_control.control(continuouszoommove=200)
    assert (
        route.calls.last.request.content
        == urlencode({"continuouszoommove": 100}).encode()
    )

    await ptz_control.control(continuouszoommove=-200)
    assert (
        route.calls.last.request.content
        == urlencode({"continuouszoommove": -100}).encode()
    )


@respx.mock
@pytest.mark.asyncio
async def test_ptz_control_continuousfocusmove(ptz_control):
    """Verify that PTZ control can send out continuousfocusmove and its limits."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi")

    await ptz_control.control(continuousfocusmove=90)
    assert (
        route.calls.last.request.content
        == urlencode({"continuousfocusmove": 90}).encode()
    )

    await ptz_control.control(continuousfocusmove=200)
    assert (
        route.calls.last.request.content
        == urlencode({"continuousfocusmove": 100}).encode()
    )

    await ptz_control.control(continuousfocusmove=-200)
    assert (
        route.calls.last.request.content
        == urlencode({"continuousfocusmove": -100}).encode()
    )


@respx.mock
@pytest.mark.asyncio
async def test_ptz_control_continuousirismove(ptz_control):
    """Verify that PTZ control can send out continuousirismove and its limits."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi")

    await ptz_control.control(continuousirismove=90)
    assert (
        route.calls.last.request.content
        == urlencode({"continuousirismove": 90}).encode()
    )

    await ptz_control.control(continuousirismove=200)
    assert (
        route.calls.last.request.content
        == urlencode({"continuousirismove": 100}).encode()
    )

    await ptz_control.control(continuousirismove=-200)
    assert (
        route.calls.last.request.content
        == urlencode({"continuousirismove": -100}).encode()
    )


@respx.mock
@pytest.mark.asyncio
async def test_ptz_control_continuousbrightnessmove(ptz_control):
    """Verify that PTZ control can send out continuousbrightnessmove and its limits."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi")

    await ptz_control.control(continuousbrightnessmove=90)
    assert (
        route.calls.last.request.content
        == urlencode({"continuousbrightnessmove": 90}).encode()
    )

    await ptz_control.control(continuousbrightnessmove=200)
    assert (
        route.calls.last.request.content
        == urlencode({"continuousbrightnessmove": 100}).encode()
    )

    await ptz_control.control(continuousbrightnessmove=-200)
    assert (
        route.calls.last.request.content
        == urlencode({"continuousbrightnessmove": -100}).encode()
    )


@respx.mock
@pytest.mark.asyncio
async def test_ptz_control_speed(ptz_control):
    """Verify that PTZ control can send out speed and its limits."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi")

    await ptz_control.control(speed=90)
    assert route.calls.last.request.content == urlencode({"speed": 90}).encode()

    await ptz_control.control(speed=200)
    assert route.calls.last.request.content == urlencode({"speed": 100}).encode()

    await ptz_control.control(speed=0)
    assert route.calls.last.request.content == urlencode({"speed": 1}).encode()


@respx.mock
@pytest.mark.asyncio
async def test_ptz_control_autofocus(ptz_control):
    """Verify that PTZ control can send out autofocus."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi")

    await ptz_control.control(autofocus=UNSUPPORTED_COMMAND)
    assert not route.called

    await ptz_control.control(autofocus=ON)
    assert route.calls.last.request.content == urlencode({"autofocus": ON}).encode()


@respx.mock
@pytest.mark.asyncio
async def test_ptz_control_autoiris(ptz_control):
    """Verify that PTZ control can send out autoiris."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi")

    await ptz_control.control(autoiris=UNSUPPORTED_COMMAND)
    assert not route.called

    await ptz_control.control(autoiris=OFF)
    assert route.calls.last.request.content == urlencode({"autoiris": OFF}).encode()


@respx.mock
@pytest.mark.asyncio
async def test_ptz_control_backlight(ptz_control):
    """Verify that PTZ control can send out backlight."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi")

    await ptz_control.control(backlight=UNSUPPORTED_COMMAND)
    assert not route.called

    await ptz_control.control(backlight=OFF)
    assert route.calls.last.request.content == urlencode({"backlight": OFF}).encode()


@respx.mock
@pytest.mark.asyncio
async def test_ptz_control_ircutfilter(ptz_control):
    """Verify that PTZ control can send out ircutfilter."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi")

    await ptz_control.control(ircutfilter=UNSUPPORTED_COMMAND)
    assert not route.called

    await ptz_control.control(ircutfilter=AUTO)
    assert route.calls.last.request.content == urlencode({"ircutfilter": AUTO}).encode()


@respx.mock
@pytest.mark.asyncio
async def test_ptz_control_imagerotation(ptz_control):
    """Verify that PTZ control can send out imagerotation."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi")

    await ptz_control.control(imagerotation=UNSUPPORTED_COMMAND)
    assert not route.called

    await ptz_control.control(imagerotation=180)
    assert (
        route.calls.last.request.content == urlencode({"imagerotation": 180}).encode()
    )


@respx.mock
@pytest.mark.asyncio
async def test_ptz_control_continuouspantiltmove(ptz_control):
    """Verify that PTZ control can send out continuouspantiltmove and its limits."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi")

    await ptz_control.control(continuouspantiltmove=(30, 60))
    assert (
        route.calls.last.request.content
        == urlencode({"continuouspantiltmove": "30,60"}).encode()
    )

    await ptz_control.control(continuouspantiltmove=(200, 200))
    assert (
        route.calls.last.request.content
        == urlencode({"continuouspantiltmove": "100,100"}).encode()
    )

    await ptz_control.control(continuouspantiltmove=(-200, -200))
    assert (
        route.calls.last.request.content
        == urlencode({"continuouspantiltmove": "-100,-100"}).encode()
    )


@respx.mock
@pytest.mark.asyncio
async def test_ptz_control_auxiliary(ptz_control):
    """Verify that PTZ control can send out auxiliary."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi")
    await ptz_control.control(auxiliary="any")
    assert route.calls.last.request.content == urlencode({"auxiliary": "any"}).encode()


@respx.mock
@pytest.mark.asyncio
async def test_ptz_control_gotoserverpresetname(ptz_control):
    """Verify that PTZ control can send out gotoserverpresetname."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi")
    await ptz_control.control(gotoserverpresetname="any")
    assert (
        route.calls.last.request.content
        == urlencode({"gotoserverpresetname": "any"}).encode()
    )


@respx.mock
@pytest.mark.asyncio
async def test_ptz_control_gotoserverpresetno(ptz_control):
    """Verify that PTZ control can send out gotoserverpresetno."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi")
    await ptz_control.control(gotoserverpresetno="any")
    assert (
        route.calls.last.request.content
        == urlencode({"gotoserverpresetno": "any"}).encode()
    )


@respx.mock
@pytest.mark.asyncio
async def test_ptz_control_gotodevicepreset(ptz_control):
    """Verify that PTZ control can send out gotodevicepreset."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi")
    await ptz_control.control(gotodevicepreset="any")
    assert (
        route.calls.last.request.content
        == urlencode({"gotodevicepreset": "any"}).encode()
    )


@respx.mock
@pytest.mark.asyncio
async def test_query_limit(ptz_control):
    """Verify PTZ control query limits."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi").respond(
        text="""MinPan=-170
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
        headers={"Content-Type": "text/plain"},
    )

    response = await ptz_control.query(QUERY_LIMITS)

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/com/ptz.cgi"
    assert (
        route.calls.last.request.content == urlencode({"query": QUERY_LIMITS}).encode()
    )
    assert (
        response
        == """MinPan=-170
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
MaxBrightness=9999"""
    )


@respx.mock
@pytest.mark.asyncio
async def test_query_mode(ptz_control):
    """Verify PTZ control query modes."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi").respond(
        text="mode=normal",
        headers={"Content-Type": "text/plain"},
    )

    response = await ptz_control.query(QUERY_MODE)

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/com/ptz.cgi"
    assert route.calls.last.request.content == urlencode({"query": QUERY_MODE}).encode()
    assert response == "mode=normal"


@respx.mock
@pytest.mark.asyncio
async def test_query_position(ptz_control):
    """Verify PTZ control query positions."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi").respond(
        text="""pan=51.2891
tilt=46.1914
zoom=1
iris=6427
focus=8265
brightness=4999
autofocus=off
autoiris=on""",
        headers={"Content-Type": "text/plain"},
    )

    response = await ptz_control.query(QUERY_POSITION)

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/com/ptz.cgi"
    assert (
        route.calls.last.request.content
        == urlencode({"query": QUERY_POSITION}).encode()
    )
    assert (
        response
        == """pan=51.2891
tilt=46.1914
zoom=1
iris=6427
focus=8265
brightness=4999
autofocus=off
autoiris=on"""
    )


@respx.mock
@pytest.mark.asyncio
async def test_query_presetposall(ptz_control):
    """Verify PTZ control query presetposalls."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi").respond(
        text="""Preset Positions for camera 1
presetposno1=Home""",
        headers={"Content-Type": "text/plain"},
    )

    response = await ptz_control.query(QUERY_PRESETPOSALL)

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/com/ptz.cgi"
    assert (
        route.calls.last.request.content
        == urlencode({"query": QUERY_PRESETPOSALL}).encode()
    )
    assert (
        response
        == """Preset Positions for camera 1
presetposno1=Home"""
    )


@respx.mock
@pytest.mark.asyncio
async def test_query_presetposcam(ptz_control):
    """Verify PTZ control query presetposcams."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi").respond(
        text="""Preset Positions for camera 1
presetposno1=Home""",
        headers={"Content-Type": "text/plain"},
    )

    response = await ptz_control.query(QUERY_PRESETPOSCAM)

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/com/ptz.cgi"
    assert (
        route.calls.last.request.content
        == urlencode({"query": QUERY_PRESETPOSCAM}).encode()
    )
    assert (
        response
        == """Preset Positions for camera 1
presetposno1=Home"""
    )


@respx.mock
@pytest.mark.asyncio
async def test_query_presetposcamdata(ptz_control):
    """Verify PTZ control query presetposcamdatas."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi").respond(
        text="""Preset Positions for camera 1
presetposno1=Home""",
        headers={"Content-Type": "text/plain"},
    )

    response = await ptz_control.query(QUERY_PRESETPOSCAMDATA)

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/com/ptz.cgi"
    assert (
        route.calls.last.request.content
        == urlencode({"query": QUERY_PRESETPOSCAMDATA}).encode()
    )
    assert (
        response
        == """Preset Positions for camera 1
presetposno1=Home"""
    )


@respx.mock
@pytest.mark.asyncio
async def test_query_speed(ptz_control):
    """Verify PTZ control query speeds."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi").respond(
        text="speed=100",
        headers={"Content-Type": "text/plain"},
    )

    response = await ptz_control.query(QUERY_SPEED)

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/com/ptz.cgi"
    assert (
        route.calls.last.request.content == urlencode({"query": QUERY_SPEED}).encode()
    )
    assert response == "speed=100"


@respx.mock
@pytest.mark.asyncio
async def test_query_unsupported_command(ptz_control):
    """Verify PTZ control query doesn't send unsupported commands."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/com/ptz.cgi")
    await ptz_control.query(UNSUPPORTED_COMMAND)
    assert not route.called


@respx.mock
@pytest.mark.asyncio
async def test_get_configured_device_driver(ptz_control):
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

    assert response == "Sony_camblock"


@respx.mock
@pytest.mark.asyncio
async def test_get_available_ptz_commands(ptz_control):
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
        == """Available commands
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
