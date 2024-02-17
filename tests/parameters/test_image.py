"""Test Axis image parameter management."""

import pytest

from axis.device import AxisDevice
from axis.vapix.interfaces.parameters.image import ImageParameterHandler

from ..conftest import HOST

IMAGE_RESPONSE = """root.Image.DateFormat=YYYY-MM-DD
root.Image.MaxViewers=20
root.Image.MotionDetection=no
root.Image.NbrOfConfigs=2
root.Image.OverlayPath=/etc/overlays/axis(128x44).ovl
root.Image.OwnDateFormat=%F
root.Image.OwnDateFormatEnabled=no
root.Image.OwnTimeFormat=%T
root.Image.OwnTimeFormatEnabled=no
root.Image.PrivacyMaskType=none
root.Image.Referrers=
root.Image.ReferrersEnabled=no
root.Image.RFCCompliantMultipartEnabled=yes
root.Image.TimeFormat=24
root.Image.TimeResolution=1
root.Image.TriggerDataEnabled=no
root.Image.I0.Enabled=yes
root.Image.I0.Name=View Area 1
root.Image.I0.Source=0
root.Image.I0.Appearance.ColorEnabled=yes
root.Image.I0.Appearance.Compression=30
root.Image.I0.Appearance.MirrorEnabled=no
root.Image.I0.Appearance.Resolution=1920x1080
root.Image.I0.Appearance.Rotation=0
root.Image.I0.MPEG.Complexity=50
root.Image.I0.MPEG.ConfigHeaderInterval=1
root.Image.I0.MPEG.FrameSkipMode=drop
root.Image.I0.MPEG.ICount=1
root.Image.I0.MPEG.PCount=31
root.Image.I0.MPEG.UserDataEnabled=no
root.Image.I0.MPEG.UserDataInterval=1
root.Image.I0.MPEG.ZChromaQPMode=off
root.Image.I0.MPEG.ZFpsMode=fixed
root.Image.I0.MPEG.ZGopMode=fixed
root.Image.I0.MPEG.ZMaxGopLength=300
root.Image.I0.MPEG.ZMinFps=0
root.Image.I0.MPEG.ZStrength=10
root.Image.I0.MPEG.H264.Profile=high
root.Image.I0.MPEG.H264.PSEnabled=no
root.Image.I0.Overlay.Enabled=no
root.Image.I0.Overlay.XPos=0
root.Image.I0.Overlay.YPos=0
root.Image.I0.Overlay.MaskWindows.Color=black
root.Image.I0.RateControl.MaxBitrate=0
root.Image.I0.RateControl.Mode=vbr
root.Image.I0.RateControl.Priority=framerate
root.Image.I0.RateControl.TargetBitrate=0
root.Image.I0.SizeControl.MaxFrameSize=0
root.Image.I0.Stream.Duration=0
root.Image.I0.Stream.FPS=0
root.Image.I0.Stream.NbrOfFrames=0
root.Image.I0.Text.BGColor=black
root.Image.I0.Text.ClockEnabled=no
root.Image.I0.Text.Color=white
root.Image.I0.Text.DateEnabled=no
root.Image.I0.Text.Position=top
root.Image.I0.Text.String=
root.Image.I0.Text.TextEnabled=no
root.Image.I0.Text.TextSize=medium
root.Image.I0.TriggerData.AudioEnabled=yes
root.Image.I0.TriggerData.MotionDetectionEnabled=yes
root.Image.I0.TriggerData.MotionLevelEnabled=no
root.Image.I0.TriggerData.TamperingEnabled=yes
root.Image.I0.TriggerData.UserTriggers=
root.Image.I1.Enabled=no
root.Image.I1.Name=View Area 2
root.Image.I1.Source=0
root.Image.I1.Appearance.ColorEnabled=yes
root.Image.I1.Appearance.Compression=30
root.Image.I1.Appearance.MirrorEnabled=no
root.Image.I1.Appearance.Resolution=1920x1080
root.Image.I1.Appearance.Rotation=0
root.Image.I1.MPEG.Complexity=50
root.Image.I1.MPEG.ConfigHeaderInterval=1
root.Image.I1.MPEG.FrameSkipMode=drop
root.Image.I1.MPEG.ICount=1
root.Image.I1.MPEG.PCount=31
root.Image.I1.MPEG.UserDataEnabled=no
root.Image.I1.MPEG.UserDataInterval=1
root.Image.I1.MPEG.ZChromaQPMode=off
root.Image.I1.MPEG.ZFpsMode=fixed
root.Image.I1.MPEG.ZGopMode=fixed
root.Image.I1.MPEG.ZMaxGopLength=300
root.Image.I1.MPEG.ZMinFps=0
root.Image.I1.MPEG.ZStrength=10
root.Image.I1.MPEG.H264.Profile=high
root.Image.I1.MPEG.H264.PSEnabled=no
root.Image.I1.Overlay.Enabled=no
root.Image.I1.Overlay.XPos=0
root.Image.I1.Overlay.YPos=0
root.Image.I1.RateControl.MaxBitrate=0
root.Image.I1.RateControl.Mode=vbr
root.Image.I1.RateControl.Priority=framerate
root.Image.I1.RateControl.TargetBitrate=0
root.Image.I1.SizeControl.MaxFrameSize=0
root.Image.I1.Stream.Duration=0
root.Image.I1.Stream.FPS=0
root.Image.I1.Stream.NbrOfFrames=0
root.Image.I1.Text.BGColor=black
root.Image.I1.Text.ClockEnabled=no
root.Image.I1.Text.Color=white
root.Image.I1.Text.DateEnabled=no
root.Image.I1.Text.Position=top
root.Image.I1.Text.String=
root.Image.I1.Text.TextEnabled=no
root.Image.I1.Text.TextSize=medium
root.Image.I1.TriggerData.AudioEnabled=yes
root.Image.I1.TriggerData.MotionDetectionEnabled=yes
root.Image.I1.TriggerData.MotionLevelEnabled=no
root.Image.I1.TriggerData.TamperingEnabled=yes
root.Image.I1.TriggerData.UserTriggers="""


@pytest.fixture
def image_handler(axis_device: AxisDevice) -> ImageParameterHandler:
    """Return the param cgi mock object."""
    return axis_device.vapix.params.image_handler


async def test_image_handler(respx_mock, image_handler: ImageParameterHandler):
    """Verify that update image works."""
    route = respx_mock.post(
        f"http://{HOST}:80/axis-cgi/param.cgi",
        data={"action": "list", "group": "root.Image"},
    ).respond(
        text=IMAGE_RESPONSE,
        headers={"Content-Type": "text/plain"},
    )
    assert not image_handler.initialized

    await image_handler.update()

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/param.cgi"

    assert image_handler.initialized
    image_0 = image_handler["0"]
    assert image_0.enabled is True
    assert image_0.name == "View Area 1"
    assert image_0.source == 0
    assert image_0.appearance == {
        "ColorEnabled": True,
        "Compression": 30,
        "MirrorEnabled": False,
        "Resolution": "1920x1080",
        "Rotation": 0,
    }
    assert image_0.mpeg == {
        "Complexity": 50,
        "ConfigHeaderInterval": 1,
        "FrameSkipMode": "drop",
        "ICount": 1,
        "PCount": 31,
        "UserDataEnabled": False,
        "UserDataInterval": 1,
        "ZChromaQPMode": "off",
        "ZFpsMode": "fixed",
        "ZGopMode": "fixed",
        "ZMaxGopLength": 300,
        "ZMinFps": 0,
        "ZStrength": 10,
        "H264": {"Profile": "high", "PSEnabled": False},
    }
    assert image_0.overlay == {
        "Enabled": False,
        "XPos": 0,
        "YPos": 0,
        "MaskWindows": {"Color": "black"},
    }
    assert image_0.rate_control == {
        "MaxBitrate": 0,
        "Mode": "vbr",
        "Priority": "framerate",
        "TargetBitrate": 0,
    }
    assert image_0.size_control == {"MaxFrameSize": 0}
    assert image_0.stream == {
        "Duration": 0,
        "FPS": 0,
        "NbrOfFrames": 0,
    }
    assert image_0.text == {
        "BGColor": "black",
        "ClockEnabled": False,
        "Color": "white",
        "DateEnabled": False,
        "Position": "top",
        "String": "",
        "TextEnabled": False,
        "TextSize": "medium",
    }
    assert image_0.trigger_data == {
        "AudioEnabled": True,
        "MotionDetectionEnabled": True,
        "MotionLevelEnabled": False,
        "TamperingEnabled": True,
        "UserTriggers": "",
    }

    image_1 = image_handler["1"]
    assert image_1.enabled is False
    assert image_1.name == "View Area 2"
    assert image_1.source == 0
    assert image_1.appearance == {
        "ColorEnabled": True,
        "Compression": 30,
        "MirrorEnabled": False,
        "Resolution": "1920x1080",
        "Rotation": 0,
    }
    assert image_1.mpeg == {
        "Complexity": 50,
        "ConfigHeaderInterval": 1,
        "FrameSkipMode": "drop",
        "ICount": 1,
        "PCount": 31,
        "UserDataEnabled": False,
        "UserDataInterval": 1,
        "ZChromaQPMode": "off",
        "ZFpsMode": "fixed",
        "ZGopMode": "fixed",
        "ZMaxGopLength": 300,
        "ZMinFps": 0,
        "ZStrength": 10,
        "H264": {"Profile": "high", "PSEnabled": False},
    }
    assert image_1.overlay == {"Enabled": False, "XPos": 0, "YPos": 0}
    assert image_1.rate_control == {
        "MaxBitrate": 0,
        "Mode": "vbr",
        "Priority": "framerate",
        "TargetBitrate": 0,
    }
    assert image_1.size_control == {"MaxFrameSize": 0}
    assert image_1.stream == {
        "Duration": 0,
        "FPS": 0,
        "NbrOfFrames": 0,
    }
    assert image_1.text == {
        "BGColor": "black",
        "ClockEnabled": False,
        "Color": "white",
        "DateEnabled": False,
        "Position": "top",
        "String": "",
        "TextEnabled": False,
        "TextSize": "medium",
    }
    assert image_1.trigger_data == {
        "AudioEnabled": True,
        "MotionDetectionEnabled": True,
        "MotionLevelEnabled": False,
        "TamperingEnabled": True,
        "UserTriggers": "",
    }
