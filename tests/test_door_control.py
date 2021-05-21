"""Test Axis Door Control API.

pytest --cov-report term-missing --cov=axis.light_control tests/test_light_control.py
"""

import json
import pytest

import respx

from axis.door_control import DoorControl
from .conftest import HOST


@pytest.fixture
def door_control(axis_device) -> DoorControl:
    """Returns the door_control mock object."""
    return DoorControl(axis_device.vapix.request)


@respx.mock
async def test_update(door_control):
    """Test update method."""
    route = respx.post(f"http://{HOST}:80/vapix/doorcontrol").respond(
        json={"DoorInfo": [
            {
                "token": "Axis-accc8ea9abac:1550808050.595717000",
                "Name": "Main Door",
                "Description": "Main Door Description",
                "Capabilities": {
                    "Access": True,
                    "Lock": True,
                    "Unlock": True,
                    "Block": True,
                    "DoubleLock": True,
                    "LockDown": True,
                    "LockOpen": True,
                    "DoorMonitor": True,
                    "LockMonitor": False,
                    "DoubleLockMonitor": False,
                    "Alarm": True,
                    "Tamper": False,
                    "Warning": True,
                    "Configurable": True
                }
            },
            {
                "token": "Axis-accc8ee70fbe:1614733258.565014000",
                "Name": "North Gym Door",
                "Description": "North Gym Door Description",
                "Capabilities": {}
            }
        ]
        }
    )

    await door_control.update()

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/vapix/doorcontrol"
    assert json.loads(route.calls.last.request.content) == {"tdc:GetDoorInfoList": {}}

    assert len(door_control.values()) == 2

    item = door_control["Axis-accc8ea9abac:1550808050.595717000"]
    assert item.id == "Axis-accc8ea9abac:1550808050.595717000"
    assert item.door_token == "Axis-accc8ea9abac:1550808050.595717000"
    assert item.door_name == "Main Door"
    assert item.door_description == "Main Door Description"

    # TODO: Check to see that comparing dict using "==" actually does what I want it to do
    assert item.door_capabilities == {
        "Access": True,
        "Lock": True,
        "Unlock": True,
        "Block": True,
        "DoubleLock": True,
        "LockDown": True,
        "LockOpen": True,
        "DoorMonitor": True,
        "LockMonitor": False,
        "DoubleLockMonitor": False,
        "Alarm": True,
        "Tamper": False,
        "Warning": True,
        "Configurable": True
    }

    item2 = door_control["Axis-accc8ee70fbe:1614733258.565014000"]
    assert item2.id == "Axis-accc8ee70fbe:1614733258.565014000"
    assert item2.door_token == "Axis-accc8ee70fbe:1614733258.565014000"
    assert item2.door_name == "North Gym Door"
    assert item2.description == "North Gym Door Description"
    # TODO: Check to see that comparing dict using "==" actually does what I want it to do
    assert item2.door_capabilities == {}


@respx.mock
async def test_get_service_capabilities(door_control):
    """Test get service capabilities API."""
    route = respx.post(f"http://{HOST}:80/vapix/doorcontrol").respond(
        json={
            "Capabilities": {
                "MaxLimit": 100,
                "GetDoorSupported": True,
                "SetDoorSupported": True,
                "PriorityConfigurationSupported": True
            }
        },
    )

    response = await door_control.get_service_capabilities()

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/vapix/doorcontrol"
    assert json.loads(route.calls.last.request.content) == {"tdc:GetServiceCapabilities": {}}

    assert response["Capabilities"] == {
        "MaxLimit": 100,
        "GetDoorSupported": True,
        "SetDoorSupported": True,
        "PriorityConfigurationSupported": True
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
