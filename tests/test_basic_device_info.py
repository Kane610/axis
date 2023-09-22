"""Test Axis Basic Device Info API.

pytest --cov-report term-missing --cov=axis.basic_device_info tests/test_basic_device_info.py
"""

import json
from unittest.mock import MagicMock

import pytest
import respx

from axis.device import AxisDevice
from axis.vapix.interfaces.basic_device_info import BasicDeviceInfoHandler

from .conftest import HOST


@pytest.fixture
def basic_device_info(axis_device: AxisDevice) -> BasicDeviceInfoHandler:
    """Return the basic_device_info mock object."""
    axis_device.vapix.api_discovery = api_discovery_mock = MagicMock()
    api_discovery_mock.__getitem__().version = "1.0"
    return axis_device.vapix.basic_device_info


@respx.mock
async def test_get_all_properties(basic_device_info: BasicDeviceInfoHandler):
    """Test get all properties api."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/basicdeviceinfo.cgi").respond(
        json=response_getAllProperties,
    )
    await basic_device_info.update()

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/basicdeviceinfo.cgi"
    assert json.loads(route.calls.last.request.content) == {
        "method": "getAllProperties",
        "apiVersion": "1.1",
        "context": "Axis library",
    }

    assert basic_device_info.architecture == "armv7hf"
    assert basic_device_info.brand == "AXIS"
    assert basic_device_info.builddate == "Apr 29 2020 06:50"
    assert basic_device_info.hardwareid == "70E"
    assert basic_device_info.prodfullname == "AXIS M1065-LW Network Camera"
    assert basic_device_info.prodnbr == "M1065-LW"
    assert basic_device_info.prodshortname == "AXIS M1065-LW"
    assert basic_device_info.prodtype == "Network Camera"
    assert basic_device_info.prodvariant == ""
    assert basic_device_info.serialnumber == "ACCC12345678"
    assert basic_device_info.soc == "Ambarella S2L (Flattened Device Tree)"
    assert basic_device_info.socserialnumber == ""
    assert basic_device_info.version == "9.80.1"
    assert basic_device_info.weburl == "http://www.axis.com"

    items = await basic_device_info.get_all_properties()
    assert len(items) == 1


@respx.mock
async def test_get_supported_versions(basic_device_info: BasicDeviceInfoHandler):
    """Test get supported versions api."""
    route = respx.post(f"http://{HOST}:80/axis-cgi/basicdeviceinfo.cgi").respond(
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
        # "apiVersion": "1.1",
        "context": "Axis library",
        "method": "getSupportedVersions",
    }

    assert response == ["1.1"]


response_getAllProperties = {
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
