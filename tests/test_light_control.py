"""Test Axis Light Control API.

pytest --cov-report term-missing --cov=axis.light_control tests/test_light_control.py
"""

import json
from types import SimpleNamespace
from typing import TYPE_CHECKING

from aiohttp import web
import pytest

from axis.models.api_discovery import Api

if TYPE_CHECKING:
    from axis.device import AxisDevice
    from axis.interfaces.light_control import LightHandler


class _CallList(list):
    @property
    def last(self):
        return self[-1]


class _Route:
    def __init__(self, path: str) -> None:
        self.path = path
        self.called = False
        self.calls = _CallList()
        self._json: dict | list | None = None
        self._text: str | None = None
        self._content: bytes | None = None
        self._status_code = 200
        self._headers: dict[str, str] | None = None

    def respond(
        self,
        *,
        json: dict | list | None = None,
        text: str | None = None,
        content: bytes | None = None,
        status_code: int = 200,
        headers: dict[str, str] | None = None,
    ):
        self._json = json
        self._text = text
        self._content = content
        self._status_code = status_code
        self._headers = headers
        return self

    def make_response(self) -> web.Response:
        if self._json is not None:
            return web.json_response(
                self._json,
                status=self._status_code,
                headers=self._headers,
            )
        if self._text is not None:
            return web.Response(
                text=self._text,
                status=self._status_code,
                headers=self._headers,
            )
        if self._content is not None:
            return web.Response(
                body=self._content,
                status=self._status_code,
                headers=self._headers,
            )
        return web.Response(status=self._status_code, headers=self._headers)


class _RespxMockShim:
    def __init__(self) -> None:
        self._routes: dict[tuple[str, str], _Route] = {}

    def post(self, path: str) -> _Route:
        route = _Route(path)
        self._routes[("POST", path)] = route
        return route

    def resolve(self, method: str, path: str) -> _Route | None:
        return self._routes.get((method, path))


@pytest.fixture
async def respx_mock(aiohttp_server, axis_device_aiohttp: AxisDevice):
    """Return a minimal respx-compatible shim backed by aiohttp_server."""
    mock = _RespxMockShim()

    async def handle_request(request: web.Request) -> web.Response:
        route = mock.resolve(request.method, request.path)
        if route is None:
            return web.Response(status=404)

        route.called = True
        content = await request.read()
        route.calls.append(
            SimpleNamespace(
                request=SimpleNamespace(
                    method=request.method,
                    url=SimpleNamespace(path=request.path),
                    content=content,
                )
            )
        )
        return route.make_response()

    app = web.Application()
    app.router.add_route("*", "/{tail:.*}", handle_request)
    server = await aiohttp_server(app)
    axis_device_aiohttp.vapix.device.config.port = server.port

    return mock


@pytest.fixture
async def light_control(axis_device_aiohttp: AxisDevice) -> LightHandler:
    """Return the light_control mock object."""
    axis_device_aiohttp.vapix.api_discovery._items = {
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
    return axis_device_aiohttp.vapix.light_control


async def test_update(respx_mock, light_control):
    """Test update method."""
    route = respx_mock.post("/axis-cgi/lightcontrol.cgi").respond(
        json={
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


async def test_get_service_capabilities(respx_mock, light_control: LightHandler):
    """Test get service capabilities API."""
    route = respx_mock.post("/axis-cgi/lightcontrol.cgi").respond(
        json={
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


async def test_get_light_information(respx_mock, light_control: LightHandler):
    """Test get light information API."""
    route = respx_mock.post("/axis-cgi/lightcontrol.cgi").respond(
        json={
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


async def test_get_light_information_error(respx_mock, light_control: LightHandler):
    """Test get light information API return error."""
    respx_mock.post("/axis-cgi/lightcontrol.cgi").respond(
        json={
            "apiVersion": "1.0",
            "context": "Axis library",
            "method": "getLightInformation",
            "error": {
                "code": 1005,
                "message": "No light hardware found, could not complete request.",
            },
        },
    )

    response = await light_control.get_light_information()
    assert len(response) == 0


async def test_activate_light(respx_mock, light_control):
    """Test activating light API."""
    route = respx_mock.post("/axis-cgi/lightcontrol.cgi").respond(
        json={
            "apiVersion": "1.0",
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
        "apiVersion": "1.0",
        "context": "Axis library",
        "params": {"lightID": "led0"},
    }


async def test_deactivate_light(respx_mock, light_control):
    """Test deactivating light API."""
    route = respx_mock.post("/axis-cgi/lightcontrol.cgi").respond(
        json={
            "apiVersion": "1.0",
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
        "apiVersion": "1.0",
        "context": "Axis library",
        "params": {"lightID": "led0"},
    }


async def test_enable_light(respx_mock, light_control):
    """Test enabling light API."""
    route = respx_mock.post("/axis-cgi/lightcontrol.cgi").respond(
        json={
            "apiVersion": "1.0",
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
        "apiVersion": "1.0",
        "context": "Axis library",
        "params": {"lightID": "led0"},
    }


async def test_disable_light(respx_mock, light_control):
    """Test disabling light API."""
    route = respx_mock.post("/axis-cgi/lightcontrol.cgi").respond(
        json={
            "apiVersion": "1.0",
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
        "apiVersion": "1.0",
        "context": "Axis library",
        "params": {"lightID": "led0"},
    }


async def test_get_light_status(respx_mock, light_control):
    """Test get light status API."""
    route = respx_mock.post("/axis-cgi/lightcontrol.cgi").respond(
        json={
            "apiVersion": "1.0",
            "context": "Axis library",
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
        "apiVersion": "1.0",
        "context": "Axis library",
        "params": {"lightID": "led0"},
    }

    assert response is False


async def test_set_automatic_intensity_mode(respx_mock, light_control):
    """Test set automatic intensity mode API."""
    route = respx_mock.post("/axis-cgi/lightcontrol.cgi").respond(
        json={
            "apiVersion": "1.0",
            "context": "Axis library",
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
        "apiVersion": "1.0",
        "context": "Axis library",
        "params": {"lightID": "led0", "enabled": True},
    }


async def test_get_manual_intensity(respx_mock, light_control):
    """Test get valid intensity API."""
    route = respx_mock.post("/axis-cgi/lightcontrol.cgi").respond(
        json={
            "apiVersion": "1.0",
            "context": "Axis library",
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
        "apiVersion": "1.0",
        "context": "Axis library",
        "params": {"lightID": "led0"},
    }

    assert response == 1000


async def test_set_manual_intensity(respx_mock, light_control):
    """Test set manual intensity API."""
    route = respx_mock.post("/axis-cgi/lightcontrol.cgi").respond(
        json={
            "apiVersion": "1.0",
            "context": "Axis library",
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
        "apiVersion": "1.0",
        "context": "Axis library",
        "params": {"lightID": "led0", "intensity": 1000},
    }


async def test_get_valid_intensity(respx_mock, light_control):
    """Test get valid intensity API."""
    route = respx_mock.post("/axis-cgi/lightcontrol.cgi").respond(
        json={
            "apiVersion": "1.0",
            "context": "Axis library",
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
        "apiVersion": "1.0",
        "context": "Axis library",
        "params": {"lightID": "led0"},
    }

    assert response.low == 0
    assert response.high == 1000


async def test_set_individual_intensity(respx_mock, light_control):
    """Test set individual intensity API."""
    route = respx_mock.post("/axis-cgi/lightcontrol.cgi").respond(
        json={
            "apiVersion": "1.0",
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
        "apiVersion": "1.0",
        "context": "Axis library",
        "params": {"lightID": "led0", "LEDID": 1, "intensity": 1000},
    }


async def test_get_individual_intensity(respx_mock, light_control):
    """Test get individual intensity API."""
    route = respx_mock.post("/axis-cgi/lightcontrol.cgi").respond(
        json={
            "apiVersion": "1.0",
            "context": "Axis library",
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
        "apiVersion": "1.0",
        "context": "Axis library",
        "params": {"lightID": "led0", "LEDID": 1},
    }

    assert response == 1000


async def test_get_current_intensity(respx_mock, light_control):
    """Test get current intensity API."""
    route = respx_mock.post("/axis-cgi/lightcontrol.cgi").respond(
        json={
            "apiVersion": "1.0",
            "context": "Axis library",
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
        "apiVersion": "1.0",
        "context": "Axis library",
        "params": {"lightID": "led0"},
    }

    assert response == 1000


async def test_set_automatic_angle_of_illumination_mode(respx_mock, light_control):
    """Test set automatic angle of illumination mode API."""
    route = respx_mock.post("/axis-cgi/lightcontrol.cgi").respond(
        json={
            "apiVersion": "1.0",
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
        "apiVersion": "1.0",
        "context": "Axis library",
        "params": {"lightID": "led0", "enabled": True},
    }


async def test_get_valid_angle_of_illumination(respx_mock, light_control: LightHandler):
    """Test get valid angle of illumination API."""
    route = respx_mock.post("/axis-cgi/lightcontrol.cgi").respond(
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
        "apiVersion": "1.0",
        "context": "Axis library",
        "params": {"lightID": "led0"},
    }

    assert response[0].low == 10
    assert response[0].high == 30
    assert response[1].low == 20
    assert response[1].high == 50


async def test_set_manual_angle_of_illumination(respx_mock, light_control):
    """Test set manual angle of illumination API."""
    route = respx_mock.post("/axis-cgi/lightcontrol.cgi").respond(
        json={
            "apiVersion": "1.0",
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
        "apiVersion": "1.0",
        "context": "Axis library",
        "params": {"lightID": "led0", "angleOfIllumination": 30},
    }


async def test_get_manual_angle_of_illumination(respx_mock, light_control):
    """Test get manual angle of illumination API."""
    route = respx_mock.post("/axis-cgi/lightcontrol.cgi").respond(
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
        "apiVersion": "1.0",
        "context": "Axis library",
        "params": {"lightID": "led0"},
    }

    assert response == 30


async def test_get_current_angle_of_illumination(respx_mock, light_control):
    """Test get current angle of illumination API."""
    route = respx_mock.post("/axis-cgi/lightcontrol.cgi").respond(
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
        "apiVersion": "1.0",
        "context": "Axis library",
        "params": {"lightID": "led0"},
    }

    assert response == 20


async def test_set_light_synchronization_day_night_mode(respx_mock, light_control):
    """Test set light synchronization day night mode API."""
    route = respx_mock.post("/axis-cgi/lightcontrol.cgi").respond(
        json={
            "apiVersion": "1.0",
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
        "apiVersion": "1.0",
        "context": "Axis library",
        "params": {"lightID": "led0", "enabled": True},
    }


async def test_get_light_synchronization_day_night_mode(
    respx_mock, light_control: LightHandler
):
    """Test get light synchronization day night mode API."""
    route = respx_mock.post("/axis-cgi/lightcontrol.cgi").respond(
        json={
            "apiVersion": "1.0",
            "context": "my context",
            "method": "getLightSynchronizeDayNightMode",
            "data": {"synchronize": True},
        },
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


async def test_get_supported_versions(respx_mock, light_control):
    """Test get supported versions api."""
    route = respx_mock.post("/axis-cgi/lightcontrol.cgi").respond(
        json={
            "apiVersion": "1.0",
            "context": "Axis library",
            "method": "getSupportedVersions",
            "data": {"apiVersions": ["1.1"]},
        },
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
