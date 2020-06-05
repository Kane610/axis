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
    light_control._request.return_value = response_getIndividualIntensith
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
    light_control._request.return_value = response_getCurrentIntensith
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

response_getIndividualIntensith = {
    "apiVersion": "1.1",
    "method": "getIndividualIntensity",
    "data": {"intensity": 1000},
}

response_getCurrentIntensith = {
    "apiVersion": "1.1",
    "method": "getCurrentIntensity",
    "data": {"intensity": 1000},
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
