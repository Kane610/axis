"""Test Axis Basic Device Info API.

pytest --cov-report term-missing --cov=axis.basic_device_info tests/test_basic_device_info.py
"""

from unittest.mock import MagicMock

import pytest

from axis.models.basic_device_info import (
    GetAllPropertiesRequest,
    GetSupportedVersionsRequest,
)

from tests.conftest import (
    MockApiRequestAssertions,
    MockApiResponseSpec,
    bind_mock_api_request,
)


@pytest.fixture
def basic_device_info(axis_device):
    """Return the basic-device-info handler with api discovery primed."""
    axis_device.vapix.api_discovery = api_discovery_mock = MagicMock()
    api_discovery_mock.get().version = "1.0"
    return axis_device.vapix.basic_device_info


@pytest.fixture
def mock_get_all_properties_request(mock_api_request):
    """Register get-all-properties mocks via ApiRequest classes."""
    bound_request = bind_mock_api_request(mock_api_request, GetAllPropertiesRequest)

    def _register(json_data):
        return bound_request(
            response=MockApiResponseSpec(json=json_data),
            assertions=MockApiRequestAssertions(
                content=GetAllPropertiesRequest(api_version="1.0").content,
            ),
        )

    return _register


@pytest.fixture
def mock_get_supported_versions_request(mock_api_request):
    """Register supported-versions mocks via ApiRequest classes."""
    bound_request = bind_mock_api_request(mock_api_request, GetSupportedVersionsRequest)

    def _register(json_data):
        return bound_request(
            response=MockApiResponseSpec(json=json_data),
            assertions=MockApiRequestAssertions(
                content=GetSupportedVersionsRequest().content,
            ),
        )

    return _register


async def test_get_all_properties(mock_get_all_properties_request, basic_device_info):
    """Test get all properties api."""
    route = mock_get_all_properties_request(GET_ALL_PROPERTIES_RESPONSE)

    await basic_device_info.update()

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/basicdeviceinfo.cgi"

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


async def test_get_supported_versions(
    mock_get_supported_versions_request,
    basic_device_info,
):
    """Test get supported versions api."""
    route = mock_get_supported_versions_request(
        {
            "apiVersion": "1.1",
            "context": "Axis library",
            "method": "getSupportedVersions",
            "data": {"apiVersions": ["1.1"]},
        }
    )

    response = await basic_device_info.get_supported_versions()

    assert route.called
    assert route.calls.last.request.method == "POST"
    assert route.calls.last.request.url.path == "/axis-cgi/basicdeviceinfo.cgi"

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
