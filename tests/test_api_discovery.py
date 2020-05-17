"""Test Axis API Discovery API.

pytest --cov-report term-missing --cov=axis.api_discovery tests/test_api_discovery.py
"""

from asynctest import Mock

from axis.api_discovery import ApiDiscovery


def test_mqtt():
    """Test MQTT Client API works."""
    mock_request = Mock()
    mock_request.return_value = ""
    api_discovery = ApiDiscovery({}, mock_request)

    api_discovery.api_list()
    mock_request.assert_called_with(
        "post",
        "/axis-cgi/apidiscovery.cgi",
        data={"method": "getApiList", "apiVersion": "1.0"},
    )

    api_discovery.supported_versions()
    mock_request.assert_called_with(
        "post",
        "/axis-cgi/apidiscovery.cgi",
        data={"method": "getSupportedVersions", "apiVersion": "1.0"},
    )


getApiListResponse = {
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

getSupportedVersionsResponse = {
    "method": "getSupportedVersions",
    "data": {"apiVersions": ["1.0"]},
}
