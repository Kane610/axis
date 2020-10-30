"""Test Axis PTZ control API.

pytest --cov-report term-missing --cov=axis.ptz.ptz tests/ptz/test_ptz.py
"""

import pytest
from unittest.mock import AsyncMock

from axis.ptz import AUTO, MOVE_HOME, OFF, ON, PtzControl, limit


UNSUPPORTED_COMMAND = "unsupported"


@pytest.fixture
def ptz_control() -> PtzControl:
    """Returns the PTZ control mock object."""
    mock_request = AsyncMock()
    mock_request.return_value = ""
    return PtzControl(mock_request)


def test_limit():
    """Verify limit function works as expected."""
    assert limit(1, 0, 2) == 1
    assert limit(0, 0, 2) == 0
    assert limit(-1, 0, 2) == 0
    assert limit(2, 0, 2) == 2
    assert limit(3, 0, 2) == 2


async def test_ptz_control_no_input(ptz_control):
    """Verify that PTZ control without input doesn't send out anything."""
    await ptz_control.control()
    ptz_control._request.assert_not_called()


async def test_ptz_control_camera_no_output(ptz_control):
    """Verify that PTZ control does not send out camera input without additional commands."""
    await ptz_control.control(camera=1)
    ptz_control._request.assert_not_called()


async def test_ptz_control_camera_with_move(ptz_control):
    """Verify that PTZ control send out camera input with additional commands."""
    await ptz_control.control(camera=2, move=MOVE_HOME)
    ptz_control._request.assert_called_with(
        "post", "/axis-cgi/com/ptz.cgi", data={"camera": 2, "move": MOVE_HOME}
    )


async def test_ptz_control_center(ptz_control):
    """Verify that PTZ control can send out center input."""
    await ptz_control.control(center=(30, 60))
    ptz_control._request.assert_called_with(
        "post", "/axis-cgi/com/ptz.cgi", data={"center": "30,60"}
    )


async def test_ptz_control_center_with_imagewidth(ptz_control):
    """Verify that PTZ control can send out center together with imagewidth."""
    await ptz_control.control(center=(30, 60), imagewidth=120)
    ptz_control._request.assert_called_with(
        "post", "/axis-cgi/com/ptz.cgi", data={"center": "30,60", "imagewidth": 120}
    )


async def test_ptz_control_areazoom(ptz_control):
    """Verify that PTZ control can send out areazoom input."""
    await ptz_control.control(areazoom=(30, 60, 90))
    ptz_control._request.assert_called_with(
        "post", "/axis-cgi/com/ptz.cgi", data={"areazoom": "30,60,90"}
    )


async def test_ptz_control_areazoom_too_little_zoom(ptz_control):
    """Verify that PTZ control can send out areazoom input."""
    await ptz_control.control(areazoom=(30, 60, 0))
    ptz_control._request.assert_called_with(
        "post", "/axis-cgi/com/ptz.cgi", data={"areazoom": "30,60,1"}
    )


async def test_ptz_control_areazoom_with_imageheight(ptz_control):
    """Verify that PTZ control can send out areazoom with imageheight."""
    await ptz_control.control(areazoom=(30, 60, 90), imageheight=120)
    ptz_control._request.assert_called_with(
        "post",
        "/axis-cgi/com/ptz.cgi",
        data={"areazoom": "30,60,90", "imageheight": 120},
    )


async def test_ptz_control_camera_with_unsupported_move(ptz_control):
    """Verify that PTZ control only send out supported moves."""
    await ptz_control.control(move=UNSUPPORTED_COMMAND)
    ptz_control._request.assert_not_called()


async def test_ptz_control_pan(ptz_control):
    """Verify that PTZ control can send out pan and its limits."""
    await ptz_control.control(pan=90)
    ptz_control._request.assert_called_with(
        "post",
        "/axis-cgi/com/ptz.cgi",
        data={"pan": 90},
    )

    await ptz_control.control(pan=200)
    ptz_control._request.assert_called_with(
        "post",
        "/axis-cgi/com/ptz.cgi",
        data={"pan": 180},
    )

    await ptz_control.control(pan=-200)
    ptz_control._request.assert_called_with(
        "post",
        "/axis-cgi/com/ptz.cgi",
        data={"pan": -180},
    )


async def test_ptz_control_tilt(ptz_control):
    """Verify that PTZ control can send out tilt and its limits."""
    await ptz_control.control(tilt=90)
    ptz_control._request.assert_called_with(
        "post",
        "/axis-cgi/com/ptz.cgi",
        data={"tilt": 90},
    )

    await ptz_control.control(tilt=200)
    ptz_control._request.assert_called_with(
        "post",
        "/axis-cgi/com/ptz.cgi",
        data={"tilt": 180},
    )

    await ptz_control.control(tilt=-200)
    ptz_control._request.assert_called_with(
        "post",
        "/axis-cgi/com/ptz.cgi",
        data={"tilt": -180},
    )


async def test_ptz_control_zoom(ptz_control):
    """Verify that PTZ control can send out zoom and its limits."""
    await ptz_control.control(zoom=90)
    ptz_control._request.assert_called_with(
        "post",
        "/axis-cgi/com/ptz.cgi",
        data={"zoom": 90},
    )

    await ptz_control.control(zoom=10000)
    ptz_control._request.assert_called_with(
        "post",
        "/axis-cgi/com/ptz.cgi",
        data={"zoom": 9999},
    )

    await ptz_control.control(zoom=0)
    ptz_control._request.assert_called_with(
        "post",
        "/axis-cgi/com/ptz.cgi",
        data={"zoom": 1},
    )


async def test_ptz_control_focus(ptz_control):
    """Verify that PTZ control can send out focus and its limits."""
    await ptz_control.control(focus=90)
    ptz_control._request.assert_called_with(
        "post",
        "/axis-cgi/com/ptz.cgi",
        data={"focus": 90},
    )

    await ptz_control.control(focus=10000)
    ptz_control._request.assert_called_with(
        "post",
        "/axis-cgi/com/ptz.cgi",
        data={"focus": 9999},
    )

    await ptz_control.control(focus=0)
    ptz_control._request.assert_called_with(
        "post",
        "/axis-cgi/com/ptz.cgi",
        data={"focus": 1},
    )


async def test_ptz_control_iris(ptz_control):
    """Verify that PTZ control can send out iris and its limits."""
    await ptz_control.control(iris=90)
    ptz_control._request.assert_called_with(
        "post",
        "/axis-cgi/com/ptz.cgi",
        data={"iris": 90},
    )

    await ptz_control.control(iris=10000)
    ptz_control._request.assert_called_with(
        "post",
        "/axis-cgi/com/ptz.cgi",
        data={"iris": 9999},
    )

    await ptz_control.control(iris=0)
    ptz_control._request.assert_called_with(
        "post",
        "/axis-cgi/com/ptz.cgi",
        data={"iris": 1},
    )


async def test_ptz_control_brightness(ptz_control):
    """Verify that PTZ control can send out brightness and its limits."""
    await ptz_control.control(brightness=90)
    ptz_control._request.assert_called_with(
        "post",
        "/axis-cgi/com/ptz.cgi",
        data={"brightness": 90},
    )

    await ptz_control.control(brightness=10000)
    ptz_control._request.assert_called_with(
        "post",
        "/axis-cgi/com/ptz.cgi",
        data={"brightness": 9999},
    )

    await ptz_control.control(brightness=0)
    ptz_control._request.assert_called_with(
        "post",
        "/axis-cgi/com/ptz.cgi",
        data={"brightness": 1},
    )


async def test_ptz_control_rpan(ptz_control):
    """Verify that PTZ control can send out rpan and its limits."""
    await ptz_control.control(rpan=90)
    ptz_control._request.assert_called_with(
        "post",
        "/axis-cgi/com/ptz.cgi",
        data={"rpan": 90},
    )

    await ptz_control.control(rpan=400)
    ptz_control._request.assert_called_with(
        "post",
        "/axis-cgi/com/ptz.cgi",
        data={"rpan": 360},
    )

    await ptz_control.control(rpan=-400)
    ptz_control._request.assert_called_with(
        "post",
        "/axis-cgi/com/ptz.cgi",
        data={"rpan": -360},
    )


async def test_ptz_control_rtilt(ptz_control):
    """Verify that PTZ control can send out rtilt and its limits."""
    await ptz_control.control(rtilt=90)
    ptz_control._request.assert_called_with(
        "post",
        "/axis-cgi/com/ptz.cgi",
        data={"rtilt": 90},
    )

    await ptz_control.control(rtilt=400)
    ptz_control._request.assert_called_with(
        "post",
        "/axis-cgi/com/ptz.cgi",
        data={"rtilt": 360},
    )

    await ptz_control.control(rtilt=-400)
    ptz_control._request.assert_called_with(
        "post",
        "/axis-cgi/com/ptz.cgi",
        data={"rtilt": -360},
    )


async def test_ptz_control_rzoom(ptz_control):
    """Verify that PTZ control can send out rzoom and its limits."""
    await ptz_control.control(rzoom=90)
    ptz_control._request.assert_called_with(
        "post",
        "/axis-cgi/com/ptz.cgi",
        data={"rzoom": 90},
    )

    await ptz_control.control(rzoom=10000)
    ptz_control._request.assert_called_with(
        "post",
        "/axis-cgi/com/ptz.cgi",
        data={"rzoom": 9999},
    )

    await ptz_control.control(rzoom=-10000)
    ptz_control._request.assert_called_with(
        "post",
        "/axis-cgi/com/ptz.cgi",
        data={"rzoom": -9999},
    )


async def test_ptz_control_rfocus(ptz_control):
    """Verify that PTZ control can send out rfocus and its limits."""
    await ptz_control.control(rfocus=90)
    ptz_control._request.assert_called_with(
        "post",
        "/axis-cgi/com/ptz.cgi",
        data={"rfocus": 90},
    )

    await ptz_control.control(rfocus=10000)
    ptz_control._request.assert_called_with(
        "post",
        "/axis-cgi/com/ptz.cgi",
        data={"rfocus": 9999},
    )

    await ptz_control.control(rfocus=-10000)
    ptz_control._request.assert_called_with(
        "post",
        "/axis-cgi/com/ptz.cgi",
        data={"rfocus": -9999},
    )


async def test_ptz_control_riris(ptz_control):
    """Verify that PTZ control can send out riris and its limits."""
    await ptz_control.control(riris=90)
    ptz_control._request.assert_called_with(
        "post",
        "/axis-cgi/com/ptz.cgi",
        data={"riris": 90},
    )

    await ptz_control.control(riris=10000)
    ptz_control._request.assert_called_with(
        "post",
        "/axis-cgi/com/ptz.cgi",
        data={"riris": 9999},
    )

    await ptz_control.control(riris=-10000)
    ptz_control._request.assert_called_with(
        "post",
        "/axis-cgi/com/ptz.cgi",
        data={"riris": -9999},
    )


async def test_ptz_control_rbrightness(ptz_control):
    """Verify that PTZ control can send out rbrightness and its limits."""
    await ptz_control.control(rbrightness=90)
    ptz_control._request.assert_called_with(
        "post",
        "/axis-cgi/com/ptz.cgi",
        data={"rbrightness": 90},
    )

    await ptz_control.control(rbrightness=10000)
    ptz_control._request.assert_called_with(
        "post",
        "/axis-cgi/com/ptz.cgi",
        data={"rbrightness": 9999},
    )

    await ptz_control.control(rbrightness=-10000)
    ptz_control._request.assert_called_with(
        "post",
        "/axis-cgi/com/ptz.cgi",
        data={"rbrightness": -9999},
    )


async def test_ptz_control_continuouszoommove(ptz_control):
    """Verify that PTZ control can send out continuouszoommove and its limits."""
    await ptz_control.control(continuouszoommove=90)
    ptz_control._request.assert_called_with(
        "post",
        "/axis-cgi/com/ptz.cgi",
        data={"continuouszoommove": 90},
    )

    await ptz_control.control(continuouszoommove=200)
    ptz_control._request.assert_called_with(
        "post",
        "/axis-cgi/com/ptz.cgi",
        data={"continuouszoommove": 100},
    )

    await ptz_control.control(continuouszoommove=-200)
    ptz_control._request.assert_called_with(
        "post",
        "/axis-cgi/com/ptz.cgi",
        data={"continuouszoommove": -100},
    )


async def test_ptz_control_continuousfocusmove(ptz_control):
    """Verify that PTZ control can send out continuousfocusmove and its limits."""
    await ptz_control.control(continuousfocusmove=90)
    ptz_control._request.assert_called_with(
        "post",
        "/axis-cgi/com/ptz.cgi",
        data={"continuousfocusmove": 90},
    )

    await ptz_control.control(continuousfocusmove=200)
    ptz_control._request.assert_called_with(
        "post",
        "/axis-cgi/com/ptz.cgi",
        data={"continuousfocusmove": 100},
    )

    await ptz_control.control(continuousfocusmove=-200)
    ptz_control._request.assert_called_with(
        "post",
        "/axis-cgi/com/ptz.cgi",
        data={"continuousfocusmove": -100},
    )


async def test_ptz_control_continuousirismove(ptz_control):
    """Verify that PTZ control can send out continuousirismove and its limits."""
    await ptz_control.control(continuousirismove=90)
    ptz_control._request.assert_called_with(
        "post",
        "/axis-cgi/com/ptz.cgi",
        data={"continuousirismove": 90},
    )

    await ptz_control.control(continuousirismove=200)
    ptz_control._request.assert_called_with(
        "post",
        "/axis-cgi/com/ptz.cgi",
        data={"continuousirismove": 100},
    )

    await ptz_control.control(continuousirismove=-200)
    ptz_control._request.assert_called_with(
        "post",
        "/axis-cgi/com/ptz.cgi",
        data={"continuousirismove": -100},
    )


async def test_ptz_control_continuousbrightnessmove(ptz_control):
    """Verify that PTZ control can send out continuousbrightnessmove and its limits."""
    await ptz_control.control(continuousbrightnessmove=90)
    ptz_control._request.assert_called_with(
        "post",
        "/axis-cgi/com/ptz.cgi",
        data={"continuousbrightnessmove": 90},
    )

    await ptz_control.control(continuousbrightnessmove=200)
    ptz_control._request.assert_called_with(
        "post",
        "/axis-cgi/com/ptz.cgi",
        data={"continuousbrightnessmove": 100},
    )

    await ptz_control.control(continuousbrightnessmove=-200)
    ptz_control._request.assert_called_with(
        "post",
        "/axis-cgi/com/ptz.cgi",
        data={"continuousbrightnessmove": -100},
    )


async def test_ptz_control_speed(ptz_control):
    """Verify that PTZ control can send out speed and its limits."""
    await ptz_control.control(speed=90)
    ptz_control._request.assert_called_with(
        "post",
        "/axis-cgi/com/ptz.cgi",
        data={"speed": 90},
    )

    await ptz_control.control(speed=200)
    ptz_control._request.assert_called_with(
        "post",
        "/axis-cgi/com/ptz.cgi",
        data={"speed": 100},
    )

    await ptz_control.control(speed=0)
    ptz_control._request.assert_called_with(
        "post",
        "/axis-cgi/com/ptz.cgi",
        data={"speed": 1},
    )


async def test_ptz_control_autofocus(ptz_control):
    """Verify that PTZ control can send out autofocus."""
    await ptz_control.control(autofocus=UNSUPPORTED_COMMAND)
    ptz_control._request.assert_not_called()

    await ptz_control.control(autofocus=ON)
    ptz_control._request.assert_called_with(
        "post",
        "/axis-cgi/com/ptz.cgi",
        data={"autofocus": ON},
    )


async def test_ptz_control_autoiris(ptz_control):
    """Verify that PTZ control can send out autoiris."""
    await ptz_control.control(autoiris=UNSUPPORTED_COMMAND)
    ptz_control._request.assert_not_called()

    await ptz_control.control(autoiris=OFF)
    ptz_control._request.assert_called_with(
        "post",
        "/axis-cgi/com/ptz.cgi",
        data={"autoiris": OFF},
    )


async def test_ptz_control_backlight(ptz_control):
    """Verify that PTZ control can send out backlight."""
    await ptz_control.control(backlight=UNSUPPORTED_COMMAND)
    ptz_control._request.assert_not_called()

    await ptz_control.control(backlight=OFF)
    ptz_control._request.assert_called_with(
        "post",
        "/axis-cgi/com/ptz.cgi",
        data={"backlight": OFF},
    )


async def test_ptz_control_ircutfilter(ptz_control):
    """Verify that PTZ control can send out ircutfilter."""
    await ptz_control.control(ircutfilter=UNSUPPORTED_COMMAND)
    ptz_control._request.assert_not_called()

    await ptz_control.control(ircutfilter=AUTO)
    ptz_control._request.assert_called_with(
        "post",
        "/axis-cgi/com/ptz.cgi",
        data={"ircutfilter": AUTO},
    )


async def test_ptz_control_imagerotation(ptz_control):
    """Verify that PTZ control can send out imagerotation."""
    await ptz_control.control(imagerotation=UNSUPPORTED_COMMAND)
    ptz_control._request.assert_not_called()

    await ptz_control.control(imagerotation=180)
    ptz_control._request.assert_called_with(
        "post",
        "/axis-cgi/com/ptz.cgi",
        data={"imagerotation": 180},
    )


async def test_ptz_control_continuouspantiltmove(ptz_control):
    """Verify that PTZ control can send out continuouspantiltmove and its limits."""
    await ptz_control.control(continuouspantiltmove=(30, 60))
    ptz_control._request.assert_called_with(
        "post",
        "/axis-cgi/com/ptz.cgi",
        data={"continuouspantiltmove": "30,60"},
    )

    await ptz_control.control(continuouspantiltmove=(200, 200))
    ptz_control._request.assert_called_with(
        "post",
        "/axis-cgi/com/ptz.cgi",
        data={"continuouspantiltmove": "100,100"},
    )

    await ptz_control.control(continuouspantiltmove=(-200, -200))
    ptz_control._request.assert_called_with(
        "post",
        "/axis-cgi/com/ptz.cgi",
        data={"continuouspantiltmove": "-100,-100"},
    )


async def test_ptz_control_auxiliary(ptz_control):
    """Verify that PTZ control can send out auxiliary."""
    await ptz_control.control(auxiliary="any")
    ptz_control._request.assert_called_with(
        "post",
        "/axis-cgi/com/ptz.cgi",
        data={"auxiliary": "any"},
    )


async def test_ptz_control_gotoserverpresetname(ptz_control):
    """Verify that PTZ control can send out gotoserverpresetname."""
    await ptz_control.control(gotoserverpresetname="any")
    ptz_control._request.assert_called_with(
        "post",
        "/axis-cgi/com/ptz.cgi",
        data={"gotoserverpresetname": "any"},
    )


async def test_ptz_control_gotoserverpresetno(ptz_control):
    """Verify that PTZ control can send out gotoserverpresetno."""
    await ptz_control.control(gotoserverpresetno="any")
    ptz_control._request.assert_called_with(
        "post",
        "/axis-cgi/com/ptz.cgi",
        data={"gotoserverpresetno": "any"},
    )


async def test_ptz_control_gotodevicepreset(ptz_control):
    """Verify that PTZ control can send out gotodevicepreset."""
    await ptz_control.control(gotodevicepreset="any")
    ptz_control._request.assert_called_with(
        "post",
        "/axis-cgi/com/ptz.cgi",
        data={"gotodevicepreset": "any"},
    )