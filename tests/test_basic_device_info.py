"""Test Axis Basic Device Info API.

pytest --cov-report term-missing --cov=axis.basic_device_info tests/test_basic_device_info.py
"""

import pytest
from unittest.mock import Mock

from axis.basic_device_info import BasicDeviceInfo


@pytest.fixture
def basic_device_info() -> BasicDeviceInfo:
    """Returns the basic_device_info mock object."""
    mock_request = Mock()
    mock_request.return_value = ""
    return BasicDeviceInfo(mock_request)


def test_get_all_properties(basic_device_info):
    """Test get all properties api."""
    basic_device_info._request.return_value = response_getAllProperties
    basic_device_info.update()
    basic_device_info._request.assert_called_with(
        "post",
        "/axis-cgi/basicdeviceinfo.cgi",
        json={
            "method": "getAllProperties",
            "apiVersion": "1.1",
            "context": "Axis library",
        },
    )

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


def test_get_supported_versions(basic_device_info):
    """Test get supported versions api."""
    basic_device_info._request.return_value = response_getSupportedVersions
    response = basic_device_info.get_supported_versions()
    basic_device_info._request.assert_called_with(
        "post",
        "/axis-cgi/basicdeviceinfo.cgi",
        json={"method": "getSupportedVersions"},
    )

    assert response["data"] == {"apiVersions": ["1.1"]}


response_getAllProperties = {
    "apiVersion": "1.1",
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


response_getSupportedVersions = {
    "method": "getSupportedVersions",
    "data": {"apiVersions": ["1.1"]},
}
