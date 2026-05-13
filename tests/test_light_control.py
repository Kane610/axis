"""Test Axis Light Control API.

pytest --cov-report term-missing --cov=axis.light_control tests/test_light_control.py
"""

import json
from typing import TYPE_CHECKING

import pytest

from axis.models.api_discovery import Api
from axis.models.light_control import (
    ActivateLightRequest,
    DeactivateLightRequest,
    DisableLightRequest,
    EnableLightRequest,
    GetCurrentAngleOfIlluminationRequest,
    GetCurrentIntensityRequest,
    GetIndividualIntensityRequest,
    GetLightInformationRequest,
    GetLightStatusRequest,
    GetLightSynchronizeDayNightModeRequest,
    GetManualAngleOfIlluminationRequest,
    GetManualIntensityRequest,
    GetServiceCapabilitiesRequest,
    GetSupportedVersionsRequest,
    GetValidAngleOfIlluminationRequest,
    GetValidIntensityRequest,
    SetAutomaticAngleOfIlluminationModeRequest,
    SetAutomaticIntensityModeRequest,
    SetIndividualIntensityRequest,
    SetLightSynchronizeDayNightModeRequest,
    SetManualAngleOfIlluminationModeRequest,
    SetManualIntensityRequest,
)

from tests.conftest import (
    MockApiRequestAssertions,
    MockApiResponseSpec,
    bind_mock_api_request,
)

if TYPE_CHECKING:
    from axis.device import AxisDevice
    from axis.interfaces.light_control import LightHandler


@pytest.fixture
async def light_control(axis_device: AxisDevice) -> LightHandler:
    """Return the light_control mock object."""
    axis_device.vapix.api_discovery._items = {
        api.id: api
        for api in [
            Api.decode(
                {
                    "id": "light-control",
                    "version": "1.0",
                    "name": "Light Control",
                    "docLink": "https://www.axis.com/partner_pages/vapix_library/#/",
                }
            )
        ]
    }
    return axis_device.vapix.light_control


@pytest.fixture
def mock_light_api_request(mock_api_request):
    """Register light-control route mocks via explicit ApiRequest classes."""

    def _register(api_request, json_data, *, content):
        return bind_mock_api_request(mock_api_request, api_request)(
            response=MockApiResponseSpec(json=json_data),
            assertions=MockApiRequestAssertions(content=content),
        )

    return _register


async def test_update(mock_light_api_request, light_control):
    """Test update method."""
    route = mock_light_api_request(
        GetLightInformationRequest,
        {
            "apiVersion": "1.0",
            "context": "Axis library",
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
        content=GetLightInformationRequest(api_version="1.0").content,
    )

    assert light_control.supported
    assert not light_control.listed_in_parameters
    await light_control.update()

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/lightcontrol.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "method": "getLightInformation",
        "apiVersion": "1.0",
        "context": "Axis library",
    }

    assert len(light_control.values()) == 1

    item = light_control["led0"]
    assert item.id == "led0"
    assert item.light_type == "IR"
    assert item.enabled is True
    assert item.synchronize_day_night_mode is True
    assert item.light_state is False
    assert item.automatic_intensity_mode is False
    assert item.automatic_angle_of_illumination_mode is False
    assert item.number_of_leds == 1
    assert item.error is False
    assert item.error_info == ""


async def test_get_service_capabilities(
    mock_light_api_request, light_control: LightHandler
):
    """Test get service capabilities API."""
    route = mock_light_api_request(
        GetServiceCapabilitiesRequest,
        {
            "apiVersion": "1.0",
            "context": "Axis library",
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
        content=GetServiceCapabilitiesRequest(api_version="1.0").content,
    )

    response = await light_control.get_service_capabilities()

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/lightcontrol.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "method": "getServiceCapabilities",
        "apiVersion": "1.0",
        "context": "Axis library",
    }

    assert response.automatic_intensity_support is True
    assert response.manual_intensity_support is True
    assert response.get_current_intensity_support is True
    assert response.individual_intensity_support is False
    assert response.automatic_angle_of_illumination_support is False
    assert response.manual_angle_of_illumination_support is False
    assert response.day_night_synchronize_support is True


async def test_get_light_information(
    mock_light_api_request, light_control: LightHandler
):
    """Test get light information API."""
    route = mock_light_api_request(
        GetLightInformationRequest,
        {
            "apiVersion": "1.0",
            "context": "Axis library",
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
        content=GetLightInformationRequest(api_version="1.0").content,
    )

    response = await light_control.get_light_information()

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/lightcontrol.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "method": "getLightInformation",
        "apiVersion": "1.0",
        "context": "Axis library",
    }

    light = response["led0"]
    assert light.id == "led0"
    assert light.light_type == "IR"
    assert light.enabled is True
    assert light.synchronize_day_night_mode is True
    assert light.light_state is False
    assert light.automatic_intensity_mode is False
    assert light.automatic_angle_of_illumination_mode is False
    assert light.number_of_leds == 1
    assert light.error is False
    assert light.error_info == ""


async def test_get_light_information_error(
    mock_light_api_request, light_control: LightHandler
):
    """Test get light information API return error."""
    mock_light_api_request(
        GetLightInformationRequest,
        {
            "apiVersion": "1.0",
            "context": "Axis library",
            "method": "getLightInformation",
            "error": {
                "code": 1005,
                "message": "No light hardware found, could not complete request.",
            },
        },
        content=GetLightInformationRequest(api_version="1.0").content,
    )

    response = await light_control.get_light_information()
    assert len(response) == 0


async def test_activate_light(mock_light_api_request, light_control):
    """Test activating light API."""
    route = mock_light_api_request(
        ActivateLightRequest,
        {
            "apiVersion": "1.0",
            "method": "activateLight",
            "data": {},
        },
        content=ActivateLightRequest(light_id="led0", api_version="1.0").content,
    )

    await light_control.activate_light("led0")

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/lightcontrol.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "method": "activateLight",
        "apiVersion": "1.0",
        "context": "Axis library",
        "params": {"lightID": "led0"},
    }


async def test_deactivate_light(mock_light_api_request, light_control):
    """Test deactivating light API."""
    route = mock_light_api_request(
        DeactivateLightRequest,
        {
            "apiVersion": "1.0",
            "method": "deactivateLight",
            "data": {},
        },
        content=DeactivateLightRequest(light_id="led0", api_version="1.0").content,
    )

    await light_control.deactivate_light("led0")

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/lightcontrol.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "method": "deactivateLight",
        "apiVersion": "1.0",
        "context": "Axis library",
        "params": {"lightID": "led0"},
    }


async def test_enable_light(mock_light_api_request, light_control):
    """Test enabling light API."""
    route = mock_light_api_request(
        EnableLightRequest,
        {
            "apiVersion": "1.0",
            "method": "enableLight",
            "data": {},
        },
        content=EnableLightRequest(light_id="led0", api_version="1.0").content,
    )

    await light_control.enable_light("led0")

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/lightcontrol.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "method": "enableLight",
        "apiVersion": "1.0",
        "context": "Axis library",
        "params": {"lightID": "led0"},
    }


async def test_disable_light(mock_light_api_request, light_control):
    """Test disabling light API."""
    route = mock_light_api_request(
        DisableLightRequest,
        {
            "apiVersion": "1.0",
            "method": "disableLight",
            "data": {},
        },
        content=DisableLightRequest(light_id="led0", api_version="1.0").content,
    )

    await light_control.disable_light("led0")

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/lightcontrol.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "method": "disableLight",
        "apiVersion": "1.0",
        "context": "Axis library",
        "params": {"lightID": "led0"},
    }


async def test_get_light_status(mock_light_api_request, light_control):
    """Test get light status API."""
    route = mock_light_api_request(
        GetLightStatusRequest,
        {
            "apiVersion": "1.0",
            "context": "Axis library",
            "method": "getLightStatus",
            "data": {"status": False},
        },
        content=GetLightStatusRequest(light_id="led0", api_version="1.0").content,
    )

    response = await light_control.get_light_status("led0")

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/lightcontrol.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "method": "getLightStatus",
        "apiVersion": "1.0",
        "context": "Axis library",
        "params": {"lightID": "led0"},
    }

    assert response is False


async def test_set_automatic_intensity_mode(mock_light_api_request, light_control):
    """Test set automatic intensity mode API."""
    route = mock_light_api_request(
        SetAutomaticIntensityModeRequest,
        {
            "apiVersion": "1.0",
            "context": "Axis library",
            "method": "setAutomaticIntensityMode",
            "data": {},
        },
        content=SetAutomaticIntensityModeRequest(
            light_id="led0",
            enabled=True,
            api_version="1.0",
        ).content,
    )

    await light_control.set_automatic_intensity_mode("led0", True)

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/lightcontrol.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "method": "setAutomaticIntensityMode",
        "apiVersion": "1.0",
        "context": "Axis library",
        "params": {"lightID": "led0", "enabled": True},
    }


async def test_get_manual_intensity(mock_light_api_request, light_control):
    """Test get valid intensity API."""
    route = mock_light_api_request(
        GetManualIntensityRequest,
        {
            "apiVersion": "1.0",
            "context": "Axis library",
            "method": "getManualIntensity",
            "data": {"intensity": 1000},
        },
        content=GetManualIntensityRequest(light_id="led0", api_version="1.0").content,
    )

    response = await light_control.get_manual_intensity("led0")

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/lightcontrol.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "method": "getManualIntensity",
        "apiVersion": "1.0",
        "context": "Axis library",
        "params": {"lightID": "led0"},
    }

    assert response == 1000


async def test_set_manual_intensity(mock_light_api_request, light_control):
    """Test set manual intensity API."""
    route = mock_light_api_request(
        SetManualIntensityRequest,
        {
            "apiVersion": "1.0",
            "context": "Axis library",
            "method": "setManualIntensity",
            "data": {},
        },
        content=SetManualIntensityRequest(
            light_id="led0",
            intensity=1000,
            api_version="1.0",
        ).content,
    )

    await light_control.set_manual_intensity("led0", 1000)

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/lightcontrol.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "method": "setManualIntensity",
        "apiVersion": "1.0",
        "context": "Axis library",
        "params": {"lightID": "led0", "intensity": 1000},
    }


async def test_get_valid_intensity(mock_light_api_request, light_control):
    """Test get valid intensity API."""
    route = mock_light_api_request(
        GetValidIntensityRequest,
        {
            "apiVersion": "1.0",
            "context": "Axis library",
            "method": "getValidIntensity",
            "data": {"ranges": [{"low": 0, "high": 1000}]},
        },
        content=GetValidIntensityRequest(light_id="led0", api_version="1.0").content,
    )

    response = await light_control.get_valid_intensity("led0")

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/lightcontrol.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "method": "getValidIntensity",
        "apiVersion": "1.0",
        "context": "Axis library",
        "params": {"lightID": "led0"},
    }

    assert response.low == 0
    assert response.high == 1000


async def test_set_individual_intensity(mock_light_api_request, light_control):
    """Test set individual intensity API."""
    route = mock_light_api_request(
        SetIndividualIntensityRequest,
        {
            "apiVersion": "1.0",
            "method": "setIndividualIntensity",
            "data": {},
        },
        content=SetIndividualIntensityRequest(
            light_id="led0",
            led_id=1,
            intensity=1000,
            api_version="1.0",
        ).content,
    )

    await light_control.set_individual_intensity("led0", 1, 1000)

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/lightcontrol.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "method": "setIndividualIntensity",
        "apiVersion": "1.0",
        "context": "Axis library",
        "params": {"lightID": "led0", "LEDID": 1, "intensity": 1000},
    }


async def test_get_individual_intensity(mock_light_api_request, light_control):
    """Test get individual intensity API."""
    route = mock_light_api_request(
        GetIndividualIntensityRequest,
        {
            "apiVersion": "1.0",
            "context": "Axis library",
            "method": "getIndividualIntensity",
            "data": {"intensity": 1000},
        },
        content=GetIndividualIntensityRequest(
            light_id="led0",
            led_id=1,
            api_version="1.0",
        ).content,
    )

    response = await light_control.get_individual_intensity("led0", 1)

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/lightcontrol.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "method": "getIndividualIntensity",
        "apiVersion": "1.0",
        "context": "Axis library",
        "params": {"lightID": "led0", "LEDID": 1},
    }

    assert response == 1000


async def test_get_current_intensity(mock_light_api_request, light_control):
    """Test get current intensity API."""
    route = mock_light_api_request(
        GetCurrentIntensityRequest,
        {
            "apiVersion": "1.0",
            "context": "Axis library",
            "method": "getCurrentIntensity",
            "data": {"intensity": 1000},
        },
        content=GetCurrentIntensityRequest(light_id="led0", api_version="1.0").content,
    )

    response = await light_control.get_current_intensity("led0")

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/lightcontrol.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "method": "getCurrentIntensity",
        "apiVersion": "1.0",
        "context": "Axis library",
        "params": {"lightID": "led0"},
    }

    assert response == 1000


async def test_set_automatic_angle_of_illumination_mode(
    mock_light_api_request, light_control
):
    """Test set automatic angle of illumination mode API."""
    route = mock_light_api_request(
        SetAutomaticAngleOfIlluminationModeRequest,
        {
            "apiVersion": "1.0",
            "method": "setAutomaticAngleOfIlluminationMode",
            "data": {},
        },
        content=SetAutomaticAngleOfIlluminationModeRequest(
            light_id="led0",
            enabled=True,
            api_version="1.0",
        ).content,
    )

    await light_control.set_automatic_angle_of_illumination_mode("led0", True)

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/lightcontrol.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "method": "setAutomaticAngleOfIlluminationMode",
        "apiVersion": "1.0",
        "context": "Axis library",
        "params": {"lightID": "led0", "enabled": True},
    }


async def test_get_valid_angle_of_illumination(
    mock_light_api_request, light_control: LightHandler
):
    """Test get valid angle of illumination API."""
    route = mock_light_api_request(
        GetValidAngleOfIlluminationRequest,
        {
            "apiVersion": "1.0",
            "context": "my context",
            "method": "getValidAngleOfIllumination",
            "data": {"ranges": [{"low": 10, "high": 30}, {"low": 20, "high": 50}]},
        },
        content=GetValidAngleOfIlluminationRequest(
            light_id="led0",
            api_version="1.0",
        ).content,
    )

    response = await light_control.get_valid_angle_of_illumination("led0")

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/lightcontrol.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "method": "getValidAngleOfIllumination",
        "apiVersion": "1.0",
        "context": "Axis library",
        "params": {"lightID": "led0"},
    }

    assert response[0].low == 10
    assert response[0].high == 30
    assert response[1].low == 20
    assert response[1].high == 50


async def test_set_manual_angle_of_illumination(mock_light_api_request, light_control):
    """Test set manual angle of illumination API."""
    route = mock_light_api_request(
        SetManualAngleOfIlluminationModeRequest,
        {
            "apiVersion": "1.0",
            "method": "setManualAngleOfIllumination",
            "data": {},
        },
        content=SetManualAngleOfIlluminationModeRequest(
            light_id="led0",
            angle_of_illumination=30,
            api_version="1.0",
        ).content,
    )

    await light_control.set_manual_angle_of_illumination("led0", 30)

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/lightcontrol.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "method": "setManualAngleOfIllumination",
        "apiVersion": "1.0",
        "context": "Axis library",
        "params": {"lightID": "led0", "angleOfIllumination": 30},
    }


async def test_get_manual_angle_of_illumination(mock_light_api_request, light_control):
    """Test get manual angle of illumination API."""
    route = mock_light_api_request(
        GetManualAngleOfIlluminationRequest,
        {
            "apiVersion": "1.0",
            "context": "my context",
            "method": "getManualAngleOfIllumination",
            "data": {"angleOfIllumination": 30},
        },
        content=GetManualAngleOfIlluminationRequest(
            light_id="led0",
            api_version="1.0",
        ).content,
    )

    response = await light_control.get_manual_angle_of_illumination("led0")

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/lightcontrol.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "method": "getManualAngleOfIllumination",
        "apiVersion": "1.0",
        "context": "Axis library",
        "params": {"lightID": "led0"},
    }

    assert response == 30


async def test_get_current_angle_of_illumination(mock_light_api_request, light_control):
    """Test get current angle of illumination API."""
    route = mock_light_api_request(
        GetCurrentAngleOfIlluminationRequest,
        {
            "apiVersion": "1.0",
            "context": "my context",
            "method": "getCurrentAngleOfIllumination",
            "data": {"angleOfIllumination": 20},
        },
        content=GetCurrentAngleOfIlluminationRequest(
            light_id="led0",
            api_version="1.0",
        ).content,
    )

    response = await light_control.get_current_angle_of_illumination("led0")

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/lightcontrol.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "method": "getCurrentAngleOfIllumination",
        "apiVersion": "1.0",
        "context": "Axis library",
        "params": {"lightID": "led0"},
    }

    assert response == 20


async def test_set_light_synchronization_day_night_mode(
    mock_light_api_request, light_control
):
    """Test set light synchronization day night mode API."""
    route = mock_light_api_request(
        SetLightSynchronizeDayNightModeRequest,
        {
            "apiVersion": "1.0",
            "method": "setLightSynchronizationDayNightMode",
            "data": {},
        },
        content=SetLightSynchronizeDayNightModeRequest(
            light_id="led0",
            enabled=True,
            api_version="1.0",
        ).content,
    )

    await light_control.set_light_synchronization_day_night_mode("led0", True)

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/lightcontrol.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "method": "setLightSynchronizationDayNightMode",
        "apiVersion": "1.0",
        "context": "Axis library",
        "params": {"lightID": "led0", "enabled": True},
    }


async def test_get_light_synchronization_day_night_mode(
    mock_light_api_request, light_control: LightHandler
):
    """Test get light synchronization day night mode API."""
    route = mock_light_api_request(
        GetLightSynchronizeDayNightModeRequest,
        {
            "apiVersion": "1.0",
            "context": "my context",
            "method": "getLightSynchronizeDayNightMode",
            "data": {"synchronize": True},
        },
        content=GetLightSynchronizeDayNightModeRequest(
            light_id="led0",
            api_version="1.0",
        ).content,
    )

    response = await light_control.get_light_synchronization_day_night_mode("led0")

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/lightcontrol.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "method": "getLightSynchronizationDayNightMode",
        "apiVersion": "1.0",
        "context": "Axis library",
        "params": {"lightID": "led0"},
    }

    assert response is True


async def test_get_supported_versions(mock_light_api_request, light_control):
    """Test get supported versions api."""
    route = mock_light_api_request(
        GetSupportedVersionsRequest,
        {
            "apiVersion": "1.0",
            "context": "Axis library",
            "method": "getSupportedVersions",
            "data": {"apiVersions": ["1.1"]},
        },
        content=GetSupportedVersionsRequest().content,
    )

    response = await light_control.get_supported_versions()

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/lightcontrol.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "method": "getSupportedVersions",
        "context": "Axis library",
    }

    assert response == ["1.1"]


GET_LIGHT_INFORMATION_RESPONSE = {
    "apiVersion": "1.0",
    "context": "Axis library",
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
