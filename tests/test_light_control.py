"""Test Axis Light Control API.

pytest --cov-report term-missing --cov=axis.light_control tests/test_light_control.py
"""

import json
import pytest

import respx

from axis.light_control import LightControl
from .conftest import HOST


@pytest.fixture
def light_control(axis_device) -> LightControl:
    """Returns the light_control mock object."""
    return LightControl(axis_device.vapix.request)


@respx.mock
async def test_update(light_control):
    """Test update method."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/lightcontrol.cgi").respond(
        json={
            "apiVersion": "1.1",
            "method": "getLightInformation",
            "data": {
                "items": [
                    {
                        "lightID": "led0",
                        "lightType": "IR",
                        "enabled": True,
                        "synchronizeDayNightMode": True,
                        "lightState": False,
                        "automaticIntensityMode": False,
                        "automaticAngleOfIlluminationMode": False,
                        "nrOfLEDs": 1,
                        "error": False,
                        "errorInfo": "",
                    }
                ]
            },
        },
    )

    await light_control.update()

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/lightcontrol.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "method": "getLightInformation",
        "apiVersion": "1.1",
        "context": "Axis library",
    }

    assert len(light_control.values()) == 1

    item = light_control["led0"]
    assert item.id == "led0"
    assert item.light_id == "led0"
    assert item.light_type == "IR"
    assert item.enabled is True
    assert item.synchronize_day_night_mode is True
    assert item.light_state is False
    assert item.automatic_intensity_mode is False
    assert item.automatic_angle_of_illumination_mode is False
    assert item.number_of_leds == 1
    assert item.error is False
    assert item.error_info == ""


@respx.mock
async def test_get_service_capabilities(light_control):
    """Test get service capabilities API."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/lightcontrol.cgi").respond(
        json={
            "apiVersion": "1.1",
            "method": "getServiceCapabilities",
            "data": {
                "automaticIntensitySupport": True,
                "manualIntensitySupport": True,
                "individualIntensitySupport": False,
                "getCurrentIntensitySupport": True,
                "manualAngleOfIlluminationSupport": False,
                "automaticAngleOfIlluminationSupport": False,
                "dayNightSynchronizeSupport": True,
            },
        },
    )

    response = await light_control.get_service_capabilities()

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/lightcontrol.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "method": "getServiceCapabilities",
        "apiVersion": "1.1",
        "context": "Axis library",
    }

    assert response["data"] == {
        "automaticIntensitySupport": True,
        "manualIntensitySupport": True,
        "individualIntensitySupport": False,
        "getCurrentIntensitySupport": True,
        "manualAngleOfIlluminationSupport": False,
        "automaticAngleOfIlluminationSupport": False,
        "dayNightSynchronizeSupport": True,
    }


@respx.mock
async def test_get_light_information(light_control):
    """Test get light information API."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/lightcontrol.cgi").respond(
        json={
            "apiVersion": "1.1",
            "method": "getLightInformation",
            "data": {
                "items": [
                    {
                        "lightID": "led0",
                        "lightType": "IR",
                        "enabled": True,
                        "synchronizeDayNightMode": True,
                        "lightState": False,
                        "automaticIntensityMode": False,
                        "automaticAngleOfIlluminationMode": False,
                        "nrOfLEDs": 1,
                        "error": False,
                        "errorInfo": "",
                    }
                ]
            },
        },
    )

    response = await light_control.get_light_information()

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/lightcontrol.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "method": "getLightInformation",
        "apiVersion": "1.1",
        "context": "Axis library",
    }

    assert response["data"] == {
        "items": [
            {
                "lightID": "led0",
                "lightType": "IR",
                "enabled": True,
                "synchronizeDayNightMode": True,
                "lightState": False,
                "automaticIntensityMode": False,
                "automaticAngleOfIlluminationMode": False,
                "nrOfLEDs": 1,
                "error": False,
                "errorInfo": "",
            }
        ]
    }


@respx.mock
async def test_activate_light(light_control):
    """Test activating light API."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/lightcontrol.cgi").respond(
        json={
            "apiVersion": "1.1",
            "method": "activateLight",
            "data": {},
        },
    )

    await light_control.activate_light("led0")

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/lightcontrol.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "method": "activateLight",
        "apiVersion": "1.1",
        "context": "Axis library",
        "params": {"lightID": "led0"},
    }


@respx.mock
async def test_deactivate_light(light_control):
    """Test deactivating light API."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/lightcontrol.cgi").respond(
        json={
            "apiVersion": "1.1",
            "method": "deactivateLight",
            "data": {},
        },
    )

    await light_control.deactivate_light("led0")

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/lightcontrol.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "method": "deactivateLight",
        "apiVersion": "1.1",
        "context": "Axis library",
        "params": {"lightID": "led0"},
    }


@respx.mock
async def test_enable_light(light_control):
    """Test enabling light API."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/lightcontrol.cgi").respond(
        json={
            "apiVersion": "1.1",
            "method": "enableLight",
            "data": {},
        },
    )

    await light_control.enable_light("led0")

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/lightcontrol.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "method": "enableLight",
        "apiVersion": "1.1",
        "context": "Axis library",
        "params": {"lightID": "led0"},
    }


@respx.mock
async def test_disable_light(light_control):
    """Test disabling light API."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/lightcontrol.cgi").respond(
        json={
            "apiVersion": "1.1",
            "method": "disableLight",
            "data": {},
        },
    )

    await light_control.disable_light("led0")

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/lightcontrol.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "method": "disableLight",
        "apiVersion": "1.1",
        "context": "Axis library",
        "params": {"lightID": "led0"},
    }


@respx.mock
async def test_get_light_status(light_control):
    """Test get light status API."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/lightcontrol.cgi").respond(
        json={
            "apiVersion": "1.1",
            "method": "getLightStatus",
            "data": {"status": False},
        },
    )

    response = await light_control.get_light_status("led0")

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/lightcontrol.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "method": "getLightStatus",
        "apiVersion": "1.1",
        "context": "Axis library",
        "params": {"lightID": "led0"},
    }

    assert response["data"] == {"status": False}


@respx.mock
async def test_set_automatic_intensity_mode(light_control):
    """Test set automatic intensity mode API."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/lightcontrol.cgi").respond(
        json={
            "apiVersion": "1.1",
            "method": "setAutomaticIntensityMode",
            "data": {},
        },
    )

    await light_control.set_automatic_intensity_mode("led0", True)

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/lightcontrol.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "method": "setAutomaticIntensityMode",
        "apiVersion": "1.1",
        "context": "Axis library",
        "params": {"lightID": "led0", "enabled": True},
    }


@respx.mock
async def test_get_manual_intensity(light_control):
    """Test get valid intensity API."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/lightcontrol.cgi").respond(
        json={
            "apiVersion": "1.1",
            "method": "getManualIntensity",
            "data": {"intensity": 1000},
        },
    )

    response = await light_control.get_manual_intensity("led0")

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/lightcontrol.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "method": "getManualIntensity",
        "apiVersion": "1.1",
        "context": "Axis library",
        "params": {"lightID": "led0"},
    }

    assert response["data"] == {"intensity": 1000}


@respx.mock
async def test_set_manual_intensity(light_control):
    """Test set manual intensity API."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/lightcontrol.cgi").respond(
        json={
            "apiVersion": "1.1",
            "method": "setManualIntensity",
            "data": {},
        },
    )

    await light_control.set_manual_intensity("led0", 1000)

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/lightcontrol.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "method": "setManualIntensity",
        "apiVersion": "1.1",
        "context": "Axis library",
        "params": {"lightID": "led0", "intensity": 1000},
    }


@respx.mock
async def test_get_valid_intensity(light_control):
    """Test get valid intensity API."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/lightcontrol.cgi").respond(
        json={
            "apiVersion": "1.1",
            "method": "getValidIntensity",
            "data": {"ranges": [{"low": 0, "high": 1000}]},
        },
    )

    response = await light_control.get_valid_intensity("led0")

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/lightcontrol.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "method": "getValidIntensity",
        "apiVersion": "1.1",
        "context": "Axis library",
        "params": {"lightID": "led0"},
    }

    assert response["data"] == {"ranges": [{"low": 0, "high": 1000}]}


@respx.mock
async def test_set_individual_intensity(light_control):
    """Test set individual intensity API."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/lightcontrol.cgi").respond(
        json={
            "apiVersion": "1.1",
            "method": "setIndividualIntensity",
            "data": {},
        },
    )

    await light_control.set_individual_intensity("led0", 1, 1000)

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/lightcontrol.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "method": "setIndividualIntensity",
        "apiVersion": "1.1",
        "context": "Axis library",
        "params": {"lightID": "led0", "LEDID": 1, "intensity": 1000},
    }


@respx.mock
async def test_get_individual_intensity(light_control):
    """Test get individual intensity API."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/lightcontrol.cgi").respond(
        json={
            "apiVersion": "1.1",
            "method": "getIndividualIntensity",
            "data": {"intensity": 1000},
        },
    )

    response = await light_control.get_individual_intensity("led0", 1)

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/lightcontrol.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "method": "getIndividualIntensity",
        "apiVersion": "1.1",
        "context": "Axis library",
        "params": {"lightID": "led0", "LEDID": 1},
    }

    assert response["data"] == {"intensity": 1000}


@respx.mock
async def test_get_current_intensity(light_control):
    """Test get current intensity API."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/lightcontrol.cgi").respond(
        json={
            "apiVersion": "1.1",
            "method": "getCurrentIntensity",
            "data": {"intensity": 1000},
        },
    )

    response = await light_control.get_current_intensity("led0")

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/lightcontrol.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "method": "getCurrentIntensity",
        "apiVersion": "1.1",
        "context": "Axis library",
        "params": {"lightID": "led0"},
    }

    assert response["data"] == {"intensity": 1000}


@respx.mock
async def test_set_automatic_angle_of_illumination_mode(light_control):
    """Test set automatic angle of illumination mode API."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/lightcontrol.cgi").respond(
        json={
            "apiVersion": "1.1",
            "method": "setAutomaticAngleOfIlluminationMode",
            "data": {},
        },
    )

    await light_control.set_automatic_angle_of_illumination_mode("led0", True)

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/lightcontrol.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "method": "setAutomaticAngleOfIlluminationMode",
        "apiVersion": "1.1",
        "context": "Axis library",
        "params": {"lightID": "led0", "enabled": True},
    }


@respx.mock
async def test_get_valid_angle_of_illumination(light_control):
    """Test get valid angle of illumination API."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/lightcontrol.cgi").respond(
        json={
            "apiVersion": "1.0",
            "context": "my context",
            "method": "getValidAngleOfIllumination",
            "data": {"ranges": [{"low": 10, "high": 30}, {"low": 20, "high": 50}]},
        },
    )

    response = await light_control.get_valid_angle_of_illumination("led0")

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/lightcontrol.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "method": "getValidAngleOfIllumination",
        "apiVersion": "1.1",
        "context": "Axis library",
        "params": {"lightID": "led0"},
    }

    assert response["data"] == {
        "ranges": [{"low": 10, "high": 30}, {"low": 20, "high": 50}]
    }


@respx.mock
async def test_set_manual_angle_of_illumination(light_control):
    """Test set manual angle of illumination API."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/lightcontrol.cgi").respond(
        json={
            "apiVersion": "1.1",
            "method": "setManualAngleOfIllumination",
            "data": {},
        },
    )

    await light_control.set_manual_angle_of_illumination("led0", 30)

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/lightcontrol.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "method": "setManualAngleOfIllumination",
        "apiVersion": "1.1",
        "context": "Axis library",
        "params": {"lightID": "led0", "angleOfIllumination": 30},
    }


@respx.mock
async def test_get_manual_angle_of_illumination(light_control):
    """Test get manual angle of illumination API."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/lightcontrol.cgi").respond(
        json={
            "apiVersion": "1.0",
            "context": "my context",
            "method": "getManualAngleOfIllumination",
            "data": {"angleOfIllumination": 30},
        },
    )

    response = await light_control.get_manual_angle_of_illumination("led0")

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/lightcontrol.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "method": "getManualAngleOfIllumination",
        "apiVersion": "1.1",
        "context": "Axis library",
        "params": {"lightID": "led0"},
    }

    assert response["data"] == {"angleOfIllumination": 30}


@respx.mock
async def test_get_current_angle_of_illumination(light_control):
    """Test get current angle of illumination API."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/lightcontrol.cgi").respond(
        json={
            "apiVersion": "1.0",
            "context": "my context",
            "method": "getCurrentAngleOfIllumination",
            "data": {"angleOfIllumination": 20},
        },
    )

    response = await light_control.get_current_angle_of_illumination("led0")

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/lightcontrol.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "method": "getCurrentAngleOfIllumination",
        "apiVersion": "1.1",
        "context": "Axis library",
        "params": {"lightID": "led0"},
    }

    assert response["data"] == {"angleOfIllumination": 20}


@respx.mock
async def test_set_light_synchronization_day_night_mode(light_control):
    """Test set light synchronization day night mode API."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/lightcontrol.cgi").respond(
        json={
            "apiVersion": "1.1",
            "method": "setLightSynchronizationDayNightMode",
            "data": {},
        },
    )

    await light_control.set_light_synchronization_day_night_mode("led0", True)

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/lightcontrol.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "method": "setLightSynchronizationDayNightMode",
        "apiVersion": "1.1",
        "context": "Axis library",
        "params": {"lightID": "led0", "enabled": True},
    }


@respx.mock
async def test_get_light_synchronization_day_night_mode(light_control):
    """Test get light synchronization day night mode API."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/lightcontrol.cgi").respond(
        json={
            "apiVersion": "1.1",
            "context": "my context",
            "method": "getLightSynchronizeDayNightMode",
            "data": {"enabled": True},
        },
    )

    response = await light_control.get_light_synchronization_day_night_mode("led0")

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/lightcontrol.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "method": "getLightSynchronizationDayNightMode",
        "apiVersion": "1.1",
        "context": "Axis library",
        "params": {"lightID": "led0"},
    }

    assert response["data"] == {"enabled": True}


@respx.mock
async def test_get_supported_versions(light_control):
    """Test get supported versions api."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/lightcontrol.cgi").respond(
        json={
            "method": "getSupportedVersions",
            "data": {"apiVersions": ["1.1"]},
        },
    )

    response = await light_control.get_supported_versions()

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/lightcontrol.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "method": "getSupportedVersions"
    }

    assert response["data"] == {"apiVersions": ["1.1"]}


response_getLightInformation = {
    "apiVersion": "1.1",
    "method": "getLightInformation",
    "data": {
        "items": [
            {
                "lightID": "led0",
                "lightType": "IR",
                "enabled": True,
                "synchronizeDayNightMode": True,
                "lightState": False,
                "automaticIntensityMode": False,
                "automaticAngleOfIlluminationMode": False,
                "nrOfLEDs": 1,
                "error": False,
                "errorInfo": "",
            }
        ]
    },
}
