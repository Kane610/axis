"""Test Vapix network API main class.

pytest --cov-report term-missing --cov=axis.vapix tests/test_vapix.py
"""

from unittest.mock import call
from asynctest import Mock, patch
import json
import pytest

from axis.vapix import Vapix
from .test_api_discovery import response_getApiList as api_discovery_response
from .test_basic_device_info import (
    response_getAllProperties as basic_device_info_response,
)
from .test_port_management import response_getPorts as io_port_management_response
from .test_param_cgi import response_param_cgi
from .test_stream_profiles import response_list as stream_profiles_response


@pytest.fixture
def mock_config() -> Mock:
    """Returns the configuration mock object."""
    mock_config = Mock()
    mock_config.host = "mock_host"
    mock_config.url = "mock_url"
    mock_config.session.get = "mock_get"
    mock_config.session.post = "mock_post"
    return mock_config


def test_initialize_api_discovery(mock_config):
    """Verify that you can initialize API Discovery and that devicelist parameters."""
    with patch(
        "axis.vapix.session_request",
        side_effect=[
            json.dumps(api_discovery_response),
            json.dumps(basic_device_info_response),
            json.dumps(io_port_management_response),
            json.dumps(stream_profiles_response),
        ],
    ) as mock_request:
        vapix = Vapix(mock_config)
        vapix.initialize_api_discovery()

    assert len(mock_request.mock_calls) == 4
    mock_request.assert_has_calls(
        [
            call(
                "mock_post",
                "mock_url/axis-cgi/apidiscovery.cgi",
                json={
                    "method": "getApiList",
                    "apiVersion": "1.0",
                    "context": "Axis library",
                },
            ),
            call(
                "mock_post",
                "mock_url/axis-cgi/basicdeviceinfo.cgi",
                json={
                    "method": "getAllProperties",
                    "apiVersion": "1.1",
                    "context": "Axis library",
                },
            ),
            call(
                "mock_post",
                "mock_url/axis-cgi/io/portmanagement.cgi",
                json={
                    "method": "getPorts",
                    "apiVersion": "1.0",
                    "context": "Axis library",
                },
            ),
            call(
                "mock_post",
                "mock_url/axis-cgi/streamprofile.cgi",
                json={
                    "method": "list",
                    "apiVersion": "1.0",
                    "context": "Axis library",
                    "params": {"streamProfileName": []},
                },
            ),
        ]
    )

    assert vapix.firmware_version == "9.80.1"
    assert vapix.product_number == "M1065-LW"
    assert vapix.product_type == "Network Camera"
    assert vapix.serial_number == "ACCC12345678"


def test_initialize_param_cgi(mock_config):
    """Verify that you can list parameters."""
    with patch(
        "axis.vapix.session_request", return_value=response_param_cgi
    ) as mock_request:
        vapix = Vapix(mock_config)
        vapix.initialize_param_cgi()

    mock_request.assert_called_with(
        "mock_get", "mock_url/axis-cgi/param.cgi?action=list"
    )
    assert vapix.params["root.Brand.Brand"].raw == "AXIS"
    assert vapix.firmware_version == "9.10.1"
    assert vapix.product_number == "M1065-LW"
    assert vapix.product_type == "Network Camera"
    assert vapix.serial_number == "ACCC12345678"


def test_initialize_params_no_data(mock_config):
    """Verify that you can list parameters."""
    with patch("axis.vapix.session_request", return_value="key=value") as mock_request:
        vapix = Vapix(mock_config)
        vapix.initialize_param_cgi(preload_data=False)

    mock_request.assert_not_called


def test_initialize_users(mock_config):
    """Verify that you can list parameters."""
    with patch(
        "axis.vapix.session_request",
        return_value="""users="userv"
viewer="userv"
operator="usera"
admin="usera"
ptz=
""",
    ) as mock_request:
        vapix = Vapix(mock_config)
        vapix.initialize_users()

    mock_request.assert_called_with(
        "mock_get", "mock_url/axis-cgi/pwdgrp.cgi?action=get"
    )
    assert vapix.users["userv"].viewer
