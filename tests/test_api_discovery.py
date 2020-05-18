"""Test Axis API Discovery API.

pytest --cov-report term-missing --cov=axis.api_discovery tests/test_api_discovery.py
"""

from asynctest import Mock

from axis.api_discovery import ApiDiscovery, API_DISCOVERY_ID


def test_api_discovery():
    """Test API Discovery API works."""
    mock_request = Mock()
    mock_request.return_value = ""
    api_discovery = ApiDiscovery({}, mock_request)

    api_discovery.get_api_list()
    mock_request.assert_called_with(
        "post",
        "/axis-cgi/apidiscovery.cgi",
        json={"method": "getApiList", "apiVersion": "1.0"},
    )

    mock_request.return_value = response_getSupportedVersions
    response = api_discovery.get_supported_versions()
    mock_request.assert_called_with(
        "post", "/axis-cgi/apidiscovery.cgi", json={"method": "getSupportedVersions"},
    )
    assert response["data"] == {"apiVersions": ["1.0"]}

    mock_request.return_value = response_getApiList
    api_discovery.update()
    assert len(api_discovery.values()) == 14

    item = api_discovery[API_DISCOVERY_ID]
    assert item.id == "api-discovery"
    assert item.name == "API Discovery Service"
    assert item.version == "1.0"


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
                "id": "io-port-management",
                "version": "1.0",
                "name": "IO Port Management",
                "docLink": "https://www.axis.com/partner_pages/vapix_library/#/",
            },
            {
                "id": "stream-profiles",
                "version": "1.0",
                "name": "Stream Profiles",
                "docLink": "https://www.axis.com/partner_pages/vapix_library/#/",
            },
            {
                "id": "mqtt-client",
                "version": "1.0",
                "name": "MQTT Client API",
                "docLink": "https://www.axis.com/partner_pages/vapix_library/#/",
            },
            {
                "id": "systemready",
                "version": "1.1",
                "name": "Systemready",
                "docLink": "https://www.axis.com/partner_pages/vapix_library/#/",
            },
            {
                "id": "basic-device-info",
                "version": "1.1",
                "name": "Basic Device Information",
                "docLink": "https://www.axis.com/partner_pages/vapix_library/#/",
            },
            {
                "id": "user-management",
                "version": "1.1",
                "name": "User Management",
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
                "id": "ptz-control",
                "version": "1.0",
                "name": "PTZ Control",
                "docLink": "https://www.axis.com/partner_pages/vapix_library/#/",
            },
            {
                "id": "capture-mode",
                "version": "1.0",
                "name": "Capture Mode",
                "docLink": "https://www.axis.com/partner_pages/vapix_library/#/",
            },
            {
                "id": "light-control",
                "version": "1.1",
                "name": "Light Control",
                "docLink": "https://www.axis.com/partner_pages/vapix_library/#/",
            },
            {
                "id": "guard-tour",
                "version": "1.0",
                "name": "Guard Tour",
                "docLink": "https://www.axis.com/partner_pages/vapix_library/#/",
            },
            {
                "id": "param-cgi",
                "version": "1.0",
                "name": "Legacy Parameter Handling",
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
