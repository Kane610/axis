"""Test Vapix network API main class.

pytest --cov-report term-missing --cov=axis.vapix tests/test_vapix.py
"""

from unittest.mock import call
from asynctest import Mock, patch
import json

from axis.vapix import Vapix
from .test_api_discovery import response_getApiList as api_discovery_response
from .test_basic_device_info import (
    response_getAllProperties as basic_device_info_response,
)
from .test_port_management import response_getPorts as io_port_management_response
from .test_param_cgi import response_param_cgi


def test_initialize_api_discovery():
    """Verify that you can initialize API Discovery and that devicelist parameters."""
    mock_config = Mock()
    mock_config.host = "mock_host"
    mock_config.url = "mock_url"
    mock_config.session.post = "mock_post"

    with patch(
        "axis.vapix.session_request",
        side_effect=[
            json.dumps(api_discovery_response),
            json.dumps(basic_device_info_response),
            json.dumps(io_port_management_response),
        ],
    ) as mock_request:
        vapix = Vapix(mock_config)
        vapix.initialize_api_discovery()

    assert len(mock_request.mock_calls) == 3
    mock_request.assert_has_calls(
        [
            call(
                "mock_post",
                "mock_url/axis-cgi/apidiscovery.cgi",
                json={"method": "getApiList", "apiVersion": "1.0"},
            ),
            call(
                "mock_post",
                "mock_url/axis-cgi/basicdeviceinfo.cgi",
                json={"method": "getAllProperties", "apiVersion": "1.1"},
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
        ]
    )

    assert vapix.firmware_version == "9.80.1"
    assert vapix.product_number == "M1065-LW"
    assert vapix.product_type == "Network Camera"
    assert vapix.serial_number == "ACCC12345678"


def test_initialize_params():
    """Verify that you can list parameters."""
    mock_config = Mock()
    mock_config.host = "mock_host"
    mock_config.url = "mock_url"
    mock_config.session.get = "mock_get"

    with patch(
        "axis.vapix.session_request", return_value=response_param_cgi
    ) as mock_request:
        vapix = Vapix(mock_config)
        vapix.initialize_params()

    mock_request.assert_called_with(
        "mock_get", "mock_url/axis-cgi/param.cgi?action=list"
    )
    assert vapix.params["root.Brand.Brand"].raw == "AXIS"
    assert vapix.firmware_version == "9.10.1"
    assert vapix.product_number == "M1065-LW"
    assert vapix.product_type == "Network Camera"
    assert vapix.serial_number == "ACCC12345678"


def test_initialize_params_no_data():
    """Verify that you can list parameters."""
    mock_config = Mock()
    mock_config.host = "mock_host"

    with patch("axis.vapix.session_request", return_value="key=value") as mock_request:
        vapix = Vapix(mock_config)
        vapix.initialize_params(preload_data=False)

    mock_request.assert_not_called


def test_initialize_ports():
    """Verify that you can list parameters."""
    mock_config = Mock()
    mock_config.host = "mock_host"
    mock_config.url = "mock_url"
    mock_config.session.get = "mock_get"

    with patch(
        "axis.vapix.session_request",
        return_value="""root.IOPort.I0.Direction=input
root.IOPort.I0.Usage=Button
""",
    ) as mock_request:
        vapix = Vapix(mock_config)
        vapix.initialize_ports()

    mock_request.assert_called_with(
        "mock_get", "mock_url/axis-cgi/param.cgi?action=list&group=root.Output"
    )
    assert vapix.ports["0"].direction == "input"


def test_initialize_users():
    """Verify that you can list parameters."""
    mock_config = Mock()
    mock_config.host = "mock_host"
    mock_config.url = "mock_url"
    mock_config.session.get = "mock_get"

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
