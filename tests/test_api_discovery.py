"""Test Axis API Discovery API.

pytest --cov-report term-missing --cov=axis.api_discovery tests/test_api_discovery.py
"""

import json
import pytest

import respx

from axis.api_discovery import ApiDiscovery, API_DISCOVERY_ID

from .conftest import HOST


@pytest.fixture
def api_discovery(axis_device) -> ApiDiscovery:
    """Returns the api_discovery mock object."""
    return ApiDiscovery(axis_device.vapix.request)


@respx.mock
@pytest.mark.asyncio
async def test_get_api_list(api_discovery):
    """Test get_api_list call."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/apidiscovery.cgi").respond(
        json=response_getApiList,
    )
    await api_discovery.update()

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/apidiscovery.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "method": "getApiList",
        "apiVersion": "1.0",
        "context": "Axis library",
    }

    assert len(api_discovery.values()) == 15

    item = api_discovery[API_DISCOVERY_ID]
    assert item.id == "api-discovery"
    assert item.name == "API Discovery Service"
    assert item.version == "1.0"


@respx.mock
@pytest.mark.asyncio
async def test_get_supported_versions(api_discovery):
    """Test get_supported_versions"""
    route = respx.post(f"http://{HOST}:80/axis-cgi/apidiscovery.cgi").respond(
        json=response_getSupportedVersions,
    )
    response = await api_discovery.get_supported_versions()

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/apidiscovery.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "method": "getSupportedVersions"
    }

    assert response["data"] == {"apiVersions": ["1.0"]}


response_getApiList = {
    "method": "getApiList",
    "apiVersion": "1.0",
    "data": {
        "apiList": [
            {
                "id": "api-discovery",
                "version": "1.0",
                "name": "API Discovery Service",
                "docLink": "https://www.axis.com/partner_pages/vapix_library/#/",
            },
            {
                "id": "basic-device-info",
                "version": "1.1",
                "name": "Basic Device Information",
                "docLink": "https://www.axis.com/partner_pages/vapix_library/#/",
            },
            {
                "id": "capture-mode",
                "version": "1.0",
                "name": "Capture Mode",
                "docLink": "https://www.axis.com/partner_pages/vapix_library/#/",
            },
            {
                "id": "guard-tour",
                "version": "1.0",
                "name": "Guard Tour",
                "docLink": "https://www.axis.com/partner_pages/vapix_library/#/",
            },
            {
                "id": "io-port-management",
                "version": "1.0",
                "name": "IO Port Management",
                "docLink": "https://www.axis.com/partner_pages/vapix_library/#/",
            },
            {
                "id": "light-control",
                "version": "1.1",
                "name": "Light Control",
                "docLink": "https://www.axis.com/partner_pages/vapix_library/#/",
            },
            {
                "id": "mqtt-client",
                "version": "1.0",
                "name": "MQTT Client API",
                "docLink": "https://www.axis.com/partner_pages/vapix_library/#/",
            },
            {
                "id": "onscreencontrols",
                "version": "1.4",
                "name": "On-Screen Controls",
                "docLink": "https://www.axis.com/partner_pages/vapix_library/#/",
            },
            {
                "id": "overlayimage",
                "version": "1.0",
                "name": "Overlay image API",
                "docLink": "https://www.axis.com/partner_pages/vapix_library/#/",
            },
            {
                "id": "param-cgi",
                "version": "1.0",
                "name": "Legacy Parameter Handling",
                "docLink": "https://www.axis.com/partner_pages/vapix_library/#/",
            },
            {
                "id": "ptz-control",
                "version": "1.0",
                "name": "PTZ Control",
                "docLink": "https://www.axis.com/partner_pages/vapix_library/#/",
            },
            {
                "id": "stream-profiles",
                "version": "1.0",
                "name": "Stream Profiles",
                "docLink": "https://www.axis.com/partner_pages/vapix_library/#/",
            },
            {
                "id": "systemready",
                "version": "1.1",
                "name": "Systemready",
                "docLink": "https://www.axis.com/partner_pages/vapix_library/#/",
            },
            {
                "id": "user-management",
                "version": "1.1",
                "name": "User Management",
                "docLink": "https://www.axis.com/partner_pages/vapix_library/#/",
            },
            {
                "id": "view-area",
                "version": "1.0",
                "name": "View Area",
                "docLink": "https://www.axis.com/partner_pages/vapix_library/#/",
            },
        ]
    },
}

response_getSupportedVersions = {
    "method": "getSupportedVersions",
    "data": {"apiVersions": ["1.0"]},
}

{
    "apiVersion": "1.0",
    "error": {
        "code": 4002,
        "message": "'apiVersion' must not be provided for method 'getSupportedVersions'",
    },
}
