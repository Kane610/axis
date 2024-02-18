"""Test Axis API Discovery API.

pytest --cov-report term-missing --cov=axis.api_discovery tests/test_api_discovery.py
"""

import json

import pytest

from axis.device import AxisDevice
from axis.vapix.interfaces.api_discovery import ApiDiscoveryHandler
from axis.vapix.models.api_discovery import ApiId, ApiStatus


@pytest.fixture
def api_discovery(axis_device: AxisDevice) -> ApiDiscoveryHandler:
    """Return the api_discovery mock object."""
    return axis_device.vapix.api_discovery


async def test_api_id_enum():
    """Verify API ID of unsupported type."""
    assert ApiId("unsupported") is ApiId.UNKNOWN


async def test_api_status_enum():
    """Verify API status of unsupported type."""
    assert ApiStatus("unsupported") is ApiStatus.UNKNOWN


async def test_get_api_list(respx_mock, api_discovery: ApiDiscoveryHandler):
    """Test get_api_list call."""
    route = respx_mock.post("/axis-cgi/apidiscovery.cgi").respond(
        json=GET_API_LIST_RESPONSE,
    )
    assert api_discovery.supported
    await api_discovery.update()

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/apidiscovery.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "method": "getApiList",
        "apiVersion": "1.0",
        "context": "Axis library",
    }

    assert api_discovery.initialized
    assert len(api_discovery.values()) == 15

    item = api_discovery[ApiId.API_DISCOVERY]
    assert item.api_id == ApiId.API_DISCOVERY
    assert item.id == "api-discovery"
    assert item.name == "API Discovery Service"
    assert item.status == ApiStatus.UNKNOWN
    assert item.version == "1.0"


async def test_get_supported_versions(respx_mock, api_discovery: ApiDiscoveryHandler):
    """Test get_supported_versions."""
    route = respx_mock.post("/axis-cgi/apidiscovery.cgi").respond(
        json=GET_SUPPORTED_VERSIONS_RESPONSE,
    )
    response = await api_discovery.get_supported_versions()

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/apidiscovery.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "context": "Axis library",
        "method": "getSupportedVersions",
    }

    assert response == ["1.0"]


GET_API_LIST_RESPONSE = {
    "method": "getApiList",
    "apiVersion": "1.0",
    "context": "Axis library",
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

GET_SUPPORTED_VERSIONS_RESPONSE = {
    "apiVersion": "1.0",
    "context": "Axis library",
    "method": "getSupportedVersions",
    "data": {"apiVersions": ["1.0"]},
}
