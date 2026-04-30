"""Test Axis Basic Device Info API.

pytest --cov-report term-missing --cov=axis.basic_device_info tests/test_basic_device_info.py
"""

import json
from unittest.mock import MagicMock


async def test_get_all_properties(http_route_mock, axis_device):
    """Test get all properties api."""
    axis_device.vapix.api_discovery = api_discovery_mock = MagicMock()
    api_discovery_mock.get().version = "1.0"
    basic_device_info = axis_device.vapix.basic_device_info

    route = http_route_mock.post("/axis-cgi/basicdeviceinfo.cgi").respond(
        json=GET_ALL_PROPERTIES_RESPONSE,
    )

    await basic_device_info.update()

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/basicdeviceinfo.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "method": "getAllProperties",
        "apiVersion": "1.0",
        "context": "Axis library",
    }

    assert basic_device_info.initialized

    device_info = basic_device_info["0"]
    assert device_info.architecture == "armv7hf"
    assert device_info.brand == "AXIS"
    assert device_info.build_date == "Apr 29 2020 06:50"
    assert device_info.firmware_version == "9.80.1"
    assert device_info.hardware_id == "70E"
    assert device_info.product_full_name == "AXIS M1065-LW Network Camera"
    assert device_info.product_number == "M1065-LW"
    assert device_info.product_short_name == "AXIS M1065-LW"
    assert device_info.product_type == "Network Camera"
    assert device_info.product_variant == ""
    assert device_info.serial_number == "ACCC12345678"
    assert device_info.soc == "Ambarella S2L (Flattened Device Tree)"
    assert device_info.soc_serial_number == ""
    assert device_info.web_url == "http://www.axis.com"


async def test_get_supported_versions(http_route_mock, axis_device):
    """Test get supported versions api."""
    axis_device.vapix.api_discovery = api_discovery_mock = MagicMock()
    api_discovery_mock.get().version = "1.0"
    basic_device_info = axis_device.vapix.basic_device_info

    route = http_route_mock.post("/axis-cgi/basicdeviceinfo.cgi").respond(
        json={
            "apiVersion": "1.1",
            "context": "Axis library",
            "method": "getSupportedVersions",
            "data": {"apiVersions": ["1.1"]},
        },
    )

    response = await basic_device_info.get_supported_versions()

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/basicdeviceinfo.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "context": "Axis library",
        "method": "getSupportedVersions",
    }

    assert response == ["1.1"]


GET_ALL_PROPERTIES_RESPONSE = {
    "apiVersion": "1.1",
    "context": "Axis library",
    "method": "getAllProperties",
    "data": {
        "propertyList": {
            "Architecture": "armv7hf",
            "ProdNbr": "M1065-LW",
            "HardwareID": "70E",
            "Version": "9.80.1",
            "ProdFullName": "AXIS M1065-LW Network Camera",
            "Brand": "AXIS",
            "ProdType": "Network Camera",
            "Soc": "Ambarella S2L (Flattened Device Tree)",
            "SocSerialNumber": "",
            "WebURL": "http://www.axis.com",
            "ProdVariant": "",
            "SerialNumber": "ACCC12345678",
            "ProdShortName": "AXIS M1065-LW",
            "BuildDate": "Apr 29 2020 06:50",
        }
    },
}
