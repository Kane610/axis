"""Test Axis parameter management.

pytest --cov-report term-missing --cov=axis.param_cgi tests/test_param_cgi.py
"""

import pytest
import respx

from axis.device import AxisDevice
from axis.vapix.interfaces.parameters.properties import PropertyParameterHandler

from ..conftest import HOST

PROPERTY_RESPONSE = """root.Properties.AlwaysMulticast.AlwaysMulticast=yes
root.Properties.API.Browser.Language=yes
root.Properties.API.Browser.RootPwdSetValue=yes
root.Properties.API.Browser.UserGroup=yes
root.Properties.API.ClientNotes.ClientNotes=yes
root.Properties.API.HTTP.AdminPath=/
root.Properties.API.HTTP.Version=3
root.Properties.API.Metadata.Metadata=yes
root.Properties.API.Metadata.Version=1.0
root.Properties.API.OnScreenControls.OnScreenControls=yes
root.Properties.API.PTZ.Presets.Version=2.00
root.Properties.API.RTSP.RTSPAuth=yes
root.Properties.API.RTSP.Version=2.01
root.Properties.API.WebService.EntryService=yes
root.Properties.API.WebService.WebService=yes
root.Properties.API.WebService.ONVIF.ONVIF=yes
root.Properties.API.WebService.ONVIF.Version=1.02
root.Properties.API.WebSocket.RTSP.RTSP=yes
root.Properties.ApiDiscovery.ApiDiscovery=yes
root.Properties.Audio.Audio=yes
root.Properties.Audio.DuplexMode=half,post,get
root.Properties.Audio.Format=lpcm,g711,g726,aac,opus
root.Properties.Audio.InputType=internal
root.Properties.Audio.Decoder.Format=g711,g726,axis-mulaw-128
root.Properties.Audio.Source.A0.Input=yes
root.Properties.Audio.Source.A0.Output=yes
root.Properties.EmbeddedDevelopment.CacheSize=76546048
root.Properties.EmbeddedDevelopment.DefaultCacheSize=92274688
root.Properties.EmbeddedDevelopment.EmbeddedDevelopment=yes
root.Properties.EmbeddedDevelopment.Version=2.16
root.Properties.EmbeddedDevelopment.RuleEngine.MultiConfiguration=yes
root.Properties.Firmware.BuildDate=Feb 15 2019 09:42
root.Properties.Firmware.BuildNumber=26
root.Properties.Firmware.Version=9.10.1
root.Properties.FirmwareManagement.Version=1.0
root.Properties.GuardTour.GuardTour=yes
root.Properties.GuardTour.MaxGuardTours=100
root.Properties.GuardTour.MinGuardTourWaitTime=10
root.Properties.GuardTour.RecordedTour=no
root.Properties.HTTPS.HTTPS=yes
root.Properties.Image.Format=jpeg,mjpeg,h264
root.Properties.Image.NbrOfViews=2
root.Properties.Image.Resolution=1920x1080,1280x960,1280x720,1024x768,1024x576,800x600,640x480,640x360,352x240,320x240
root.Properties.Image.Rotation=0,180
root.Properties.Image.ShowSuboptimalResolutions=false
root.Properties.Image.H264.Profiles=Baseline,Main,High
root.Properties.ImageSource.DayNight=yes
root.Properties.IO.ManualTriggerNbr=6
root.Properties.LEDControl.LEDControl=yes
root.Properties.LightControl.LightControl2=yes
root.Properties.LightControl.LightControlAvailable=yes
root.Properties.LocalStorage.AutoRepair=yes
root.Properties.LocalStorage.ContinuousRecording=yes
root.Properties.LocalStorage.DiskEncryption=yes
root.Properties.LocalStorage.DiskHealth=yes
root.Properties.LocalStorage.ExportRecording=yes
root.Properties.LocalStorage.FailOverRecording=yes
root.Properties.LocalStorage.LocalStorage=yes
root.Properties.LocalStorage.NbrOfContinuousRecordingProfiles=1
root.Properties.LocalStorage.RequiredFileSystem=yes
root.Properties.LocalStorage.SDCard=yes
root.Properties.LocalStorage.StorageLimit=yes
root.Properties.LocalStorage.Version=1.00
root.Properties.Motion.MaxNbrOfWindows=10
root.Properties.Motion.Motion=yes
root.Properties.Network.WLAN.WLANScan2=yes
root.Properties.NetworkShare.CIFS=yes
root.Properties.NetworkShare.IPV6=yes
root.Properties.NetworkShare.NameLookup=yes
root.Properties.NetworkShare.NetworkShare=yes
root.Properties.PackageManager.FormatListing=yes
root.Properties.PackageManager.LicenseKeyManagement=yes
root.Properties.PackageManager.PackageManager=yes
root.Properties.PrivacyMask.MaxNbrOfPrivacyMasks=10
root.Properties.PrivacyMask.Polygon=no
root.Properties.PrivacyMask.PrivacyMask=no
root.Properties.PrivacyMask.Query=list,position,listpxjson,positionpxjson
root.Properties.PTZ.DigitalPTZ=yes
root.Properties.PTZ.DriverManagement=no
root.Properties.PTZ.DriverModeList=none
root.Properties.PTZ.PTZ=yes
root.Properties.PTZ.PTZOnQuadView=no
root.Properties.PTZ.SelectableDriverMode=no
root.Properties.RemoteService.RemoteService=no
root.Properties.RTC.RTC=yes
root.Properties.Sensor.PIR=yes
root.Properties.Serial.Serial=no
root.Properties.System.Architecture=armv7hf
root.Properties.System.HardwareID=70E
root.Properties.System.Language=English
root.Properties.System.LanguageType=default
root.Properties.System.SerialNumber=ACCC12345678
root.Properties.System.Soc=Ambarella S2L (Flattened Device Tree)
root.Properties.Tampering.Tampering=yes
root.Properties.TemperatureSensor.Fan=no
root.Properties.TemperatureSensor.Heater=no
root.Properties.TemperatureSensor.TemperatureControl=yes
root.Properties.TemperatureSensor.TemperatureSensor=yes
root.Properties.VirtualInput.VirtualInput=yes
root.Properties.ZipStream.ZipStream=yes"""


@pytest.fixture
def property_handler(axis_device: AxisDevice) -> PropertyParameterHandler:
    """Return the param cgi mock object."""
    return axis_device.vapix.params.property_handler


@respx.mock
async def test_update_properties(property_handler: PropertyParameterHandler):
    """Verify that update properties works."""
    route = respx.post(
        f"http://{HOST}:80/axis-cgi/param.cgi",
        data={"action": "list", "group": "root.Properties"},
    ).respond(
        text=PROPERTY_RESPONSE,
        headers={"Content-Type": "text/plain"},
    )
    await property_handler.update()

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/param.cgi"

    assert property_handler.supported
    properties = property_handler["0"]
    assert properties.api_http_version == 3
    assert properties.api_metadata is True
    assert properties.api_metadata_version == "1.0"
    # assert params[f"{PROPERTIES}.API.OnScreenControls.OnScreenControls"] == "yes"
    assert properties.api_ptz_presets_version == "2.00"
    # assert params[f"{PROPERTIES}.API.RTSP.RTSPAuth"] == "yes"
    # assert params[f"{PROPERTIES}.API.RTSP.Version"] == "2.01"
    # assert params[f"{PROPERTIES}.ApiDiscovery.ApiDiscovery"] == "yes"
    # assert params[f"{PROPERTIES}.EmbeddedDevelopment.EmbeddedDevelopment"] == "yes"
    assert properties.embedded_development == "2.16"
    assert properties.firmware_build_date == "Feb 15 2019 09:42"
    assert properties.firmware_build_number == 26
    assert properties.firmware_version == "9.10.1"
    assert properties.image_format == "jpeg,mjpeg,h264"
    assert properties.image_number_of_views == 2
    assert (
        properties.image_resolution
        == "1920x1080,1280x960,1280x720,1024x768,1024x576,800x600,640x480,640x360,352x240,320x240"
    )
    assert properties.image_rotation == "0,180"
    # assert params[f"{PROPERTIES}.LEDControl.LEDControl"] == "yes"
    assert properties.light_control is True
    # assert params[f"{PROPERTIES}.LightControl.LightControlAvailable"] == "yes"
    # assert params[f"{PROPERTIES}.LocalStorage.AutoRepair"] == "yes"
    # assert params[f"{PROPERTIES}.LocalStorage.ContinuousRecording"] == "yes"
    # assert params[f"{PROPERTIES}.LocalStorage.DiskEncryption"] == "yes"
    # assert params[f"{PROPERTIES}.LocalStorage.DiskHealth"] == "yes"
    # assert params[f"{PROPERTIES}.LocalStorage.ExportRecording"] == "yes"
    # assert params[f"{PROPERTIES}.LocalStorage.FailOverRecording"] == "yes"
    # assert params[f"{PROPERTIES}.LocalStorage.LocalStorage"] == "yes"
    # assert params[f"{PROPERTIES}.LocalStorage.NbrOfContinuousRecordingProfiles"] == "1"
    # assert params[f"{PROPERTIES}.LocalStorage.RequiredFileSystem"] == "yes"
    # assert params[f"{PROPERTIES}.LocalStorage.SDCard"] == "yes"
    # assert params[f"{PROPERTIES}.LocalStorage.StorageLimit"] == "yes"
    # assert params[f"{PROPERTIES}.LocalStorage.Version"] == "1.00"
    assert properties.digital_ptz is True
    assert properties.ptz is True
    # assert params[f"{PROPERTIES}.Sensor.PIR"] == "yes"
    assert properties.system_serial_number == "ACCC12345678"
