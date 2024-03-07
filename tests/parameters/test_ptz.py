"""Test AXIS PTZ parameter management."""

import pytest

from axis.device import AxisDevice
from axis.vapix.interfaces.parameters.ptz import PtzParameterHandler

PTZ_RESPONSE = """root.PTZ.BoaProtPTZOperator=password
root.PTZ.CameraDefault=1
root.PTZ.NbrOfCameras=1
root.PTZ.NbrOfSerPorts=1
root.PTZ.CamPorts.Cam1Port=1
root.PTZ.ImageSource.I0.PTZEnabled=true
root.PTZ.Limit.L1.MaxBrightness=9999
root.PTZ.Limit.L1.MaxFieldAngle=623
root.PTZ.Limit.L1.MaxFocus=9999
root.PTZ.Limit.L1.MaxIris=9999
root.PTZ.Limit.L1.MaxPan=170
root.PTZ.Limit.L1.MaxTilt=90
root.PTZ.Limit.L1.MaxZoom=9999
root.PTZ.Limit.L1.MinBrightness=1
root.PTZ.Limit.L1.MinFieldAngle=22
root.PTZ.Limit.L1.MinFocus=770
root.PTZ.Limit.L1.MinIris=1
root.PTZ.Limit.L1.MinPan=-170
root.PTZ.Limit.L1.MinTilt=-20
root.PTZ.Limit.L1.MinZoom=1
root.PTZ.Preset.P0.HomePosition=1
root.PTZ.Preset.P0.ImageSource=0
root.PTZ.Preset.P0.Name=
root.PTZ.Preset.P0.Position.P1.Data=tilt=0.000000:focus=32766.000000:pan=0.000000:iris=32766.000000:zoom=1.000000
root.PTZ.Preset.P0.Position.P1.Name=Home
root.PTZ.PTZDriverStatuses.Driver1Status=3
root.PTZ.SerDriverStatuses.Ser1Status=3
root.PTZ.Support.S1.AbsoluteBrightness=true
root.PTZ.Support.S1.AbsoluteFocus=true
root.PTZ.Support.S1.AbsoluteIris=true
root.PTZ.Support.S1.AbsolutePan=true
root.PTZ.Support.S1.AbsoluteTilt=true
root.PTZ.Support.S1.AbsoluteZoom=true
root.PTZ.Support.S1.ActionNotification=true
root.PTZ.Support.S1.AreaZoom=true
root.PTZ.Support.S1.AutoFocus=true
root.PTZ.Support.S1.AutoIrCutFilter=true
root.PTZ.Support.S1.AutoIris=true
root.PTZ.Support.S1.Auxiliary=true
root.PTZ.Support.S1.BackLight=true
root.PTZ.Support.S1.ContinuousBrightness=false
root.PTZ.Support.S1.ContinuousFocus=true
root.PTZ.Support.S1.ContinuousIris=false
root.PTZ.Support.S1.ContinuousPan=true
root.PTZ.Support.S1.ContinuousTilt=true
root.PTZ.Support.S1.ContinuousZoom=true
root.PTZ.Support.S1.DevicePreset=false
root.PTZ.Support.S1.DigitalZoom=true
root.PTZ.Support.S1.GenericHTTP=false
root.PTZ.Support.S1.IrCutFilter=true
root.PTZ.Support.S1.JoyStickEmulation=true
root.PTZ.Support.S1.LensOffset=false
root.PTZ.Support.S1.OSDMenu=false
root.PTZ.Support.S1.ProportionalSpeed=true
root.PTZ.Support.S1.RelativeBrightness=true
root.PTZ.Support.S1.RelativeFocus=true
root.PTZ.Support.S1.RelativeIris=true
root.PTZ.Support.S1.RelativePan=true
root.PTZ.Support.S1.RelativeTilt=true
root.PTZ.Support.S1.RelativeZoom=true
root.PTZ.Support.S1.ServerPreset=true
root.PTZ.Support.S1.SpeedCtl=true
root.PTZ.UserAdv.U1.AdjustableZoomSpeedEnabled=true
root.PTZ.UserAdv.U1.DeviceModVer=model:0467, version:0310
root.PTZ.UserAdv.U1.DeviceStatus=cam=ok,pan=ok,tilt=ok
root.PTZ.UserAdv.U1.LastTestDate=Thu Oct 29 08:12:04 2020
root.PTZ.UserAdv.U1.MoveSpeed=100
root.PTZ.UserAdv.U1.WhiteBalanceOnePushModeEnabled=true
root.PTZ.UserCtlQueue.U0.Priority=10
root.PTZ.UserCtlQueue.U0.TimeoutTime=60
root.PTZ.UserCtlQueue.U0.TimeoutType=activity
root.PTZ.UserCtlQueue.U0.UseCookie=yes
root.PTZ.UserCtlQueue.U0.UserGroup=Administrator
root.PTZ.UserCtlQueue.U1.Priority=30
root.PTZ.UserCtlQueue.U1.TimeoutTime=60
root.PTZ.UserCtlQueue.U1.TimeoutType=activity
root.PTZ.UserCtlQueue.U1.UseCookie=yes
root.PTZ.UserCtlQueue.U1.UserGroup=Operator
root.PTZ.UserCtlQueue.U2.Priority=50
root.PTZ.UserCtlQueue.U2.TimeoutTime=60
root.PTZ.UserCtlQueue.U2.TimeoutType=timespan
root.PTZ.UserCtlQueue.U2.UseCookie=yes
root.PTZ.UserCtlQueue.U2.UserGroup=Viewer
root.PTZ.UserCtlQueue.U3.Priority=20
root.PTZ.UserCtlQueue.U3.TimeoutTime=20
root.PTZ.UserCtlQueue.U3.TimeoutType=activity
root.PTZ.UserCtlQueue.U3.UseCookie=no
root.PTZ.UserCtlQueue.U3.UserGroup=Event
root.PTZ.UserCtlQueue.U4.Priority=35
root.PTZ.UserCtlQueue.U4.TimeoutTime=60
root.PTZ.UserCtlQueue.U4.TimeoutType=infinity
root.PTZ.UserCtlQueue.U4.UseCookie=no
root.PTZ.UserCtlQueue.U4.UserGroup=Autotracking
root.PTZ.UserCtlQueue.U5.Priority=0
root.PTZ.UserCtlQueue.U5.TimeoutTime=60
root.PTZ.UserCtlQueue.U5.TimeoutType=infinity
root.PTZ.UserCtlQueue.U5.UseCookie=no
root.PTZ.UserCtlQueue.U5.UserGroup=Onvif
root.PTZ.Various.V1.AutoFocus=true
root.PTZ.Various.V1.AutoIris=true
root.PTZ.Various.V1.BackLight=false
root.PTZ.Various.V1.BackLightEnabled=true
root.PTZ.Various.V1.BrightnessEnabled=true
root.PTZ.Various.V1.CtlQueueing=false
root.PTZ.Various.V1.CtlQueueLimit=20
root.PTZ.Various.V1.CtlQueuePollTime=20
root.PTZ.Various.V1.FocusEnabled=true
root.PTZ.Various.V1.HomePresetSet=true
root.PTZ.Various.V1.IrCutFilter=auto
root.PTZ.Various.V1.IrCutFilterEnabled=true
root.PTZ.Various.V1.IrisEnabled=true
root.PTZ.Various.V1.MaxProportionalSpeed=200
root.PTZ.Various.V1.PanEnabled=true
root.PTZ.Various.V1.ProportionalSpeedEnabled=true
root.PTZ.Various.V1.PTZCounter=8
root.PTZ.Various.V1.ReturnToOverview=0
root.PTZ.Various.V1.SpeedCtlEnabled=true
root.PTZ.Various.V1.TiltEnabled=true
root.PTZ.Various.V1.ZoomEnabled=true"""


PTZ_5_51_M1054_RESPONSE = """root.PTZ.NbrOfSerPorts=0
root.PTZ.NbrOfCameras=1
root.PTZ.CameraDefault=1
root.PTZ.BoaProtPTZOperator=password
root.PTZ.CamPorts.Cam1Port=1
root.PTZ.ImageSource.I0.PTZEnabled=false
root.PTZ.Limit.L1.MinPan=-180
root.PTZ.Limit.L1.MaxPan=180
root.PTZ.Limit.L1.MinTilt=-180
root.PTZ.Limit.L1.MaxTilt=180
root.PTZ.Limit.L1.MinZoom=1
root.PTZ.Limit.L1.MaxZoom=9999
root.PTZ.Preset.P0.Name=
root.PTZ.Preset.P0.ImageSource=0
root.PTZ.Preset.P0.HomePosition=1
root.PTZ.Preset.P0.Position.P1.Name=Home
root.PTZ.Preset.P0.Position.P1.Data=tilt=0.000000:pan=0.000000:zoom=1.000000
root.PTZ.PTZDriverStatuses.Driver1Status=3
root.PTZ.Support.S1.AbsolutePan=true
root.PTZ.Support.S1.RelativePan=true
root.PTZ.Support.S1.AbsoluteTilt=true
root.PTZ.Support.S1.RelativeTilt=true
root.PTZ.Support.S1.AbsoluteZoom=true
root.PTZ.Support.S1.RelativeZoom=true
root.PTZ.Support.S1.DigitalZoom=false
root.PTZ.Support.S1.AbsoluteFocus=false
root.PTZ.Support.S1.RelativeFocus=false
root.PTZ.Support.S1.AutoFocus=false
root.PTZ.Support.S1.AbsoluteIris=false
root.PTZ.Support.S1.RelativeIris=false
root.PTZ.Support.S1.AutoIris=false
root.PTZ.Support.S1.AbsoluteBrightness=false
root.PTZ.Support.S1.RelativeBrightness=false
root.PTZ.Support.S1.ContinuousPan=true
root.PTZ.Support.S1.ContinuousTilt=true
root.PTZ.Support.S1.ContinuousZoom=true
root.PTZ.Support.S1.ContinuousFocus=false
root.PTZ.Support.S1.ContinuousIris=false
root.PTZ.Support.S1.ContinuousBrightness=false
root.PTZ.Support.S1.Auxiliary=false
root.PTZ.Support.S1.ServerPreset=true
root.PTZ.Support.S1.DevicePreset=false
root.PTZ.Support.S1.SpeedCtl=true
root.PTZ.Support.S1.JoyStickEmulation=true
root.PTZ.Support.S1.IrCutFilter=false
root.PTZ.Support.S1.AutoIrCutFilter=false
root.PTZ.Support.S1.BackLight=false
root.PTZ.Support.S1.OSDMenu=false
root.PTZ.Support.S1.ActionNotification=true
root.PTZ.Support.S1.ProportionalSpeed=true
root.PTZ.Support.S1.GenericHTTP=false
root.PTZ.Support.S1.LensOffset=false
root.PTZ.Support.S1.AreaZoom=true
root.PTZ.UserAdv.U1.MoveSpeed=100
root.PTZ.UserCtlQueue.U0.UserGroup=Administrator
root.PTZ.UserCtlQueue.U0.UseCookie=yes
root.PTZ.UserCtlQueue.U0.Priority=10
root.PTZ.UserCtlQueue.U0.TimeoutType=activity
root.PTZ.UserCtlQueue.U0.TimeoutTime=60
root.PTZ.UserCtlQueue.U1.UserGroup=Operator
root.PTZ.UserCtlQueue.U1.UseCookie=yes
root.PTZ.UserCtlQueue.U1.Priority=30
root.PTZ.UserCtlQueue.U1.TimeoutType=activity
root.PTZ.UserCtlQueue.U1.TimeoutTime=60
root.PTZ.UserCtlQueue.U2.UserGroup=Viewer
root.PTZ.UserCtlQueue.U2.UseCookie=yes
root.PTZ.UserCtlQueue.U2.Priority=50
root.PTZ.UserCtlQueue.U2.TimeoutType=timespan
root.PTZ.UserCtlQueue.U2.TimeoutTime=60
root.PTZ.UserCtlQueue.U3.UserGroup=Event
root.PTZ.UserCtlQueue.U3.UseCookie=no
root.PTZ.UserCtlQueue.U3.Priority=20
root.PTZ.UserCtlQueue.U3.TimeoutType=activity
root.PTZ.UserCtlQueue.U3.TimeoutTime=20
root.PTZ.UserCtlQueue.U4.UserGroup=Guardtour
root.PTZ.UserCtlQueue.U4.UseCookie=no
root.PTZ.UserCtlQueue.U4.Priority=40
root.PTZ.UserCtlQueue.U4.TimeoutType=infinity
root.PTZ.UserCtlQueue.U4.TimeoutTime=60
root.PTZ.UserCtlQueue.U5.UserGroup=Autotracking
root.PTZ.UserCtlQueue.U5.UseCookie=no
root.PTZ.UserCtlQueue.U5.Priority=35
root.PTZ.UserCtlQueue.U5.TimeoutType=infinity
root.PTZ.UserCtlQueue.U5.TimeoutTime=60
root.PTZ.UserCtlQueue.U6.UserGroup=Onvif
root.PTZ.UserCtlQueue.U6.UseCookie=no
root.PTZ.UserCtlQueue.U6.Priority=1
root.PTZ.UserCtlQueue.U6.TimeoutType=infinity
root.PTZ.UserCtlQueue.U6.TimeoutTime=60
root.PTZ.Various.V1.CtlQueueing=false
root.PTZ.Various.V1.CtlQueueLimit=20
root.PTZ.Various.V1.CtlQueuePollTime=20
root.PTZ.Various.V1.PanEnabled=true
root.PTZ.Various.V1.TiltEnabled=true
root.PTZ.Various.V1.ZoomEnabled=true
root.PTZ.Various.V1.SpeedCtlEnabled=true
root.PTZ.Various.V1.HomePresetSet=true
root.PTZ.Various.V1.ProportionalSpeedEnabled=true
root.PTZ.Various.V1.MaxProportionalSpeed=200
root.PTZ.Various.V1.ReturnToOverview=30
root.PTZ.Various.V1.Locked=true
"""

PTZ_5_51_M3024_RESPONSE = """root.PTZ.NbrOfSerPorts=0
root.PTZ.CameraDefault=1
root.PTZ.BoaProtPTZOperator=password
root.PTZ.CamPorts.Cam1Port=1
root.PTZ.ImageSource.I0.PTZEnabled=false
root.PTZ.Limit.L1.MinPan=-180
root.PTZ.Limit.L1.MaxPan=180
root.PTZ.Limit.L1.MinTilt=-180
root.PTZ.Limit.L1.MaxTilt=180
root.PTZ.Limit.L1.MinZoom=1
root.PTZ.Limit.L1.MaxZoom=9999
root.PTZ.Preset.P0.Name=
root.PTZ.Preset.P0.ImageSource=0
root.PTZ.Preset.P0.HomePosition=1
root.PTZ.Preset.P0.Position.P1.Name=Home
root.PTZ.Preset.P0.Position.P1.Data=tilt=0.000000:pan=0.000000:zoom=1.000000
root.PTZ.PTZDriverStatuses.Driver1Status=3
root.PTZ.Support.S1.AbsolutePan=true
root.PTZ.Support.S1.RelativePan=true
root.PTZ.Support.S1.AbsoluteTilt=true
root.PTZ.Support.S1.RelativeTilt=true
root.PTZ.Support.S1.AbsoluteZoom=true
root.PTZ.Support.S1.RelativeZoom=true
root.PTZ.Support.S1.DigitalZoom=false
root.PTZ.Support.S1.AbsoluteFocus=false
root.PTZ.Support.S1.RelativeFocus=false
root.PTZ.Support.S1.AutoFocus=false
root.PTZ.Support.S1.AbsoluteIris=false
root.PTZ.Support.S1.RelativeIris=false
root.PTZ.Support.S1.AutoIris=false
root.PTZ.Support.S1.AbsoluteBrightness=false
root.PTZ.Support.S1.RelativeBrightness=false
root.PTZ.Support.S1.ContinuousPan=true
root.PTZ.Support.S1.ContinuousTilt=true
root.PTZ.Support.S1.ContinuousZoom=true
root.PTZ.Support.S1.ContinuousFocus=false
root.PTZ.Support.S1.ContinuousIris=false
root.PTZ.Support.S1.ContinuousBrightness=false
root.PTZ.Support.S1.Auxiliary=false
root.PTZ.Support.S1.ServerPreset=true
root.PTZ.Support.S1.DevicePreset=false
root.PTZ.Support.S1.SpeedCtl=true
root.PTZ.Support.S1.JoyStickEmulation=true
root.PTZ.Support.S1.IrCutFilter=false
root.PTZ.Support.S1.AutoIrCutFilter=false
root.PTZ.Support.S1.BackLight=false
root.PTZ.Support.S1.OSDMenu=false
root.PTZ.Support.S1.ActionNotification=true
root.PTZ.Support.S1.ProportionalSpeed=true
root.PTZ.Support.S1.GenericHTTP=false
root.PTZ.Support.S1.LensOffset=false
root.PTZ.Support.S1.AreaZoom=true
root.PTZ.UserAdv.U1.MoveSpeed=100
root.PTZ.Various.V1.CtlQueueing=false
root.PTZ.Various.V1.CtlQueueLimit=20
root.PTZ.Various.V1.CtlQueuePollTime=20
root.PTZ.Various.V1.PanEnabled=true
root.PTZ.Various.V1.TiltEnabled=true
root.PTZ.Various.V1.ZoomEnabled=true
root.PTZ.Various.V1.SpeedCtlEnabled=true
root.PTZ.Various.V1.HomePresetSet=true
root.PTZ.Various.V1.ProportionalSpeedEnabled=true
root.PTZ.Various.V1.MaxProportionalSpeed=200
root.PTZ.Various.V1.ReturnToOverview=30
root.PTZ.Various.V1.Locked=true
"""


@pytest.fixture
def ptz_handler(axis_device: AxisDevice) -> PtzParameterHandler:
    """Return the PTZ control mock object."""
    return axis_device.vapix.params.ptz_handler


async def test_update_ptz(respx_mock, ptz_handler: PtzParameterHandler):
    """Verify that update ptz works."""
    route = respx_mock.post(
        "/axis-cgi/param.cgi",
        data={"action": "list", "group": "root.PTZ"},
    ).respond(
        text=PTZ_RESPONSE,
        headers={"Content-Type": "text/plain"},
    )
    assert not ptz_handler.initialized

    await ptz_handler.update()

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/param.cgi"

    assert ptz_handler.initialized
    ptz = ptz_handler["0"]
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

    await ptz_handler.update()


@pytest.mark.parametrize(
    ("ptz_response"), [PTZ_5_51_M1054_RESPONSE, PTZ_5_51_M3024_RESPONSE]
)
async def test_ptz_5_51(respx_mock, ptz_handler: PtzParameterHandler, ptz_response):
    """Verify that update ptz works.

    Max/Min Field Angle not reported.
    NbrOfCameras not reported.
    """
    respx_mock.post(
        "/axis-cgi/param.cgi", data={"action": "list", "group": "root.PTZ"}
    ).respond(text=ptz_response, headers={"Content-Type": "text/plain"})

    await ptz_handler.update()
