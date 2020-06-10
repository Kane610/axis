"""Test Axis Light Control API.

pytest --cov-report term-missing --cov=axis.light_control tests/test_light_control.py
"""

import pytest

from asynctest import Mock

from axis.light_control import LightControl


@pytest.fixture
def light_control() -> LightControl:
    """Returns the light_control mock object."""
    mock_request = Mock()
    mock_request.return_value = ""
    return LightControl({}, mock_request)


def test_update(light_control):
    """Test update method."""
    light_control._request.return_value = response_getLightInformation
    light_control.update()
    light_control._request.assert_called_with(
        "post",
        "/axis-cgi/lightcontrol.cgi",
        json={
            "method": "getLightInformation",
            "apiVersion": "1.1",
            "context": "Axis library",
        },
    )

    assert len(light_control.values()) == 1

    item = light_control["led0"]
    assert item.id == "led0"
    assert item.light_id == "led0"
    assert item.light_type == "IR"
    assert item.enabled is True
    assert item.synchronize_day_night_mode is True
    assert item.light_state is False
    assert item.automatic_intensity_mode is False
    assert item.number_of_leds == 1
    assert item.error is False
    assert item.error_info == ""


def test_get_service_capabilities(light_control):
    """Test get service capabilities API."""
    light_control._request.return_value = response_getServiceCapabilities
    light_control.get_service_capabilities()
    light_control._request.assert_called_with(
        "post",
        "/axis-cgi/lightcontrol.cgi",
        json={
            "method": "getServiceCapabilities",
            "apiVersion": "1.1",
            "context": "Axis library",
        },
    )


def test_get_light_information(light_control):
    """Test get light information API."""
    light_control._request.return_value = response_getLightInformation
    light_control.get_light_information()
    light_control._request.assert_called_with(
        "post",
        "/axis-cgi/lightcontrol.cgi",
        json={
            "method": "getLightInformation",
            "apiVersion": "1.1",
            "context": "Axis library",
        },
    )


def test_activate_light(light_control):
    """Test activating light API."""
    light_control.activate_light("led0")
    light_control._request.assert_called_with(
        "post",
        "/axis-cgi/lightcontrol.cgi",
        json={
            "method": "activateLight",
            "apiVersion": "1.1",
            "context": "Axis library",
            "params": {"lightID": "led0"},
        },
    )


def test_deactivate_light(light_control):
    """Test deactivating light API."""
    light_control.deactivate_light("led0")
    light_control._request.assert_called_with(
        "post",
        "/axis-cgi/lightcontrol.cgi",
        json={
            "method": "deactivateLight",
            "apiVersion": "1.1",
            "context": "Axis library",
            "params": {"lightID": "led0"},
        },
    )


def test_enable_light(light_control):
    """Test enabling light API."""
    light_control.enable_light("led0")
    light_control._request.assert_called_with(
        "post",
        "/axis-cgi/lightcontrol.cgi",
        json={
            "method": "enableLight",
            "apiVersion": "1.1",
            "context": "Axis library",
            "params": {"lightID": "led0"},
        },
    )


def test_disable_light(light_control):
    """Test disabling light API."""
    light_control.disable_light("led0")
    light_control._request.assert_called_with(
        "post",
        "/axis-cgi/lightcontrol.cgi",
        json={
            "method": "disableLight",
            "apiVersion": "1.1",
            "context": "Axis library",
            "params": {"lightID": "led0"},
        },
    )


def test_get_light_status(light_control):
    """Test get light status API."""
    light_control._request.return_value = response_getLightStatus
    response = light_control.get_light_status("led0")
    light_control._request.assert_called_with(
        "post",
        "/axis-cgi/lightcontrol.cgi",
        json={
            "method": "getLightStatus",
            "apiVersion": "1.1",
            "context": "Axis library",
            "params": {"lightID": "led0"},
        },
    )

    assert response["data"] == {"status": False}


def test_set_automatic_intensity_mode(light_control):
    """Test set automatic intensity mode API."""
    light_control.set_automatic_intensity_mode("led0", True)
    light_control._request.assert_called_with(
        "post",
        "/axis-cgi/lightcontrol.cgi",
        json={
            "method": "setAutomaticIntensityMode",
            "apiVersion": "1.1",
            "context": "Axis library",
            "params": {"lightID": "led0", "enabled": True},
        },
    )


def test_get_valid_intensity(light_control):
    """Test get valid intensity API."""
    light_control._request.return_value = response_getManualIntensity
    response = light_control.get_manual_intensity("led0")
    light_control._request.assert_called_with(
        "post",
        "/axis-cgi/lightcontrol.cgi",
        json={
            "method": "getManualIntensity",
            "apiVersion": "1.1",
            "context": "Axis library",
            "params": {"lightID": "led0"},
        },
    )

    assert response["data"] == {"intensity": 1000}


def test_set_manual_intensity(light_control):
    """Test set manual intensity API."""
    light_control.set_manual_intensity("led0", 1000)
    light_control._request.assert_called_with(
        "post",
        "/axis-cgi/lightcontrol.cgi",
        json={
            "method": "setManualIntensity",
            "apiVersion": "1.1",
            "context": "Axis library",
            "params": {"lightID": "led0", "intensity": 1000},
        },
    )


def test_get_manual_intensity(light_control):
    """Test get manual intensity API."""
    light_control._request.return_value = response_getValidIntensity
    response = light_control.get_valid_intensity("led0")
    light_control._request.assert_called_with(
        "post",
        "/axis-cgi/lightcontrol.cgi",
        json={
            "method": "getValidIntensity",
            "apiVersion": "1.1",
            "context": "Axis library",
            "params": {"lightID": "led0"},
        },
    )

    assert response["data"] == {"ranges": [{"low": 0, "high": 1000}]}


def test_set_individual_intensity(light_control):
    """Test set individual intensity API."""
    light_control.set_individual_intensity("led0", 1, 1000)
    light_control._request.assert_called_with(
        "post",
        "/axis-cgi/lightcontrol.cgi",
        json={
            "method": "setIndividualIntensity",
            "apiVersion": "1.1",
            "context": "Axis library",
            "params": {"lightID": "led0", "LEDID": 1, "intensity": 1000},
        },
    )


def test_get_individual_intensity(light_control):
    """Test get individual intensity API."""
    light_control._request.return_value = response_getIndividualIntensity
    response = light_control.get_individual_intensity("led0", 1)
    light_control._request.assert_called_with(
        "post",
        "/axis-cgi/lightcontrol.cgi",
        json={
            "method": "getIndividualIntensity",
            "apiVersion": "1.1",
            "context": "Axis library",
            "params": {"lightID": "led0", "LEDID": 1},
        },
    )

    assert response["data"] == {"intensity": 1000}


def test_get_current_intensity(light_control):
    """Test get current intensity API."""
    light_control._request.return_value = response_getCurrentIntensity
    response = light_control.get_current_intensity("led0")
    light_control._request.assert_called_with(
        "post",
        "/axis-cgi/lightcontrol.cgi",
        json={
            "method": "getCurrentIntensity",
            "apiVersion": "1.1",
            "context": "Axis library",
            "params": {"lightID": "led0"},
        },
    )

    assert response["data"] == {"intensity": 1000}


def test_set_automatic_angle_of_illumination_mode(light_control):
    """Test set automatic angle of illumination mode API."""
    light_control.set_automatic_angle_of_illumination_mode("led0", True)
    light_control._request.assert_called_with(
        "post",
        "/axis-cgi/lightcontrol.cgi",
        json={
            "method": "setAutomaticAngleOfIlluminationMode",
            "apiVersion": "1.1",
            "context": "Axis library",
            "params": {"lightID": "led0", "enabled": True},
        },
    )


def test_get_valid_angle_of_illumination(light_control):
    """Test get valid angle of illumination API."""
    light_control._request.return_value = response_getValidAngleOfIllumination
    response = light_control.get_valid_angle_of_illumination("led0")
    light_control._request.assert_called_with(
        "post",
        "/axis-cgi/lightcontrol.cgi",
        json={
            "method": "getValidAngleOfIllumination",
            "apiVersion": "1.1",
            "context": "Axis library",
            "params": {"lightID": "led0"},
        },
    )

    assert response["data"] == {
        "ranges": [{"low": 10, "high": 30}, {"low": 20, "high": 50}]
    }


def test_set_manual_angle_of_illumination(light_control):
    """Test set manual angle of illumination API."""
    light_control.set_manual_angle_of_illumination("led0", 30)
    light_control._request.assert_called_with(
        "post",
        "/axis-cgi/lightcontrol.cgi",
        json={
            "method": "setManualAngleOfIllumination",
            "apiVersion": "1.1",
            "context": "Axis library",
            "params": {"lightID": "led0", "angleOfIllumination": 30},
        },
    )


def test_get_manual_angle_of_illumination(light_control):
    """Test get manual angle of illumination API."""
    light_control._request.return_value = response_getManualAngleOfIllumination
    response = light_control.get_manual_angle_of_illumination("led0")
    light_control._request.assert_called_with(
        "post",
        "/axis-cgi/lightcontrol.cgi",
        json={
            "method": "getManualAngleOfIllumination",
            "apiVersion": "1.1",
            "context": "Axis library",
            "params": {"lightID": "led0"},
        },
    )

    assert response["data"] == {"angleOfIllumination": 30}


def test_get_current_angle_of_illumination(light_control):
    """Test get current angle of illumination API."""
    light_control._request.return_value = response_getCurrentAngleOfIllumination
    response = light_control.get_current_angle_of_illumination("led0")
    light_control._request.assert_called_with(
        "post",
        "/axis-cgi/lightcontrol.cgi",
        json={
            "method": "getCurrentAngleOfIllumination",
            "apiVersion": "1.1",
            "context": "Axis library",
            "params": {"lightID": "led0"},
        },
    )

    assert response["data"] == {"angleOfIllumination": 20}


def test_set_light_synchronization_day_night_mode(light_control):
    """Test set light synchronization day night mode API."""
    light_control.set_light_synchronization_day_night_mode("led0", True)
    light_control._request.assert_called_with(
        "post",
        "/axis-cgi/lightcontrol.cgi",
        json={
            "method": "setLightSynchronizationDayNightMode",
            "apiVersion": "1.1",
            "context": "Axis library",
            "params": {"lightID": "led0", "enabled": True},
        },
    )


def test_get_light_synchronization_day_night_mode(light_control):
    """Test get light synchronization day night mode API."""
    light_control._request.return_value = response_getLightSynchronizationDayNightMode
    response = light_control.get_light_synchronization_day_night_mode("led0")
    light_control._request.assert_called_with(
        "post",
        "/axis-cgi/lightcontrol.cgi",
        json={
            "method": "getLightSynchronizationDayNightMode",
            "apiVersion": "1.1",
            "context": "Axis library",
            "params": {"lightID": "led0"},
        },
    )

    assert response["data"] == {"enabled": True}


def test_get_supported_versions(light_control):
    """Test get supported versions api."""
    light_control._request.return_value = response_getSupportedVersions
    response = light_control.get_supported_versions()
    light_control._request.assert_called_with(
        "post", "/axis-cgi/lightcontrol.cgi", json={"method": "getSupportedVersions"},
    )

    assert response["data"] == {"apiVersions": ["1.1"]}


response_getServiceCapabilities = {
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
}

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

response_getValidIntensity = {
    "apiVersion": "1.1",
    "method": "getValidIntensity",
    "data": {"ranges": [{"low": 0, "high": 1000}]},
}

response_getLightStatus = {
    "apiVersion": "1.1",
    "method": "getLightStatus",
    "data": {"status": False},
}

response_getManualIntensity = {
    "apiVersion": "1.1",
    "method": "getManualIntensity",
    "data": {"intensity": 1000},
}

response_getIndividualIntensity = {
    "apiVersion": "1.1",
    "method": "getIndividualIntensity",
    "data": {"intensity": 1000},
}

response_getCurrentIntensity = {
    "apiVersion": "1.1",
    "method": "getCurrentIntensity",
    "data": {"intensity": 1000},
}

response_getValidAngleOfIllumination = {
    "apiVersion": "1.0",
    "context": "my context",
    "method": "getValidAngleOfIllumination",
    "data": {"ranges": [{"low": 10, "high": 30}, {"low": 20, "high": 50}]},
}

response_getManualAngleOfIllumination = {
    "apiVersion": "1.0",
    "context": "my context",
    "method": "getManualAngleOfIllumination",
    "data": {"angleOfIllumination": 30},
}

response_getCurrentAngleOfIllumination = {
    "apiVersion": "1.0",
    "context": "my context",
    "method": "getCurrentAngleOfIllumination",
    "data": {"angleOfIllumination": 20},
}

response_getLightSynchronizationDayNightMode = {
    "apiVersion": "1.1",
    "context": "my context",
    "method": "getLightSynchronizeDayNightMode",
    "data": {"enabled": True},
}

response_getSupportedVersions = {
    "method": "getSupportedVersions",
    "data": {"apiVersions": ["1.1"]},
}
